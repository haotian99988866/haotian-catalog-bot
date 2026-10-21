import sqlite3
from typing import List, Dict, Optional


DB_FILE = "catalog.db"


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 影片表
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
    """添加影片，已存在返回 False"""
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
    """检查影片是否已收录"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM shows WHERE title = ?", (title,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def get_all_shows() -> List[Dict]:
    """获取全部影片，按时间倒序"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, tags, created_at FROM shows ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "title": row[1],
            "tags": row[2].split() if row[2] else [],
            "created_at": row[3]
        }
        for row in rows
    ]


def search_shows(keyword: str) -> List[Dict]:
    """按关键词搜索片名"""
    keyword = f"%{keyword}%"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT id, title, tags, created_at FROM shows WHERE title LIKE ? ORDER BY created_at DESC",
        (keyword,)
    )
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "title": row[1],
            "tags": row[2].split() if row[2] else [],
            "created_at": row[3]
        }
        for row in rows
    ]


def get_shows_by_tags(tag: str) -> List[Dict]:
    """按标签筛选"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, tags, created_at FROM shows ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "title": row[1],
            "tags": row[2].split() if row[2] else [],
            "created_at": row[3]
        }
        for row in rows
        if tag in (row[2] or "").split()
    ]
