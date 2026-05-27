from typing import List, Dict, Any, Tuple


def attendance_percent(student: Dict[str, Any]) -> float:
    total = student.get("attendance_total", 0)
    present = student.get("attendance_present", 0)
    if total <= 0:
        return 0.0
    return round((present / total) * 100, 2)


def top_performers(students: List[Dict[str, Any]], min_marks: int = 85) -> List[Dict[str, Any]]:
    return [s for s in students if s.get("marks", 0) >= min_marks]


def low_attendance(students: List[Dict[str, Any]], threshold: float = 75.0) -> List[Dict[str, Any]]:
    return [s for s in students if attendance_percent(s) < threshold]


def marks_summary(students: List[Dict[str, Any]]) -> Tuple[int, int, float]:
    if not students:
        return 0, 0, 0.0
    marks = [s.get("marks", 0) for s in students]
    return min(marks), max(marks), round(sum(marks) / len(marks), 2)
