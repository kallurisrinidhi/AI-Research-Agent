
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "research_history.db"


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            analysis TEXT NOT NULL,
            total_sources INTEGER,
            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_research(topic, analysis, total_sources):
    create_database()

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO research_history
        (topic, analysis, total_sources, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        topic,
        analysis,
        total_sources,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()

    print("Research saved successfully!")


def get_research_history():
    create_database()

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, topic, total_sources, created_at
        FROM research_history
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    return records


def get_research_by_id(research_id):
    create_database()

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, topic, analysis, total_sources, created_at
        FROM research_history
        WHERE id = ?
    """, (research_id,))

    record = cursor.fetchone()
    connection.close()

    return record
if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
    print("Database location:", DB_PATH)