"""
Database layer for Couples Bucket List App.
SQLite setup, connection helper, and schema initialization.
"""

import sqlite3
import os

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "bucket_list.db")

# Default categories for couples goals
DEFAULT_CATEGORIES = [
    ("Travel", "✈️"),
    ("Food", "🍽️"),
    ("Experience", "🎭"),
    ("Life", "🏠"),
    ("Challenges", "💪"),
    ("Romance", "💌"),
]


def get_connection():
    """Get a SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables and seed default categories if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avatar TEXT DEFAULT '😊',
            pin_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            emoji TEXT DEFAULT '📌'
        );

        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category_id INTEGER NOT NULL,
            added_by INTEGER NOT NULL,
            goal_type TEXT DEFAULT 'together' CHECK(goal_type IN ('together', 'solo')),
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'completed')),
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (added_by) REFERENCES partners(id)
        );

        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            partner_id INTEGER NOT NULL,
            vote TEXT NOT NULL CHECK(vote IN ('approve', 'skip')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES goals(id),
            FOREIGN KEY (partner_id) REFERENCES partners(id),
            UNIQUE(goal_id, partner_id)
        );
    """)

    # Seed categories if empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO categories (name, emoji) VALUES (?, ?)",
            DEFAULT_CATEGORIES,
        )

    conn.commit()
    conn.close()


def is_setup_complete():
    """Check if both partners have been registered."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM partners").fetchone()[0]
    conn.close()
    return count >= 2


def get_partners():
    """Return all registered partners."""
    conn = get_connection()
    partners = conn.execute("SELECT * FROM partners ORDER BY id").fetchall()
    conn.close()
    return partners


def get_categories():
    """Return all categories."""
    conn = get_connection()
    cats = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return cats
