from typing import List, Dict, Any


def built_in_sort(students: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    return sorted(students, key=lambda s: s.get(key, ""), reverse=reverse)


def bubble_sort(students: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    items = students[:]
    n = len(items)
    for i in range(n):
        for j in range(0, n - i - 1):
            a = items[j].get(key, "")
            b = items[j + 1].get(key, "")
            if (a > b and not reverse) or (a < b and reverse):
                items[j], items[j + 1] = items[j + 1], items[j]
    return items


def quick_sort(students: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    if len(students) <= 1:
        return students[:]
    pivot = students[len(students) // 2].get(key, "")
    left = [s for s in students if s.get(key, "") < pivot]
    middle = [s for s in students if s.get(key, "") == pivot]
    right = [s for s in students if s.get(key, "") > pivot]
    result = quick_sort(left, key) + middle + quick_sort(right, key)
    return list(reversed(result)) if reverse else result
