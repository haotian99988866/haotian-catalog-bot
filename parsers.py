import re
from typing import Dict, Optional

def parse_message_text(text: Optional[str]) -> Dict[str, Optional[str]]:
    """解析频道消息文本，提取剧名、季、集数"""
    result = {
        "show_name": None,
        "season": None,
        "episode": None,
        "title": None
    }
    if not text:
        return result
    
    # 提取《》中的剧名
    title_match = re.search(r"《([^》]+)》", text)
    if title_match:
        result["show_name"] = title_match.group(1).strip()
        result["title"] = result["show_name"]
    
    # 匹配季数
    season_match = re.search(r"(第[一二三四五六七八九十\d]+季|Season\s*\d+)", text, re.I)
    if season_match:
        result["season"] = season_match.group(1)
    
    # 匹配集数
    ep_match = re.search(r"第(\d+)集|(\d+)(?=\s|$)", text)
    if ep_match:
        result["episode"] = ep_match.group(1) or ep_match.group(2)
    
    return result

def extract_tags(text: Optional[str]) -> str:
    """提取 #标签"""
    if not text:
        return ""
    tags = re.findall(r"#(\w+)", text)
    return " ".join(tags)