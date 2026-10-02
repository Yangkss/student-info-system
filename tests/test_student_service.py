"""Unit tests for the Student model and StudentService."""
import csv
import logging
import tempfile
import unittest
from pathlib import Path

from src.models.student import Student
from src.services.student_service import StudentService
from src.utils.exceptions import (DataStorageError, DuplicateStudentError,
                                  StudentNotFoundError, ValidationError)


class StudentModelTests(unittest.TestCase):
    def test_valid_student(self):
        s = Student(" 1 ", " Ana ", "ana@example.com", "BSIT", "2")
        self.assertEqual((s.student_id, s.name, s.year_level), ("1", "Ana", 2))

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            Student("1", "Ana", "not-an-email", "BSIT", 2)

    def test_invalid_year(self):
        with self.assertRaises(ValidationError):
            Student("1", "Ana", "ana@example.com", "BSIT", 9)

    def test_missing_name(self):
        with self.assertRaises(ValidationError):
            Student("1", "  ", "ana@example.com", "BSIT", 2)


class StudentServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.logger = logging.getLogger("test-sis")
        self.service = self._new_service()

    def tearDown(self):
        self.tmp.cleanup()

    def _new_service(self):
        return StudentService(self.dir / "students.json", self.logger, self.dir / "exports")

    def _add(self, sid="1", name="Ana", course="BSIT"):
        return self.service.add_student(sid, name, f"{name.lower()}@example.com", course, 1)

    def test_add_and_get(self):
        self._add()
        self.assertEqual(self.service.get_student("1").name, "Ana")

    def test_duplicate_id(self):
        self._add()
        with self.assertRaises(DuplicateStudentError):
            self._add()

    def test_update(self):
        self._add()
        self.service.update_student("1", name="Anna", year_level=3)
        s = self.service.get_student("1")
        self.assertEqual((s.name, s.year_level), ("Anna", 3))

    def test_update_invalid_keeps_old_value(self):
        self._add()
        with self.assertRaises(ValidationError):
            self.service.update_student("1", email="bad")
        self.assertEqual(self.service.get_student("1").email, "ana@example.com")

    def test_delete(self):
        self._add()
        self.service.delete_student("1")
        with self.assertRaises(StudentNotFoundError):
            self.service.get_student("1")

    def test_persistence(self):
        self._add()
        self.assertEqual(len(self._new_service().list_students()), 1)

    def test_search(self):
        self._add("1", "Ana", "BSIT")
        self._add("2", "Ben", "BSCS")
        self.assertEqual([s.student_id for s in self.service.search_students("bscs")], ["2"])

    def test_export_csv(self):
        self._add()
        path = self.service.export_csv()
        with open(path, newline="", encoding="utf-8") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 1)

    def test_recovers_from_backup_when_file_corrupt(self):
        self._add("1")
        self._add("2", "Ben")  # second save creates a backup of the first
        (self.dir / "students.json").write_text("{ not json", encoding="utf-8")
        recovered = self._new_service()
        self.assertGreaterEqual(len(recovered.list_students()), 1)

    def test_corrupt_file_without_backup_raises(self):
        (self.dir / "students.json").write_text("{ not json", encoding="utf-8")
        with self.assertRaises(DataStorageError):
            self._new_service()


if __name__ == "__main__":
    unittest.main()
