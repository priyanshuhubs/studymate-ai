"""
app.py
------
Main Flask application for StudyMate AI - Academic Productivity Assistant.

Pages (5-page wireframe):
  1. /login         - Student Login page
  2. /signup        - Student Registration page
  3. /dashboard     - Overview Dashboard & Learning Task Organizer
  4. /study-studio  - AI Study Studio (Notes, Summaries, Revision Questions, Assignment Outlines)
  5. /planner       - Personalized AI Study Schedule Planner
"""

import csv
import io
import os
from functools import wraps
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db_connection, init_db
from gemini_helper import (
    generate_study_content,
    generate_study_schedule,
    is_gemini_configured,
)

# Load environment variables from .env (GEMINI_API_KEY, SECRET_KEY, GEMINI_MODEL)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "studymate-dev-secret-key-change-me")

# Ensure SQLite tables exist when the app starts
init_db()


# ---------------------------------------------------------------------------
# Helper Decorator: Protect private pages so only logged-in users can view them
# ---------------------------------------------------------------------------
def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access StudyMate AI.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view


# Make AI mode status available in every HTML template automatically
@app.context_processor
def inject_global_context():
    return {
        "gemini_live": is_gemini_configured(),
        "current_user_name": session.get("user_name"),
    }


# ---------------------------------------------------------------------------
# Home Route
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Redirects logged-in users to Dashboard, and guests to Login."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Page 1: Login
# ---------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        # Verify user exists and password matches the stored hash
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_email"] = user["email"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password. Please try again.", "error")

    return render_template("login.html")


# ---------------------------------------------------------------------------
# Page 2: Signup
# ---------------------------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validation checks
        if not full_name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        # Hash the password before saving (never store plain-text passwords)
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, password_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid
        except Exception:
            conn.close()
            flash("An account with this email already exists. Please log in.", "error")
            return render_template("signup.html")
        conn.close()

        # Log the new student in immediately
        session["user_id"] = user_id
        session["user_name"] = full_name
        session["user_email"] = email
        flash("Account created successfully! Welcome to StudyMate AI.", "success")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    """Clears user session and redirects to login page."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Page 3: Dashboard & Learning Task Organizer
# ---------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    conn = get_db_connection()

    tasks = conn.execute(
        """
        SELECT * FROM tasks
        WHERE user_id = ?
        ORDER BY is_completed ASC, created_at DESC
        """,
        (user_id,),
    ).fetchall()

    material_count = conn.execute(
        "SELECT COUNT(*) FROM study_materials WHERE user_id = ?", (user_id,)
    ).fetchone()[0]

    schedule_count = conn.execute(
        "SELECT COUNT(*) FROM study_schedules WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    conn.close()

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["is_completed"] == 1)
    pending_tasks = total_tasks - completed_tasks

    stats = {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "material_count": material_count,
        "schedule_count": schedule_count,
    }

    return render_template("dashboard.html", tasks=tasks, stats=stats)


@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    """Adds a new learning task for the logged-in student."""
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "General").strip() or "General"
    priority = request.form.get("priority", "Medium").strip()
    due_date = request.form.get("due_date", "").strip()

    if not title:
        flash("Task title cannot be empty.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO tasks (user_id, title, subject, priority, due_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session["user_id"], title, subject, priority, due_date),
    )
    conn.commit()
    conn.close()

    flash("Learning task added!", "success")
    return redirect(url_for("dashboard"))


@app.route("/tasks/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    """Toggles a learning task between pending (0) and completed (1)."""
    conn = get_db_connection()
    task = conn.execute(
        "SELECT is_completed FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    ).fetchone()

    if task:
        new_status = 0 if task["is_completed"] == 1 else 1
        conn.execute(
            "UPDATE tasks SET is_completed = ? WHERE id = ? AND user_id = ?",
            (new_status, task_id, session["user_id"]),
        )
        conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    """Deletes a learning task owned by the logged-in student."""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    flash("Task deleted.", "info")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Page 4: AI Study Studio (Notes, Summaries, Revision Questions, Outlines)
# ---------------------------------------------------------------------------
@app.route("/study-studio")
@login_required
def study_studio():
    """Displays the AI Study Studio and the student's saved AI-generated materials."""
    conn = get_db_connection()
    materials = conn.execute(
        """
        SELECT * FROM study_materials
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template("study_studio.html", materials=materials)


@app.route("/api/study-studio/generate", methods=["POST"])
@login_required
def api_generate_study_content():
    """
    JSON API endpoint called by JavaScript on the AI Study Studio page.
    Generates study notes, summaries, revision questions, or assignment outlines,
    saves the result to SQLite, and returns it to the browser.
    """
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "notes").strip().lower()
    title = data.get("title", "").strip()
    source_text = data.get("source_text", "").strip()
    extra_option = data.get("extra_option", "").strip()

    if mode not in {"notes", "summary", "questions", "outline"}:
        return jsonify({"error": "Invalid study mode selected."}), 400

    if not source_text:
        return jsonify({"error": "Please enter some study text or topic details first."}), 400

    final_title = title or f"{mode.capitalize()} - Study Material"
    ai_output, used_live_ai = generate_study_content(mode, final_title, source_text, extra_option)

    # Save the generated material in SQLite so the student can revisit it later
    conn = get_db_connection()
    cursor = conn.execute(
        """
        INSERT INTO study_materials (user_id, material_type, title, source_text, ai_output)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session["user_id"], mode, final_title, source_text, ai_output),
    )
    conn.commit()
    material_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": material_id,
        "mode": mode,
        "title": final_title,
        "output": ai_output,
        "used_live_ai": used_live_ai,
    })


@app.route("/study-studio/delete/<int:material_id>", methods=["POST"])
@login_required
def delete_material(material_id):
    """Deletes a saved AI study material."""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM study_materials WHERE id = ? AND user_id = ?",
        (material_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    flash("Saved study material removed.", "info")
    return redirect(url_for("study_studio"))


# ---------------------------------------------------------------------------
# Page 5: Personalized Study Schedule Planner
# ---------------------------------------------------------------------------
@app.route("/planner")
@login_required
def planner():
    """Displays the Personalized Study Schedule generator and saved schedules."""
    conn = get_db_connection()
    schedules = conn.execute(
        """
        SELECT * FROM study_schedules
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template("planner.html", schedules=schedules)


@app.route("/api/planner/generate", methods=["POST"])
@login_required
def api_generate_schedule():
    """
    JSON API endpoint called by JavaScript on the Study Planner page.
    Generates a personalized study schedule with Gemini AI and saves it to SQLite.
    """
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    subjects = data.get("subjects", "").strip()
    exam_date = data.get("exam_date", "").strip()
    focus_areas = data.get("focus_areas", "").strip()

    try:
        daily_hours = float(data.get("daily_hours", 2))
    except (TypeError, ValueError):
        return jsonify({"error": "Daily study hours must be a valid number."}), 400

    if not subjects or not exam_date:
        return jsonify({"error": "Please enter your subjects and target exam date."}), 400

    if daily_hours <= 0 or daily_hours > 16:
        return jsonify({"error": "Daily study hours must be between 0.5 and 16."}), 400

    plan_title = title or f"Study Plan until {exam_date}"
    schedule_output, used_live_ai = generate_study_schedule(
        subjects=subjects,
        exam_date=exam_date,
        daily_hours=daily_hours,
        focus_areas=focus_areas,
    )

    conn = get_db_connection()
    cursor = conn.execute(
        """
        INSERT INTO study_schedules
            (user_id, title, subjects, exam_date, daily_hours, focus_areas, schedule_output)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (session["user_id"], plan_title, subjects, exam_date, daily_hours, focus_areas, schedule_output),
    )
    conn.commit()
    schedule_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": schedule_id,
        "title": plan_title,
        "output": schedule_output,
        "used_live_ai": used_live_ai,
    })


@app.route("/planner/delete/<int:schedule_id>", methods=["POST"])
@login_required
def delete_schedule(schedule_id):
    """Deletes a saved study schedule."""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM study_schedules WHERE id = ? AND user_id = ?",
        (schedule_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    flash("Study schedule deleted.", "info")
    return redirect(url_for("planner"))

# ---------------------------------------------------------------------------
# Page 6: Smart Focus Mode (Camera & No-Camera Distraction Tracker)
# ---------------------------------------------------------------------------
@app.route("/focus")
@login_required
def focus_mode():
    """Displays the Focus Mode tracker and saved focus session history."""
    conn = get_db_connection()
    sessions = conn.execute(
        """
        SELECT * FROM focus_sessions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 12
        """,
        (session["user_id"],),
    ).fetchall()
    conn.close()
    return render_template("focus.html", sessions=sessions)


@app.route("/api/focus/save", methods=["POST"])
@login_required
def api_save_focus_session():
    """Saves a completed Focus Mode session to SQLite."""
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "Camera Focus").strip()
    goal_minutes = int(data.get("goal_minutes", 25))
    focused_seconds = int(data.get("focused_seconds", 0))
    total_seconds = int(data.get("total_seconds", 0))

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO focus_sessions (user_id, mode, goal_minutes, focused_seconds, total_seconds)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session["user_id"], mode, goal_minutes, focused_seconds, total_seconds),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "saved"})



@app.route("/focus/export")
@login_required
def export_focus_csv():
    """Exports the student's focus sessions as a downloadable CSV report."""
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT mode, goal_minutes, focused_seconds, total_seconds, created_at
        FROM focus_sessions
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Mode", "Goal (min)", "Focused (sec)", "Total (sec)", "Date"])
    for r in rows:
        writer.writerow([r["mode"], r["goal_minutes"], r["focused_seconds"], r["total_seconds"], r["created_at"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=focus_report.csv"},
    )
# ---------------------------------------------------------------------------
# Run the Flask development server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(">>> GEMINI LIVE:", is_gemini_configured())
    app.run(debug=True, port=5001)