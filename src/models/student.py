"""Student model with built-in data validation."""
import re
from dataclasses import dataclass, asdict

from src.utils.exceptions import ValidationError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Student:
    """A single student record."""

    student_id: str
    name: str
    email: str
    course: str
    year_level: int

    def __post_init__(self):
        # Clean whitespace, then validate every time a Student is created
        self.student_id = str(self.student_id).strip()
        self.name = str(self.name).strip()
        self.email = str(self.email).strip()
        self.course = str(self.course).strip()
        self.validate()

    def validate(self):
        """Raise ValidationError if any field is invalid."""
        if not self.student_id:
            raise ValidationError("Student ID is required.")
        if not self.name:
            raise ValidationError("Name is required.")
        if not EMAIL_PATTERN.match(self.email):
            raise ValidationError(f"'{self.email}' is not a valid email address.")
        if not self.course:
            raise ValidationError("Course is required.")
        try:
            self.year_level = int(self.year_level)
        except (TypeError, ValueError):
            raise ValidationError("Year level must be a whole number.")
        if not 1 <= self.year_level <= 6:
            raise ValidationError("Year level must be between 1 and 6.")

    def to_dict(self):
        """Convert to a plain dict for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """Build a Student from a dict (e.g. one loaded from JSON)."""
        try:
            return cls(**data)
        except TypeError as exc:
            raise ValidationError(f"Invalid student record: {exc}") from exc
