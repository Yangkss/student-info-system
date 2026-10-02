# Student Information System

A command-line Student Information System written in Python. It manages student records (add, view, update, delete) and stores them in a JSON file. The project is built with a cloud-ready structure: modular code, external configuration, error handling, and logging.

## Features

- **CRUD operations:** add, view (all or one), update, and delete students
- **JSON storage:** records are saved in `data/students.json`
- **Data validation:** checks required fields, email format, and year level (1-6)
- **Search:** find students by ID, name, email, or course
- **CSV export:** export all records to a timestamped file
- **Error recovery:** safe file writes plus automatic restore from a backup if the data file is corrupted
- **Logging:** all actions and errors are written to `logs/app.log`
- **Configuration:** settings live in `config/config.json` and can be overridden with environment variables
- **Unit tests:** model validation, CRUD, persistence, search, export, and recovery

## Project Structure

```
student-info-system/
├── src/
│   ├── models/student.py            # Student model and validation
│   ├── services/student_service.py  # CRUD, JSON storage, search, export
│   ├── utils/
│   │   ├── config.py                # Configuration loader
│   │   ├── logger.py                # Logging setup
│   │   └── exceptions.py            # Custom exceptions
│   └── main.py                      # Command-line menu
├── data/students.json               # Student records
├── config/config.json               # Application settings
├── logs/                            # Log files
├── tests/test_student_service.py    # Unit tests
├── requirements.txt
└── .gitignore
```

## Getting Started

**Requirements:** Python 3.8 or newer. No extra packages are needed to run the app.

```bash
git clone https://github.com/biancaestacio/student-info-system.git
cd student-info-system
python -m src.main
```

On Windows you can use `py -m src.main`.

## Usage

The program shows a menu:

| Option | Action |
|--------|--------|
| 1 | Add a student |
| 2 | View all students |
| 3 | View one student by ID |
| 4 | Update a student (press Enter to keep a value) |
| 5 | Delete a student (asks for confirmation) |
| 6 | Search students |
| 7 | Export to CSV (saved in `exports/`) |
| 0 | Exit |

## Configuration

Edit `config/config.json`:

```json
{
  "data_file": "data/students.json",
  "log_file": "logs/app.log",
  "log_level": "INFO",
  "export_dir": "exports"
}
```

Environment variables override the file, which is useful on cloud hosts and in containers:

| Variable | Overrides |
|----------|-----------|
| `SIS_CONFIG` | Path to the config file |
| `SIS_DATA_FILE` | `data_file` |
| `SIS_LOG_FILE` | `log_file` |
| `SIS_LOG_LEVEL` | `log_level` |

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

## Design Notes

- **Separation of concerns:** the model validates data, the service handles storage and business rules, and `main.py` only handles user interaction.
- **Safe saving:** data is written to a temporary file, the previous version is kept as `students.json.bak`, and then the new file replaces the old one.
- **Error handling:** custom exceptions (`ValidationError`, `StudentNotFoundError`, `DuplicateStudentError`, `DataStorageError`) give clear messages to users, while unexpected errors are logged with full details.

## Git Workflow

Work was done on feature branches and merged into `main` with pull requests (for example `feature/student-model`, `feature/student-service`, `feature/cli-menu`, `feature/tests`). Commit messages describe a single change each.

## Author

Bianca Micaela Estacio
