const apiBaseInput = document.getElementById("api-base");
const pageSizeInput = document.getElementById("page-size");
const saveSettings = document.getElementById("save-settings");
const logout = document.getElementById("logout");

const statsTotal = document.getElementById("stat-total");
const statsMarks = document.getElementById("stat-marks");
const statsAttendance = document.getElementById("stat-attendance");
const statsTop = document.getElementById("stat-top");

const studentsTable = document.getElementById("students-table");
const pageLabel = document.getElementById("page-label");
const prevPage = document.getElementById("prev-page");
const nextPage = document.getElementById("next-page");
const searchField = document.getElementById("search-field");
const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");

const modal = document.getElementById("student-modal");
const modalTitle = document.getElementById("modal-title");
const closeModal = document.getElementById("close-modal");
const openAdd = document.getElementById("open-add");
const studentForm = document.getElementById("student-form");
const formError = document.getElementById("form-error");

const studentDbId = document.getElementById("student-db-id");
const studentId = document.getElementById("student-id");
const studentName = document.getElementById("student-name");
const studentAge = document.getElementById("student-age");
const studentGender = document.getElementById("student-gender");
const studentCourse = document.getElementById("student-course");
const studentDepartment = document.getElementById("student-department");
const studentMarks = document.getElementById("student-marks");
const studentAttendance = document.getElementById("student-attendance");
const studentContact = document.getElementById("student-contact");

const activityList = document.getElementById("activity-list");
const markPresent = document.getElementById("mark-present");
const markAbsent = document.getElementById("mark-absent");
const attendanceId = document.getElementById("attendance-id");

const reportOutput = document.getElementById("report-output");
const reportTop = document.getElementById("report-top");
const reportLow = document.getElementById("report-low");
const reportSummary = document.getElementById("report-summary");
const reportCourse = document.getElementById("report-course");
const courseReport = document.getElementById("course-report");

const menuButtons = document.querySelectorAll(".menu-btn");
const sections = {
  dashboard: document.getElementById("dashboard-section"),
  students: document.getElementById("students-section"),
  attendance: document.getElementById("attendance-section"),
  reports: document.getElementById("reports-section"),
  settings: document.getElementById("settings-section"),
};

let currentPage = 1;
let totalPages = 1;
let activityLog = [];

const apiBase = () => window.API_BASE || localStorage.getItem("apiBase") || "http://localhost:5000/api";

const pageSize = () => {
  const value = parseInt(localStorage.getItem("pageSize") || "10", 10);
  return Number.isNaN(value) ? 10 : value;
};

const isLoggedIn = () => localStorage.getItem("loggedIn") === "true";

if (!isLoggedIn()) {
  window.location.href = "index.html";
}

const logActivity = (text) => {
  activityLog.unshift({ text, time: new Date().toLocaleTimeString() });
  if (activityLog.length > 6) {
    activityLog = activityLog.slice(0, 6);
  }
  renderActivities();
};

const renderActivities = () => {
  activityList.innerHTML = "";
  activityLog.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.time} - ${item.text}`;
    activityList.appendChild(li);
  });
};

const fetchStats = async () => {
  const response = await fetch(`${apiBase()}/stats`);
  const result = await response.json();
  statsTotal.textContent = result.total;
  statsMarks.textContent = result.avg_marks;
  statsAttendance.textContent = result.avg_attendance;
  statsTop.textContent = result.top_count;
};

const fetchStudents = async () => {
  const response = await fetch(
    `${apiBase()}/students?page=${currentPage}&page_size=${pageSize()}&q=${encodeURIComponent(
      searchInput.value.trim()
    )}&field=${searchField.value}`
  );
  const result = await response.json();
  renderStudents(result.data);
  totalPages = Math.max(1, Math.ceil(result.total / result.page_size));
  pageLabel.textContent = `Page ${currentPage} of ${totalPages}`;
};

const renderStudents = (students) => {
  studentsTable.innerHTML = "";
  students.forEach((student) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${student.id}</td>
      <td>${student.student_id}</td>
      <td>${student.name}</td>
      <td>${student.course}</td>
      <td>${student.department}</td>
      <td>${student.marks}</td>
      <td>${student.attendance}</td>
      <td class="actions">
        <button class="btn ghost" data-action="edit" data-id="${student.id}">Edit</button>
        <button class="btn danger" data-action="delete" data-id="${student.id}">Delete</button>
      </td>
    `;
    studentsTable.appendChild(row);
  });
};

const openModal = (title) => {
  modalTitle.textContent = title;
  modal.classList.remove("hidden");
};

const closeModalView = () => {
  modal.classList.add("hidden");
  studentForm.reset();
  studentDbId.value = "";
  formError.textContent = "";
};

const loadStudentIntoForm = (student) => {
  studentDbId.value = student.id;
  studentId.value = student.student_id;
  studentName.value = student.name;
  studentAge.value = student.age;
  studentGender.value = student.gender;
  studentCourse.value = student.course;
  studentDepartment.value = student.department;
  studentMarks.value = student.marks;
  studentAttendance.value = student.attendance;
  studentContact.value = student.contact;
};

const submitStudent = async (payload, id = null) => {
  const method = id ? "PUT" : "POST";
  const url = id ? `${apiBase()}/students/${id}` : `${apiBase()}/students`;

  const response = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error || "Something went wrong.");
  }

  return result.data;
};

const deleteStudent = async (id) => {
  const response = await fetch(`${apiBase()}/students/${id}`, { method: "DELETE" });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error || "Failed to delete.");
  }
  return result.data;
};

const updateAttendance = async (id, present) => {
  const response = await fetch(`${apiBase()}/attendance/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ present }),
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error || "Failed to update attendance.");
  }
  return result.data;
};

studentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.textContent = "";

  const payload = {
    student_id: studentId.value.trim(),
    name: studentName.value.trim(),
    age: studentAge.value,
    gender: studentGender.value.trim(),
    course: studentCourse.value.trim(),
    department: studentDepartment.value.trim(),
    marks: studentMarks.value,
    attendance: studentAttendance.value,
    contact: studentContact.value.trim(),
  };

  try {
    const saved = await submitStudent(payload, studentDbId.value || null);
    logActivity(`${studentDbId.value ? "Updated" : "Added"} ${saved.name}`);
    closeModalView();
    await fetchStats();
    await fetchStudents();
  } catch (err) {
    formError.textContent = err.message;
  }
});

studentsTable.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) {
    return;
  }
  const action = button.dataset.action;
  const id = button.dataset.id;

  if (action === "edit") {
    const response = await fetch(`${apiBase()}/students/${id}`);
    const result = await response.json();
    if (response.ok) {
      loadStudentIntoForm(result.data);
      openModal("Update Student");
    }
  }

  if (action === "delete") {
    if (!confirm("Delete this student?")) {
      return;
    }
    await deleteStudent(id);
    logActivity(`Deleted student ID ${id}`);
    await fetchStats();
    await fetchStudents();
  }
});

openAdd.addEventListener("click", () => {
  studentForm.reset();
  studentDbId.value = "";
  openModal("Add Student");
});

closeModal.addEventListener("click", closeModalView);

searchBtn.addEventListener("click", () => {
  currentPage = 1;
  fetchStudents();
});

prevPage.addEventListener("click", () => {
  currentPage = Math.max(1, currentPage - 1);
  fetchStudents();
});

nextPage.addEventListener("click", () => {
  currentPage = Math.min(totalPages, currentPage + 1);
  fetchStudents();
});

markPresent.addEventListener("click", async () => {
  const id = parseInt(attendanceId.value, 10);
  if (!id) {
    alert("Enter a student DB ID.");
    return;
  }
  await updateAttendance(id, true);
  logActivity(`Marked present for ID ${id}`);
  await fetchStats();
  await fetchStudents();
});

markAbsent.addEventListener("click", async () => {
  const id = parseInt(attendanceId.value, 10);
  if (!id) {
    alert("Enter a student DB ID.");
    return;
  }
  await updateAttendance(id, false);
  logActivity(`Marked absent for ID ${id}`);
  await fetchStats();
  await fetchStudents();
});

reportTop.addEventListener("click", async () => {
  const response = await fetch(`${apiBase()}/reports/top`);
  const result = await response.json();
  reportOutput.textContent = JSON.stringify(result.data, null, 2);
});

reportLow.addEventListener("click", async () => {
  const response = await fetch(`${apiBase()}/reports/low-attendance`);
  const result = await response.json();
  reportOutput.textContent = JSON.stringify(result.data, null, 2);
});

reportSummary.addEventListener("click", async () => {
  const response = await fetch(`${apiBase()}/reports/summary`);
  const result = await response.json();
  reportOutput.textContent = JSON.stringify(result, null, 2);
});

reportCourse.addEventListener("click", async () => {
  const course = courseReport.value.trim();
  if (!course) {
    alert("Enter a course name.");
    return;
  }
  const response = await fetch(`${apiBase()}/reports/course?course=${encodeURIComponent(course)}`);
  const result = await response.json();
  reportOutput.textContent = JSON.stringify(result.data, null, 2);
});

saveSettings.addEventListener("click", () => {
  localStorage.setItem("apiBase", apiBaseInput.value.trim());
  localStorage.setItem("pageSize", pageSizeInput.value.trim());
  alert("Settings saved.");
});

logout.addEventListener("click", () => {
  localStorage.removeItem("loggedIn");
  window.location.href = "index.html";
});

menuButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    menuButtons.forEach((item) => item.classList.remove("active"));
    btn.classList.add("active");
    Object.values(sections).forEach((section) => section.classList.add("hidden"));
    const target = sections[btn.dataset.section];
    if (target) {
      target.classList.remove("hidden");
    }
  });
});

const init = () => {
  apiBaseInput.value = apiBase();
  pageSizeInput.value = pageSize();
  fetchStats();
  fetchStudents();
};

init();
