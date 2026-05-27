import tkinter as tk
from tkinter import ttk, messagebox

from .config import APP_TITLE, ADMIN_USERNAME, ADMIN_PASSWORD, COLORS, DATA_FILE
from .store import StudentStore
from .validators import validate_age, validate_marks, validate_attendance_percent
from .reports import top_performers, low_attendance, marks_summary


class StudentApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1200x720")
        self.root.configure(bg=COLORS["bg"])

        self.store = StudentStore(DATA_FILE)
        self.store.load()

        self._configure_style()
        self._build_login()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
        style.configure("Sidebar.TFrame", background=COLORS["primary"])
        style.configure("Sidebar.TButton", background=COLORS["primary"], foreground="white")
        style.map(
            "Sidebar.TButton",
            background=[("active", COLORS["secondary"])],
            foreground=[("active", "white")],
        )
        style.configure("Card.TFrame", background=COLORS["card"])
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TButton", padding=6)

    def _build_login(self) -> None:
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(fill="both", expand=True)

        card = ttk.Frame(self.login_frame, style="Card.TFrame", padding=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Admin Login", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 12))

        ttk.Label(card, text="Username").grid(row=1, column=0, sticky="w")
        ttk.Label(card, text="Password").grid(row=2, column=0, sticky="w")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Entry(card, textvariable=self.username_var).grid(row=1, column=1, pady=4)
        ttk.Entry(card, textvariable=self.password_var, show="*").grid(row=2, column=1, pady=4)

        ttk.Button(card, text="Login", command=self._handle_login).grid(row=3, column=0, columnspan=2, pady=(12, 0))

    def _handle_login(self) -> None:
        if self.username_var.get() == ADMIN_USERNAME and self.password_var.get() == ADMIN_PASSWORD:
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

        ttk.Label(sidebar, text="Dashboard", background=COLORS["primary"], foreground="white", font=("Segoe UI", 14, "bold")).pack(pady=16)

        self.frames = {}
        self.content_container = content

        for name, label in [
            ("dashboard", "Home"),
            ("add", "Add Student"),
            ("view", "View Students"),
            ("search", "Search"),
            ("update", "Update"),
            ("delete", "Delete"),
            ("attendance", "Attendance"),
            ("sorting", "Sorting"),
            ("reports", "Reports"),
            ("queue", "Requests"),
        ]:
            ttk.Button(sidebar, text=label, style="Sidebar.TButton", command=lambda n=name: self.show_frame(n)).pack(fill="x", padx=12, pady=4)

        self._create_dashboard_frame()
        self._create_add_frame()
        self._create_view_frame()
        self._create_search_frame()
        self._create_update_frame()
        self._create_delete_frame()
        self._create_attendance_frame()
        self._create_sorting_frame()
        self._create_reports_frame()
        self._create_queue_frame()

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
        for label in ["Total Students", "Avg Marks", "Top Marks"]:
            card = ttk.Frame(stats, style="Card.TFrame", padding=16)
            card.pack(side="left", padx=8)
            ttk.Label(card, text=label, foreground=COLORS["text_muted"]).pack(anchor="w")
            value_label = ttk.Label(card, text="0", font=("Segoe UI", 14, "bold"))
            value_label.pack(anchor="w")
            self.stat_labels[label] = value_label

        self._update_dashboard()

        self.frames["dashboard"] = frame

    def _create_add_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Add Student", style="Header.TLabel").pack(anchor="w")

        form = ttk.Frame(frame)
        form.pack(pady=12, fill="x")

        self.add_vars = {
            "name": tk.StringVar(),
            "age": tk.StringVar(),
            "gender": tk.StringVar(),
            "course": tk.StringVar(),
            "marks": tk.StringVar(),
            "contact": tk.StringVar(),
        }

        fields = [
            ("Name", "name"),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Course", "course"),
            ("Marks", "marks"),
            ("Contact", "contact"),
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
        except ValueError:
            messagebox.showerror("Invalid Input", "Age and marks must be numbers.")
            return

        valid, msg = validate_age(age)
        if not valid:
            messagebox.showerror("Invalid Age", msg)
            return
        valid, msg = validate_marks(marks)
        if not valid:
            messagebox.showerror("Invalid Marks", msg)
            return

        student = {
            "id": 0,
            "name": self.add_vars["name"].get().strip(),
            "age": age,
            "gender": self.add_vars["gender"].get().strip(),
            "course": self.add_vars["course"].get().strip(),
            "marks": marks,
            "attendance_total": 0,
            "attendance_present": 0,
            "contact": self.add_vars["contact"].get().strip(),
        }

        if not student["name"]:
            messagebox.showerror("Invalid Name", "Name is required.")
            return

        self.store.add_student(student)
        for var in self.add_vars.values():
            var.set("")
        self._refresh_tables()
        messagebox.showinfo("Success", "Student added successfully.")

    def _create_view_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="All Students", style="Header.TLabel").pack(anchor="w")

        self.view_table = self._create_student_table(frame)
        self.view_table.pack(fill="both", expand=True, pady=12)
        self.frames["view"] = frame

    def _create_search_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Search Student", style="Header.TLabel").pack(anchor="w")

        search_bar = ttk.Frame(frame)
        search_bar.pack(fill="x", pady=8)

        self.search_var = tk.StringVar()
        self.search_type = tk.StringVar(value="id")

        ttk.Entry(search_bar, textvariable=self.search_var).pack(side="left", padx=(0, 8))
        ttk.Combobox(search_bar, textvariable=self.search_type, values=["id", "name", "course"], width=10).pack(side="left")
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
            "marks": tk.StringVar(),
            "attendance": tk.StringVar(),
            "contact": tk.StringVar(),
        }

        fields = [
            ("Name", "name"),
            ("Age", "age"),
            ("Gender", "gender"),
            ("Course", "course"),
            ("Marks", "marks"),
            ("Attendance %", "attendance"),
            ("Contact", "contact"),
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
        self.update_vars["marks"].set(str(student.get("marks", "")))
        self.update_vars["attendance"].set(str(self.store.get_attendance_percent(student)))
        self.update_vars["contact"].set(student.get("contact", ""))

    def _handle_update_student(self) -> None:
        try:
            student_id = int(self.update_id.get())
            age = int(self.update_vars["age"].get())
            marks = int(self.update_vars["marks"].get())
            attendance_percent = float(self.update_vars["attendance"].get())
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
        valid, msg = validate_attendance_percent(attendance_percent)
        if not valid:
            messagebox.showerror("Invalid Attendance", msg)
            return

        total = 100
        present = int(round((attendance_percent / 100) * total))

        updates = {
            "name": self.update_vars["name"].get().strip(),
            "age": age,
            "gender": self.update_vars["gender"].get().strip(),
            "course": self.update_vars["course"].get().strip(),
            "marks": marks,
            "attendance_total": total,
            "attendance_present": present,
            "contact": self.update_vars["contact"].get().strip(),
        }

        if self.store.update_student(student_id, updates):
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
            self._refresh_tables()
            messagebox.showinfo("Deleted", "Student deleted. You can undo from this screen.")
            return
        messagebox.showwarning("Not Found", "Student not found.")

    def _handle_undo_delete(self) -> None:
        restored = self.store.undo_delete()
        if restored:
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

        ttk.Button(controls, text="Mark Present", command=lambda: self._mark_attendance(True)).pack(side="left", padx=4)
        ttk.Button(controls, text="Mark Absent", command=lambda: self._mark_attendance(False)).pack(side="left", padx=4)

        self.frames["attendance"] = frame

    def _mark_attendance(self, present: bool) -> None:
        selected = self.attendance_table.selection()
        if not selected:
            messagebox.showwarning("Attendance", "Select a student in the table.")
            return
        student_id = int(self.attendance_table.item(selected[0], "values")[0])
        if self.store.mark_attendance(student_id, present):
            self._refresh_tables()
            messagebox.showinfo("Attendance", "Attendance updated.")
            return
        messagebox.showerror("Attendance", "Failed to update attendance.")

    def _create_sorting_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Sorting", style="Header.TLabel").pack(anchor="w")

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=8)

        self.sort_key = tk.StringVar(value="name")
        self.sort_algo = tk.StringVar(value="built_in")
        self.sort_order = tk.StringVar(value="asc")

        ttk.Combobox(controls, textvariable=self.sort_key, values=["name", "id", "marks", "attendance"], width=12).pack(side="left")
        ttk.Combobox(controls, textvariable=self.sort_algo, values=["built_in", "bubble", "quick"], width=12).pack(side="left", padx=8)
        ttk.Combobox(controls, textvariable=self.sort_order, values=["asc", "desc"], width=8).pack(side="left")
        ttk.Button(controls, text="Sort", command=self._handle_sort).pack(side="left", padx=8)

        self.sort_table = self._create_student_table(frame)
        self.sort_table.pack(fill="both", expand=True, pady=12)

        self.frames["sorting"] = frame

    def _handle_sort(self) -> None:
        key_map = {
            "name": "name",
            "id": "id",
            "marks": "marks",
            "attendance": "attendance_percent",
        }
        key = self.sort_key.get()
        algo = self.sort_algo.get()
        reverse = self.sort_order.get() == "desc"

        students = []
        for s in self.store.students:
            student = dict(s)
            student["attendance_percent"] = self.store.get_attendance_percent(s)
            students.append(student)

        sorted_list = self.store.sort_students(key_map[key], algo, reverse, students)
        self._populate_table(self.sort_table, sorted_list)

    def _create_reports_frame(self) -> None:
        frame = ttk.Frame(self.content_container, padding=20)
        ttk.Label(frame, text="Reports", style="Header.TLabel").pack(anchor="w")

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=8)

        ttk.Button(controls, text="Top Performers", command=self._report_top).pack(side="left", padx=4)
        ttk.Button(controls, text="Low Attendance", command=self._report_low_attendance).pack(side="left", padx=4)
        ttk.Button(controls, text="Marks Summary", command=self._report_summary).pack(side="left", padx=4)

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

    def _render_report(self, title: str, students) -> None:
        lines = [title, "----------------"]
        for s in students:
            percent = self.store.get_attendance_percent(s)
            lines.append(f"{s['id']} | {s['name']} | {s['course']} | {s['marks']} | {percent}%")
        if len(lines) == 2:
            lines.append("No records found.")
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, "\n".join(lines))

    def _create_queue_frame(self) -> None:
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

        self.frames["queue"] = frame

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

    def _dequeue_request(self) -> None:
        request = self.store.dequeue_request()
        if not request:
            self.queue_output.insert(tk.END, "No requests in queue.\n")
            return
        self.queue_output.insert(tk.END, f"Processed request for {request['student_id']}: {request['note']}\n")

    def _create_student_table(self, parent) -> ttk.Treeview:
        columns = ("id", "name", "course", "marks", "attendance")
        table = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        for col, label in zip(columns, ["ID", "Name", "Course", "Marks", "Attendance %"]):
            table.heading(col, text=label)
            table.column(col, width=120, anchor="center")
        return table

    def _refresh_tables(self) -> None:
        for table in [self.view_table, self.search_table, self.attendance_table, self.sort_table]:
            self._populate_table(table, self.store.students)
        self._update_dashboard()

    def _populate_table(self, table: ttk.Treeview, students) -> None:
        table.delete(*table.get_children())
        for s in students:
            percent = self.store.get_attendance_percent(s)
            table.insert("", tk.END, values=(s["id"], s["name"], s["course"], s["marks"], percent))

    def _update_dashboard(self) -> None:
        if not hasattr(self, "stat_labels"):
            return
        total_students = len(self.store.students)
        _, max_marks, avg_marks = marks_summary(self.store.students)
        self.stat_labels["Total Students"].configure(text=str(total_students))
        self.stat_labels["Avg Marks"].configure(text=str(avg_marks))
        self.stat_labels["Top Marks"].configure(text=str(max_marks))


def main() -> None:
    root = tk.Tk()
    StudentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
