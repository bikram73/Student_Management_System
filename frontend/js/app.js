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
const addTestMark = document.getElementById("add-test-mark");
const testMarksList = document.getElementById("test-marks-list");

const activityList = document.getElementById("activity-list");
const attendanceCalendar = document.getElementById("attendance-calendar");
const calendarMonth = document.getElementById("calendar-month");
const calendarWeekdays = document.getElementById("calendar-weekdays");
const attendanceTable = document.getElementById("attendance-table");
const saveAttendanceAll = document.getElementById("save-attendance-all");

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
const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

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

const fetchAllStudentsForAttendance = async () => {
  const response = await fetch(`${apiBase()}/students?page=1&page_size=1000`);
  const result = await response.json();
  renderAttendanceStudents(result.data || []);
};

const renderCalendar = () => {
  if (!attendanceCalendar || !calendarMonth || !calendarWeekdays) {
    return;
  }

  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth();

  const firstDayDate = new Date(currentYear, currentMonth, 1);
  const firstWeekDay = firstDayDate.getDay();
  const totalDays = new Date(currentYear, currentMonth + 1, 0).getDate();

  calendarMonth.textContent = firstDayDate.toLocaleDateString(undefined, {
    month: "long",
    year: "numeric",
  });

  calendarWeekdays.innerHTML = weekDays.map((day) => `<span>${day}</span>`).join("");

  attendanceCalendar.innerHTML = "";
  for (let i = 0; i < firstWeekDay; i += 1) {
    const emptyCell = document.createElement("span");
    emptyCell.className = "calendar-day empty";
    attendanceCalendar.appendChild(emptyCell);
  }

  for (let day = 1; day <= totalDays; day += 1) {
    const cell = document.createElement("span");
    cell.className = "calendar-day";
    cell.textContent = day;

    if (day === today.getDate()) {
      cell.classList.add("today");
    }

    attendanceCalendar.appendChild(cell);
  }
};

const renderAttendanceStudents = (students) => {
  if (!attendanceTable) {
    return;
  }

  attendanceTable.innerHTML = "";
  if (!students.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="5" class="muted">No students found.</td>';
    attendanceTable.appendChild(row);
    return;
  }

  students.forEach((student) => {
    const status = student.today_status || "Not Marked";
    const isLocked = Boolean(student.today_locked);

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${student.student_id}</td>
      <td>${student.name}</td>
      <td>${student.attendance}%</td>
      <td><span class="attendance-status ${isLocked ? "locked" : ""}">${isLocked ? `${status} (Saved)` : status}</span></td>
      <td class="actions">
        <div class="attendance-row-actions">
          <button class="btn success" data-attendance-id="${student.id}" data-action="present" ${isLocked ? "disabled" : ""}>Mark Present</button>
          <button class="btn danger" data-attendance-id="${student.id}" data-action="absent" ${isLocked ? "disabled" : ""}>Mark Absent</button>
          <button class="btn ghost" data-attendance-id="${student.id}" data-action="reverse" ${isLocked ? "disabled" : ""}>Reverse</button>
        </div>
      </td>
    `;
    attendanceTable.appendChild(row);
  });
};

const renderStudents = (students) => {
  studentsTable.innerHTML = "";
  students.forEach((student) => {
    const scores = Array.isArray(student.test_scores) ? student.test_scores : [];
    const test1 = scores.length > 0 ? scores[0] : "-";
    const test2 = scores.length > 1 ? scores[1] : "-";
    const total = scores.length > 0 ? scores.reduce((sum, value) => sum + Number(value || 0), 0).toFixed(2) : "0";

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${student.id}</td>
      <td>${student.student_id}</td>
      <td>${student.name}</td>
      <td>${student.course}</td>
      <td>${student.department}</td>
      <td>${test1}</td>
      <td>${test2}</td>
      <td>${total}</td>
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

const createTestMarkField = (value = "") => {
  const wrapper = document.createElement("label");
  wrapper.className = "inline-field";

  const count = testMarksList.querySelectorAll(".test-mark-input").length + 1;
  wrapper.innerHTML = `
    Test Mark ${count}
    <input type="number" class="test-mark-input" min="0" max="100" placeholder="0" value="${value}" />
  `;

  return wrapper;
};

const resetTestMarks = () => {
  if (!testMarksList) {
    return;
  }
  testMarksList.innerHTML = "";
  testMarksList.appendChild(createTestMarkField());
};

const getTestMarksValue = () => {
  if (!testMarksList) {
    return [];
  }
  return Array.from(testMarksList.querySelectorAll(".test-mark-input"))
    .map((input) => input.value.trim())
    .filter((value) => value !== "");
};

if (addTestMark && testMarksList) {
  addTestMark.addEventListener("click", () => {
    testMarksList.appendChild(createTestMarkField());
  });
}

const closeModalView = () => {
  modal.classList.add("hidden");
  studentForm.reset();
  studentDbId.value = "";
  formError.textContent = "";
  resetTestMarks();
};

const loadStudentIntoForm = (student) => {
  studentDbId.value = student.id;
  studentId.value = student.student_id;
  studentName.value = student.name;
  studentAge.value = student.age;
  studentGender.value = student.gender;
  studentCourse.value = student.course;
  studentDepartment.value = student.department;
  studentMarks.value = student.marks ?? 0;
  studentAttendance.value = student.attendance;
  studentContact.value = student.contact;
  if (testMarksList) {
    testMarksList.innerHTML = "";
    const scores = Array.isArray(student.test_scores) ? student.test_scores : [];
    if (scores.length) {
      scores.forEach((score, index) => {
        testMarksList.appendChild(createTestMarkField(score));
        const lastInput = testMarksList.querySelectorAll(".test-mark-input")[index];
        if (lastInput) {
          lastInput.value = score;
        }
      });
    } else {
      testMarksList.appendChild(createTestMarkField());
    }
  }
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

const updateTodayAttendance = async (id, status) => {
  const response = await fetch(`${apiBase()}/attendance/${id}/today`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error || "Failed to update today's attendance.");
  }
  return result.data;
};

const lockTodayAttendanceByStudent = async (id) => {
  const response = await fetch(`${apiBase()}/attendance/${id}/today/lock`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  const text = await response.text();
  let result = {};
  try {
    result = text ? JSON.parse(text) : {};
  } catch {
    result = {};
  }

  if (!response.ok) {
    throw new Error(result.error || "Failed to lock today's attendance.");
  }

  return result.data;
};

const lockTodayAttendanceForAll = async () => {
  const response = await fetch(`${apiBase()}/attendance/today/lock-all`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  const text = await response.text();
  let result = {};
  try {
    result = text ? JSON.parse(text) : {};
  } catch {
    result = {};
  }

  if (response.ok) {
    return result;
  }

  if (response.status !== 404) {
    throw new Error(result.error || "Failed to save today's attendance for all students.");
  }

  const studentsResponse = await fetch(`${apiBase()}/students?page=1&page_size=1000`);
  const studentsResult = await studentsResponse.json();
  if (!studentsResponse.ok) {
    throw new Error(studentsResult.error || "Failed to load students for bulk save.");
  }

  let lockedCount = 0;
  const rows = studentsResult.data || [];
  for (const student of rows) {
    const hasTodayMark = student.today_status === "present" || student.today_status === "absent";
    if (!hasTodayMark || student.today_locked) {
      continue;
    }

    await lockTodayAttendanceByStudent(student.id);
    lockedCount += 1;
  }

  return { locked_count: lockedCount };
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
    test_scores: getTestMarksValue(),
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
  studentMarks.value = "0";
  studentAttendance.value = "0";
  resetTestMarks();
  openModal("Add Student");
});

resetTestMarks();

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

attendanceTable.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-attendance-id][data-action]");
  if (!button) {
    return;
  }

  const id = parseInt(button.dataset.attendanceId, 10);
  const action = button.dataset.action;

  if (!id) {
    return;
  }

  try {
    if (action === "present") {
      await updateTodayAttendance(id, "present");
      logActivity(`Marked present for ID ${id}`);
    } else if (action === "absent") {
      await updateTodayAttendance(id, "absent");
      logActivity(`Marked absent for ID ${id}`);
    } else if (action === "reverse") {
      await updateTodayAttendance(id, "clear");
      logActivity(`Reversed today's attendance for ID ${id}`);
    }

    await fetchStats();
    await fetchStudents();
    await fetchAllStudentsForAttendance();
  } catch (err) {
    alert(err.message || "Attendance action failed.");
  }
});

if (saveAttendanceAll) {
  saveAttendanceAll.addEventListener("click", async () => {
    try {
      const result = await lockTodayAttendanceForAll();
      logActivity(`Saved today's attendance for ${result.locked_count || 0} students`);
      await fetchStats();
      await fetchStudents();
      await fetchAllStudentsForAttendance();
    } catch (err) {
      alert(err.message || "Failed to save all attendance.");
    }
  });
}

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
  renderCalendar();
  fetchStats();
  fetchStudents();
  fetchAllStudentsForAttendance();
};

init();
