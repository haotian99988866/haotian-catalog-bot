import re


def parse_message_text(text: str) -> dict:
    """解析频道消息：片名、集数、标签"""
    if not text:
        return None

    # 匹配《片名》
    title_match = re.search(r"《([^》]+)》", text)
    if not title_match:
        return None

    title = title_match.group(1).strip()

    # 提取集数：第X集 / 第XX集 / 第X季 第X集
    episode = ""
    ep_match = re.search(r"(第[零一二三四五六七八九十\d]+(?:集|季))", text)
    if ep_match:
        episode = ep_match.group(1)
        title = f"{title} {episode}"  # 合并到片名显示

    # 提取标签：#标签
    tags = re.findall(r"#(\w+)", text)

    return {
        "title": title,
        "tags": tags,
        "episode": episode
    }
