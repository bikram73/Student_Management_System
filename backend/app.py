from __future__ import annotations

import json
import os
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

    students = data if isinstance(data, list) else []
    changed = False
    for record in students:
        if not isinstance(record, dict):
            continue
        if normalize_attendance_record(record):
            changed = True

    if changed:
        save_students(students)

    return students


def save_students(students: List[Dict[str, Any]]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(students, indent=2), encoding="utf-8")


def validate_student(payload: Dict[str, Any]) -> Tuple[bool, str]:
    required = ["name", "age", "gender", "course", "department", "attendance", "contact"]
    for key in required:
        if key not in payload or str(payload[key]).strip() == "":
            return False, f"{key} is required."
    try:
        age = int(payload["age"])
        attendance = float(payload["attendance"])
    except ValueError:
        return False, "Age and attendance must be numeric."

    if age <= 0 or age > 120:
        return False, "Age must be between 1 and 120."
    if attendance < 0 or attendance > 100:
        return False, "Attendance must be between 0 and 100."
    return True, ""


def parse_test_scores(value: Any) -> List[float]:
    if value is None:
        return []

    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = [item.strip() for item in str(value).split(",") if item.strip()]

    scores: List[float] = []
    for item in raw_values:
        try:
            score = float(item)
        except (TypeError, ValueError):
            continue
        if 0 <= score <= 100:
            scores.append(round(score, 2))
    return scores


def derive_marks(payload: Dict[str, Any]) -> Tuple[int, List[float]]:
    test_scores = parse_test_scores(payload.get("test_scores"))
    if test_scores:
        marks = int(round(sum(test_scores) / len(test_scores)))
        return marks, test_scores
    return int(payload.get("marks", 0)), []


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


def initialize_attendance_counters(record: Dict[str, Any]) -> Tuple[int, int]:
    total = record.get("attendance_total_count")
    present = record.get("attendance_present_count")

    if isinstance(total, int) and isinstance(present, int) and total >= 0 and present >= 0:
        if present > total:
            present = total
            record["attendance_present_count"] = present
        return present, total

    attendance_percent = float(record.get("attendance", 0.0))
    attendance_percent = max(0.0, min(100.0, attendance_percent))

    total = 100
    present = int(round((attendance_percent / 100.0) * total))

    record["attendance_present_count"] = present
    record["attendance_total_count"] = total
    return present, total


def attendance_percentage(present: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((present / total) * 100.0, 2)


def normalize_attendance_record(record: Dict[str, Any]) -> bool:
    daily = get_daily_attendance(record)

    daily_present = 0
    daily_total = 0
    for entry in daily.values():
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        if status == "present":
            daily_present += 1
            daily_total += 1
        elif status == "absent":
            daily_total += 1

    new_present = daily_present
    new_total = daily_total
    new_attendance = attendance_percentage(new_present, new_total)

    changed = False
    if record.get("attendance_present_count") != new_present:
        record["attendance_present_count"] = new_present
        changed = True
    if record.get("attendance_total_count") != new_total:
        record["attendance_total_count"] = new_total
        changed = True
    if float(record.get("attendance", 0.0)) != float(new_attendance):
        record["attendance"] = new_attendance
        changed = True

    # Legacy base fields are now unused; keep them zeroed to avoid stale math.
    if record.get("attendance_base_present_count") != 0:
        record["attendance_base_present_count"] = 0
        changed = True
    if record.get("attendance_base_total_count") != 0:
        record["attendance_base_total_count"] = 0
        changed = True

    return changed


def today_key() -> str:
    return datetime.now().date().isoformat()


def get_daily_attendance(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    raw = record.get("attendance_daily")
    if isinstance(raw, dict):
        return raw
    record["attendance_daily"] = {}
    return record["attendance_daily"]


def ensure_attendance_base(record: Dict[str, Any]) -> Tuple[int, int]:
    base_present = record.get("attendance_base_present_count")
    base_total = record.get("attendance_base_total_count")
    if isinstance(base_present, int) and isinstance(base_total, int):
        if base_present < 0:
            base_present = 0
        if base_total < 0:
            base_total = 0
        if base_present > base_total:
            base_present = base_total
        record["attendance_base_present_count"] = base_present
        record["attendance_base_total_count"] = base_total
        return base_present, base_total

    present_count, total_count = initialize_attendance_counters(record)
    record["attendance_base_present_count"] = present_count
    record["attendance_base_total_count"] = total_count
    return present_count, total_count


def recompute_attendance(record: Dict[str, Any]) -> None:
    daily = get_daily_attendance(record)

    daily_present = 0
    daily_total = 0
    for entry in daily.values():
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        if status == "present":
            daily_present += 1
            daily_total += 1
        elif status == "absent":
            daily_total += 1

    present_count = daily_present
    total_count = daily_total

    record["attendance_present_count"] = present_count
    record["attendance_total_count"] = total_count
    record["attendance"] = attendance_percentage(present_count, total_count)


def serialize_student(record: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(record)
    daily = get_daily_attendance(record)
    today_entry = daily.get(today_key(), {})
    data["today_status"] = today_entry.get("status")
    data["today_locked"] = bool(today_entry.get("locked", False))
    return data


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
    page_rows = [serialize_student(s) for s in students[start:end]]

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

    marks, test_scores = derive_marks(payload)

    record = {
        "id": next_db_id(students),
        "student_id": student_id,
        "name": payload["name"].strip(),
        "age": int(payload["age"]),
        "gender": payload["gender"].strip(),
        "course": payload["course"].strip(),
        "department": payload["department"].strip(),
        "marks": marks,
        "test_scores": test_scores,
        "tests_count": len(test_scores),
        "attendance": float(payload["attendance"]),
        "attendance_present_count": 0,
        "attendance_total_count": 0,
        "attendance_base_present_count": 0,
        "attendance_base_total_count": 0,
        "attendance_daily": {},
        "contact": payload["contact"].strip(),
        "created_at": datetime.utcnow().isoformat(),
    }
    students.append(record)
    save_students(students)

    return jsonify({"data": serialize_student(record)})


@app.get("/api/students/<int:student_id>")
def get_student(student_id: int) -> Any:
    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404
    return jsonify({"data": serialize_student(record)})


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

    marks, test_scores = derive_marks(payload)

    record.update(
        {
            "name": payload["name"].strip(),
            "age": int(payload["age"]),
            "gender": payload["gender"].strip(),
            "course": payload["course"].strip(),
            "department": payload["department"].strip(),
            "marks": marks,
            "test_scores": test_scores,
            "tests_count": len(test_scores),
            "attendance": float(payload["attendance"]),
            "attendance_present_count": 0,
            "attendance_total_count": 0,
            "attendance_base_present_count": 0,
            "attendance_base_total_count": 0,
            "attendance_daily": {},
            "contact": payload["contact"].strip(),
        }
    )
    save_students(students)

    return jsonify({"data": serialize_student(record)})


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

    status = "present" if present else "absent"

    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404

    daily = get_daily_attendance(record)
    key = today_key()
    existing = daily.get(key, {})
    if existing.get("locked"):
        return jsonify({"error": "Today's attendance is locked for this student."}), 400

    daily[key] = {"status": status, "locked": False}
    recompute_attendance(record)
    save_students(students)

    return jsonify({"data": serialize_student(record)})


@app.post("/api/attendance/<int:student_id>/today")
def update_today_attendance(student_id: int) -> Any:
    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip().lower()
    if status not in {"present", "absent", "clear"}:
        return jsonify({"error": "status must be present, absent, or clear."}), 400

    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404

    daily = get_daily_attendance(record)
    key = today_key()
    existing = daily.get(key, {})
    if existing.get("locked"):
        return jsonify({"error": "Today's attendance is locked for this student."}), 400

    if status == "clear":
        if key in daily:
            del daily[key]
    else:
        daily[key] = {
            "status": status,
            "locked": bool(existing.get("locked", False)),
        }

    recompute_attendance(record)
    save_students(students)

    return jsonify({"data": serialize_student(record)})


@app.post("/api/attendance/<int:student_id>/today/lock")
def lock_today_attendance(student_id: int) -> Any:
    students = load_students()
    record = next((s for s in students if s.get("id") == student_id), None)
    if not record:
        return jsonify({"error": "Student not found."}), 404

    daily = get_daily_attendance(record)
    key = today_key()
    entry = daily.get(key)
    if not isinstance(entry, dict) or entry.get("status") not in {"present", "absent"}:
        return jsonify({"error": "Mark attendance for today before locking."}), 400

    entry["locked"] = True
    recompute_attendance(record)
    save_students(students)
    return jsonify({"data": serialize_student(record)})


@app.post("/api/attendance/today/lock-all")
def lock_today_attendance_all() -> Any:
    students = load_students()
    key = today_key()
    locked_count = 0

    for record in students:
        daily = get_daily_attendance(record)
        entry = daily.get(key)
        if not isinstance(entry, dict):
            continue
        if entry.get("status") not in {"present", "absent"}:
            continue
        if entry.get("locked"):
            continue
        entry["locked"] = True
        recompute_attendance(record)
        locked_count += 1

    if locked_count > 0:
        save_students(students)

    return jsonify({"locked_count": locked_count})


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
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
