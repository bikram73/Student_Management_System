from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils import load_json, save_json, built_in_sort, bubble_sort, quick_sort, merge_sort


class StudentStore:
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.students: List[Dict[str, Any]] = []
        self.deleted_stack: List[Dict[str, Any]] = []
        self.request_queue = deque()
        self.id_index: Dict[int, Dict[str, Any]] = {}
        self.name_index: Dict[str, List[Dict[str, Any]]] = {}
        self.course_index: Dict[str, List[Dict[str, Any]]] = {}
        self.id_set = set()

    def load(self) -> None:
        self.students = load_json(self.data_file, [])
        self._rebuild_indexes()

    def save(self) -> None:
        save_json(self.data_file, self.students)

    def _rebuild_indexes(self) -> None:
        self.id_index = {}
        self.name_index = {}
        self.course_index = {}
        self.id_set = set()
        for s in self.students:
            self.id_index[s["id"]] = s
            self.id_set.add(s["id"])
            name_key = s.get("name", "").strip().lower()
            self.name_index.setdefault(name_key, []).append(s)
            course_key = s.get("course", "").strip().lower()
            self.course_index.setdefault(course_key, []).append(s)

    def _next_id(self) -> int:
        if not self.students:
            return 1001
        return max(s["id"] for s in self.students) + 1

    def add_student(self, student: Dict[str, Any]) -> Dict[str, Any]:
        student_id = student.get("id")
        if not student_id:
            student_id = self._next_id()
            student["id"] = student_id
        if student_id in self.id_set:
            raise ValueError("Student ID already exists.")
        self.students.append(student)
        self._rebuild_indexes()
        self.save()
        return student

    def update_student(self, student_id: int, updates: Dict[str, Any]) -> bool:
        target = self.id_index.get(student_id)
        if not target:
            return False
        target.update(updates)
        self._rebuild_indexes()
        self.save()
        return True

    def delete_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        target = self.id_index.get(student_id)
        if not target:
            return None
        self.students = [s for s in self.students if s["id"] != student_id]
        self.deleted_stack.append(target)
        self._rebuild_indexes()
        self.save()
        return target

    def undo_delete(self) -> Optional[Dict[str, Any]]:
        if not self.deleted_stack:
            return None
        record = self.deleted_stack.pop()
        if record["id"] in self.id_set:
            return None
        self.students.append(record)
        self._rebuild_indexes()
        self.save()
        return record

    def search_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        return self.id_index.get(student_id)

    def search_by_name(self, name: str) -> List[Dict[str, Any]]:
        return self.name_index.get(name.strip().lower(), [])

    def search_by_course(self, course: str) -> List[Dict[str, Any]]:
        return self.course_index.get(course.strip().lower(), [])

    def sort_students(
        self,
        key: str,
        algorithm: str,
        reverse: bool = False,
        dataset: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        data = dataset if dataset is not None else self.students
        if algorithm == "bubble":
            return bubble_sort(data, key, reverse)
        if algorithm == "quick":
            return quick_sort(data, key, reverse)
        if algorithm == "merge":
            return merge_sort(data, key, reverse)
        return built_in_sort(data, key, reverse)

    def enqueue_request(self, request: Dict[str, Any]) -> None:
        self.request_queue.append(request)

    def dequeue_request(self) -> Optional[Dict[str, Any]]:
        if not self.request_queue:
            return None
        return self.request_queue.popleft()
