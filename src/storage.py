import json
from pathlib import Path
from typing import List, Dict, Any


def ensure_data_file(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        file_path.write_text("[]", encoding="utf-8")


def load_students(file_path: Path) -> List[Dict[str, Any]]:
    ensure_data_file(file_path)
    raw = file_path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return data


def save_students(file_path: Path, students: List[Dict[str, Any]]) -> None:
    ensure_data_file(file_path)
    file_path.write_text(json.dumps(students, indent=2), encoding="utf-8")
