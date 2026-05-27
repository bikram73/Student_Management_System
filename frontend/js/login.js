const form = document.getElementById("login-form");
const error = document.getElementById("login-error");

const apiBase = localStorage.getItem("apiBase") || "http://localhost:5000/api";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";

  const formData = new FormData(form);
  const payload = {
    username: formData.get("username"),
    password: formData.get("password"),
  };

  try {
    const response = await fetch(`${apiBase}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Invalid credentials.");
    }

    const result = await response.json();
    if (!result.success) {
      throw new Error("Invalid credentials.");
    }

    localStorage.setItem("loggedIn", "true");
    window.location.href = "dashboard.html";
  } catch (err) {
    error.textContent = err.message;
  }
});
