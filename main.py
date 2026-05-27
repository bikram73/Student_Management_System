from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any, List

from utils import (
    COLORS,
    DEFAULT_SETTINGS,
    load_json,
    save_json,
    validate_age,
    validate_marks,
    validate_attendance_percent,
)
from students import StudentStore
from attendance import attendance_percent, set_attendance_percent, mark_attendance
from reports import top_performers, low_attendance, course_report, marks_summary

ROOT_DIR = Path(__file__).resolve().parent
DATA_FILE = ROOT_DIR / "database" / "students.json"
SETTINGS_FILE = ROOT_DIR / "database" / "settings.json"


class StudentApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1280x760")
        self.root.configure(bg=COLORS["background"])

        self.settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
        self.activity_log: List[str] = []

        self.store = StudentStore(DATA_FILE)
        self.store.load()

        self._configure_style()
        self._build_login()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["background"])
        style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
        style.configure("Sidebar.TFrame", background=COLORS["sidebar"])
        style.configure("Sidebar.TButton", background=COLORS["sidebar"], foreground="white")
        style.map(
            "Sidebar.TButton",
            background=[("active", COLORS["primary"])],
            foreground=[("active", "white")],
        )
        style.configure("Card.TFrame", background=COLORS["card"])
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TButton", padding=6)

    def _build_login(self) -> None:
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(fill="both", expand=True)

        card = ttk.Frame(self.login_frame, style="Card.TFrame", padding=24)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Admin Login", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 12))

        ttk.Label(card, text="Username").grid(row=1, column=0, sticky="w")
        ttk.Label(card, text="Password").grid(row=2, column=0, sticky="w")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Entry(card, textvariable=self.username_var).grid(row=1, column=1, pady=4)
        ttk.Entry(card, textvariable=self.password_var, show="*").grid(row=2, column=1, pady=4)

        default_user = self.settings.get("admin_username", "admin")
        default_pass = self.settings.get("admin_password", "admin123")
        ttk.Label(
            card,
            text=f"Default credentials: {default_user} / {default_pass}",
            foreground=COLORS["text_muted"],
        ).grid(row=3, column=0, columnspan=2, pady=(6, 0))

        ttk.Button(card, text="Login", command=self._handle_login).grid(row=4, column=0, columnspan=2, pady=(12, 0))

    def _handle_login(self) -> None:
        if (
            self.username_var.get() == self.settings.get("admin_username")
            and self.password_var.get() == self.settings.get("admin_password")
        ):
            self.login_frame.destroy()
            self._build_main_ui()
            return
        messagebox.showerror("Login Failed", "Invalid username or password.")

    def _build_main_ui(self) -> None:
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        sidebar = ttk.Frame(self.main_frame, style="Sidebar.TFrame", width=220)
        sidebar.pack(side="left", fill="y")

        content = ttk.Frame(self.main_frame)
        content.pack(side="right", fill="both", expand=True)

        ttk.Label(
            sidebar,
            text="Dashboard",
            background=COLORS["sidebar"],
            foreground="white",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=16)

        self.frames: Dict[str, ttk.Frame] = {}
        self.content_container = content

        for name, label in [
            ("dashboard", "Home"),
            ("add", "Add Student"),
            ("view", "View Students"),
            ("search", "Search"),
            ("update", "Update"),
            ("delete", "Delete"),
            ("attendance", "Attendance"),
            ("reports", "Reports"),
            ("requests", "Requests"),
            ("settings", "Settings"),
        ]:
            ttk.Button(sidebar, text=label, style="Sidebar.TButton", command=lambda n=name: self.show_frame(n)).pack(
                fill="x", padx=12, pady=4
            )

        self._create_dashboard_frame()
        self._create_add_frame()
        self._create_view_frame()
        self._create_search_frame()
        self._create_update_frame()
        self._create_delete_frame()
        self._create_attendance_frame()
        self._create_reports_frame()
        self._create_requests_frame()
        self._create_settings_frame()

        self.show_frame("dashboard")

    def show_frame(self, name: str) -> None:
        for frame in self.frames.values():
            frame.pack_forget()
        frame = self.frames[name]
        frame.pack(fill="both", expand=True)

    def _create_dashboard_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Student Management System", style="Header.TLabel").pack(anchor="w")

        stats = ttk.Frame(frame)
        stats.pack(fill="x", pady=16)

        self.stat_labels = {}
        for label in ["Total Students", "Avg Marks", "Attendance %", "Top Performers"]:
            card = ttk.Frame(stats, style="Card.TFrame", padding=16)
            card.pack(side="left", padx=8)
            ttk.Label(card, text=label, foreground=COLORS["text_muted"]).pack(anchor="w")
            value_label = ttk.Label(card, text="0", font=("Segoe UI", 14, "bold"))
            value_label.pack(anchor="w")
            self.stat_labels[label] = value_label

        ttk.Label(frame, text="Recent Activities", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(16, 4))
        self.activity_list = tk.Listbox(frame, height=8)
        self.activity_list.pack(fill="x")

        self.frames["dashboard"] = frame
        self._update_dashboard()

    def _create_add_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Add Student", style="Header.TLabel").pack(anchor="w")

        form = ttk.Frame(frame)
        form.pack(pady=12, fill="x")

        self.add_vars = {
            "id": tk.StringVar(),
            "name": tk.StringVar(),
            "age": tk.StringVar(),
            "gender": tk.StringVar(),
            "course": tk.StringVar(),
            "department": tk.StringVar(),
            "marks": tk.StringVar(),
            "attendance": tk.StringVar(),
            "contact": tk.StringVar(),
        }

        fields = [
            ("Student ID (optional)", "id"),
            ("Full Name", "name"),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Course", "course"),
            ("Department", "department"),
            ("Marks", "marks"),
            ("Attendance %", "attendance"),
            ("Contact Number", "contact"),
        ]

        for idx, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=idx, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=self.add_vars[key]).grid(row=idx, column=1, pady=4, sticky="ew")

        form.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Add Student", command=self._handle_add_student).pack(pady=8, anchor="w")

        self.frames["add"] = frame

    def _handle_add_student(self) -> None:
        try:
            age = int(self.add_vars["age"].get())
            marks = int(self.add_vars["marks"].get())
            attendance_value = float(self.add_vars["attendance"].get() or "0")
        except ValueError:
            messagebox.showerror("Invalid Input", "Age, marks, and attendance must be numbers.")
            return

        valid, msg = validate_age(age)
        if not valid:
            messagebox.showerror("Invalid Age", msg)
            return
        valid, msg = validate_marks(marks)
        if not valid:
            messagebox.showerror("Invalid Marks", msg)
            return
        valid, msg = validate_attendance_percent(attendance_value)
        if not valid:
            messagebox.showerror("Invalid Attendance", msg)
            return

        name = self.add_vars["name"].get().strip()
        if not name:
            messagebox.showerror("Invalid Name", "Name is required.")
            return

        student = {
            "id": 0,
            "name": name,
            "age": age,
            "gender": self.add_vars["gender"].get().strip(),
            "course": self.add_vars["course"].get().strip(),
            "department": self.add_vars["department"].get().strip(),
            "marks": marks,
            "attendance_total": 0,
            "attendance_present": 0,
            "contact": self.add_vars["contact"].get().strip(),
        }

        raw_id = self.add_vars["id"].get().strip()
        if raw_id:
            try:
                student["id"] = int(raw_id)
            except ValueError:
                messagebox.showerror("Invalid ID", "Student ID must be a number.")
                return

        set_attendance_percent(student, attendance_value)

        try:
            added = self.store.add_student(student)
        except ValueError as exc:
            messagebox.showerror("Duplicate ID", str(exc))
            return

        for var in self.add_vars.values():
            var.set("")
        self._log_activity(f"Added student {added['name']} (ID {added['id']})")
        self._refresh_tables()
        messagebox.showinfo("Success", "Student added successfully.")

    def _create_view_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="View Students", style="Header.TLabel").pack(anchor="w")

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=8)

        self.view_search_var = tk.StringVar()
        self.view_search_type = tk.StringVar(value="name")

        ttk.Entry(controls, textvariable=self.view_search_var).pack(side="left", padx=(0, 8))
        ttk.Combobox(controls, textvariable=self.view_search_type, values=["name", "course", "id"], width=10).pack(
            side="left"
        )
        ttk.Button(controls, text="Search", command=self._refresh_view_table).pack(side="left", padx=8)
        ttk.Button(controls, text="Reset", command=self._reset_view_search).pack(side="left")

        self.view_table = self._create_student_table(frame)
        self.view_table.pack(fill="both", expand=True, pady=12)

        pagination = ttk.Frame(frame)
        pagination.pack(fill="x")

        self.view_page = 0
        ttk.Button(pagination, text="Prev", command=lambda: self._change_page(-1)).pack(side="left")
        ttk.Button(pagination, text="Next", command=lambda: self._change_page(1)).pack(side="left", padx=6)
        self.view_page_label = ttk.Label(pagination, text="Page 1")
        self.view_page_label.pack(side="left", padx=8)

        self.frames["view"] = frame

    def _reset_view_search(self) -> None:
        self.view_search_var.set("")
        self.view_search_type.set("name")
        self.view_page = 0
        self._refresh_view_table()

    def _change_page(self, delta: int) -> None:
        page_size = int(self.settings.get("page_size", 10))
        filtered = self._filter_view_students()
        max_page = max((len(filtered) - 1) // page_size, 0)
        self.view_page = max(0, min(self.view_page + delta, max_page))
        self._refresh_view_table()

    def _filter_view_students(self) -> List[Dict[str, Any]]:
        term = self.view_search_var.get().strip().lower()
        search_type = self.view_search_type.get()
        if not term:
            return self.store.students
        results = []
        for student in self.store.students:
            if search_type == "id":
                if term.isdigit() and int(term) == student.get("id"):
                    results.append(student)
            elif search_type == "course":
                if term in student.get("course", "").lower():
                    results.append(student)
            else:
                if term in student.get("name", "").lower():
                    results.append(student)
        return results

    def _refresh_view_table(self) -> None:
        data = self._filter_view_students()
        page_size = int(self.settings.get("page_size", 10))
        start = self.view_page * page_size
        end = start + page_size
        page = data[start:end]
        self._populate_table(self.view_table, page)
        total_pages = max((len(data) - 1) // page_size + 1, 1)
        self.view_page_label.configure(text=f"Page {self.view_page + 1} of {total_pages}")

    def _create_search_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Search Student", style="Header.TLabel").pack(anchor="w")

        search_bar = ttk.Frame(frame)
        search_bar.pack(fill="x", pady=8)

        self.search_var = tk.StringVar()
        self.search_type = tk.StringVar(value="id")

        ttk.Entry(search_bar, textvariable=self.search_var).pack(side="left", padx=(0, 8))
        ttk.Combobox(search_bar, textvariable=self.search_type, values=["id", "name", "course"], width=10).pack(
            side="left"
        )
        ttk.Button(search_bar, text="Search", command=self._handle_search).pack(side="left", padx=8)

        self.search_table = self._create_student_table(frame)
        self.search_table.pack(fill="both", expand=True, pady=12)

        self.frames["search"] = frame

    def _handle_search(self) -> None:
        term = self.search_var.get().strip()
        if not term:
            messagebox.showwarning("Search", "Enter a search term.")
            return

        results = []
        search_type = self.search_type.get()
        if search_type == "id":
            try:
                student_id = int(term)
            except ValueError:
                messagebox.showerror("Invalid ID", "Student ID must be a number.")
                return
            match = self.store.search_by_id(student_id)
            if match:
                results = [match]
        elif search_type == "name":
            results = self.store.search_by_name(term)
        elif search_type == "course":
            results = self.store.search_by_course(term)

        self._populate_table(self.search_table, results)

    def _create_update_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Update Student", style="Header.TLabel").pack(anchor="w")

        form = ttk.Frame(frame)
        form.pack(fill="x", pady=8)

        self.update_id = tk.StringVar()
        ttk.Label(form, text="Student ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.update_id).grid(row=0, column=1, sticky="ew")
        ttk.Button(form, text="Load", command=self._load_update_student).grid(row=0, column=2, padx=8)

        self.update_vars = {
            "name": tk.StringVar(),
            "age": tk.StringVar(),
            "gender": tk.StringVar(),
            "course": tk.StringVar(),
            "department": tk.StringVar(),
            "marks": tk.StringVar(),
            "attendance": tk.StringVar(),
            "contact": tk.StringVar(),
        }

        fields = [
            ("Full Name", "name"),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Course", "course"),
            ("Department", "department"),
            ("Marks", "marks"),
            ("Attendance %", "attendance"),
            ("Contact Number", "contact"),
        ]

        for idx, (label, key) in enumerate(fields, start=1):
            ttk.Label(form, text=label).grid(row=idx, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=self.update_vars[key]).grid(row=idx, column=1, columnspan=2, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)
        ttk.Button(frame, text="Update Student", command=self._handle_update_student).pack(anchor="w", pady=8)

        self.frames["update"] = frame

    def _load_update_student(self) -> None:
        try:
            student_id = int(self.update_id.get())
        except ValueError:
            messagebox.showerror("Invalid ID", "Student ID must be a number.")
            return

        student = self.store.search_by_id(student_id)
        if not student:
            messagebox.showwarning("Not Found", "Student not found.")
            return

        self.update_vars["name"].set(student.get("name", ""))
        self.update_vars["age"].set(str(student.get("age", "")))
        self.update_vars["gender"].set(student.get("gender", ""))
        self.update_vars["course"].set(student.get("course", ""))
        self.update_vars["department"].set(student.get("department", ""))
        self.update_vars["marks"].set(str(student.get("marks", "")))
        self.update_vars["attendance"].set(str(attendance_percent(student)))
        self.update_vars["contact"].set(student.get("contact", ""))

    def _handle_update_student(self) -> None:
        try:
            student_id = int(self.update_id.get())
            age = int(self.update_vars["age"].get())
            marks = int(self.update_vars["marks"].get())
            attendance_value = float(self.update_vars["attendance"].get())
        except ValueError:
            messagebox.showerror("Invalid Input", "ID, age, marks, and attendance must be numbers.")
            return

        valid, msg = validate_age(age)
        if not valid:
            messagebox.showerror("Invalid Age", msg)
            return
        valid, msg = validate_marks(marks)
        if not valid:
            messagebox.showerror("Invalid Marks", msg)
            return
        valid, msg = validate_attendance_percent(attendance_value)
        if not valid:
            messagebox.showerror("Invalid Attendance", msg)
            return

        updates = {
            "name": self.update_vars["name"].get().strip(),
            "age": age,
            "gender": self.update_vars["gender"].get().strip(),
            "course": self.update_vars["course"].get().strip(),
            "department": self.update_vars["department"].get().strip(),
            "marks": marks,
            "contact": self.update_vars["contact"].get().strip(),
        }
        set_attendance_percent(updates, attendance_value)

        if self.store.update_student(student_id, updates):
            self._log_activity(f"Updated student ID {student_id}")
            self._refresh_tables()
            messagebox.showinfo("Updated", "Student updated successfully.")
            return
        messagebox.showerror("Update Failed", "Student not found.")

    def _create_delete_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Delete Student", style="Header.TLabel").pack(anchor="w")

        row = ttk.Frame(frame)
        row.pack(fill="x", pady=8)

        self.delete_id = tk.StringVar()
        ttk.Label(row, text="Student ID").pack(side="left")
        ttk.Entry(row, textvariable=self.delete_id).pack(side="left", padx=8)
        ttk.Button(row, text="Delete", command=self._handle_delete_student).pack(side="left")
        ttk.Button(row, text="Undo Delete", command=self._handle_undo_delete).pack(side="left", padx=8)

        self.frames["delete"] = frame

    def _handle_delete_student(self) -> None:
        try:
            student_id = int(self.delete_id.get())
        except ValueError:
            messagebox.showerror("Invalid ID", "Student ID must be a number.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            return
        deleted = self.store.delete_student(student_id)
        if deleted:
            self._log_activity(f"Deleted student ID {student_id}")
            self._refresh_tables()
            messagebox.showinfo("Deleted", "Student deleted. You can undo from this screen.")
            return
        messagebox.showwarning("Not Found", "Student not found.")

    def _handle_undo_delete(self) -> None:
        restored = self.store.undo_delete()
        if restored:
            self._log_activity(f"Restored student ID {restored['id']}")
            self._refresh_tables()
            messagebox.showinfo("Restored", "Student restored successfully.")
            return
        messagebox.showwarning("Undo", "No deleted record to restore.")

    def _create_attendance_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Attendance", style="Header.TLabel").pack(anchor="w")

        self.attendance_table = self._create_student_table(frame)
        self.attendance_table.pack(fill="both", expand=True, pady=12)

        controls = ttk.Frame(frame)
        controls.pack(fill="x")

        ttk.Button(controls, text="Mark Present", command=lambda: self._handle_attendance(True)).pack(side="left", padx=4)
        ttk.Button(controls, text="Mark Absent", command=lambda: self._handle_attendance(False)).pack(side="left", padx=4)

        self.frames["attendance"] = frame

    def _handle_attendance(self, present: bool) -> None:
        selected = self.attendance_table.selection()
        if not selected:
            messagebox.showwarning("Attendance", "Select a student in the table.")
            return
        student_id = int(self.attendance_table.item(selected[0], "values")[0])
        student = self.store.search_by_id(student_id)
        if not student:
            messagebox.showerror("Attendance", "Student not found.")
            return
        mark_attendance(student, present)
        self.store.save()
        self.store.load()
        self._log_activity(f"Marked attendance for ID {student_id} ({'present' if present else 'absent'})")
        self._refresh_tables()
        messagebox.showinfo("Attendance", "Attendance updated.")

    def _create_reports_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Reports", style="Header.TLabel").pack(anchor="w")

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=8)

        ttk.Button(controls, text="Top Performers", command=self._report_top).pack(side="left", padx=4)
        ttk.Button(controls, text="Low Attendance", command=self._report_low_attendance).pack(side="left", padx=4)
        ttk.Button(controls, text="Marks Summary", command=self._report_summary).pack(side="left", padx=4)

        self.course_report_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.course_report_var, width=18).pack(side="left", padx=8)
        ttk.Button(controls, text="Course Report", command=self._report_course).pack(side="left")

        self.report_text = tk.Text(frame, height=18)
        self.report_text.pack(fill="both", expand=True, pady=8)

        self.frames["reports"] = frame

    def _report_top(self) -> None:
        results = top_performers(self.store.students)
        self._render_report("Top Performing Students", results)

    def _report_low_attendance(self) -> None:
        results = low_attendance(self.store.students)
        self._render_report("Low Attendance Students", results)

    def _report_summary(self) -> None:
        minimum, maximum, average = marks_summary(self.store.students)
        lines = [
            "Marks Summary",
            "----------------",
            f"Min Marks: {minimum}",
            f"Max Marks: {maximum}",
            f"Avg Marks: {average}",
        ]
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, "\n".join(lines))

    def _report_course(self) -> None:
        course = self.course_report_var.get().strip()
        if not course:
            messagebox.showwarning("Course Report", "Enter a course name.")
            return
        results = course_report(self.store.students, course)
        self._render_report(f"Course Report: {course}", results)

    def _render_report(self, title: str, students: List[Dict[str, Any]]) -> None:
        lines = [title, "----------------"]
        for s in students:
            percent = attendance_percent(s)
            lines.append(f"{s['id']} | {s['name']} | {s['course']} | {s['marks']} | {percent}%")
        if len(lines) == 2:
            lines.append("No records found.")
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, "\n".join(lines))

    def _create_requests_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Student Requests Queue", style="Header.TLabel").pack(anchor="w")

        form = ttk.Frame(frame)
        form.pack(fill="x", pady=8)

        self.queue_student_id = tk.StringVar()
        self.queue_note = tk.StringVar()

        ttk.Label(form, text="Student ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.queue_student_id).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Label(form, text="Request").grid(row=1, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.queue_note).grid(row=1, column=1, sticky="ew", padx=6)
        ttk.Button(form, text="Add Request", command=self._enqueue_request).grid(row=0, column=2, rowspan=2, padx=8)

        form.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Process Next", command=self._dequeue_request).pack(anchor="w", pady=6)
        self.queue_output = tk.Text(frame, height=10)
        self.queue_output.pack(fill="both", expand=True, pady=8)

        self.frames["requests"] = frame

    def _enqueue_request(self) -> None:
        try:
            student_id = int(self.queue_student_id.get())
        except ValueError:
            messagebox.showerror("Invalid ID", "Student ID must be a number.")
            return
        note = self.queue_note.get().strip()
        if not note:
            messagebox.showwarning("Request", "Enter a request description.")
            return
        request = {"student_id": student_id, "note": note}
        self.store.enqueue_request(request)
        self.queue_student_id.set("")
        self.queue_note.set("")
        self.queue_output.insert(tk.END, f"Queued request for {student_id}: {note}\n")
        self._log_activity(f"Queued request for ID {student_id}")

    def _dequeue_request(self) -> None:
        request = self.store.dequeue_request()
        if not request:
            self.queue_output.insert(tk.END, "No requests in queue.\n")
            return
        self.queue_output.insert(tk.END, f"Processed request for {request['student_id']}: {request['note']}\n")
        self._log_activity(f"Processed request for ID {request['student_id']}")

    def _create_settings_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Settings", style="Header.TLabel").pack(anchor="w")

        form = ttk.Frame(frame)
        form.pack(fill="x", pady=8)

        self.settings_vars = {
            "username": tk.StringVar(value=self.settings.get("admin_username")),
            "password": tk.StringVar(value=self.settings.get("admin_password")),
            "page_size": tk.StringVar(value=str(self.settings.get("page_size", 10))),
        }

        fields = [
            ("Admin Username", "username"),
            ("Admin Password", "password"),
            ("Page Size", "page_size"),
        ]

        for idx, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=idx, column=0, sticky="w", pady=4)
            show = "*" if key == "password" else ""
            ttk.Entry(form, textvariable=self.settings_vars[key], show=show).grid(row=idx, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)
        ttk.Button(frame, text="Save Settings", command=self._save_settings).pack(anchor="w", pady=8)

        self.frames["settings"] = frame

    def _save_settings(self) -> None:
        try:
            page_size = int(self.settings_vars["page_size"].get())
        except ValueError:
            messagebox.showerror("Settings", "Page size must be a number.")
            return
        if page_size <= 0:
            messagebox.showerror("Settings", "Page size must be greater than 0.")
            return

        self.settings["admin_username"] = self.settings_vars["username"].get().strip() or "admin"
        self.settings["admin_password"] = self.settings_vars["password"].get().strip() or "admin123"
        self.settings["page_size"] = page_size
        save_json(SETTINGS_FILE, self.settings)
        self._refresh_tables()
        messagebox.showinfo("Settings", "Settings saved successfully.")

    def _create_student_table(self, parent) -> ttk.Treeview:
        columns = ("id", "name", "course", "department", "marks", "attendance")
        table = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        for col, label in zip(
            columns, ["ID", "Name", "Course", "Department", "Marks", "Attendance %"]
        ):
            table.heading(col, text=label)
            table.column(col, width=130, anchor="center")
        return table

    def _populate_table(self, table: ttk.Treeview, students: List[Dict[str, Any]]) -> None:
        table.delete(*table.get_children())
        for s in students:
            percent = attendance_percent(s)
            table.insert(
                "",
                tk.END,
                values=(
                    s["id"],
                    s.get("name", ""),
                    s.get("course", ""),
                    s.get("department", ""),
                    s.get("marks", 0),
                    percent,
                ),
            )

    def _refresh_tables(self) -> None:
        self._refresh_view_table()
        self._populate_table(self.search_table, [])
        self._populate_table(self.attendance_table, self.store.students)
        self._update_dashboard()

    def _update_dashboard(self) -> None:
        if not hasattr(self, "stat_labels"):
            return
        total_students = len(self.store.students)
        _, _, avg_marks = marks_summary(self.store.students)
        attendance_values = [attendance_percent(s) for s in self.store.students]
        avg_attendance = round(sum(attendance_values) / len(attendance_values), 2) if attendance_values else 0
        top_count = len(top_performers(self.store.students))

        self.stat_labels["Total Students"].configure(text=str(total_students))
        self.stat_labels["Avg Marks"].configure(text=str(avg_marks))
        self.stat_labels["Attendance %"].configure(text=str(avg_attendance))
        self.stat_labels["Top Performers"].configure(text=str(top_count))

        if hasattr(self, "activity_list"):
            self.activity_list.delete(0, tk.END)
            for entry in self.activity_log[-6:]:
                self.activity_list.insert(tk.END, entry)

    def _log_activity(self, message: str) -> None:
        self.activity_log.append(message)


def main() -> None:
    root = tk.Tk()
    StudentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
