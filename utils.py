from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

COLORS = {
    "primary": "#2563EB",
    "secondary": "#38BDF8",
    "background": "#F8FAFC",
    "sidebar": "#0F172A",
    "card": "#FFFFFF",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    "text": "#1E293B",
    "text_muted": "#64748B",
}

DEFAULT_SETTINGS = {
    "admin_username": "admin",
    "admin_password": "admin123",
    "page_size": 10,
}


def load_json(path: Path, default: Any) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        save_json(path, default)
        return default
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return default
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


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


def built_in_sort(items: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    return sorted(items, key=lambda s: s.get(key, ""), reverse=reverse)


def bubble_sort(items: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    data = items[:]
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            a = data[j].get(key, "")
            b = data[j + 1].get(key, "")
            if (a > b and not reverse) or (a < b and reverse):
                data[j], data[j + 1] = data[j + 1], data[j]
    return data


def quick_sort(items: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    if len(items) <= 1:
        return items[:]
    pivot = items[len(items) // 2].get(key, "")
    left = [s for s in items if s.get(key, "") < pivot]
    middle = [s for s in items if s.get(key, "") == pivot]
    right = [s for s in items if s.get(key, "") > pivot]
    result = quick_sort(left, key) + middle + quick_sort(right, key)
    return list(reversed(result)) if reverse else result


def merge_sort(items: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    if len(items) <= 1:
        return items[:]
    mid = len(items) // 2
    left = merge_sort(items[:mid], key, reverse)
    right = merge_sort(items[mid:], key, reverse)
    return _merge(left, right, key, reverse)


def _merge(left: List[Dict[str, Any]], right: List[Dict[str, Any]], key: str, reverse: bool) -> List[Dict[str, Any]]:
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        a = left[i].get(key, "")
        b = right[j].get(key, "")
        if (a <= b and not reverse) or (a >= b and reverse):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
