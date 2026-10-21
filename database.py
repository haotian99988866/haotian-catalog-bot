import sqlite3
from typing import List, Dict, Optional


DB_FILE = "catalog.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            tags TEXT,
            message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def add_show(title: str, tags: List[str] = None, message_id: int = None):
    tags_str = " ".join(tags or [])
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO shows (title, tags, message_id) VALUES (?, ?, ?)",
            (title, tags_str, message_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def show_exists(title: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM shows WHERE title = ?", (title,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


# ✅ 新增：更新影片的 message_id，补全旧链接
def update_message_id(title: str, message_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE shows SET message_id = ? WHERE title = ?",
        (message_id, title)
    )
    conn.commit()
    conn.close()


def get_all_shows() -> List[Dict]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, tags, message_id, created_at FROM shows ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "title": row[1],
            "tags": row[2].split() if row[2] else [],
            "message_id": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]


def search_shows(keyword: str) -> List[Dict]:
    keyword = f"%{keyword}%"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT id, title, tags, message_id, created_at FROM shows WHERE title LIKE ? ORDER BY created_at DESC",
        (keyword,)
    )
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "title": row[1],
            "tags": row[2].split() if row[2] else [],
            "message_id": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]


def get_shows_by_tags(tag: str) -> List[Dict]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, tags, message_id, created_at FROM shows ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "title": row[1],
            "tags": row[2].split() if row[2] else [],
            "message_id": row[3],
            "created_at": row[4]
        }
        for row in rows
        if tag in (row[2] or "").split()
    ]
