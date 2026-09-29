import sqlite3
import json

DB_PATH = "courses.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            level TEXT,
            data TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtopic_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            subtopic_title TEXT,
            content TEXT,
            review TEXT,
            quiz TEXT,
            UNIQUE(filename, subtopic_title)
        )
    """)
    conn.commit()
    conn.close()


def save_course(topic: str, level: str, course_data: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO courses (topic, level, data) VALUES (?, ?, ?)",
        (topic, level, json.dumps(course_data))
    )
    conn.commit()
    course_id = cursor.lastrowid
    conn.close()
    return course_id


def get_course(course_id: int) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM courses WHERE id = ?", (course_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None


def save_subtopic_content(filename: str, subtopic_title: str, content: str, review: str, quiz: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO subtopic_content (filename, subtopic_title, content, review, quiz)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(filename, subtopic_title) DO UPDATE SET
            content=excluded.content, review=excluded.review, quiz=excluded.quiz
    """, (filename, subtopic_title, content, review, json.dumps(quiz)))
    conn.commit()
    conn.close()


def get_subtopic_content(filename: str, subtopic_title: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT content, review, quiz FROM subtopic_content WHERE filename=? AND subtopic_title=?",
        (filename, subtopic_title)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"content": row[0], "review": row[1], "quiz": json.loads(row[2])}
    return None


def save_full_course(filename: str, course_data: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO courses (topic, level, data) VALUES (?, ?, ?)",
        (filename, "", json.dumps(course_data))
    )
    conn.commit()
    course_id = cursor.lastrowid
    conn.close()
    return course_id


def list_saved_courses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic FROM courses ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "filename": r[1]} for r in rows]