
import sqlite3
from contextlib import contextmanager
from pathlib import Path
import json

DB_PATH = Path(__file__).parent / "lesson_memory.db"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS lesson_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                rejection_log TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS learning_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                criterion TEXT NOT NULL,
                suggestion TEXT NOT NULL,
                occurrences INTEGER DEFAULT 1,
                UNIQUE(criterion, suggestion)
            )
        """)


def save_run(topic, status, attempts, rejection_log):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO lesson_runs
            (topic, status, attempts, rejection_log)
            VALUES (?, ?, ?, ?)
            """,
            (topic, status, attempts, json.dumps(rejection_log))
        )


def get_previous_runs(topic):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM lesson_runs
            WHERE topic = ?
            ORDER BY id DESC
            """,
            (topic,)
        ).fetchall()

    return [dict(row) for row in rows]


def learn_from_rejections(rejection_log):
    """Store repeated improvement suggestions from failed evaluations."""

    with get_connection() as connection:
        for rejection in rejection_log:
            for criterion, details in rejection["failed_criteria"].items():
                suggestion = details["suggestion"].strip()

                if not suggestion:
                    continue

                connection.execute(
                    """
                    INSERT INTO learning_rules
                    (criterion, suggestion)
                    VALUES (?, ?)
                    ON CONFLICT(criterion, suggestion)
                    DO UPDATE SET occurrences = occurrences + 1
                    """,
                    (criterion, suggestion)
                )


def get_learning_rules():
    """Return improvement rules observed in at least two failures."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT criterion, suggestion, occurrences
            FROM learning_rules
            WHERE occurrences >= 2
            ORDER BY occurrences DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
