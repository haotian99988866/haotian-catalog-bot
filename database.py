import sqlite3
from typing import List, Dict, Optional

DB = "catalog.db"

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS episodes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_name TEXT NOT NULL,
            episode TEXT NOT NULL,
            tags TEXT,
            message_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(work_name, episode)
        )''')

def add_episode(work: str, ep: str, tags=None, mid=None) -> bool:
    try:
        with sqlite3.connect(DB) as c:
            c.execute("INSERT INTO episodes VALUES(NULL,?,?,?,?,CURRENT_TIMESTAMP)",
                     (work, ep, " ".join(tags or []), mid))
        return True
    except sqlite3.IntegrityError:
        return False

def update_message_id_if_exists(work: str, ep: str, mid: int) -> bool:
    with sqlite3.connect(DB) as c:
        c.execute("UPDATE episodes SET message_id=? WHERE work_name=? AND episode=?", (mid, work, ep))
        return c.rowcount > 0

def get_all_works() -> List[Dict]:
    with sqlite3.connect(DB) as c:
        rs = c.execute('''SELECT work_name,COUNT(*),GROUP_CONCAT(episode,'|||'),GROUP_CONCAT(message_id,'|||')
                          FROM episodes GROUP BY 1 ORDER BY MAX(created_at) DESC''').fetchall()
    return [{"work_name":r[0],"total_episodes":r[1],"episodes":
            [{"episode":e,"message_id":int(m)} for e,m in zip(r[2].split('|||'),r[3].split('|||'))]} for r in rs]

def get_episodes_of_work(work: str) -> Optional[Dict]:
    with sqlite3.connect(DB) as c:
        rs = c.execute("SELECT episode,message_id FROM episodes WHERE work_name=?", (work,)).fetchall()
    return {"work_name":work,"total_episodes":len(rs),"episodes":[{"episode":r[0],"message_id":r[1]}]} if rs else None

def search_works_by_keyword(kw: str) -> List[Dict]:
    with sqlite3.connect(DB) as c:
        rs = c.execute('''SELECT work_name,COUNT(*),GROUP_CONCAT(episode,'|||'),GROUP_CONCAT(message_id,'|||')
                          FROM episodes WHERE work_name LIKE ? GROUP BY 1 ORDER BY MAX(created_at) DESC''', (f"%{kw}%",)).fetchall()
    return [{"work_name":r[0],"total_episodes":r[1],"episodes":
            [{"episode":e,"message_id":int(m)} for e,m in zip(r[2].split('|||'),r[3].split('|||'))]} for r in rs]
