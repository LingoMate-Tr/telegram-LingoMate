# database.py
import sqlite3
import logging

logger = logging.getLogger(__name__)

def initialize_database():
    conn = sqlite3.connect('user_preferences.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            translation_mode TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def set_user_preference(user_id: int, translation_mode: str):
    conn = sqlite3.connect('user_preferences.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_preferences (user_id, translation_mode)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET translation_mode = excluded.translation_mode
    ''', (user_id, translation_mode))
    conn.commit()
    conn.close()

def get_user_preference(user_id: int) -> str:
    conn = sqlite3.connect('user_preferences.db')
    cursor = conn.cursor()
    cursor.execute('SELECT translation_mode FROM user_preferences WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
