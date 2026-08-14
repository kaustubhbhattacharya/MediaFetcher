import sqlite3
from datetime import datetime

from config import DATABASE_ROOT


def init_db():
    connection = sqlite3.connect(DATABASE_ROOT)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Download_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            file_name TEXT NOT NULL,
            media_type TEXT NOT NULL,
            download_date TEXT NOT NULL,
            download_location TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

def add_download_record(url, file_name, media_type, location):
    connection = sqlite3.connect(DATABASE_ROOT)
    cursor = connection.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO Download_history (url, file_name, media_type, download_date, download_location)
        VALUES (?, ?, ?, ?, ?)
    """, (url, file_name, media_type, now, location))
    connection.commit()
    connection.close()

def get_recent_downloads(limit=25):
    connection = sqlite3.connect(DATABASE_ROOT)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Download_history ORDER BY id DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    connection.close()
    return results

def delete_download_record(record_id):
    connection = sqlite3.connect(DATABASE_ROOT)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Download_history WHERE id = ?", (record_id,))
    connection.commit()
    connection.close()

def clear_all_history():
    connection = sqlite3.connect(DATABASE_ROOT)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Download_history")
    connection.commit()
    connection.close()