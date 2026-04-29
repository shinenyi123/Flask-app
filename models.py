"""
Database models and operations for the Student Dashboard application.
Handles all SQLite database interactions.
"""
import sqlite3
from typing import List, Tuple, Optional, Dict, Any
from contextlib import contextmanager
import config


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


@contextmanager
def get_db_connection():
    """Context manager for database connections with proper cleanup."""
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH, timeout=config.DB_TIMEOUT)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        raise DatabaseError(f"Database connection error: {e}")
    finally:
        if conn:
            conn.close()


def init_database() -> None:
    """Initialize the database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                စဉ် TEXT,
                ကျောင်းဝင်အမှတ် INTEGER UNIQUE,
                နံမည် TEXT NOT NULL,
                ကျားမ TEXT,
                အဖေနံမည် TEXT,
                မွေးနေ့ TEXT,
                class TEXT
            )
        """)
        conn.commit()


def get_all_students() -> List[Tuple]:
    """Fetch all students from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT စဉ်, ကျောင်းဝင်အမှတ်, နံမည်, ကျားမ, အဖေနံမည်, မွေးနေ့, class 
            FROM students
            ORDER BY CAST(စဉ် AS INTEGER)
        """)
        return cursor.fetchall()


def insert_student(no: int, school_no: int, name: str, gender: str, 
                   father_name: str, birthday: str, class_name: str) -> bool:
    """Insert a single student record. Returns True if successful."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO students 
                (စဉ်, ကျောင်းဝင်အမှတ်, နံမည်, ကျားမ, အဖေနံမည်, မွေးနေ့, class)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (no, school_no, name, gender, father_name, birthday, class_name))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False  # Duplicate school_no


def bulk_insert_students(student_data: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Bulk insert students from a list of dictionaries.
    Returns (successful_inserts, failed_inserts) count.
    """
    success_count = 0
    fail_count = 0
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for student in student_data:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO students 
                    (စဉ်, ကျောင်းဝင်အမှတ်, နံမည်, ကျားမ, အဖေနံမည်, မွေးနေ့, class)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    student.get('စဉ်'),
                    student.get('ကျောင်းဝင်အမှတ်'),
                    student.get('နံမည်'),
                    student.get('ကျားမ'),
                    student.get('အဖေနံမည်'),
                    student.get('မွေးနေ့'),
                    student.get('class')
                ))
                if cursor.rowcount > 0:
                    success_count += 1
                else:
                    fail_count += 1
            except sqlite3.Error:
                fail_count += 1
        
        conn.commit()
    
    return success_count, fail_count


def get_student_count() -> Dict[str, int]:
    """Get total count of students by gender."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ကျားမ, COUNT(*) as count FROM students GROUP BY ကျားမ")
        results = cursor.fetchall()
        
        counts = {'all': 0, 'male': 0, 'female': 0}
        for row in results:
            gender = row[0]
            count = row[1]
            counts['all'] += count
            if gender == 'ကျား':
                counts['male'] = count
            elif gender == 'မ':
                counts['female'] = count
        
        return counts


def clear_all_students() -> int:
    """Clear all student records. Returns count of deleted records."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM students")
        conn.commit()
        
        return count