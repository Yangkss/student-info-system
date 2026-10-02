"""Custom exceptions so callers can handle each failure type clearly."""


class SISError(Exception):
    """Base class for all Student Information System errors."""


class ValidationError(SISError):
    """Raised when student data is missing or invalid."""


class StudentNotFoundError(SISError):
    """Raised when a student ID does not exist."""


class DuplicateStudentError(SISError):
    """Raised when adding a student ID that already exists."""


class DataStorageError(SISError):
    """Raised when the data file cannot be read or written."""


class ConfigError(SISError):
    """Raised when the configuration file is invalid."""
