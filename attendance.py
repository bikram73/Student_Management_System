from typing import Dict, Any


def attendance_percent(student: Dict[str, Any]) -> float:
    total = student.get("attendance_total", 0)
    present = student.get("attendance_present", 0)
    if total <= 0:
        return 0.0
    return round((present / total) * 100, 2)


def set_attendance_percent(student: Dict[str, Any], percent: float) -> None:
    total = 100
    present = int(round((percent / 100) * total))
    student["attendance_total"] = total
    student["attendance_present"] = present


def mark_attendance(student: Dict[str, Any], present: bool) -> None:
    student["attendance_total"] = student.get("attendance_total", 0) + 1
    if present:
        student["attendance_present"] = student.get("attendance_present", 0) + 1
