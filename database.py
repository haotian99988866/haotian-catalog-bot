import sqlite3
from typing import List, Dict, Optional


DB_FILE = "catalog.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_name TEXT NOT NULL,
            episode TEXT NOT NULL,
            tags TEXT,
            message_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(work_name, episode)
        )
    ''')
    
    conn.commit()
    conn.close()


def add_episode(work_name: str, episode: str, tags: List[str] = None, message_id: int = None) -> bool:
    tags_str = " ".join(tags or [])
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO episodes (work_name, episode, tags, message_id) VALUES (?, ?, ?, ?)",
            (work_name, episode, tags_str, message_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_message_id_if_exists(work_name: str, episode: str, message_id: int) -> bool:
    """集已存在则更新链接，返回是否更新"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE episodes SET message_id = ? WHERE work_name = ? AND episode = ?",
        (message_id, work_name, episode)
    )
    updated = c.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def get_all_works() -> List[Dict]:
    """获取所有作品分组及集数统计"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT 
            work_name,
            COUNT(*) as total_episodes,
            GROUP_CONCAT(episode, '|||') as episodes,
            GROUP_CONCAT(message_id, '|||') as message_ids,
            MAX(created_at) as latest_at
        FROM episodes
        GROUP BY work_name
        ORDER BY latest_at DESC
    ''')
    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        episodes = row[2].split('|||')
        msg_ids = row[3].split('|||')
        result.append({
            "work_name": row[0],
            "total_episodes": row[1],
            "episodes": [{"episode": e, "message_id": int(mid)} for e, mid in zip(episodes, msg_ids)]
        })
    return result


def get_episodes_of_work(work_name: str) -> Optional[Dict]:
    """获取指定作品的全部集数"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT episode, message_id FROM episodes 
        WHERE work_name = ? ORDER BY rowid
    ''', (work_name,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        return None

    return {
        "work_name": work_name,
        "total_episodes": len(rows),
        "episodes": [{"episode": r[0], "message_id": r[1]} for r in rows]
    }


def search_works_by_keyword(keyword: str) -> List[Dict]:
    """搜索作品，按名称分组"""
    keyword = f"%{keyword}%"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT 
            work_name,
            COUNT(*) as total_episodes,
            GROUP_CONCAT(episode, '|||') as episodes,
            GROUP_CONCAT(message_id, '|||') as message_ids
        FROM episodes
        WHERE work_name LIKE ?
        GROUP BY work_name
        ORDER BY MAX(created_at) DESC
    ''', (keyword,))
    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        episodes = row[2].split('|||')
        msg_ids = row[3].split('|||')
        result.append({
            "work_name": row[0],
            "total_episodes": row[1],
            "episodes": [{"episode": e, "message_id": int(mid)} for e, mid in zip(episodes, msg_ids)]
        })
    return result
