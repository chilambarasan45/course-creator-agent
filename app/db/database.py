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