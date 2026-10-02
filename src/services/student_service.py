"""Student service: CRUD operations plus JSON persistence."""
import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from src.models.student import Student
from src.utils.exceptions import (DataStorageError, DuplicateStudentError,
                                  StudentNotFoundError, ValidationError)

UPDATABLE_FIELDS = ("name", "email", "course", "year_level")


class StudentService:
    """Manages students and keeps them saved in a JSON file."""

    def __init__(self, data_file, logger, export_dir="exports"):
        self.data_file = Path(data_file)
        self.export_dir = Path(export_dir)
        self.logger = logger
        self._students = {}
        self._load()

    # ---------- persistence ----------
    def _read_file(self, path):
        """Read a JSON file and return a dict of Student objects."""
        with open(path, "r", encoding="utf-8") as f:
            records = json.load(f)
        if not isinstance(records, list):
            raise ValueError("Data file must contain a JSON list.")
        students = {}
        for record in records:
            student = Student.from_dict(record)
            students[student.student_id] = student
        return students

    def _load(self):
        """Load students from disk, recovering from the backup if needed."""
        if not self.data_file.exists():
            self.logger.info("Data file not found; creating %s", self.data_file)
            self._save()
            return

        backup = self.data_file.with_suffix(self.data_file.suffix + ".bak")
        try:
            self._students = self._read_file(self.data_file)
            self.logger.info("Loaded %d student(s)", len(self._students))
        except (OSError, ValueError, ValidationError) as exc:
            self.logger.error("Could not read %s: %s", self.data_file, exc)
            if backup.exists():
                try:
                    self._students = self._read_file(backup)
                    self.logger.warning("Recovered %d student(s) from backup", len(self._students))
                    self._save()
                    return
                except (OSError, ValueError, ValidationError) as exc2:
                    self.logger.error("Backup also unreadable: %s", exc2)
            raise DataStorageError(f"Could not load data file: {exc}") from exc

    def _save(self):
        """Write all students to disk safely (temp file, backup, then replace)."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.data_file.with_suffix(self.data_file.suffix + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump([s.to_dict() for s in self._students.values()], f, indent=2)
            if self.data_file.exists():
                shutil.copy2(self.data_file, self.data_file.with_suffix(self.data_file.suffix + ".bak"))
            os.replace(tmp, self.data_file)
        except OSError as exc:
            self.logger.error("Failed to save data: %s", exc)
            raise DataStorageError(f"Could not save data: {exc}") from exc

    # ---------- CRUD ----------
    def add_student(self, student_id, name, email, course, year_level):
        """Create a new student."""
        student = Student(student_id, name, email, course, year_level)  # validates
        if student.student_id in self._students:
            raise DuplicateStudentError(f"Student ID '{student.student_id}' already exists.")
        self._students[student.student_id] = student
        self._save()
        self.logger.info("Added student %s", student.student_id)
        return student

    def get_student(self, student_id):
        """Return one student or raise StudentNotFoundError."""
        try:
            return self._students[str(student_id).strip()]
        except KeyError:
            raise StudentNotFoundError(f"No student with ID '{student_id}'.") from None

    def list_students(self):
        """Return all students sorted by ID."""
        return sorted(self._students.values(), key=lambda s: s.student_id)

    def update_student(self, student_id, **changes):
        """Update name, email, course, or year_level of a student."""
        current = self.get_student(student_id)
        unknown = set(changes) - set(UPDATABLE_FIELDS)
        if unknown:
            raise ValidationError(f"Cannot update field(s): {', '.join(sorted(unknown))}")
        merged = current.to_dict()
        merged.update({k: v for k, v in changes.items() if v is not None})
        updated = Student.from_dict(merged)  # validates the new values
        self._students[current.student_id] = updated
        self._save()
        self.logger.info("Updated student %s", current.student_id)
        return updated

    def delete_student(self, student_id):
        """Delete a student."""
        student = self.get_student(student_id)
        del self._students[student.student_id]
        self._save()
        self.logger.info("Deleted student %s", student.student_id)

    # ---------- bonus features ----------
    def search_students(self, keyword):
        """Case-insensitive search across ID, name, email, and course."""
        key = keyword.strip().lower()
        return [s for s in self.list_students()
                if key in s.student_id.lower() or key in s.name.lower()
                or key in s.email.lower() or key in s.course.lower()]

    def export_csv(self):
        """Export all students to a timestamped CSV file and return its path."""
        try:
            self.export_dir.mkdir(parents=True, exist_ok=True)
            path = self.export_dir / f"students_{datetime.now():%Y%m%d_%H%M%S}.csv"
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["student_id", "name", "email", "course", "year_level"])
                writer.writeheader()
                writer.writerows(s.to_dict() for s in self.list_students())
        except OSError as exc:
            self.logger.error("Export failed: %s", exc)
            raise DataStorageError(f"Could not export data: {exc}") from exc
        self.logger.info("Exported %d student(s) to %s", len(self._students), path)
        return path
