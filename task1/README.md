# COMP2090SEF Task 1 
# Multi-Sport University Team Management System(MSUTMS)

---

## Introduction 
In contemporary education enviroments, teachers manage many sports team using Excel or paper. This is very slow because the diversification of sports teams has outpaced traditional adminstrative methods. This project aims to improve the following problems.

1. we want to increase the administrative efficiency. Teachers need to spend more time to manage scattered Excel sheets and manual registrations. MSUTMS centralizes data concerning students, coaches and teams through a single interface.

2. we also want to validate eligibility compliance automatically. Since there is big chance of human error that checking from manual verification of GPA and attendance. MSUTMS can block students who fail academic standards or attendance requirement in real time.

3. Third, only managing teacher or coaches posses deep insights into their specific teams, leaving other departments disconnected. Teachers burdened with administrative tasks find it challenging to maintain a macroscopic view of performance and win rates across different sports. They cannot distribute resources effectively to enhance some teams quality. MSUTMS can generates  standardized report with various team.

4. Finally, there is a risk of data loss or versioning issues when useing local spreadsheet files. MSUTMS uses JSON file to store and update the records efficiently.

---

## Project Structure
```
Task 3
├─ main.py # menu flows
├─ logic.py # logic for validation, save/load, mangement system
├─ models.py # models of Class (teacher, student, coach, team, useraccount)
├─ data.json # dataset for saving input data
```

---
## How to run (to be continued)


---

## Core function and technology 
1. The system upports three user interface: Teacher, Coach and Student, each with specific permission(eg. only teacher and coach can edit the team member)
2. The system automatically check students who do not achieve the acadmic standards (GPA larger than 2.0) or attendance requirements.
3. The system tracks standardizes performance across different sport teams (eg Goals for Football, Point Per Game for Basketball)
4. The system use json to save and load data.

---

## The usage of OOP concept (to be continued in more detail and image)
### Encapsulation
The system use private attribute(__gpa,__attendance_rate) to protect sensitive student data. The actual data (__gpa) is hidden inside the object.We set the ```@gpa.setter``` becasue we don't want the user touch the __gpa directly. In ```@gpa.setter```, we require the user input/set suitable gpa value between 0.0 to 4.0 range. It can avoid user to set the student gpa 9999 leading system crash. Also, we use ```@property```  to turn a method ```gpa``` into a managed attribute.
<p><img src="/assert/image/encapsulation_1.png" height="500"></p>

### Inheritance
The system uses a hierachical structure to reduce the code duplication and create hierarchical relationships between categories. 
Hierachical Structure: ```subclasses``` -->(inherit form)  ```parent class``` 
* ```Student```,```Coach```,```Teacher``` --> ```Person```
*
```FootballTeam```,```BasketballTeam```,```BadmintonTeam```,```SwimmingTeam```,```TrackAndFieldTeam```,```HandballTeam``` --> ```SportTeam```
* Code Reuse:  subclasses like ```FootballTeam``` inherit the ```team_name```, ```coach``` attributes and ```add_member``` logic from parent class ```SportTeam```.We don't need to rewrite them.


### Polymorphism
The system uses the polymorphism in performance calcutetion and unit. ```calculate_performance()``` and ```performance_unit``` are called for all teams but the execution logic changes based on the sport.

### Abstraction
The system use Abstract Base Classes (ABC) to set blueprints.

---

## Something may improve or add(if have time)
1. Replace CLI to website
2. Add new modules (ingury record system, other teams)
3. Use SQLite instead of Json for better data handling

---

## Project Links( to be continued)
1. Project report:
2. Intrduction Video

---

## References (to be continued)
