from abc import ABC, abstractmethod


# Base abstract class for all people in the system.
class Person(ABC):
    def __init__(self, name, member_id):
        self.name = name.strip()
        self.member_id = member_id.strip()

    @abstractmethod
    def get_role_details(self):
        pass


# Student model with encapsulated GPA and attendance validation.
class Student(Person):
    def __init__(self, name, member_id, gpa, attendance_rate):
        super().__init__(name, member_id)
        self.__gpa = 0.0
        self.__attendance_rate = 0.0
        self.gpa = gpa
        self.attendance_rate = attendance_rate

    @property
    def gpa(self):
        return self.__gpa

    @gpa.setter
    def gpa(self, value):
        if not 0.0 <= value <= 4.0:
            raise ValueError("GPA must be between 0.0 and 4.0.")
        self.__gpa = float(value)

    @property
    def attendance_rate(self):
        return self.__attendance_rate

    @attendance_rate.setter
    def attendance_rate(self, value):
        if not 0.0 <= value <= 100.0:
            raise ValueError("Attendance rate must be between 0.0 and 100.0.")
        self.__attendance_rate = float(value)

    # Eligibility rule for joining sports teams.
    def is_eligible(self):
        return self.__gpa >= 2.0

    def get_role_details(self):
        eligibility = "Eligible" if self.is_eligible() else "Ineligible"
        return (
            f"Student: {self.name} (ID: {self.member_id}) | "
            f"GPA: {self.gpa:.2f} | Attendance: {self.attendance_rate:.1f}% | "
            f"Status: {eligibility}"
        )


# Coach model.
class Coach(Person):
    def __init__(self, name, member_id, specialization):
        super().__init__(name, member_id)
        self.specialization = specialization.strip()

    def get_role_details(self):
        return (
            f"Coach: {self.name} (ID: {self.member_id}) | "
            f"Specialization: {self.specialization}"
        )


# Teacher model for staff-level management access.
class Teacher(Person):
    def __init__(self, name, member_id, department):
        super().__init__(name=name, member_id=member_id)
        self.department = department.strip()

    def get_role_details(self):
        return (
            f"Teacher: {self.name} (ID: {self.member_id}) | "
            f"Department: {self.department}"
        )


# Abstract sport team class for polymorphic performance evaluation.
class SportTeam(ABC):
    def __init__(self, team_name, coach):
        self.team_name = team_name.strip()
        self.coach = coach
        self.members = []

    # Only eligible students can be added to team.
    def add_member(self, student):
        if not isinstance(student, Student):
            raise TypeError("Only Student instances can be added to a team.")
        if not student.is_eligible():
            raise ValueError(
                f"Student '{student.name}' is ineligible (GPA must be >= 2.0)."
            )
        if student.member_id in {member.member_id for member in self.members}:
            return
        self.members.append(student)

    @abstractmethod
    def calculate_performance(self):
        pass

    @abstractmethod
    def performance_unit(self):
        pass


# Football team uses goals scored.
class FootballTeam(SportTeam):
    def __init__(self, team_name, coach, goals_scored):
        super().__init__(team_name, coach)
        self.goals_scored = int(goals_scored)

    def calculate_performance(self):
        return float(self.goals_scored)

    def performance_unit(self):
        return "goals"


# Basketball team uses points per game.
class BasketballTeam(SportTeam):
    def __init__(self, team_name, coach, points_per_game):
        super().__init__(team_name, coach)
        self.points_per_game = float(points_per_game)

    def calculate_performance(self):
        return self.points_per_game

    def performance_unit(self):
        return "PPG"


# Badminton team uses win rate.
class BadmintonTeam(SportTeam):
    def __init__(self, team_name, coach, win_rate):
        super().__init__(team_name=team_name, coach=coach)
        if not 0.0 <= win_rate <= 100.0:
            raise ValueError("Win rate must be between 0.0 and 100.0.")
        self.win_rate = float(win_rate)

    def calculate_performance(self):
        return self.win_rate

    def performance_unit(self):
        return "win rate (%)"


# Swimming team uses average meet points.
class SwimmingTeam(SportTeam):
    def __init__(self, team_name, coach, average_meet_points):
        super().__init__(team_name=team_name, coach=coach)
        self.average_meet_points = float(average_meet_points)

    def calculate_performance(self):
        return self.average_meet_points

    def performance_unit(self):
        return "meet points"


# Track and field team uses medal count.
class TrackAndFieldTeam(SportTeam):
    def __init__(self, team_name, coach, medals_won):
        super().__init__(team_name=team_name, coach=coach)
        self.medals_won = int(medals_won)

    def calculate_performance(self):
        return float(self.medals_won)

    def performance_unit(self):
        return "medals"


# Handball team uses goals per match.
class HandballTeam(SportTeam):
    def __init__(self, team_name, coach, goals_per_match):
        super().__init__(team_name=team_name, coach=coach)
        self.goals_per_match = float(goals_per_match)

    def calculate_performance(self):
        return self.goals_per_match

    def performance_unit(self):
        return "goals/match"


# Account model for role-based authorization.
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
