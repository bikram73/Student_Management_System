from pathlib import Path

APP_TITLE = "Student Management System"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DATA_FILE = DATA_DIR / "students.json"

COLORS = {
    "primary": "#1E3A8A",
    "secondary": "#3B82F6",
    "accent": "#10B981",
    "bg": "#F3F4F6",
    "card": "#FFFFFF",
    "text": "#111827",
    "text_muted": "#6B7280",
    "error": "#EF4444",
    "warning": "#F59E0B",
}
