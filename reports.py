from typing import Dict, Any, List, Tuple

from attendance import attendance_percent


def top_performers(students: List[Dict[str, Any]], min_marks: int = 85) -> List[Dict[str, Any]]:
    return [s for s in students if s.get("marks", 0) >= min_marks]


def low_attendance(students: List[Dict[str, Any]], threshold: float = 75.0) -> List[Dict[str, Any]]:
    return [s for s in students if attendance_percent(s) < threshold]


def course_report(students: List[Dict[str, Any]], course: str) -> List[Dict[str, Any]]:
    course_key = course.strip().lower()
    return [s for s in students if s.get("course", "").strip().lower() == course_key]


def marks_summary(students: List[Dict[str, Any]]) -> Tuple[int, int, float]:
    if not students:
        return 0, 0, 0.0
    marks = [s.get("marks", 0) for s in students]
    return min(marks), max(marks), round(sum(marks) / len(marks), 2)
