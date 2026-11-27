# Complete Antigravity Prompt – StudyMate AI

Copy and paste the prompt below directly into **Antigravity** (or submit it as part of your project documentation):

---

Build a complete, beginner-friendly, GitHub-ready mini project called **StudyMate AI – Academic Productivity Assistant** using **Python, Flask, HTML Templates (Jinja2), CSS, Vanilla JavaScript, SQLite**, and the **Google Gemini API (`google-genai` Python SDK)**.

### Problem Statement
Students spend considerable time preparing notes, summarizing study materials, organizing assignments, and creating revision plans. Develop an AI-powered academic productivity web application that helps students manage their learning activities.

### Required Key Features
1. **Generate study notes** from provided text.
2. **Create summaries** of study materials.
3. **Generate revision questions** (multiple-choice and short-answer questions with an answer key).
4. **Prepare assignment outlines** with structured sections and submission checklists.
5. **Create personalized study schedules** based on subjects, target exam date, daily available hours, and focus/weak areas.
6. **Organize learning tasks** (create, filter by status, mark complete/incomplete, set subject/priority/due date, and delete).
7. **Saved Study Library & Copy Support** so students can view, copy, and manage their saved AI-generated notes and schedules.

### Required 5-Page Wireframe
1. **Login Page (`/login`)**: Dark-themed authentication form with email and password validation using hashed passwords (`werkzeug.security`) and Flask sessions.
2. **Signup Page (`/signup`)**: Dark-themed registration form (full name, email, password, confirm password) storing users in SQLite.
3. **Dashboard & Learning Task Organizer (`/dashboard`)**: Summary stats (pending tasks, completed tasks, saved AI materials, saved schedules), quick links to AI tools, an "Add Learning Task" form, and a filterable task list (All / Pending / Completed) with toggle-complete and delete buttons.
4. **AI Study Studio (`/study-studio`)**: A 4-tab interactive workspace for Study Notes, Summaries, Revision Questions, and Assignment Outlines powered by Gemini AI via a Flask JSON endpoint (`/api/study-studio/generate`), with formatted Markdown output, one-click Copy button, and a Saved Study Library below.
5. **Personalized Study Schedule Planner (`/planner`)**: A form taking plan name, comma-separated subjects, target exam date, daily study hours, and priority focus areas, calling Gemini AI via `/api/planner/generate` to build and save a day-by-day revision schedule.

### Design & Code Quality Requirements
- **Dark Theme**: Use a clean, modern dark theme across all 5 pages using CSS custom properties (deep slate/navy backgrounds `#0b1120` / `#162033`, crisp high-contrast light text `#f1f5f9`, indigo `#6366f1` and teal `#14b8a6` accents, responsive two-column grid).
- **Gemini AI Integration**: Use the official `google-genai` Python SDK reading `GEMINI_API_KEY` and `GEMINI_MODEL` (default `gemini-2.5-flash`) from a `.env` file via `python-dotenv`. Include a graceful offline **Demo Mode fallback** when `GEMINI_API_KEY` is not set so the app never crashes during testing.
- **Simple, Well-Commented Code**: Keep the code clean, modular, and easy for a student to understand, with clear comments explaining every route, database table, helper function, CSS section, and JS handler.
- **GitHub-Ready Folder Structure**: Organize into `app.py`, `database.py`, `gemini_helper.py`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md`, `templates/` (`base.html`, `login.html`, `signup.html`, `dashboard.html`, `study_studio.html`, `planner.html`), and `static/` (`css/style.css`, `js/main.js`).
