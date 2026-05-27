# 🎓 Student Management System (Web)

A modern web-based Student Management System with a Flask backend and a clean HTML/CSS/JS dashboard.

## ✨ Features
- Add, view, search, update, and delete student records
- Attendance tracking and reports
- Dashboard stats (total students, average marks, attendance, top performers)
- Course-wise and performance reports
- Settings screen for API base URL and page size
- Student ID auto-generation starting at 1001

## 🧰 Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- Storage: JSON file

## 🚀 Local Run
### Backend
1. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

2. Start the API server:

```bash
python backend/app.py
```

### Frontend
Option 1: Open [frontend/index.html](frontend/index.html) in a browser.

Option 2 (recommended):
```bash
python -m http.server 5500 --directory frontend
```

Then visit `http://localhost:5500`.

## 🔐 Default Admin Login
- Username: admin
- Password: admin123

## 🗂️ Data Storage
- Students JSON: [backend/database/students.json](backend/database/students.json)
- Admin settings: [backend/settings.json](backend/settings.json)

## 🧭 File Structure
```
Student_Management_System/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── settings.json
│   └── database/
│       └── students.json
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── _redirects
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── login.js
├── docs/
│   └── PRD.md
├── assets/
│   └── icons/
├── main.py
├── src/
└── README.md
```

## 🧪 Legacy Desktop Version
The earlier Tkinter desktop app remains in [main.py](main.py) and [src/](src/).
