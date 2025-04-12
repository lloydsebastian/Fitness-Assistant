import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_name = os.getenv("DATABASE_NAME", "fitness_tracker.db")
        self.conn = sqlite3.connect(self.db_name)
        self.create_tables()
    
    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    age INTEGER,
                    sex TEXT,
                    height INTEGER,
                    weight INTEGER,
                    goal TEXT,
                    routine TEXT,
                    progress TEXT DEFAULT '',
                    start_date TEXT
                )
            """)
    
    def get_user(self, user_id):
        return self.conn.execute(
            "SELECT * FROM users WHERE user_id = ?", 
            (user_id,)
        ).fetchone()
    
    def update_user(self, user_id, **kwargs):
        set_clause = ", ".join([f"{k} = ?" for k in kwargs])
        values = list(kwargs.values()) + [user_id]
        self.conn.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ?",
            values
        )
        self.conn.commit()