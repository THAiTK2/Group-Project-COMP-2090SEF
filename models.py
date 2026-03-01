from abc import ABC, abstractmethod
from typing import Optional

class Person(ABC):  # abstract basic class for all people in the system
    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id

    @abstractmethod 
    def get_role_details(self): #return a human-readable role description
        pass


class Student(Person): # there is student athlete candidate
    def __init__(self,name,member_id,gpa,attendance_rate):
        super().__init__(name,member_id)
        self.__gpa = 0.0 # gpa grade range 0.0 to 4.0
        self.__attendance_rate = 0.0 # attendance percentage range 0.0 to 100.0
        self.gpa =gpa
        self.attendance_rate = attendance_rate

    @property
    def gpa(self): 
        # get the current gpa value
        return self.__gpa
    
    @gpa.setter 
    def gpa(self,value):
        # set the gpa with validation
        if not 0.0 <= value <= 4.0:
            raise ValueError('GPA must be between 0.0 and 4.0')
        self.__gpa = float(value)

    @property
    def attendance_rate(self):
        # get the current attendance rate percentage
        return self.__attendance_rate
    
    @attendance_rate.setter
    def attendance_rate(self, value):
        # set attendance rate validation
        if not 0.0 <= value <= 100.0:
            raise ValueError('Attendance rate must be between 0.0 and 100.0')
        self.__attendance_rate = float(value)

    def is_eligible(self):
        # if tthe student is eligible to participate the sport team, return ture
        # rule: GPA >= 2.0
        return self.__gpa >= 2.0
    
    def get_role_details(self): # return the student information summary
        if self.is_eligible():
            eligibility = 'Eligible'
        else:
            eligibility = 'Ineligible'
        return(
            f'Student: {self.name} (ID: {self.member_id})\n'
            f'GPA: P{self.gpa:2f} Attendance: {self.attendance_rate:.1f}%\n'
            f'Status: {eligibility}'
        )
    
class Coach(Person):
    # this is for coach 

    def __init__(self, name, member_id, specialization):
        super().__init__(name,member_id)
        self.specialization = specialization
    
    def get_role_details(self): # give the coach information summary
        return (
            f'Coach: {self.name} (ID: {self.member_id})'
            f'Specialiazation: {self.specialization}'
        )
    
class Teacher(Person):
    # this is for teacher
    def __init__(self,name, member_id,department):
        super().__init__(name,member_id)
        self.department = department

    def get_role_details(self): # give the teacher information summary
        return (
            f'Teacher: {self.name} (ID: {self.member_id})'
            f'Department: {self.department}'
        )
    
class SportTeam(ABC):
    # abstract base class for school sport teams
    def __init__(self, team_name, coach):
        self.team_name = team_name
        self.coach = coach
        self.members = []

    def add_member(self,student):
        # add the eligible student to the team
        
        if not isinstance(student, Student):
            raise TypeError('Only Student instance can be added to a team')
        if not student.is_eligible():
            raise ValueError(f'Student "{student.name}" is ineligible (GPA must >= 2.0)')
        if student.member_id in {member.member_id for member in self.members}:
            return 
        self.members.append(student)

    @abstractmethod
    def calculate_performance(self):
        # calculate and return sport specific performance value
        pass
    
    def performance_unit(self):
        # return the unit label for the performance metric
        pass 

class FootballTeam(SportTeam):
    
    def __init__(self,team_name, coach, goals_scored): # football team evaluated by goals scored
        super().__init__(team_name,coach)
        self.goals_scored = int(goals_scored)
    
    def calculate_performance(self):
        return float(self.goals_scored)
    
    def performance_unit(self):
        return 'goals'
    

class BasketballTeam(SportTeam):
    def __init__(self, team_name, coach, points_per_game): # basketball evaluate by points per game (PPG)
        super().__init__(team_name, coach)
        self.points_per_game = float(points_per_game)

    def calculate_performance(self):
        return self.points_per_game
    
    def performance_unit(self):
        return 'Points per Games (PPG)'

class BadmintonTeam(SportTeam):
    def __init__(self, team_name, coach, win_rate):
        super().__init__(team_name, coach)
        if not 0.0 <= win_rate <= 100.0:
            raise ValueError('win rate must be between 0.0 and 100.0')
        self.win_rate = float(win_rate)

    def calculate_performance(self):
        return self.win_rate
    
    def performance_unit(self):
        return 'win rate (%)'
    
class SwimmingTeam(SportTeam):
    def __init__(self, team_name, coach, average_meet_points):
        super().__init__(team_name, coach)
        self.average_meet_points = average_meet_points

    def calculate_performance(self):
        return self.average_meet_points
    
    def performance_unit(self):
        return 'meet points'
    
class TrackAndFieldTeam(SportTeam):    
    def __init__(self,team_name,coach, medals_won):
        super().__init__(team_name, coach)
        self.medals_won = medals_won

    def calculate_performance(self):
        return float(self.medals_won)
    
    def performance_unit(self):
        return 'medals'
    
class HandballTeam(SportTeam):
    def __init__(self, team_name, coach, goals_per_match):
        super().__init__(team_name, coach)
        self.goals_per_match = float(goals_per_match)

    def calculate_performance(self):
        return self.goals_per_match
    
    def performance_unit(self):
        return 'goals/match'

class EquipmentItem:
    # it is equipment type with stock management

    def __init__(self, name, total_quantity):
        if total_quantity < 0:
            raise ValueError('Total quantity cannot be negative.')
        self.name = name
        self.total_quantity = int(total_quantity)
        self.available_quantity = int(total_quantity)

    def allocate(self,quantity):
        # allocate equipment units to rental request
        if quantity <= 0:
            raise ValueError('Rental quantity must be greater than zero')
        if quantity > self.available_quantity:
            raise ValueError(
                f'Insufficient stock for "{self.name}"'
                f'Available: {self.available_quantity}'
            )
        self.available_quantity -= quantity
    
    def release(self, quantity):
        # release returne units back to availale stock

        if quantity <= 0:
            raise ValueError('Return quantity must be greater than zero')
        self.available_quantity = min(self.total_quantity, self.available_quantity + quantity)


class EquipmentRental:
    # this is one equipement rental transaction

    def __init__(
            self,
            rental_id,
            student_id,
            equipment_name,
            student_name,
            quantity,
            renter_type,
            borrowed_on,
            expected_return_on,
            team_name = None,
            is_returned = False
    ):
        self.rental_id = rental_id
        self.student_id = student_id
        self.equipment_name = equipment_name
        self.student_name = student_name
        self.quantity = quantity
        self.renter_type = renter_type
        self.borrowed_on = borrowed_on
        self.expected_return_on = expected_return_on
        self.team_name = team_name
        self.is_returned = is_returned

    def to_dict(self):
        # serialize the rental record into a Json dictionary
        return {
            'rental_id': self.rental_id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'equipment_name': self.equipment_name,
            'quantity': self.quantity,
            'renter_type': self.renter_type,
            'borrowed_on': self.borrowed_on,
            'expected_return_on': self.expected_return_on,
            'team_name': self.team_name,
            'is_returned': self.is_returned,
        }
    
    @classmethod
    def from_dict(cls,payload):
        # create a rental record from a dictionary payload
        return cls(
            rental_id=str(payload['rental_id']),
            student_id=str(payload['student_id']),
            student_name=str(payload['student_name']),
            equipment_name=str(payload['equipment_name']),
            quantity=int(payload['quantity']),
            renter_type=str(payload['renter_type']),
            borrowed_on=str(payload.get('borrowed_on', '')),
            expected_return_on=payload.get('expected_return_on'),
            team_name=payload.get('team_name'),
            is_returned=bool(payload.get('is_returned', False)),
        )

class UserAccount:
    # a longin account for authorization 
    def __init__(self,username,password,role,member_id):
        self.username = username
        self.password = password
        self.role = role
        self.member_id = member_id

    def to_dict(self):
        # serialize account into json dictionary
        return {
            'username': self.username,
            'password': self.password,
            'role': self.role,
            'member_id': self.member_id,
        }
    
    @classmethod
    def from_dict(cls, payload):
        # create account from dictionary payload
        return cls(
            username=str(payload['username']),
            password=str(payload['password']),
            role=str(payload['role']),
            member_id=str(payload['member_id']),

        )