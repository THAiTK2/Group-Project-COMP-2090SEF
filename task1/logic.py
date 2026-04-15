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


'''    
    Service layer 
    TeamManagementSystem acts as the "use case" layer:
    receives requests from GUI/CLI
    validates business rules
    calls repository for SQL persistence
    rebuilds in-memory objects for OOP operations'''
class TeamManagementSystem:
    # Core application logic with SQLite persistence

    def __init__(self, db_path=None):
        # In-memory caches used by GUI/logic for fast object access
        self.students = {}
        self.coaches = {}
        self.teachers = {}
        self.teams = {}
        self.accounts = {}
        self.db_manager = DatabaseManager(db_path=db_path)
        self.repository = TeamManagementRepository(self.db_manager)

        # ensure minimum login account exists for first-time run
        self._seed_default_staff_account()
        # synchronize SQL data into domain objects
        self._refresh_state()
        # IMPORTANT:
        # initialization must not perform destructive cleanup.
        # any data maintenance should be invoked manually by developer/admin only.

        # Seed demo competition data only when applicable (idempotent check inside)
        #self.auto_seed_competition_demo_records()

    # public services
    def add_student(self, name, member_id, gpa, attendance_rate):
        # Student profile only: no login account is created.
        # build domain object first to enforce model-level validation (GPA and attendance)
        student = Student(name, member_id, float(gpa), float(attendance_rate))
        self.repository.add_student(
            name=student.name,
            member_id=student.member_id,
            gpa=student.gpa,
            attendance_rate=student.attendance_rate,
        )

        self._refresh_state()
        return self.students[student.member_id]

    def add_coach(
        self,
        name,
        member_id,
        specialization,
        username,
        password,
    ):
        # need to creat Coach account
        normalized_username = str(username).strip().lower()
        normalized_password = str(password)
        if not normalized_username:
            raise ValueError("Coach username is required.")
        if not normalized_password.strip():
            raise ValueError("Coach password is required.")
        if len(normalized_password.strip()) < 4:
            raise ValueError("Password must be at least 4 characters.")

        # Coach object creation ensures consistent domain shape
        coach = Coach(name, member_id, specialization)
        self.repository.add_coach_with_account(
            name=coach.name,
            member_id=coach.member_id,
            specialization=coach.specialization,
            username=normalized_username,
            password=normalized_password,
            role="coach",
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
        # Teacher account is required in this flow
        normalized_username = str(username).strip().lower()
        normalized_password = str(password)
        if not normalized_username:
            raise ValueError("Username cannot be empty.")
        if len(normalized_password.strip()) < 4:
            raise ValueError("Password must be at least 4 characters.")

        teacher = Teacher(name, member_id, department)
        self.repository.add_teacher_with_account(
            name=teacher.name,
            member_id=teacher.member_id,
            department=teacher.department,
            username=normalized_username,
            password=normalized_password,
            role="teacher",
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
        # Normalize username and role for consistent lookup and permission check
        normalized_username = username.strip().lower()
        normalized_role = role.strip().lower()

        # basic credential validation
        if not normalized_username:
            raise ValueError("Username cannot be empty.")
        if len(password.strip()) < 4:
            raise ValueError("Password must be at least 4 characters.")
        if normalized_role not in {"teacher", "coach"}:
            raise ValueError("Role must be teacher or coach.")

        self._refresh_state()

        # role-member mapping validation:
        # account role must match an existing domain member
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
        # Login checks current SQL state to avoid stale in-memory data
        self._refresh_state()
        account = self.accounts.get(username.strip().lower())
        if account is None or account.password != password:
            raise ValueError("Invalid username or password.")
        return account

    @staticmethod
    def is_staff_role(role):
        # Staff users are currently teacher and coach
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

        # Normalize sports aliases to canonical key before object creation
        canonical_sport = self._normalize_sport_type(sport_type)
        temp_team = self._build_team_object(
            sport_type=canonical_sport,
            team_name=team_name,
            coach=self.coaches[coach_id],
            metric_value=metric_value,
        )

        # persist only primal values in SQL. OOP object stays in memory cache
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

        # validate eligibility through domain object so rule is not bypassed by UI and SQL
        team.add_member(student)

        self.repository.add_team_member(team_name=team_name, student_id=student_id)
        self._refresh_state()

    def update_student_profile(
        self,
        member_id,
        name=None,
        gpa=None,
        attendance_rate=None,
    ):
        self._refresh_state()

        student = self.students.get(member_id)
        if student is None:
            raise ValueError(f"Student ID '{member_id}' not found.")

        # Update mutable fields only when optional input is provided.
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
            # Same password policy as create_account.
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

    def delete_student(self, member_id):
        self._refresh_state()
        normalized_member_id = str(member_id).strip()
        if not normalized_member_id:
            raise ValueError("Student ID cannot be empty.")
        if normalized_member_id not in self.students:
            raise ValueError(f"Student ID '{normalized_member_id}' not found.")

        self.repository.delete_student_with_account(normalized_member_id)
        self._refresh_state()

    def delete_coach(self, member_id):
        self._refresh_state()
        normalized_member_id = str(member_id).strip()
        if not normalized_member_id:
            raise ValueError("Coach ID cannot be empty.")
        if normalized_member_id not in self.coaches:
            raise ValueError(f"Coach ID '{normalized_member_id}' not found.")
        if self.repository.coach_has_team(normalized_member_id):
            raise ValueError(
                f"Coach ID '{normalized_member_id}' cannot be deleted because this coach still manages team(s)."
            )

        self.repository.delete_coach_with_account(normalized_member_id)
        self._refresh_state()

    def delete_teacher(self, member_id):
        self._refresh_state()
        normalized_member_id = str(member_id).strip()
        if not normalized_member_id:
            raise ValueError("Teacher ID cannot be empty.")
        if normalized_member_id not in self.teachers:
            raise ValueError(f"Teacher ID '{normalized_member_id}' not found.")

        self.repository.delete_teacher_with_account(normalized_member_id)
        self._refresh_state()

    def delete_team(self, team_name):
        self._refresh_state()
        normalized_team_name = str(team_name).strip()
        if not normalized_team_name:
            raise ValueError("Team name cannot be empty.")
        if normalized_team_name not in self.teams:
            raise ValueError(f"Team '{normalized_team_name}' not found.")

        self.repository.delete_team(normalized_team_name)
        self._refresh_state()

    def update_team(self, team_name, new_coach_id=None, new_metric=None):
        self._refresh_state()

        team = self.teams.get(team_name)
        if team is None:
            raise ValueError(f"Team '{team_name}' not found.")

        coach_id = team.coach.member_id
        # Update coach reference after validating coach existence
        if new_coach_id is not None:
            normalized_coach_id = new_coach_id.strip()
            if not normalized_coach_id:
                raise ValueError("Coach ID cannot be empty.")
            if normalized_coach_id not in self.coaches:
                raise ValueError(f"Coach ID '{normalized_coach_id}' not found.")
            coach_id = normalized_coach_id
            team.coach = self.coaches[normalized_coach_id]

        if new_metric is not None:
            # delegate metric conversion to helper for sport-specific handling.
            self._apply_metric_update(team, new_metric)

        self.repository.update_team(
            team_name=team_name,
            coach_id=coach_id,
            metric_value=self._extract_team_metric(team),
        )
        self._refresh_state()
        return self.teams[team_name]

    def list_team_performance(self):
        # Build readable report lines for CLI and student dashboard
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
        # central method used by reports tab and CLI
        self._refresh_state()
        return [
            student
            for student in self.students.values()
            if not student.is_eligible()
        ]

    def get_sql_snapshot(self):
        # return dashboard payload in "columns + rows" format for GUI grid rendering
        snapshot = self.repository.get_dashboard_snapshot()
        result = {}
        for table_name, rows in snapshot.items():
            columns = self.repository.list_table_columns(table_name)
            result[table_name] = {
                "columns": columns,
                "rows": [dict(row) for row in rows],
            }
        return result

    def add_team_competition_record(
        self,
        team_name,
        year,
        month,
        competition_name,
        result,
        opponent,
    ):
        # This method validates all business inputs before writing to SQL
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
        # Limit valid year/month range to avoid dirty records.
        if not 2000 <= normalized_year <= 2100:
            raise ValueError("Year must be between 2000 and 2100.")
        if not 1 <= normalized_month <= 12:
            raise ValueError("Month must be between 1 and 12.")

        normalized_result = str(result).strip().lower()
        # W/L/D simplified model
        if normalized_result not in {"win", "loss", "draw"}:
            raise ValueError("Result must be 'win', 'loss', or 'draw'.")

        team = self.teams[normalized_team_name]

        self.repository.add_competition_record(
            team_name=normalized_team_name,
            sport_type=team.SPORT_NAME,
            year=normalized_year,
            month=normalized_month,
            competition_name=normalized_competition_name,
            result=normalized_result,
            opponent=normalized_opponent,
        )

    def delete_competition_record(self, record_id):
        self._refresh_state()
        try:
            normalized_record_id = int(record_id)
        except (TypeError, ValueError) as error:
            raise ValueError("Competition record ID must be an integer.") from error

        if normalized_record_id <= 0:
            raise ValueError("Competition record ID must be a positive integer.")

        row = self.repository.get_competition_record_by_id(normalized_record_id)
        if row is None:
            raise ValueError(f"Competition record ID '{normalized_record_id}' not found.")

        self.repository.delete_competition_record(normalized_record_id)
        self._refresh_state()

    def list_team_records(
        self,
        team_name=None,
        year=None,
        month=None,
        competition_name=None,
    ):
        # query raw SQL rows and convert to plain Python dictionaries for GUI
        rows = self.repository.list_competition_records(
            team_name=team_name,
            year=year,
            month=month,
            competition_name=competition_name,
        )
        records = []
        for row in rows:
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
                    "created_at": str(row["created_at"]),
                }
            )
        return records

    def list_win_loss_summary(self, team_name=None, year=None, month=None):
        # aggregate query result is normalized into integer counters
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
                "draws": int(row["draws"] or 0),
                "total_matches": int(row["total_matches"] or 0),
            }
            for row in rows
        ]
    
    # we don't call this part because we have alreadly use SQL
    def seed_demo_competitions(self, force=False):
        # demo seeding is useful for first presentation/screenshots.
        # force=False keeps existing real data untouched.
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
                result = ("win", "draw", "loss")[index % 3]
                competition_name = f"{team.SPORT_NAME.title()} League Round {index + 1}"
                opponent = f"Opponent_{index + 1}"
                self.add_team_competition_record(
                    team_name=team_name,
                    year=year,
                    month=month,
                    competition_name=competition_name,
                    result=result,
                    opponent=opponent,
                )
                seeded += 1

        return seeded

    # still dont call this part in main.py
    def auto_seed_competition_demo_records(self):
        # Auto-seed only when:
        # teams exist
        # competition table is empty
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

    # internal helpers 
    def _refresh_state(self):
        # rebuild all in-memory domain objects from SQL tables
        # This keeps GUI logic consistent with latest persisted state
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
                # defensive handling: skip corrupted team row if referenced coach is missing
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
            # DB rehydration path:
            # keep historical team membership even if student becomes ineligible later.
            if student.member_id in {member.member_id for member in team.members}:
                continue
            team.members.append(student)

    def _seed_default_staff_account(self):
        # create default admin account if database is fresh
        if self.repository.get_account("admin") is not None:
            return

        self.repository.add_account(
            username="admin",
            password="1234",
            role="teacher",
            member_id="SYSTEM",
        )

    def _cleanup_records_without_accounts(self):
        # Deprecated maintenance helper (destructive).
        # This method is intentionally NOT called during app startup.
        # Run manually only when you explicitly need to normalize old datasets.
        #
        # Policy logic:
        # remove all student-role accounts but keep student profiles.
        self.repository.delete_accounts_by_role("student")

        # Remove coaches with no coach-role account.
        # Teams must be removed first because teams.coach_id has RESTRICT on delete
        for row in self.repository.list_coaches_without_account():
            coach_id = str(row["member_id"])
            self.repository.delete_teams_by_coach_id(coach_id)
            self.repository.delete_coach(coach_id)

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
