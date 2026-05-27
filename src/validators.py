from typing import Tuple


def validate_age(age: int) -> Tuple[bool, str]:
    if age <= 0 or age > 120:
        return False, "Age must be between 1 and 120."
    return True, ""


def validate_marks(marks: int) -> Tuple[bool, str]:
    if marks < 0 or marks > 100:
        return False, "Marks must be between 0 and 100."
    return True, ""


def validate_attendance_percent(percent: float) -> Tuple[bool, str]:
    if percent < 0 or percent > 100:
        return False, "Attendance must be between 0 and 100."
    return True, ""
