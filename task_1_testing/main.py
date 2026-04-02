from logic import TeamManagementSystem


# Authentication menu before entering role-based sessions.
def _show_auth_menu():
    print("\n=== Authentication ===")
    print("1. Login")
    print("0. Exit")


# Staff-only menu for teacher and coach.
def _show_staff_menu():
    print("\n=== Staff Menu (Teacher/Coach) ===")
    print("1. Add student (and optional account)")
    print("2. Add teacher account")
    print("3. Add coach (and optional account)")
    print("4. Create team")
    print("5. Assign student to team")
    print("6. Show team performance")
    print("7. List ineligible students")
    print("8. Save data to JSON")
    print("9. Load data from JSON")
    print("10. Data correction")
    print("11. Logout")
    print("0. Exit")


# Student menu with limited access.
def _show_student_menu():
    print("\n=== Student Menu ===")
    print("1. Show team performance")
    print("2. Show my profile")
    print("3. Logout")
    print("0. Exit")


# Data correction submenu for staff.
def _show_correction_menu():
    print("\n=== Data Correction Menu ===")
    print("1. Edit student")
    print("2. Edit coach")
    print("3. Edit team")
    print("0. Back")


# Prompt helper to reject empty input.
def _prompt_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


# Prompt helper that allows blank input to keep current value.
def _prompt_optional(prompt):
    return input(prompt).strip()


# Prompt sport-specific metric for team creation.
def _prompt_metric_by_sport(sport_type):
    sport_key = sport_type.strip().lower()

    if sport_key == "football":
        return float(input("Goals scored: ").strip())
    if sport_key == "basketball":
        return float(input("Points per game (PPG): ").strip())
    if sport_key == "badminton":
        return float(input("Win rate (0 - 100): ").strip())
    if sport_key == "swimming":
        return float(input("Average meet points: ").strip())
    if sport_key in {"track_and_field", "trackandfield", "athletics", "田徑"}:
        return float(input("Total medals won: ").strip())
    if sport_key in {"handball", "手球"}:
        return float(input("Goals per match: ").strip())

    raise ValueError(
        "Sport type must be football, basketball, badminton, "
        "swimming, track_and_field, or handball."
    )


# Prompt yes/no value.
def _prompt_yes_no(prompt):
    answer = _prompt_non_empty(prompt).strip().lower()
    return answer in {"y", "yes"}


# Data correction session loop for staff.
def _run_data_correction(system):
    while True:
        _show_correction_menu()
        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                student_id = _prompt_non_empty("Student ID: ")
                new_name = _prompt_optional(
                    "New name (leave blank to keep current): "
                )
                new_gpa_text = _prompt_optional(
                    "New GPA (leave blank to keep current): "
                )
                new_attendance_text = _prompt_optional(
                    "New attendance rate (leave blank to keep current): "
                )

                new_password = None
                if _prompt_yes_no("Reset password? (y/n): "):
                    new_password = _prompt_non_empty("New password: ")

                gpa = float(new_gpa_text) if new_gpa_text else None
                attendance_rate = (
                    float(new_attendance_text)
                    if new_attendance_text
                    else None
                )

                student = system.update_student_profile(
                    member_id=student_id,
                    name=new_name or None,
                    gpa=gpa,
                    attendance_rate=attendance_rate,
                    new_password=new_password,
                )
                print(f"Updated: {student.get_role_details()}")

            elif choice == "2":
                coach_id = _prompt_non_empty("Coach ID: ")
                new_name = _prompt_optional(
                    "New name (leave blank to keep current): "
                )
                new_specialization = _prompt_optional(
                    "New specialization (leave blank to keep current): "
                )

                new_password = None
                if _prompt_yes_no("Reset password? (y/n): "):
                    new_password = _prompt_non_empty("New password: ")

                coach = system.update_coach_profile(
                    member_id=coach_id,
                    name=new_name or None,
                    specialization=new_specialization or None,
                    new_password=new_password,
                )
                print(f"Updated: {coach.get_role_details()}")

            elif choice == "3":
                team_name = _prompt_non_empty("Team name: ")
                team = system.teams.get(team_name)
                if team is None:
                    raise ValueError(f"Team '{team_name}' not found.")

                new_coach_id = _prompt_optional(
                    "New coach ID (leave blank to keep current): "
                )
                current_metric = team.calculate_performance()
                new_metric_text = _prompt_optional(
                    "New metric "
                    f"({team.performance_unit()}, current: "
                    f"{current_metric:.2f}, leave blank to keep current): "
                )
                new_metric = float(new_metric_text) if new_metric_text else None

                updated_team = system.update_team(
                    team_name=team_name,
                    new_coach_id=new_coach_id or None,
                    new_metric=new_metric,
                )
                print(
                    f"Updated team '{updated_team.team_name}' | "
                    f"Coach: {updated_team.coach.name} | "
                    f"Performance: {updated_team.calculate_performance():.2f} "
                    f"{updated_team.performance_unit()}"
                )

            elif choice == "0":
                return

            else:
                print("Invalid menu choice. Please select a valid option.")

        except ValueError as error:
            print(f"Input error: {error}")
        except Exception as error:  # pylint: disable=broad-except
            print(f"Operation error: {error}")


# Staff session loop.
def _run_staff_session(system, role):
    if not system.is_staff_role(role):
        raise ValueError("Only teacher or coach can access staff menu.")

    while True:
        _show_staff_menu()
        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                name = _prompt_non_empty("Student name: ")
                student_id = _prompt_non_empty("Student ID: ")
                gpa = float(input("GPA (0.0 - 4.0): ").strip())
                attendance_rate = float(
                    input("Attendance rate (0 - 100): ").strip()
                )
                create_login = _prompt_yes_no(
                    "Create student login account? (y/n): "
                )

                username = None
                password = None
                if create_login:
                    username = _prompt_non_empty("Student username: ")
                    password = _prompt_non_empty("Student password: ")

                student = system.add_student(
                    name=name,
                    member_id=student_id,
                    gpa=gpa,
                    attendance_rate=attendance_rate,
                    username=username,
                    password=password,
                )
                print(f"Added: {student.get_role_details()}")

            elif choice == "2":
                name = _prompt_non_empty("Teacher name: ")
                teacher_id = _prompt_non_empty("Teacher ID: ")
                department = _prompt_non_empty("Department: ")
                username = _prompt_non_empty("Teacher username: ")
                password = _prompt_non_empty("Teacher password: ")

                teacher = system.add_teacher(
                    name=name,
                    member_id=teacher_id,
                    department=department,
                    username=username,
                    password=password,
                )
                print(f"Added: {teacher.get_role_details()}")

            elif choice == "3":
                name = _prompt_non_empty("Coach name: ")
                coach_id = _prompt_non_empty("Coach ID: ")
                specialization = _prompt_non_empty("Specialization: ")
                create_login = _prompt_yes_no(
                    "Create coach login account? (y/n): "
                )

                username = None
                password = None
                if create_login:
                    username = _prompt_non_empty("Coach username: ")
                    password = _prompt_non_empty("Coach password: ")

                coach = system.add_coach(
                    name=name,
                    member_id=coach_id,
                    specialization=specialization,
                    username=username,
                    password=password,
                )
                print(f"Added: {coach.get_role_details()}")

            elif choice == "4":
                sport_type = _prompt_non_empty(
                    "Sport type (football/basketball/badminton/"
                    "swimming/track_and_field/handball): "
                )
                team_name = _prompt_non_empty("Team name: ")
                coach_id = _prompt_non_empty("Coach ID: ")
                metric = _prompt_metric_by_sport(sport_type)
                team = system.create_team(
                    sport_type, team_name, coach_id, metric
                )
                print(
                    f"Created team '{team.team_name}' with coach "
                    f"{team.coach.name}."
                )

            elif choice == "5":
                student_id = _prompt_non_empty("Student ID: ")
                team_name = _prompt_non_empty("Team name: ")
                system.assign_student_to_team(student_id, team_name)
                print("Student assigned successfully.")

            elif choice == "6":
                reports = system.list_team_performance()
                if not reports:
                    print("No teams available.")
                else:
                    print("\nTeam Performance Report")
                    for line in reports:
                        print(f"- {line}")

            elif choice == "7":
                ineligible = system.get_ineligible_students()
                if not ineligible:
                    print("All students are eligible.")
                else:
                    print("\nIneligible Students (GPA < 2.0)")
                    for student in ineligible:
                        print(
                            f"- {student.name} (ID: {student.member_id}, "
                            f"GPA: {student.gpa:.2f})"
                        )

            elif choice == "8":
                file_path = _prompt_non_empty("JSON file path to save: ")
                system.save_to_json(file_path)
                print(f"Data saved to '{file_path}'.")

            elif choice == "9":
                file_path = _prompt_non_empty("JSON file path to load: ")
                system.load_from_json(file_path)
                print(f"Data loaded from '{file_path}'.")

            elif choice == "10":
                _run_data_correction(system)

            elif choice == "11":
                return "logout"

            elif choice == "0":
                return "exit"

            else:
                print("Invalid menu choice. Please select a valid option.")

        except ValueError as error:
            print(f"Input error: {error}")
        except FileNotFoundError:
            print("File error: JSON file not found.")
        except KeyError as error:
            print(f"Data error: Missing required field {error} in JSON file.")
        except Exception as error:  # pylint: disable=broad-except
            print(f"Operation error: {error}")


# Student session loop.
def _run_student_session(system, student_id):
    student = system.students.get(student_id)
    if student is None:
        raise ValueError(
            f"Student profile '{student_id}' does not exist. "
            "Please contact teacher/coach."
        )

    while True:
        _show_student_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            reports = system.list_team_performance()
            if not reports:
                print("No teams available.")
            else:
                print("\nTeam Performance Report")
                for line in reports:
                    print(f"- {line}")

        elif choice == "2":
            print(student.get_role_details())

        elif choice == "3":
            return "logout"

        elif choice == "0":
            return "exit"

        else:
            print("Invalid menu choice. Please select a valid option.")


# Program entry point.
def run_cli():
    system = TeamManagementSystem()

    print(
        "Default staff account: username='admin', password='1234'"
    )

    while True:
        _show_auth_menu()
        auth_choice = input("Select an option: ").strip()

        try:
            if auth_choice == "0":
                print("Exiting system. Goodbye.")
                break

            if auth_choice != "1":
                print("Invalid choice.")
                continue

            username = _prompt_non_empty("Username: ")
            password = _prompt_non_empty("Password: ")
            account = system.authenticate(username, password)

            if system.is_staff_role(account.role):
                result = _run_staff_session(system=system, role=account.role)
            elif account.role == "student":
                result = _run_student_session(
                    system=system,
                    student_id=account.member_id,
                )
            else:
                raise ValueError(f"Unsupported role: {account.role}")

            if result == "exit":
                print("Exiting system. Goodbye.")
                break

        except ValueError as error:
            print(f"Input/Auth error: {error}")
        except FileNotFoundError:
            print("File error: JSON file not found.")
        except KeyError as error:
            print(f"Data error: Missing required field {error} in JSON file.")
        except Exception as error:  # pylint: disable=broad-except
            print(f"Unexpected error: {error}")


if __name__ == "__main__":
    run_cli()
