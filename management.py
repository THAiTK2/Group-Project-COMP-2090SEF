from abc import ABC, abstractmethod

class Person(ABC):
    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id
    
    @abstractmethod
    def get_role_details(self):
        pass

class Coach(Person):
    def __init__(self, name, member_id, specialization):
        super().__init__(name,member_id)
        self.specialization = specialization

    def get_role_details(self):
        return (f'Coach: {self.name}, Specialization: {self.specialization}')
    
class Student(Person):
    def __init__(self, name, member_id, gpa, attendance_rate):
        super().__init__(name, member_id)
        self.__gpa = 0.0
        self.attendance_rate = 0.0
        self.gpa = gpa
        self.attendance_rate = attendance_rate

    @property
    def gpa(self):
        return self.__gpa
    
    @gpa.setter
    def gpa(self, value):
        if not 0.0 <= value <= 4.0:
            raise ValueError('Invalid GPA. Must be between 0.0 and 4.0')
        self.__gpa = float(value)

    @property
    def attendance_rate(self):
        return self.__attendance_rate

    @attendance_rate.setter
    def attendance_rate(self, value):
        if not 0.0 <= value <= 100.0:
            raise ValueError('Attendance rate is must be between 0.0 and 100.0')
        self.__attendance_rate = float(value)

    def is_eligible(self):
        return self.__gpa >= 2.0
    
    def get_role_details(self):
        if self.eligible():
            status = 'Eligible'
        else:
            status = 'Ineligible'
        return (f'Student: {self.name}, ID: {self.member_id}, GPA: {self.gpa:.2f}, Attendance: {self.attendance_rate:.1f} ({status})')
    
class SportTeam(ABC):
    def __init__(self, team_name, coach):
        self.team_name = team_name
        self.coach = coach
        self.members = []

    def add_member(self,student):
        self.members.append(student)

    @abstractmethod
    def evaluate_performance(self):
        pass

class Footaball(SportTeam):
    def __init__(self, team_name, coach, goals_scored):
        super().__init__(team_name, coach)
        self.goals_scored = goals_scored

    def evaluate_performance(self):
        return (f'Football Team {self.team_name} performance: {self.goals_scored} goals scored.')
    
class BasketballTeam(SportTeam):
    def __init__(self, team_name, coach, points_per_game):
        super().__init__(team_name, coach)
        self.points_per_game = points_per_game

    def evaluate_performance(self):
        return (f'Basketball Team {self.team_name} performance: {self.points_per_game} PPG.')