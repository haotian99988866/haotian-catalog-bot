import sqlite3
from typing import List, Tuple, Optional

DB_NAME = "catalog.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg_id INTEGER UNIQUE,
        title TEXT,
        show_name TEXT,
        season TEXT,
        episode TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_video(msg_id: int, title: str, show_name: str, 
               season: Optional[str], episode: Optional[str], tags: str = ""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''INSERT OR REPLACE INTO videos 
            (msg_id, title, show_name, season, episode, tags)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (msg_id, title, show_name, season, episode, tags))
    except Exception as e:
        print(f"保存失败: {e}")
    conn.commit()
    conn.close()

def get_all_shows() -> List[Tuple]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT show_name, COUNT(*) as cnt FROM videos GROUP BY show_name ORDER BY cnt DESC")
    res = c.fetchall()
    conn.close()
    return res

def get_episodes(show_name: str) -> List[Tuple]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT msg_id, show_name, season, episode FROM videos WHERE show_name = ? ORDER BY episode, msg_id", (show_name,))
    res = c.fetchall()
    conn.close()
    return res

def search_videos(keyword: str) -> List[Tuple]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    kw = f"%{keyword}%"
    c.execute("SELECT * FROM videos WHERE title LIKE ? OR show_name LIKE ? ORDER BY created_at DESC LIMIT 30", (kw, kw))
    res = c.fetchall()
    conn.close()
    return res