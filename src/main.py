"""Command-line menu for the Student Information System.

Run from the project root:  python -m src.main
"""
from src.services.student_service import StudentService
from src.utils.config import load_config
from src.utils.exceptions import SISError
from src.utils.logger import setup_logger

MENU = """
===== Student Information System =====
1. Add student
2. View all students
3. View one student
4. Update student
5. Delete student
6. Search students
7. Export to CSV
0. Exit
"""


def show(students):
    """Print students as a simple table."""
    if not students:
        print("No students found.")
        return
    print(f"{'ID':<12}{'Name':<24}{'Email':<28}{'Course':<12}{'Year'}")
    print("-" * 80)
    for s in students:
        print(f"{s.student_id:<12}{s.name:<24}{s.email:<28}{s.course:<12}{s.year_level}")


def ask(label, current=None):
    """Prompt for a value; pressing Enter keeps the current one (for updates)."""
    suffix = f" [{current}]" if current is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    return value if value else current


def handle_add(service):
    student = service.add_student(ask("Student ID"), ask("Name"), ask("Email"),
                                  ask("Course"), ask("Year level (1-6)"))
    print(f"Added {student.name} ({student.student_id}).")


def handle_update(service):
    current = service.get_student(ask("Student ID to update"))
    print("Press Enter to keep the current value.")
    service.update_student(current.student_id,
                           name=ask("Name", current.name),
                           email=ask("Email", current.email),
                           course=ask("Course", current.course),
                           year_level=ask("Year level", current.year_level))
    print("Student updated.")


def handle_delete(service):
    student = service.get_student(ask("Student ID to delete"))
    if input(f"Delete {student.name}? (y/n): ").strip().lower() == "y":
        service.delete_student(student.student_id)
        print("Student deleted.")
    else:
        print("Cancelled.")


def main():
    config = load_config()
    logger = setup_logger(config["log_file"], config["log_level"])
    service = StudentService(config["data_file"], logger, config["export_dir"])
    logger.info("Application started")

    actions = {
        "1": handle_add,
        "2": lambda s: show(s.list_students()),
        "3": lambda s: show([s.get_student(ask("Student ID"))]),
        "4": handle_update,
        "5": handle_delete,
        "6": lambda s: show(s.search_students(ask("Search keyword") or "")),
        "7": lambda s: print(f"Exported to {s.export_csv()}"),
    }

    while True:
        print(MENU)
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("Invalid option. Please choose 0-7.")
            continue
        try:
            action(service)
        except SISError as exc:  # expected, user-facing errors
            print(f"Error: {exc}")
        except Exception:  # unexpected: log the details, keep the app running
            logger.exception("Unexpected error")
            print("Something went wrong. Details were written to the log file.")

    logger.info("Application stopped")


if __name__ == "__main__":
    main()
