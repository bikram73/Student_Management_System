from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS

ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = ROOT_DIR / "database" / "students.json"
SETTINGS_PATH = ROOT_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "admin_username": "admin",
    "admin_password": "admin123",
}

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def load_settings() -> Dict[str, Any]:
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding="utf-8")
        return DEFAULT_SETTINGS
    raw = SETTINGS_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return DEFAULT_SETTINGS
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return DEFAULT_SETTINGS


def load_students() -> List[Dict[str, Any]]:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text("[]", encoding="utf-8")
        return []
    raw = DATA_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_students(students: List[Dict[str, Any]]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(students, indent=2), encoding="utf-8")


def validate_student(payload: Dict[str, Any]) -> Tuple[bool, str]:
    required = ["name", "age", "gender", "course", "department", "marks", "attendance", "contact"]
    for key in required:
        if key not in payload or str(payload[key]).strip() == "":
            return False, f"{key} is required."
    try:
        age = int(payload["age"])
        marks = int(payload["marks"])
        attendance = float(payload["attendance"])
    except ValueError:
        return False, "Age, marks, and attendance must be numeric."

    if age <= 0 or age > 120:
        return False, "Age must be between 1 and 120."
    if marks < 0 or marks > 100:
        return False, "Marks must be between 0 and 100."
    if attendance < 0 or attendance > 100:
        return False, "Attendance must be between 0 and 100."
    return True, ""


def generate_student_id(students: List[Dict[str, Any]]) -> str:
    if not students:
        return "1001"

    numeric_ids = []
    for student in students:
        raw = str(student.get("student_id", "")).strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        if digits:
            numeric_ids.append(int(digits))

    max_id = max(numeric_ids, default=1000)
    return str(max_id + 1)


def next_db_id(students: List[Dict[str, Any]]) -> int:
    if not students:
        return 1
    return max(s.get("id", 0) for s in students) + 1


@app.get("/api/health")
def health() -> Any:
    return jsonify({"status": "ok"})


@app.post("/api/auth/login")
def login() -> Any:
    payload = request.get_json(silent=True) or {}
    settings = load_settings()
    if (
        payload.get("username") == settings.get("admin_username")
        and payload.get("password") == settings.get("admin_password")
    ):
        return jsonify({"success": True})
    return jsonify({"success": False}), 401


@app.get("/api/students")
def get_students() -> Any:
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    query = request.args.get("q", "").strip().lower()
    field = request.args.get("field", "name")

    students = load_students()
    if query:
        if field == "course":
            students = [s for s in students if query in s.get("course", "").lower()]
        elif field == "student_id":
            students = [s for s in students if query in s.get("student_id", "").lower()]
        elif field == "id":
            students = [s for s in students if str(s.get("id", "")) == query]
        else:
            students = [s for s in students if query in s.get("name", "").lower()]

    students.sort(key=lambda s: s.get("id", 0), reverse=True)
    total = len(students)
    start = (page - 1) * page_size
    end = start + page_size
    page_rows = students[start:end]

    return jsonify(
        {
            "data": page_rows,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@app.post("/api/students")
def add_student() -> Any:
    payload = request.get_json(silent=True) or {}
    valid, message = validate_student(payload)
    if not valid:
        return jsonify({"error": message}), 400

    students = load_students()
    student_id = payload.get("student_id") or generate_student_id(students)
    if any(s.get("student_id") == student_id for s in students):
        return jsonify({"error": "Student ID already exists."}), 400

    record = {
        "id": next_db_id(students),
        "student_id": student_id,
        "name": payload["name"].strip(),
        "age": int(payload["age"]),
        "gender": payload["gender"].strip(),
        "course": payload["course"].strip(),
        "department": payload["department"].strip(),
        "marks": int(payload["marks"]),
        "attendance": float(payload["attendance"]),
        "contact": payload["contact"].strip(),
        "created_at": datetime.utcnow().isoformat(),
    }
    students.append(record)
    save_students(students)

    return jsonify({"data": record})


@app.get("/api/students/<int:student_id>")
def get_student(student_id: int) -> Any:
    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404
    return jsonify({"data": record})


@app.put("/api/students/<int:student_id>")
def update_student(student_id: int) -> Any:
    payload = request.get_json(silent=True) or {}
    valid, message = validate_student(payload)
    if not valid:
        return jsonify({"error": message}), 400

    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404

    record.update(
        {
            "name": payload["name"].strip(),
            "age": int(payload["age"]),
            "gender": payload["gender"].strip(),
            "course": payload["course"].strip(),
            "department": payload["department"].strip(),
            "marks": int(payload["marks"]),
            "attendance": float(payload["attendance"]),
            "contact": payload["contact"].strip(),
        }
    )
    save_students(students)

    return jsonify({"data": record})


@app.delete("/api/students/<int:student_id>")
def delete_student(student_id: int) -> Any:
    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404
    students = [s for s in students if s.get("id") != student_id]
    save_students(students)
    return jsonify({"data": record})


@app.post("/api/attendance/<int:student_id>")
def update_attendance(student_id: int) -> Any:
    payload = request.get_json(silent=True) or {}
    present = bool(payload.get("present", False))

    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404

    attendance = float(record.get("attendance", 0))
    attendance = min(100.0, attendance + (1.0 if present else -1.0))
    attendance = max(0.0, attendance)
    record["attendance"] = attendance
    save_students(students)

    return jsonify({"data": record})


@app.get("/api/reports/top")
def report_top() -> Any:
    min_marks = int(request.args.get("min_marks", 85))
    students = load_students()
    rows = [s for s in students if int(s.get("marks", 0)) >= min_marks]
    rows.sort(key=lambda s: s.get("marks", 0), reverse=True)
    return jsonify({"data": rows})


@app.get("/api/reports/low-attendance")
def report_low_attendance() -> Any:
    threshold = float(request.args.get("threshold", 75))
    students = load_students()
    rows = [s for s in students if float(s.get("attendance", 0)) < threshold]
    rows.sort(key=lambda s: s.get("attendance", 0))
    return jsonify({"data": rows})


@app.get("/api/reports/course")
def report_course() -> Any:
    course = request.args.get("course", "").strip().lower()
    students = load_students()
    rows = [s for s in students if s.get("course", "").strip().lower() == course]
    rows.sort(key=lambda s: s.get("name", "").lower())
    return jsonify({"data": rows})


@app.get("/api/reports/summary")
def report_summary() -> Any:
    students = load_students()
    if not students:
        return jsonify({"min_marks": 0, "max_marks": 0, "avg_marks": 0, "avg_attendance": 0})

    marks = [int(s.get("marks", 0)) for s in students]
    attendance = [float(s.get("attendance", 0)) for s in students]
    return jsonify(
        {
            "min_marks": min(marks),
            "max_marks": max(marks),
            "avg_marks": round(sum(marks) / len(marks), 2),
            "avg_attendance": round(sum(attendance) / len(attendance), 2),
        }
    )


@app.get("/api/stats")
def stats() -> Any:
    students = load_students()
    total = len(students)
    if not students:
        return jsonify({"total": total, "avg_marks": 0, "avg_attendance": 0, "top_count": 0})

    marks = [int(s.get("marks", 0)) for s in students]
    attendance = [float(s.get("attendance", 0)) for s in students]
    top_count = len([m for m in marks if m >= 85])

    return jsonify(
        {
            "total": total,
            "avg_marks": round(sum(marks) / len(marks), 2),
            "avg_attendance": round(sum(attendance) / len(attendance), 2),
            "top_count": top_count,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
