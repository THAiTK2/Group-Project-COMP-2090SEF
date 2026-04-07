from abc import ABC, abstractmethod


# ---------------- Person hierarchy (Abstraction + Inheritance) ----------------
# This abstract class defines common fields/methods for all people in the system.
# Child classes (Student/Coach/Teacher) must implement get_role_details().
class Person(ABC):
    def __init__(self, name, member_id):
        # Normalize user input early to keep data clean in all modules.
        self.name = name.strip()
        self.member_id = member_id.strip()

    @abstractmethod
    def get_role_details(self):
        pass


# Student uses encapsulation:
# - private attributes (__gpa, __attendance_rate)
# - property setter validation before data is accepted.
class Student(Person):
    def __init__(self, name, member_id, gpa, attendance_rate):
        super().__init__(name, member_id)
        self.__gpa = 0.0
        self.__attendance_rate = 0.0
        self.gpa = gpa  # use setter to validate whether gpa in 0.0 to 4.0
        self.attendance_rate = attendance_rate

    @property
    def gpa(self):
        return self.__gpa

    @gpa.setter
    def gpa(self, value):
        # Business rule: GPA must stay in 0.0 - 4.0.
        if not 0.0 <= value <= 4.0:
            raise ValueError("GPA must be between 0.0 and 4.0.")
        self.__gpa = float(value)

    @property
    def attendance_rate(self):
        return self.__attendance_rate

    @attendance_rate.setter
    def attendance_rate(self, value):
        # Attendance is represented as percentage 0 - 100.
        if not 0.0 <= value <= 100.0:
            raise ValueError("Attendance rate must be between 0.0 and 100.0.")
        self.__attendance_rate = float(value)

    # Eligibility rule for joining sports teams.
    def is_eligible(self):
        # Current project rule: GPA >= 2.0 can be assigned to team.
        return self.__gpa >= 2.0

    def get_role_details(self):
        eligibility = "Eligible" if self.is_eligible() else "Ineligible"
        return (
            f"Student: {self.name} (ID: {self.member_id}) | "
            f"GPA: {self.gpa:.2f} | Attendance: {self.attendance_rate:.1f}% | "
            f"Status: {eligibility}"
        )


# Coach is a simple Person subtype with specialization field.
class Coach(Person):
    def __init__(self, name, member_id, specialization):
        super().__init__(name, member_id)
        self.specialization = specialization.strip()

    def get_role_details(self):
        return (
            f"Coach: {self.name} (ID: {self.member_id}) | "
            f"Specialization: {self.specialization}"
        )


# Teacher is a Person subtype with department field.
class Teacher(Person):
    def __init__(self, name, member_id, department):
        super().__init__(name, member_id)
        self.department = department.strip()

    def get_role_details(self):
        return (
            f"Teacher: {self.name} (ID: {self.member_id}) | "
            f"Department: {self.department}"
        )


# ---------------- Team hierarchy (Abstraction + Polymorphism) ----------------
# SportTeam is abstract and defines behavior contract for all sports.
# Each sport team class provides its own calculate_performance() logic.
class SportTeam(ABC):
    SPORT_NAME = "generic"

    def __init__(self, team_name, coach, extras=None):
        # team_name is normalized to avoid duplicated keys caused by extra spaces.
        self.team_name = team_name.strip()
        self.coach = coach
        self.members = []
        # extras holds additional metrics used in performance formulas.
        self.extras = self._sanitize_extras(extras)

    # Only eligible students can be added to team.
    def add_member(self, student):
        # Type safety: prevent wrong object from being added.
        if not isinstance(student, Student):
            raise TypeError("Only Student instances can be added to a team.")
        # Eligibility rule is checked again at domain level (not only in GUI).
        if not student.is_eligible():
            raise ValueError(
                f"Student '{student.name}' is ineligible (GPA must be >= 2.0)."
            )
        # Avoid duplicate assignment in the same team.
        if student.member_id in {member.member_id for member in self.members}:
            return
        self.members.append(student)

    @classmethod
    @abstractmethod
    def _sample_default_extras(cls):
        pass

    @abstractmethod
    def _default_extras(self):
        pass

    def _sanitize_extras(self, extras):
        # Fallback strategy:
        # 1) start from sport default values
        # 2) override with payload values if provided
        # 3) force float conversion; invalid input falls back to default
        defaults = self._default_extras()
        payload = extras if isinstance(extras, dict) else {}
        normalized = {}
        for key, default_value in defaults.items():
            raw_value = payload.get(key, default_value)
            try:
                normalized[key] = float(raw_value)
            except (TypeError, ValueError):
                normalized[key] = float(default_value)
        return normalized

    @abstractmethod
    def calculate_performance(self):
        pass

    @abstractmethod
    def performance_unit(self):
        pass


# Football team implementation (polymorphic performance formula).
class FootballTeam(SportTeam):
    SPORT_NAME = "football"

    def __init__(self, team_name, coach, goals_scored, extras=None):
        self.goals_scored = int(goals_scored)
        super().__init__(team_name, coach, extras)

    @classmethod
    def _sample_default_extras(cls):
        return {
            "shots_on_target": 8.0,
            "possession_rate": 55.0,
            "pass_accuracy": 82.0,
        }

    def _default_extras(self):
        return {
            "shots_on_target": max(float(self.goals_scored) * 2.4, 1.0),
            "possession_rate": 50.0 + min(float(self.goals_scored) * 0.9, 25.0),
            "pass_accuracy": 75.0 + min(float(self.goals_scored) * 0.7, 15.0),
        }

    def calculate_performance(self):
        # Composite score is used for demonstration/reporting in this project.
        return (
            float(self.goals_scored) * 3.0
            + self.extras["shots_on_target"] * 0.8
            + self.extras["possession_rate"] * 0.1
            + self.extras["pass_accuracy"] * 0.1
        )

    def performance_unit(self):
        return "composite score"


# Basketball team implementation.
class BasketballTeam(SportTeam):
    SPORT_NAME = "basketball"

    def __init__(self, team_name, coach, points_per_game, extras=None):
        self.points_per_game = float(points_per_game)
        super().__init__(team_name, coach, extras)

    @classmethod
    def _sample_default_extras(cls):
        return {
            "assists_per_game": 18.0,
            "rebounds_per_game": 36.0,
            "turnovers_per_game": 12.0,
        }

    def _default_extras(self):
        return {
            "assists_per_game": max(self.points_per_game * 0.22, 5.0),
            "rebounds_per_game": max(self.points_per_game * 0.45, 10.0),
            "turnovers_per_game": max(self.points_per_game * 0.12, 3.0),
        }

    def calculate_performance(self):
        return (
            self.points_per_game
            + self.extras["assists_per_game"] * 1.2
            + self.extras["rebounds_per_game"] * 0.8
            - self.extras["turnovers_per_game"] * 0.6
        )

    def performance_unit(self):
        return "composite score"


# Badminton team implementation.
class BadmintonTeam(SportTeam):
    SPORT_NAME = "badminton"

    def __init__(self, team_name, coach, win_rate, extras=None):
        # Win rate is percentage value.
        if not 0.0 <= float(win_rate) <= 100.0:
            raise ValueError("Win rate must be between 0.0 and 100.0.")
        self.win_rate = float(win_rate)
        super().__init__(team_name, coach, extras)

    @classmethod
    def _sample_default_extras(cls):
        return {
            "smash_win_rate": 52.0,
            "unforced_errors": 10.0,
        }

    def _default_extras(self):
        return {
            "smash_win_rate": min(self.win_rate * 0.75, 100.0),
            "unforced_errors": max(20.0 - self.win_rate * 0.12, 2.0),
        }

    def calculate_performance(self):
        return (
            self.win_rate * 0.7
            + self.extras["smash_win_rate"] * 0.25
            - self.extras["unforced_errors"] * 0.5
        )

    def performance_unit(self):
        return "composite score"


# Swimming team implementation.
class SwimmingTeam(SportTeam):
    SPORT_NAME = "swimming"

    def __init__(self, team_name, coach, average_meet_points, extras=None):
        self.average_meet_points = float(average_meet_points)
        super().__init__(team_name, coach, extras)

    @classmethod
    def _sample_default_extras(cls):
        return {
            "relay_points": 24.0,
            "avg_finish_rank": 4.0,
        }

    def _default_extras(self):
        return {
            "relay_points": max(self.average_meet_points * 0.55, 4.0),
            "avg_finish_rank": max(8.0 - self.average_meet_points * 0.08, 1.0),
        }

    def calculate_performance(self):
        return (
            self.average_meet_points
            + self.extras["relay_points"] * 0.6
            + (10.0 - self.extras["avg_finish_rank"]) * 1.5
        )

    def performance_unit(self):
        return "composite score"


# Track and field team implementation.
class TrackAndFieldTeam(SportTeam):
    SPORT_NAME = "track_and_field"

    def __init__(self, team_name, coach, medals_won, extras=None):
        self.medals_won = int(medals_won)
        super().__init__(team_name, coach, extras)

    @classmethod
    def _sample_default_extras(cls):
        return {
            "gold_medals": 3.0,
            "podium_finishes": 9.0,
            "season_best_count": 11.0,
        }

    def _default_extras(self):
        return {
            "gold_medals": max(float(self.medals_won) * 0.45, 0.0),
            "podium_finishes": max(float(self.medals_won) * 1.4, 1.0),
            "season_best_count": max(float(self.medals_won) * 1.7, 1.0),
        }

    def calculate_performance(self):
        return (
            float(self.medals_won) * 4.0
            + self.extras["gold_medals"] * 3.0
            + self.extras["podium_finishes"] * 1.5
            + self.extras["season_best_count"] * 0.7
        )

    def performance_unit(self):
        return "composite score"


# Handball team implementation.
class HandballTeam(SportTeam):
    SPORT_NAME = "handball"

    def __init__(self, team_name, coach, goals_per_match, extras=None):
        self.goals_per_match = float(goals_per_match)
        super().__init__(team_name, coach, extras)

    @classmethod
    def _sample_default_extras(cls):
        return {
            "save_rate": 32.0,
            "fast_break_goals": 4.0,
            "foul_rate": 7.0,
        }

    def _default_extras(self):
        return {
            "save_rate": min(25.0 + self.goals_per_match * 0.9, 60.0),
            "fast_break_goals": max(self.goals_per_match * 0.35, 0.5),
            "foul_rate": max(12.0 - self.goals_per_match * 0.18, 2.0),
        }

    def calculate_performance(self):
        return (
            self.goals_per_match * 2.0
            + self.extras["save_rate"] * 0.2
            + self.extras["fast_break_goals"] * 0.8
            - self.extras["foul_rate"] * 0.5
        )

    def performance_unit(self):
        return "composite score"


# ---------------- Account model ----------------
# UserAccount represents login identity used in authentication/authorization.
class UserAccount:
    def __init__(self, username, password, role, member_id):
        self.username = username
        self.password = password
        self.role = role
        self.member_id = member_id

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "member_id": self.member_id,
        }

    @classmethod
    def from_dict(cls, payload):
        return cls(
            username=str(payload["username"]),
            password=str(payload["password"]),
            role=str(payload["role"]),
            member_id=str(payload["member_id"]),
        )
