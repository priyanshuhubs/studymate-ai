"""
database.py
-----------
Handles SQLite database connection and table creation for StudyMate AI.
Using Python's built-in sqlite3 module means no external database server is needed.
"""

import os
import sqlite3

# Path to the local SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studymate.db")


def get_db_connection():
    """
    Opens a connection to the SQLite database.
    Setting row_factory = sqlite3.Row allows accessing columns by name
    (e.g., row['title']) instead of index numbers (e.g., row[1]).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates all required tables if they do not already exist.
    Tables:
      1. users           - Stores registered student accounts
      2. tasks           - Stores learning tasks & assignment to-dos
      3. study_materials - Stores AI-generated notes, summaries, questions, and outlines
      4. study_schedules - Stores AI-generated personalized study schedules
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table for Login & Signup
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Learning Tasks table (Organize learning tasks)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            subject TEXT DEFAULT 'General',
            priority TEXT DEFAULT 'Medium',
            due_date TEXT DEFAULT '',
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 3. AI Study Materials table (Notes, Summaries, Revision Questions, Assignment Outlines)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            material_type TEXT NOT NULL,
            title TEXT NOT NULL,
            source_text TEXT NOT NULL,
            ai_output TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 4. Personalized Study Schedules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            subjects TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            daily_hours REAL NOT NULL,
            focus_areas TEXT DEFAULT '',
            schedule_output TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
