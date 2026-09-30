import sqlite3
import os
from datetime import datetime

DEFAULT_EXPENSE_CATEGORIES = [
    "Food", "Transport", "Utilities", "Entertainment", "Health", "Shopping", "Other"
]

DEFAULT_INCOME_CATEGORIES = [
    "Salary", "Business", "Freelance", "Gift", "Investment", "Other"
]

class LocalDatabase:
    def __init__(self, db_path="finance_app.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Default settings
            default_settings = {
                "language": "uz",
                "currency": "uzs",
                "fullname": "User",
                "sex": "male",
                "social_status": "employee"
            }
            for k, v in default_settings.items():
                cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

            # Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    UNIQUE(type, name)
                )
            """)

            # Insert default categories
            for cat in DEFAULT_EXPENSE_CATEGORIES:
                cursor.execute("INSERT OR IGNORE INTO categories (type, name) VALUES (?, ?)", ("expense", cat))
            for cat in DEFAULT_INCOME_CATEGORIES:
                cursor.execute("INSERT OR IGNORE INTO categories (type, name) VALUES (?, ?)", ("income", cat))

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    source TEXT NOT NULL,
                    additional_info TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    # --- Settings ---
    def get_setting(self, key: str, default: str = None) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    def get_all_settings(self) -> dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}

    # --- Categories ---
    def get_categories(self, cat_type: str) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories WHERE type = ? ORDER BY id ASC", (cat_type,))
            rows = cursor.fetchall()
            return [{"id": row["id"], "name": row["name"]} for row in rows]

    def add_category(self, cat_type: str, name: str) -> bool:
        name = name.strip()
        if not name:
            return False
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (type, name) VALUES (?, ?)", (cat_type, name))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_category(self, cat_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Transactions ---
    def add_transaction(self, trans_type: str, amount: float, currency: str, source: str, additional_info: str = "") -> int:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (type, amount, currency, source, additional_info, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (trans_type, amount, currency, source, additional_info, created_at))
            conn.commit()
            return cursor.lastrowid

    def get_transactions(self, limit: int = 50) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
