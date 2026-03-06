# COMP2090SEF Task 1 
# Multi-Sport University Team Management System(MSUTMS)

---

## Introduction 
In contemporary education enviroments, teachers manage many sports team using Excel or paper. This is very slow because the diversification of sports teams has outpaced traditional adminstrative methods. This project aims to improve  the following problems.

1. we want to increase the administrative efficiency. Teachers need to spend more time to manage scattered Excel sheets and manual registrations. MSUTMS centralizes data concerning students, coaches and teams through a single interface.

2. we also want to validate eligibility compliance automatically. Since there is big chance of human error that checking from manual verification of GPA and attendance. MSUTMS can block students who fail academic standards or attendance requirement in real time.

3. Third, only managing teacher or coaches posses deep insights into their specific teams, leaving other departments disconnected. Teachers burdened with administrative tasks find it challenging to maintain a macroscopic view of performance and win rates across different sports. They cannot distribute resources effectively to enhance some teams quality. MSUTMS can generates  standardized report with various team.

4. Finally, there is a risk of data loss or versioning issues when useing local spreadsheet files. MSUTMS uses JSON file to store and update the records efficiently.

## Project Structure
```
Task 3
├─ main.py # menu flows
├─ logic.py # logic for validation, save/load, mangement system
├─ models.py # models of Class (teacher, student, coach, team, useraccount)
├─ data.json # dataset for saving input data
