# Multi-Sport University Team Management System (MSUTMS)

An application for university sport teams 

## Requirement 
- Visual Studio Code
- Python extension for VSCode
- Python 3.10+
- pip

## Installation & Run (macOS + Windows)

### 1) Clone the repository
```bash
git clone https://github.com/THAiTK2/Group-Project-COMP-2090SEF.git
```

### 2) Enter Task 1 folder 
```bash 
cd task1
```

### 3) Create virtual environment
macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows(PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4) Install dependencies
```bash
pip install -r requirements.txt
```

### 5) Run the app
```bash
python main.py
```

if ```python``` does not work on Windows, try:
```cmd
py main.py
```

## 6) Default Login (for demo)
- Username: ```admin```
- Password: ```1234```

## 7) Main File Structure
- ```main.py```: GUI layer
- ```logic.py```: service logic
- ```repositories.py```: database CRUD operations
- ```database.py```: SQLite connection + schema initialization
- ```models.py```: OOP domain classes 

---

## Video introduction
[click this to watch the video in Google Drive ](https://drive.google.com/file/d/1TA1cZWbz0nNacvoHAkwpCX4l6Qf4zH0w/view?usp=drive_link)
since the video size is too large than 25MB. we cannot put the video into github
