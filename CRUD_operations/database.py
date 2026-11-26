
import sqlite3
from pathlib import Path

# Locate the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to the existing SQLite database
DB_PATH = BASE_DIR / "database" / "chicago_crime.db"


def get_connection():
    """Create and return a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create a separate table for CRUD API operations."""

    conn = get_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crime_records_api (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT NOT NULL UNIQUE,
                date TEXT,
                block TEXT,
                iucr_code TEXT,
                location_desc TEXT,
                arrest TEXT,
                domestic TEXT,
                beat_num TEXT,
                district_code TEXT,
                ward_no INTEGER,
                community_code TEXT,
                fbi_code TEXT,
                x_coordinate REAL,
                y_coordinate REAL,
                year INTEGER,
                date_of_update TEXT,
                latitude REAL,
                longitude REAL,
                location TEXT,
                Month INTEGER,
                DayOfWeek TEXT
            )
        """)

        conn.commit()

    finally:
        conn.close()
