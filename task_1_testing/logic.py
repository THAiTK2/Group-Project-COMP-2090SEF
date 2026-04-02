import json
from pathlib import Path

from database import DatabaseManager
from models import (
    BadmintonTeam,
    BasketballTeam,
    Coach,
    FootballTeam,
    HandballTeam,
    Student,
    SwimmingTeam,
    Teacher,
    TrackAndFieldTeam,
    UserAccount,
)
from repositories import TeamManagementRepository


class TeamManagementSystem:
    """Core application logic with SQLite persistence."""

    def __init__(self, db_path=None, auto_import_json=True, default_json_path=None):
        self.students = {}
        self.coaches = {}
        self.teachers = {}
        self.teams = {}
        self.accounts = {}
        self.default_json_path = (
            Path(default_json_path)
            if default_json_path is not None
            else Path(__file__).resolve().parent / "data.json"
        )

        self.db_manager = DatabaseManager(db_path=db_path)
        self.repository = TeamManagementRepository(self.db_manager)

        self._seed_default_staff_account()
        self._refresh_state()

        if auto_import_json:
            self.auto_migrate_from_default_json()

        self.auto_seed_competition_demo_records()

    # ---------- public services ----------
    def add_student(
        self,
        name,
        member_id,
        gpa,
        attendance_rate,
        username=None,
        password=None,
    ):
        student = Student(name, member_id, float(gpa), float(attendance_rate))
        self.repository.add_student(
            name=student.name,
            member_id=student.member_id,
            gpa=student.gpa,
            attendance_rate=student.attendance_rate,
        )

        if username and password:
            self.create_account(
                username=username,
                password=password,
                role="student",
                member_id=student.member_id,
            )

        self._refresh_state()
        return self.students[student.member_id]

    def add_coach(
        self,
        name,
        member_id,
        specialization,
        username=None,
        password=None,
    ):
        coach = Coach(name, member_id, specialization)
        self.repository.add_coach(
            name=coach.name,
            member_id=coach.member_id,
            specialization=coach.specialization,
        )

        if username and password:
            self.create_account(
                username=username,
                password=password,
                role="coach",
                member_id=coach.member_id,
            )

        self._refresh_state()
        return self.coaches[coach.member_id]

    def add_teacher(
        self,
        name,
        member_id,
        department,
        username,
        password,
    ):
        teacher = Teacher(name, member_id, department)
        self.repository.add_teacher(
            name=teacher.name,
            member_id=teacher.member_id,
            department=teacher.department,
        )

        self.create_account(
            username=username,
            password=password,
            role="teacher",
            member_id=teacher.member_id,
        )

        self._refresh_state()
        return self.teachers[teacher.member_id]

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
        if normalized_role not in {"student", "teacher", "coach"}:
            raise ValueError("Role must be student, teacher, or coach.")

        self._refresh_state()

        if normalized_role == "student" and member_id not in self.students:
            raise ValueError(f"Student ID '{member_id}' not found.")
        if (
            normalized_role == "teacher"
            and member_id not in self.teachers
            and member_id != "SYSTEM"
        ):
            raise ValueError(f"Teacher ID '{member_id}' not found.")
        if normalized_role == "coach" and member_id not in self.coaches:
            raise ValueError(f"Coach ID '{member_id}' not found.")

        self.repository.add_account(
            username=normalized_username,
            password=password,
            role=normalized_role,
            member_id=member_id,
        )
        self._refresh_state()
        return self.accounts[normalized_username]

    def authenticate(self, username, password):
        self._refresh_state()
        account = self.accounts.get(username.strip().lower())
        if account is None or account.password != password:
            raise ValueError("Invalid username or password.")
        return account

    @staticmethod
    def is_staff_role(role):
        return role.strip().lower() in {"teacher", "coach"}

    def create_team(
        self,
        sport_type,
        team_name,
        coach_id,
        metric_value,
    ):
        self._refresh_state()

        if coach_id not in self.coaches:
            raise ValueError(f"Coach ID '{coach_id}' not found.")

        canonical_sport = self._normalize_sport_type(sport_type)
        temp_team = self._build_team_object(
            sport_type=canonical_sport,
            team_name=team_name,
            coach=self.coaches[coach_id],
            metric_value=metric_value,
        )

        self.repository.add_team(
            team_name=temp_team.team_name,
            sport_type=canonical_sport,
            coach_id=coach_id,
            metric_value=self._extract_team_metric(temp_team),
        )
        self._refresh_state()
        return self.teams[temp_team.team_name]

    def assign_student_to_team(self, student_id, team_name):
        self._refresh_state()

        student = self.students.get(student_id)
        if student is None:
            raise ValueError(f"Student ID '{student_id}' not found.")

        team = self.teams.get(team_name)
        if team is None:
            raise ValueError(f"Team '{team_name}' not found.")

        # 使用 domain object 驗證資格，確保 OOP 規則不被 SQL 旁路
        team.add_member(student)

        self.repository.add_team_member(team_name=team_name, student_id=student_id)
        self._refresh_state()

    def update_student_profile(
        self,
        member_id,
        name=None,
        gpa=None,
        attendance_rate=None,
        new_password=None,
    ):
        self._refresh_state()

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

        self.repository.update_student(
            member_id=member_id,
            name=student.name,
            gpa=student.gpa,
            attendance_rate=student.attendance_rate,
        )

        if new_password is not None:
            password_value = new_password.strip()
            if len(password_value) < 4:
                raise ValueError("Password must be at least 4 characters.")

            account = self.repository.find_account_by_role_member("student", member_id)
            if account is None:
                raise ValueError("No login account found for student.")
            self.repository.update_account_password(
                username=account["username"],
                new_password=password_value,
            )

        self._refresh_state()
        return self.students[member_id]

    def update_coach_profile(
        self,
        member_id,
        name=None,
        specialization=None,
        new_password=None,
    ):
        self._refresh_state()

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

        self.repository.update_coach(
            member_id=member_id,
            name=coach.name,
            specialization=coach.specialization,
        )

        if new_password is not None:
            password_value = new_password.strip()
            if len(password_value) < 4:
                raise ValueError("Password must be at least 4 characters.")

            account = self.repository.find_account_by_role_member("coach", member_id)
            if account is None:
                raise ValueError("No login account found for coach.")
            self.repository.update_account_password(
                username=account["username"],
                new_password=password_value,
            )

        self._refresh_state()
        return self.coaches[member_id]

    def update_team(self, team_name, new_coach_id=None, new_metric=None):
        self._refresh_state()

        team = self.teams.get(team_name)
        if team is None:
            raise ValueError(f"Team '{team_name}' not found.")

        coach_id = team.coach.member_id
        if new_coach_id is not None:
            normalized_coach_id = new_coach_id.strip()
            if not normalized_coach_id:
                raise ValueError("Coach ID cannot be empty.")
            if normalized_coach_id not in self.coaches:
                raise ValueError(f"Coach ID '{normalized_coach_id}' not found.")
            coach_id = normalized_coach_id
            team.coach = self.coaches[normalized_coach_id]

        if new_metric is not None:
            self._apply_metric_update(team, new_metric)

        self.repository.update_team(
            team_name=team_name,
            coach_id=coach_id,
            metric_value=self._extract_team_metric(team),
        )
        self._refresh_state()
        return self.teams[team_name]

    def list_team_performance(self):
        self._refresh_state()
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

    def get_ineligible_students(self):
        self._refresh_state()
        return [
            student
            for student in self.students.values()
            if not student.is_eligible()
        ]

    def get_sql_snapshot(self):
        snapshot = self.repository.get_dashboard_snapshot()
        result = {}
        for table_name, rows in snapshot.items():
            columns = self.repository.list_table_columns(table_name)
            result[table_name] = {
                "columns": columns,
                "rows": [dict(row) for row in rows],
            }
        return result

    def list_supported_performance_types(self):
        return [
            FootballTeam.supported_performance_types(),
            BasketballTeam.supported_performance_types(),
            BadmintonTeam.supported_performance_types(),
            SwimmingTeam.supported_performance_types(),
            TrackAndFieldTeam.supported_performance_types(),
            HandballTeam.supported_performance_types(),
        ]

    def list_supported_competition_detail_fields(self):
        return [
            FootballTeam.supported_competition_detail_fields(),
            BasketballTeam.supported_competition_detail_fields(),
            BadmintonTeam.supported_competition_detail_fields(),
            SwimmingTeam.supported_competition_detail_fields(),
            TrackAndFieldTeam.supported_competition_detail_fields(),
            HandballTeam.supported_competition_detail_fields(),
        ]

    def add_team_competition_record(
        self,
        team_name,
        year,
        month,
        competition_name,
        result,
        opponent,
        details,
    ):
        self._refresh_state()
        normalized_team_name = str(team_name).strip()
        if normalized_team_name not in self.teams:
            raise ValueError(f"Team '{normalized_team_name}' not found.")

        normalized_competition_name = str(competition_name).strip()
        if not normalized_competition_name:
            raise ValueError("Competition name cannot be empty.")

        normalized_opponent = str(opponent).strip()
        if not normalized_opponent:
            raise ValueError("Opponent cannot be empty.")

        normalized_year = int(year)
        normalized_month = int(month)
        if not 2000 <= normalized_year <= 2100:
            raise ValueError("Year must be between 2000 and 2100.")
        if not 1 <= normalized_month <= 12:
            raise ValueError("Month must be between 1 and 12.")

        normalized_result = str(result).strip().lower()
        if normalized_result not in {"win", "loss"}:
            raise ValueError("Result must be 'win' or 'loss'.")

        team = self.teams[normalized_team_name]
        supported_fields = set(team.COMPETITION_DETAIL_FIELDS)
        payload = details if isinstance(details, dict) else {}
        normalized_details = {}
        for field in supported_fields:
            if field not in payload:
                raise ValueError(f"Missing detail field: {field}")
            try:
                normalized_details[field] = float(payload[field])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Detail field '{field}' must be numeric.") from error

        self.repository.add_competition_record(
            team_name=normalized_team_name,
            sport_type=team.SPORT_NAME,
            year=normalized_year,
            month=normalized_month,
            competition_name=normalized_competition_name,
            result=normalized_result,
            opponent=normalized_opponent,
            details=normalized_details,
        )

    def list_team_records(
        self,
        team_name=None,
        year=None,
        month=None,
        competition_name=None,
    ):
        rows = self.repository.list_competition_records(
            team_name=team_name,
            year=year,
            month=month,
            competition_name=competition_name,
        )
        records = []
        for row in rows:
            details = {}
            raw_details = row["details_json"]
            if raw_details:
                try:
                    details = json.loads(raw_details)
                except json.JSONDecodeError:
                    details = {}
            records.append(
                {
                    "id": int(row["id"]),
                    "team_name": str(row["team_name"]),
                    "sport_type": str(row["sport_type"]),
                    "year": int(row["year"]),
                    "month": int(row["month"]),
                    "competition_name": str(row["competition_name"]),
                    "result": str(row["result"]),
                    "opponent": str(row["opponent"]),
                    "details": details,
                    "created_at": str(row["created_at"]),
                }
            )
        return records

    def list_win_loss_summary(self, team_name=None, year=None, month=None):
        rows = self.repository.get_team_win_loss_summary(
            team_name=team_name,
            year=year,
            month=month,
        )
        return [
            {
                "team_name": str(row["team_name"]),
                "wins": int(row["wins"] or 0),
                "losses": int(row["losses"] or 0),
                "total_matches": int(row["total_matches"] or 0),
            }
            for row in rows
        ]

    def seed_demo_competitions(self, force=False):
        self._refresh_state()
        if not self.teams:
            return 0

        existing_count = self.repository.count_rows("competition_records")
        if existing_count > 0 and not force:
            return 0

        seeded = 0
        for team_name in sorted(self.teams.keys()):
            team = self.teams[team_name]
            for index in range(3):
                year = 2024 + index
                month = 3 + index
                result = "win" if index % 2 == 0 else "loss"
                competition_name = f"{team.SPORT_NAME.title()} League Round {index + 1}"
                opponent = f"Opponent_{index + 1}"
                details = self._build_demo_competition_details(team, index)
                self.add_team_competition_record(
                    team_name=team_name,
                    year=year,
                    month=month,
                    competition_name=competition_name,
                    result=result,
                    opponent=opponent,
                    details=details,
                )
                seeded += 1

        return seeded

    def auto_seed_competition_demo_records(self):
        self._refresh_state()
        if not self.teams:
            print("Skipped demo competition seed: no teams available")
            return False

        if self.repository.count_rows("competition_records") > 0:
            print("Skipped demo competition seed: records already exist")
            return False

        seeded_count = self.seed_demo_competitions(force=False)
        if seeded_count > 0:
            print(f"Auto-seeded {seeded_count} demo competition records into SQLite")
            return True
        return False

    def auto_migrate_from_default_json(self):
        json_path = self.default_json_path
        if not json_path.exists():
            print(f"Skipped auto-import: '{json_path.name}' not found")
            return False

        if not self._should_auto_import_json():
            print("Skipped auto-import: database already has data")
            return False

        try:
            self.load_from_json(str(json_path))
            print(f"Auto-imported {json_path.name} into SQLite")
            return True
        except Exception as error:  # pylint: disable=broad-except
            print(f"Auto-import failed: {error}")
            return False

    def save_to_json(self, file_path):
        self._refresh_state()
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
                    "extras": dict(getattr(team, "extras", {})),
                    "member_ids": [
                        student.member_id for student in team.members
                    ],
                }
                for team in self.teams.values()
            ],
            "competition_records": self.list_team_records(),
        }

        Path(file_path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_from_json(self, file_path):
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))

        self.repository.clear_all()

        for student_payload in data.get("students", []):
            self.repository.add_student(
                name=str(student_payload["name"]),
                member_id=str(student_payload["member_id"]),
                gpa=float(student_payload["gpa"]),
                attendance_rate=float(student_payload["attendance_rate"]),
            )

        for coach_payload in data.get("coaches", []):
            self.repository.add_coach(
                name=str(coach_payload["name"]),
                member_id=str(coach_payload["member_id"]),
                specialization=str(coach_payload["specialization"]),
            )

        for teacher_payload in data.get("teachers", []):
            self.repository.add_teacher(
                name=str(teacher_payload["name"]),
                member_id=str(teacher_payload["member_id"]),
                department=str(teacher_payload["department"]),
            )

        for account_payload in data.get("accounts", []):
            self.repository.add_account(
                username=str(account_payload["username"]).strip().lower(),
                password=str(account_payload["password"]),
                role=str(account_payload["role"]).strip().lower(),
                member_id=str(account_payload["member_id"]),
            )

        # 先建立 coach 快取讓 team 反序列化可查 coach
        self._refresh_state()

        for team_payload in data.get("teams", []):
            sport_type = self._json_sport_to_canonical(
                team_payload.get("sport", team_payload.get("sport_type", ""))
            )
            coach_id = str(team_payload["coach_id"])
            if coach_id not in self.coaches:
                raise ValueError(f"Coach ID '{coach_id}' in file does not exist.")

            temp_team = self._build_team_object(
                sport_type=sport_type,
                team_name=str(team_payload["team_name"]),
                coach=self.coaches[coach_id],
                metric_value=float(team_payload["metric"]),
                extras=team_payload.get("extras"),
            )
            self.repository.add_team(
                team_name=temp_team.team_name,
                sport_type=sport_type,
                coach_id=coach_id,
                metric_value=self._extract_team_metric(temp_team),
            )

        for team_payload in data.get("teams", []):
            team_name = str(team_payload["team_name"])
            for member_id in team_payload.get("member_ids", []):
                self.repository.add_team_member(
                    team_name=team_name,
                    student_id=str(member_id),
                )

        self._seed_default_staff_account()
        self._refresh_state()

        # Extras are stored in JSON only (v1), re-attach them to in-memory teams.
        for team_payload in data.get("teams", []):
            team_name = str(team_payload.get("team_name", "")).strip()
            team = self.teams.get(team_name)
            if team is None:
                continue
            extras = team_payload.get("extras")
            if isinstance(extras, dict):
                team.extras = team._sanitize_extras(extras)

        for record in data.get("competition_records", []):
            self.add_team_competition_record(
                team_name=record.get("team_name", ""),
                year=record.get("year"),
                month=record.get("month"),
                competition_name=record.get("competition_name", ""),
                result=record.get("result", ""),
                opponent=record.get("opponent", ""),
                details=record.get("details", {}),
            )

    # ---------- internal helpers ----------
    def _refresh_state(self):
        self.students = {}
        self.coaches = {}
        self.teachers = {}
        self.teams = {}
        self.accounts = {}

        for row in self.repository.list_students():
            student = Student(
                name=str(row["name"]),
                member_id=str(row["member_id"]),
                gpa=float(row["gpa"]),
                attendance_rate=float(row["attendance_rate"]),
            )
            self.students[student.member_id] = student

        for row in self.repository.list_coaches():
            coach = Coach(
                name=str(row["name"]),
                member_id=str(row["member_id"]),
                specialization=str(row["specialization"]),
            )
            self.coaches[coach.member_id] = coach

        for row in self.repository.list_teachers():
            teacher = Teacher(
                name=str(row["name"]),
                member_id=str(row["member_id"]),
                department=str(row["department"]),
            )
            self.teachers[teacher.member_id] = teacher

        for row in self.repository.list_accounts():
            account = UserAccount(
                username=str(row["username"]),
                password=str(row["password"]),
                role=str(row["role"]),
                member_id=str(row["member_id"]),
            )
            self.accounts[account.username] = account

        for row in self.repository.list_teams():
            coach_id = str(row["coach_id"])
            coach = self.coaches.get(coach_id)
            if coach is None:
                # 如果資料被手動改壞，保留可讀性並直接略過損壞隊伍
                continue

            team = self._build_team_object(
                sport_type=str(row["sport_type"]),
                team_name=str(row["team_name"]),
                coach=coach,
                metric_value=float(row["metric_value"]),
                extras=None,
            )
            self.teams[team.team_name] = team

        for row in self.repository.list_team_members():
            team_name = str(row["team_name"])
            student_id = str(row["student_id"])
            team = self.teams.get(team_name)
            student = self.students.get(student_id)
            if team is None or student is None:
                continue
            team.add_member(student)

    def _seed_default_staff_account(self):
        if self.repository.get_account("admin") is not None:
            return

        self.repository.add_account(
            username="admin",
            password="1234",
            role="teacher",
            member_id="SYSTEM",
        )

    def _should_auto_import_json(self):
        counts = self.repository.get_table_counts(
            ("students", "coaches", "teams", "accounts")
        )

        if counts["students"] > 0 or counts["coaches"] > 0 or counts["teams"] > 0:
            return False

        if counts["accounts"] == 0:
            return True

        if counts["accounts"] == 1:
            admin_account = self.repository.get_account("admin")
            if admin_account is None:
                return False
            return (
                str(admin_account["role"]).strip().lower() == "teacher"
                and str(admin_account["member_id"]) == "SYSTEM"
            )

        return False

    @staticmethod
    def _normalize_sport_type(sport_type):
        sport_key = sport_type.strip().lower()
        mapping = {
            "football": "football",
            "basketball": "basketball",
            "badminton": "badminton",
            "swimming": "swimming",
            "track_and_field": "track_and_field",
            "trackandfield": "track_and_field",
            "athletics": "track_and_field",
            "田徑": "track_and_field",
            "handball": "handball",
            "手球": "handball",
        }
        if sport_key not in mapping:
            raise ValueError(
                "Sport type must be football, basketball, badminton, "
                "swimming, track_and_field, or handball."
            )
        return mapping[sport_key]

    def _build_team_object(
        self,
        sport_type,
        team_name,
        coach,
        metric_value,
        extras=None,
    ):
        canonical_sport = self._normalize_sport_type(sport_type)

        if canonical_sport == "football":
            return FootballTeam(
                team_name,
                coach,
                int(float(metric_value)),
                extras=extras,
            )
        if canonical_sport == "basketball":
            return BasketballTeam(
                team_name,
                coach,
                float(metric_value),
                extras=extras,
            )
        if canonical_sport == "badminton":
            return BadmintonTeam(
                team_name,
                coach,
                float(metric_value),
                extras=extras,
            )
        if canonical_sport == "swimming":
            return SwimmingTeam(
                team_name,
                coach,
                float(metric_value),
                extras=extras,
            )
        if canonical_sport == "track_and_field":
            return TrackAndFieldTeam(
                team_name,
                coach,
                int(float(metric_value)),
                extras=extras,
            )
        if canonical_sport == "handball":
            return HandballTeam(
                team_name,
                coach,
                float(metric_value),
                extras=extras,
            )

        raise ValueError("Unsupported team type.")

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

    @staticmethod
    def _json_sport_to_canonical(sport_value):
        sport = str(sport_value)
        class_mapping = {
            "FootballTeam": "football",
            "BasketballTeam": "basketball",
            "BadmintonTeam": "badminton",
            "SwimmingTeam": "swimming",
            "TrackAndFieldTeam": "track_and_field",
            "HandballTeam": "handball",
        }
        if sport in class_mapping:
            return class_mapping[sport]
        return TeamManagementSystem._normalize_sport_type(sport)

    @staticmethod
    def _build_demo_competition_details(team, index):
        fields = list(getattr(team, "COMPETITION_DETAIL_FIELDS", ()))
        details = {}
        base = float(team.calculate_performance())
        for offset, field in enumerate(fields, start=1):
            value = max(base * (0.08 + 0.03 * offset) + index * offset, 0.0)
            details[field] = round(value, 2)
        return details
