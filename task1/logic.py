import json
from pathlib import Path

from models import (
    BadmintonTeam,
    BasketballTeam,
    Coach,
    FootballTeam,
    HandballTeam,
    SportTeam,
    Student,
    SwimmingTeam,
    Teacher,
    TrackAndFieldTeam,
    UserAccount,
)


# Core application logic with role-based access support.
class TeamManagementSystem:
    def __init__(self):
        self.students = {}
        self.coaches = {}
        self.teachers = {}
        self.teams = {}
        self.accounts = {}

        self._seed_default_staff_account()

    # Add a student and optionally create student login account.
    def add_student(
        self,
        name,
        member_id,
        gpa,
        attendance_rate,
        username=None,
        password=None,
    ):
        if member_id in self.students:
            raise ValueError(f"Student ID '{member_id}' already exists.")

        student = Student(name, member_id, gpa, attendance_rate)
        self.students[member_id] = student

        if username and password:
            self.create_account(
                username=username,
                password=password,
                role="student",
                member_id=member_id,
            )
        return student

    # Add a coach and optionally create coach login account.
    def add_coach(
        self,
        name,
        member_id,
        specialization,
        username=None,
        password=None,
    ):
        if member_id in self.coaches:
            raise ValueError(f"Coach ID '{member_id}' already exists.")

        coach = Coach(name, member_id, specialization)
        self.coaches[member_id] = coach

        if username and password:
            self.create_account(
                username=username,
                password=password,
                role="coach",
                member_id=member_id,
            )
        return coach

    # Add a teacher with mandatory login account.
    def add_teacher(
        self,
        name,
        member_id,
        department,
        username,
        password,
    ):
        if member_id in self.teachers:
            raise ValueError(f"Teacher ID '{member_id}' already exists.")

        teacher = Teacher(name, member_id, department)
        self.teachers[member_id] = teacher

        self.create_account(
            username=username,
            password=password,
            role="teacher",
            member_id=member_id,
        )
        return teacher

    # Create account for role-based authentication.
    def create_account(
        self,
        username,
        password,
        role,
        member_id,
    ):
        normalized_username = username.strip().lower()
        normalized_role = role.strip().lower()

        if not normalized_username:
            raise ValueError("Username cannot be empty.")
        if len(password.strip()) < 4:
            raise ValueError("Password must be at least 4 characters.")
        if normalized_username in self.accounts:
            raise ValueError(
                f"Username '{normalized_username}' already exists."
            )
        if normalized_role not in {"student", "teacher", "coach"}:
            raise ValueError("Role must be student, teacher, or coach.")

        if normalized_role == "student" and member_id not in self.students:
            raise ValueError(f"Student ID '{member_id}' not found.")
        if normalized_role == "teacher" and member_id not in self.teachers:
            raise ValueError(f"Teacher ID '{member_id}' not found.")
        if normalized_role == "coach" and member_id not in self.coaches:
            raise ValueError(f"Coach ID '{member_id}' not found.")

        account = UserAccount(
            username=normalized_username,
            password=password,
            role=normalized_role,
            member_id=member_id,
        )
        self.accounts[normalized_username] = account
        return account

    # Authenticate user login.
    def authenticate(self, username, password):
        account = self.accounts.get(username.strip().lower())
        if account is None or account.password != password:
            raise ValueError("Invalid username or password.")
        return account

    # Staff includes teacher and coach.
    @staticmethod
    def is_staff_role(role):
        return role.strip().lower() in {"teacher", "coach"}

    # Create team by sport type.
    def create_team(
        self,
        sport_type,
        team_name,
        coach_id,
        metric_value,
    ):
        if team_name in self.teams:
            raise ValueError(f"Team '{team_name}' already exists.")

        coach = self.coaches.get(coach_id)
        if coach is None:
            raise ValueError(f"Coach ID '{coach_id}' not found.")

        sport_key = sport_type.strip().lower()
        if sport_key == "football":
            team = FootballTeam(team_name, coach, int(metric_value))
        elif sport_key == "basketball":
            team = BasketballTeam(team_name, coach, float(metric_value))
        elif sport_key == "badminton":
            team = BadmintonTeam(team_name, coach, float(metric_value))
        elif sport_key == "swimming":
            team = SwimmingTeam(team_name, coach, float(metric_value))
        elif sport_key in {
            "track_and_field",
            "trackandfield",
            "athletics",
            "田徑",
        }:
            team = TrackAndFieldTeam(team_name, coach, int(metric_value))
        elif sport_key in {"handball", "手球"}:
            team = HandballTeam(team_name, coach, float(metric_value))
        else:
            raise ValueError(
                "Sport type must be football, basketball, badminton, "
                "swimming, track_and_field, or handball."
            )

        self.teams[team_name] = team
        return team

    # Assign student to a specific team.
    def assign_student_to_team(self, student_id, team_name):
        student = self.students.get(student_id)
        if student is None:
            raise ValueError(f"Student ID '{student_id}' not found.")

        team = self.teams.get(team_name)
        if team is None:
            raise ValueError(f"Team '{team_name}' not found.")

        team.add_member(student)

    # Update student profile and optionally reset student password.
    def update_student_profile(
        self,
        member_id,
        name=None,
        gpa=None,
        attendance_rate=None,
        new_password=None,
    ):
        student = self.students.get(member_id)
        if student is None:
            raise ValueError(f"Student ID '{member_id}' not found.")

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("Student name cannot be empty.")
            student.name = normalized_name

        if gpa is not None:
            student.gpa = float(gpa)

        if attendance_rate is not None:
            student.attendance_rate = float(attendance_rate)

        if new_password is not None:
            password_value = new_password.strip()
            if len(password_value) < 4:
                raise ValueError("Password must be at least 4 characters.")

            account = self._find_account_by_role_and_member(
                role="student",
                member_id=member_id,
            )
            if account is None:
                raise ValueError("No login account found for student.")
            account.password = new_password

        return student

    # Update coach profile and optionally reset coach password.
    def update_coach_profile(
        self,
        member_id,
        name=None,
        specialization=None,
        new_password=None,
    ):
        coach = self.coaches.get(member_id)
        if coach is None:
            raise ValueError(f"Coach ID '{member_id}' not found.")

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("Coach name cannot be empty.")
            coach.name = normalized_name

        if specialization is not None:
            normalized_specialization = specialization.strip()
            if not normalized_specialization:
                raise ValueError("Specialization cannot be empty.")
            coach.specialization = normalized_specialization

        if new_password is not None:
            password_value = new_password.strip()
            if len(password_value) < 4:
                raise ValueError("Password must be at least 4 characters.")

            account = self._find_account_by_role_and_member(
                role="coach",
                member_id=member_id,
            )
            if account is None:
                raise ValueError("No login account found for coach.")
            account.password = new_password

        return coach

    # Update team coach and metric by team name.
    def update_team(self, team_name, new_coach_id=None, new_metric=None):
        team = self.teams.get(team_name)
        if team is None:
            raise ValueError(f"Team '{team_name}' not found.")

        if new_coach_id is not None:
            normalized_coach_id = new_coach_id.strip()
            if not normalized_coach_id:
                raise ValueError("Coach ID cannot be empty.")
            coach = self.coaches.get(normalized_coach_id)
            if coach is None:
                raise ValueError(f"Coach ID '{normalized_coach_id}' not found.")
            team.coach = coach

        if new_metric is not None:
            self._apply_metric_update(team, new_metric)

        return team

    # Return all teams' performance summaries.
    def list_team_performance(self):
        lines = []
        for team_name in sorted(self.teams):
            team = self.teams[team_name]
            lines.append(
                (
                    f"{team.team_name} | Coach: {team.coach.name} | "
                    f"Performance: {team.calculate_performance():.2f} "
                    f"{team.performance_unit()} | Members: {len(team.members)}"
                )
            )
        return lines

    # Return student eligibility list where GPA < 2.0.
    def get_ineligible_students(self):
        return [
            student
            for student in self.students.values()
            if not student.is_eligible()
        ]

    # Save all core data to JSON.
    def save_to_json(self, file_path):
        payload = {
            "students": [
                {
                    "name": student.name,
                    "member_id": student.member_id,
                    "gpa": student.gpa,
                    "attendance_rate": student.attendance_rate,
                }
                for student in self.students.values()
            ],
            "coaches": [
                {
                    "name": coach.name,
                    "member_id": coach.member_id,
                    "specialization": coach.specialization,
                }
                for coach in self.coaches.values()
            ],
            "teachers": [
                {
                    "name": teacher.name,
                    "member_id": teacher.member_id,
                    "department": teacher.department,
                }
                for teacher in self.teachers.values()
            ],
            "accounts": [
                account.to_dict() for account in self.accounts.values()
            ],
            "teams": [
                {
                    "sport": team.__class__.__name__,
                    "team_name": team.team_name,
                    "coach_id": team.coach.member_id,
                    "metric": self._extract_team_metric(team),
                    "member_ids": [
                        student.member_id for student in team.members
                    ],
                }
                for team in self.teams.values()
            ],
        }

        Path(file_path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # Load all core data from JSON.
    def load_from_json(self, file_path):
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))

        self.students.clear()
        self.coaches.clear()
        self.teachers.clear()
        self.teams.clear()
        self.accounts.clear()

        for student_payload in data.get("students", []):
            student = Student(
                student_payload["name"],
                student_payload["member_id"],
                float(student_payload["gpa"]),
                float(student_payload["attendance_rate"]),
            )
            self.students[student.member_id] = student

        for coach_payload in data.get("coaches", []):
            coach = Coach(
                coach_payload["name"],
                coach_payload["member_id"],
                coach_payload["specialization"],
            )
            self.coaches[coach.member_id] = coach

        for teacher_payload in data.get("teachers", []):
            teacher = Teacher(
                teacher_payload["name"],
                teacher_payload["member_id"],
                teacher_payload["department"],
            )
            self.teachers[teacher.member_id] = teacher

        for account_payload in data.get("accounts", []):
            account = UserAccount.from_dict(account_payload)
            self.accounts[account.username] = account

        for team_payload in data.get("teams", []):
            team = self._build_team_from_record(team_payload)
            self.teams[team.team_name] = team

        for team_payload in data.get("teams", []):
            team = self.teams[team_payload["team_name"]]
            for member_id in team_payload.get("member_ids", []):
                if member_id in self.students:
                    team.add_member(self.students[member_id])

        if not self.accounts:
            self._seed_default_staff_account()

    # Bootstrap staff account to avoid first-run lockout.
    def _seed_default_staff_account(self):
        if "admin" in self.accounts:
            return
        self.accounts["admin"] = UserAccount(
            username="admin",
            password="1234",
            role="teacher",
            member_id="SYSTEM",
        )

    # Extract metric by concrete team type.
    @staticmethod
    def _extract_team_metric(team):
        if isinstance(team, FootballTeam):
            return float(team.goals_scored)
        if isinstance(team, BasketballTeam):
            return team.points_per_game
        if isinstance(team, BadmintonTeam):
            return team.win_rate
        if isinstance(team, SwimmingTeam):
            return team.average_meet_points
        if isinstance(team, TrackAndFieldTeam):
            return float(team.medals_won)
        if isinstance(team, HandballTeam):
            return team.goals_per_match
        raise ValueError("Unsupported team type for serialization.")

    # Find account by role and member id.
    def _find_account_by_role_and_member(self, role, member_id):
        normalized_role = role.strip().lower()
        for account in self.accounts.values():
            if (
                account.role.strip().lower() == normalized_role
                and account.member_id == member_id
            ):
                return account
        return None

    # Apply metric updates with sport-specific validation rules.
    @staticmethod
    def _apply_metric_update(team, metric_value):
        if isinstance(team, FootballTeam):
            team.goals_scored = int(metric_value)
            return
        if isinstance(team, BasketballTeam):
            team.points_per_game = float(metric_value)
            return
        if isinstance(team, BadmintonTeam):
            converted_value = float(metric_value)
            if not 0.0 <= converted_value <= 100.0:
                raise ValueError("Win rate must be between 0.0 and 100.0.")
            team.win_rate = converted_value
            return
        if isinstance(team, SwimmingTeam):
            team.average_meet_points = float(metric_value)
            return
        if isinstance(team, TrackAndFieldTeam):
            team.medals_won = int(metric_value)
            return
        if isinstance(team, HandballTeam):
            team.goals_per_match = float(metric_value)
            return
        raise ValueError("Unsupported team type for metric update.")

    # Rebuild team object from serialized payload.
    def _build_team_from_record(self, record):
        sport = record["sport"]
        team_name = record["team_name"]
        coach_id = record["coach_id"]
        metric = float(record["metric"])

        coach = self.coaches.get(coach_id)
        if coach is None:
            raise ValueError(f"Coach ID '{coach_id}' in file does not exist.")

        if sport == "FootballTeam":
            return FootballTeam(team_name, coach, int(metric))
        if sport == "BasketballTeam":
            return BasketballTeam(team_name, coach, metric)
        if sport == "BadmintonTeam":
            return BadmintonTeam(team_name, coach, metric)
        if sport == "SwimmingTeam":
            return SwimmingTeam(team_name, coach, metric)
        if sport == "TrackAndFieldTeam":
            return TrackAndFieldTeam(team_name, coach, int(metric))
        if sport == "HandballTeam":
            return HandballTeam(team_name, coach, metric)
        raise ValueError(f"Unsupported sport type in file: {sport}")
