# StudyMate AI – Academic Productivity Assistant

An AI-powered academic productivity web application built with **Python**, **[Flask](https://flask.palletsprojects.com/en/stable/quickstart/)**, **HTML/CSS/JavaScript**, **SQLite**, and the **[Google Gemini API](https://aistudio.google.com/docs/get-started)** (`google-genai`).

## Problem Statement

Students spend considerable time preparing notes, summarizing study materials, organizing assignments, and creating revision plans. **StudyMate AI** brings these academic workflows into one dark-themed web application powered by Google Gemini.

## Key Features

- **Student Authentication (`/login`, `/signup`)**: Secure registration and login using hashed passwords (`werkzeug.security`) and Flask sessions.
- **Dashboard & Learning Task Organizer (`/dashboard`)**: View productivity stats, add learning tasks with subject, priority, and due date, filter by status (All / Pending / Completed), toggle completion, and delete tasks.
- **AI Study Studio (`/study-studio`)**:
  - **Generate Study Notes** from pasted lecture text or textbook excerpts.
  - **Create Summaries** of long study materials.
  - **Generate Revision Questions** (multiple-choice and short-answer questions with an answer key).
  - **Prepare Assignment Outlines** with structured sections and a pre-submission checklist.
  - **Saved Study Library**: Automatically saves every generated output in SQLite with one-click copy and delete support.
- **Personalized Study Schedule Planner (`/planner`)**: Generates and saves a day-by-day revision timetable based on subjects, target exam date, daily study hours, and priority focus areas.
- **Dark Theme UI & Demo Mode Fallback**: Accessible dark theme across all 5 pages, plus an offline Demo Mode if `GEMINI_API_KEY` is not yet configured.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, [Flask](https://flask.palletsprojects.com/en/stable/quickstart/) |
| AI Model | [Google Gemini API](https://aistudio.google.com/docs/get-started) (`google-genai`, `gemini-3.5-flash-lite`) |
| Database | SQLite (`sqlite3`) |
| Frontend | HTML5 (Jinja2 Templates), CSS3 (Dark Theme), Vanilla JavaScript |
| Security & Config | `werkzeug.security` password hashing, `python-dotenv` |

## Wireframe (5 Pages)

| # | Page | Route | Description |
|---|------|-------|-------------|
| 1 | Login | `/login` | Student sign-in page |
| 2 | Sign Up | `/signup` | New student registration page |
| 3 | Dashboard & Task Organizer | `/dashboard` | Productivity summary cards and learning task manager |
| 4 | AI Study Studio | `/study-studio` | 4-tab Gemini AI workspace + saved study library |
| 5 | Study Schedule Planner | `/planner` | Personalized AI study schedule generator + saved plans |

## Project Structure

```text
studymate-ai/
├── app.py                    # Main Flask application & routes
├── database.py               # SQLite database initialization & helper
├── gemini_helper.py          # Google Gemini API integration & Demo Mode fallback
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template (safe for GitHub)
├── .gitignore                # Excludes .env, venv/, __pycache__/, and studymate.db
├── README.md                 # Project documentation
├── ANTIGRAVITY_PROMPT.md     # Complete Antigravity project prompt
├── templates/
│   ├── base.html             # Shared dark-theme layout & navbar
│   ├── login.html            # Page 1: Login
│   ├── signup.html           # Page 2: Sign Up
│   ├── dashboard.html        # Page 3: Dashboard & Task Organizer
│   ├── study_studio.html     # Page 4: AI Study Studio
│   └── planner.html          # Page 5: Study Schedule Planner
└── static/
    ├── css/
    │   └── style.css         # Dark theme styling
    └── js/
        └── main.js           # AJAX fetch calls, tab switching, Markdown rendering, filters
```

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/studymate-ai.git
   cd studymate-ai
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # macOS / Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy `.env.example` to `.env` and add your API key from [Google AI Studio](https://aistudio.google.com/docs/get-started):
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash-lite
   SECRET_KEY=change-this-to-a-random-secret-key
   ```

5. **Run the Flask server:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` (or `http://127.0.0.1:5001` if configured on port 5001) in your browser.

## Team Members

| # | Name | Role / Contribution | GitHub Profile |
|---|------|---------------------|----------------|
| 1 | [Member 1 Name] | [Backend & Gemini AI Integration] | [@member1-username] |
| 2 | [Member 2 Name] | [Frontend Templates & Dark Theme CSS] | [@member2-username] |
| 3 | [Member 3 Name] | [JavaScript Interactivity & Study Planner] | [@member3-username] |
| 4 | [Member 4 Name] | [Database Design, Testing & Documentation] | [@member4-username] |

## Course & Submission Info

- **Course / Subject:** [Subject or Course Name]
- **Institution:** [College / University Name]
- **Submitted To:** [Teacher / Faculty Name]
