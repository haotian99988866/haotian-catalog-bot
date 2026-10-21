import sqlite3
import re
from typing import List, Dict, Optional

DB = "catalog.db"

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS episodes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_name TEXT NOT NULL,
            episode TEXT NOT NULL,
            episode_num INTEGER,
            episode_type TEXT NOT NULL DEFAULT '集',
            tags TEXT,
            message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(work_name, episode)
        )''')

def parse_episode_text(ep_text: str) -> tuple:
    """解析：返回 (数字, 类型) 例：第5期 → (5, '期')"""
    m = re.search(r"第\s*(\d+)\s*(集|期|季|部)", ep_text)
    if m:
        return int(m.group(1)), m.group(2)
    m2 = re.search(r"(\d+)", ep_text)
    if m2:
        return int(m2.group(1)), "集"
    return None, "集"

def add_episode(work: str, ep: str, tags=None, mid=None) -> bool:
    ep_num, ep_type = parse_episode_text(ep)
    try:
        with sqlite3.connect(DB) as c:
            c.execute(
                "INSERT INTO episodes VALUES(NULL,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                (work, ep, ep_num, ep_type, " ".join(tags or []), mid)
            )
        return True
    except sqlite3.IntegrityError:
        return False

def update_message_id_if_exists(work: str, ep: str, mid: int) -> bool:
    with sqlite3.connect(DB) as c:
        c.execute("UPDATE episodes SET message_id=? WHERE work_name=? AND episode=?", (mid, work, ep))
        return c.rowcount > 0

def get_all_works() -> List[Dict]:
    with sqlite3.connect(DB) as c:
        rs = c.execute('''
            SELECT work_name, COUNT(*),
                   MIN(episode_num), MAX(episode_num),
                   GROUP_CONCAT(episode, '|||'),
                   GROUP_CONCAT(episode_num, '|||'),
                   GROUP_CONCAT(episode_type, '|||'),
                   GROUP_CONCAT(COALESCE(message_id, ''), '|||')
            FROM episodes GROUP BY 1 ORDER BY MAX(created_at) DESC
        ''').fetchall()
    result = []
    for r in rs:
        eps = []
        ep_texts = r[4].split('|||')
        ep_nums = [int(x) if x else None for x in r[5].split('|||')]
        ep_types = r[6].split('|||')
        msg_ids = r[7].split('|||')
        stored = dict(zip(ep_nums, zip(ep_texts, ep_types, msg_ids)))
        
        max_num = r[3] or 1
        main_type = "期" if any(t == "期" for t in ep_types) else "集"
        
        for n in range(1, max_num + 1):
            if n in stored and stored[n][2]:
                eps.append({
                    "episode": stored[n][0],
                    "episode_num": n,
                    "episode_type": stored[n][1],
                    "message_id": int(stored[n][2]),
                    "has_link": True
                })
            else:
                eps.append({
                    "episode": f"第{n}{main_type}",
                    "episode_num": n,
                    "episode_type": main_type,
                    "message_id": None,
                    "has_link": False
                })
        result.append({
            "work_name": r[0],
            "total_episodes": max_num,
            "actual_uploaded": r[1],
            "main_type": main_type,
            "episodes": eps
        })
    return result

def get_episodes_of_work(work: str) -> Optional[Dict]:
    all_works = get_all_works()
    for w in all_works:
        if w["work_name"] == work:
            return w
    return None

def search_works_by_keyword(kw: str) -> List[Dict]:
    with sqlite3.connect(DB) as c:
        rs = c.execute('''
            SELECT work_name FROM episodes WHERE work_name LIKE ?
            GROUP BY work_name ORDER BY MAX(created_at) DESC
        ''', (f"%{kw}%",)).fetchall()
    matched = [r[0] for r in rs]
    return [w for w in get_all_works() if w["work_name"] in matched]
