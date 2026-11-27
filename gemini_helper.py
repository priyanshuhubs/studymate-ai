"""
gemini_helper.py
----------------
Connects StudyMate AI to Google's Gemini API using the official `google-genai` SDK.
If no GEMINI_API_KEY is set in `.env`, this module automatically falls back to a
helpful offline Demo Mode so the application can still be tested and demonstrated
without crashing.
"""

import os
from datetime import date, datetime, timedelta

# Try importing the official Google GenAI SDK
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

# Default model name (can be overridden in .env with GEMINI_MODEL)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def is_gemini_configured():
    """Returns True when the google-genai SDK is installed and GEMINI_API_KEY is set."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(GENAI_AVAILABLE and api_key and api_key != "your_gemini_api_key_here")


def _call_gemini(prompt):
    """
    Sends a prompt to the configured Gemini model and returns the generated text.
    Raises an exception if the API call fails so the caller can fall back gracefully.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    return response.text.strip()


def generate_study_content(mode, title, source_text, extra_option=""):
    """
    Generates academic study content based on the selected mode:
      - 'notes'     : Structured study notes from provided text
      - 'summary'   : Concise summary of study materials
      - 'questions' : Revision questions (MCQs + short-answer with answer key)
      - 'outline'   : Structured assignment outline

    Returns a tuple: (generated_markdown_text, used_live_ai_bool)
    """
    clean_title = title.strip() or "Study Topic"
    clean_text = source_text.strip()

    # Build a clear, student-friendly prompt for each mode
    prompts = {
        "notes": (
            f"You are StudyMate AI, an expert academic tutor. "
            f"Convert the following study material about '{clean_title}' into clear, well-structured study notes.\n"
            f"Include:\n"
            f"1. Key Concepts & Definitions\n"
            f"2. Detailed Bullet-Point Breakdown\n"
            f"3. Important Examples or Formulas (if applicable)\n"
            f"4. Quick Revision Takeaways\n\n"
            f"Study Material:\n{clean_text}"
        ),
        "summary": (
            f"You are StudyMate AI, an academic assistant. "
            f"Summarize the following study material about '{clean_title}'.\n"
            f"Include:\n"
            f"1. One-Paragraph Executive Summary\n"
            f"2. 5 Key Bullet Points\n"
            f"3. Important Terms to Remember\n\n"
            f"Study Material:\n{clean_text}"
        ),
        "questions": (
            f"You are StudyMate AI, an exam preparation coach. "
            f"Create revision questions from the following material about '{clean_title}'.\n"
            f"Difficulty/Preference: {extra_option or 'Balanced (Medium)'}\n"
            f"Include:\n"
            f"1. 5 Multiple-Choice Questions (with options A-D)\n"
            f"2. 3 Short-Answer Questions\n"
            f"3. A clearly separated Answer Key at the bottom.\n\n"
            f"Study Material:\n{clean_text}"
        ),
        "outline": (
            f"You are StudyMate AI, an academic writing mentor. "
            f"Prepare a structured assignment outline for the topic '{clean_title}'.\n"
            f"Additional instructions/requirements: {extra_option or 'Standard college assignment'}\n"
            f"Include:\n"
            f"1. Proposed Title & Thesis Statement\n"
            f"2. Section-by-Section Outline (Introduction, Body Sections, Conclusion)\n"
            f"3. Key Points & Suggested Evidence for each section\n"
            f"4. Checklist before Submission\n\n"
            f"Topic Details / Prompt:\n{clean_text}"
        ),
    }

    prompt = prompts.get(mode, prompts["notes"])

    # Try calling live Gemini API first
    if is_gemini_configured():
        try:
            return _call_gemini(prompt), True
        except Exception as err:
            fallback = _demo_study_content(mode, clean_title, clean_text)
            note = f"> **Note:** Live Gemini API call failed ({err}). Showing Demo Mode output instead.\n\n"
            return note + fallback, False

    # Offline Demo Mode fallback when API key is not configured yet
    return _demo_study_content(mode, clean_title, clean_text), False


def generate_study_schedule(subjects, exam_date, daily_hours, focus_areas=""):
    """
    Generates a personalized study schedule using Gemini AI (or Demo Mode fallback).
    Returns a tuple: (generated_schedule_markdown, used_live_ai_bool)
    """
    today_str = date.today().isoformat()
    prompt = (
        f"You are StudyMate AI, an academic study planner. "
        f"Create a realistic, personalized day-by-day study schedule starting from {today_str} "
        f"until the target exam/deadline date {exam_date}.\n"
        f"- Subjects to cover: {subjects}\n"
        f"- Available study hours per day: {daily_hours} hours\n"
        f"- Priority / weak areas: {focus_areas or 'Balanced coverage across all subjects'}\n\n"
        f"Format the output cleanly with:\n"
        f"1. Strategy Overview (time allocation per subject)\n"
        f"2. Day-by-Day Study Plan (keep to at most 7-10 focused days or weekly blocks if far away)\n"
        f"3. Short Break & Revision Tips (e.g., Pomodoro intervals & active recall)."
    )

    if is_gemini_configured():
        try:
            return _call_gemini(prompt), True
        except Exception as err:
            fallback = _demo_study_schedule(subjects, exam_date, daily_hours, focus_areas)
            note = f"> **Note:** Live Gemini API call failed ({err}). Showing Demo Mode schedule instead.\n\n"
            return note + fallback, False

    return _demo_study_schedule(subjects, exam_date, daily_hours, focus_areas), False


def _demo_study_content(mode, title, source_text):
    """Generates clean, structured sample output when running without a Gemini API key."""
    # Extract a few short preview sentences from the user's input
    sentences = [s.strip() for s in source_text.replace("\n", " ").split(".") if s.strip()]
    preview_1 = sentences[0] if len(sentences) > 0 else f"Core fundamentals of {title}"
    preview_2 = sentences[1] if len(sentences) > 1 else f"Key concepts and real-world applications of {title}"
    preview_3 = sentences[2] if len(sentences) > 2 else f"Important takeaways to review before exams"

    banner = "> **Demo Mode Active:** Add your `GEMINI_API_KEY` in `.env` for live Gemini AI responses.\n\n"

    if mode == "summary":
        return (
            f"{banner}"
            f"## Summary: {title}\n\n"
            f"### Overview\n"
            f"This study material explains **{title}**, highlighting how its core ideas connect together. "
            f"{preview_1}.\n\n"
            f"### Key Takeaways\n"
            f"- **Main Idea:** {preview_1}.\n"
            f"- **Supporting Detail:** {preview_2}.\n"
            f"- **Revision Focus:** {preview_3}.\n"
            f"- **Exam Tip:** Practice explaining {title} in your own words without looking at your notes."
        )

    if mode == "questions":
        return (
            f"{banner}"
            f"## Revision Questions: {title}\n\n"
            f"### Multiple-Choice Questions\n"
            f"1. What is the primary focus of **{title}**?\n"
            f"   - A) {preview_1}\n"
            f"   - B) An unrelated historical event\n"
            f"   - C) Only hardware configuration\n"
            f"   - D) None of the above\n\n"
            f"2. Which strategy best reinforces understanding of **{title}**?\n"
            f"   - A) Passive re-reading once\n"
            f"   - B) Active recall and spaced repetition\n"
            f"   - C) Skipping practice problems\n"
            f"   - D) Memorizing without context\n\n"
            f"### Short-Answer Questions\n"
            f"1. Explain the main concept behind **{title}** in 3–4 sentences.\n"
            f"2. Describe one practical example or use case related to **{title}**.\n"
            f"3. Summarize the significance of: *{preview_2}*.\n\n"
            f"### Answer Key\n"
            f"- **MCQ 1:** A\n"
            f"- **MCQ 2:** B\n"
            f"- **Short Answers:** Compare your explanation against your core notes on {title}."
        )

    if mode == "outline":
        return (
            f"{banner}"
            f"## Assignment Outline: {title}\n\n"
            f"### 1. Introduction (10–15%)\n"
            f"- Hook / background context on **{title}**\n"
            f"- Problem definition: {preview_1}\n"
            f"- Clear thesis statement outlining your main argument\n\n"
            f"### 2. Core Concepts & Literature Background (25–30%)\n"
            f"- Define key terminology and foundational principles\n"
            f"- Discuss supporting context: {preview_2}\n\n"
            f"### 3. Analysis & Practical Application (35–40%)\n"
            f"- Break down the topic into 2–3 structured sub-sections\n"
            f"- Include concrete examples, diagrams, or case studies\n"
            f"- Address challenges, limitations, or comparisons\n\n"
            f"### 4. Conclusion & Future Scope (15%)\n"
            f"- Restate key findings clearly\n"
            f"- Summarize takeaway: {preview_3}\n\n"
            f"### 5. Pre-Submission Checklist\n"
            f"- Verify citations and formatting guidelines\n"
            f"- Proofread headings, grammar, and word count"
        )

    # Default: 'notes'
    return (
        f"{banner}"
        f"## Study Notes: {title}\n\n"
        f"### 1. Core Concept\n"
        f"- **{title}:** {preview_1}.\n\n"
        f"### 2. Structured Breakdown\n"
        f"- **Point 1:** {preview_1}.\n"
        f"- **Point 2:** {preview_2}.\n"
        f"- **Point 3:** {preview_3}.\n\n"
        f"### 3. Quick Revision Tips\n"
        f"- Highlight definitions and draw a quick concept map.\n"
        f"- Test yourself using the **Revision Questions** tab after reading."
    )


def _demo_study_schedule(subjects, exam_date, daily_hours, focus_areas):
    """Generates a clean sample day-by-day study schedule in Demo Mode."""
    subject_list = [s.strip() for s in subjects.split(",") if s.strip()] or ["Core Subject"]
    start_day = date.today()

    try:
        target = datetime.strptime(exam_date, "%Y-%m-%d").date()
        days_left = max(1, (target - start_day).days)
    except ValueError:
        days_left = 5

    plan_days = min(days_left, 5)
    lines = [
        "> **Demo Mode Active:** Add your `GEMINI_API_KEY` in `.env` for live AI-tailored study schedules.\n",
        f"## Personalized Study Schedule (Target: {exam_date})",
        f"- **Subjects:** {', '.join(subject_list)}",
        f"- **Daily Budget:** {daily_hours} hours/day",
        f"- **Focus Areas:** {focus_areas or 'Balanced coverage across all subjects'}\n",
        "### Day-by-Day Plan",
    ]

    for i in range(plan_days):
        current_day = start_day + timedelta(days=i)
        primary_subject = subject_list[i % len(subject_list)]
        secondary_subject = subject_list[(i + 1) % len(subject_list)]
        half_hours = round(float(daily_hours) / 2, 1)
        lines.append(
            f"- **Day {i + 1} ({current_day.strftime('%a, %b %d')}):**\n"
            f"  - Session 1 ({half_hours}h): Deep study & note-making for **{primary_subject}**\n"
            f"  - Session 2 ({half_hours}h): Practice questions & recap for **{secondary_subject}**"
        )

    lines.append("\n### Study Technique Tip")
    lines.append("- Use 50-minute focus blocks followed by 10-minute breaks, and review key flashcards before sleep.")
    return "\n".join(lines)
