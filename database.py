# 内存临时存储，如需持久化可替换为 SQLite
_works = {}

def get_all_works():
    """返回所有作品列表"""
    return list(_works.values())

def get_episodes_of_work(work_name):
    """按作品名获取详情"""
    return _works.get(work_name)

def add_or_update_work(work_name, total_episodes, uploaded_episodes):
    """添加/更新作品信息"""
    _works[work_name] = {
        "work_name": work_name,
        "total_episodes": total_episodes,
        "actual_uploaded": len(uploaded_episodes),
        "uploaded_list": uploaded_episodes
    }
