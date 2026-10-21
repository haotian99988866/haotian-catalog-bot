import re


def parse_message_text(text: str) -> dict:
    if not text:
        return None

    title_match = re.search(r"《([^》]+)》", text)
    if not title_match:
        return None

    full_title = title_match.group(1).strip()

    ep_pattern = r"\s+(第[零一二三四五六七八九十百\d]+(?:集|季|期)|[上下]部)\s*$"
    ep_match = re.search(ep_pattern, full_title)
    
    if ep_match:
        work_name = re.sub(ep_pattern, "", full_title).strip()
        episode = ep_match.group(1)
    else:
        work_name = full_title
        episode = "第1集"

    tags = re.findall(r"#(\w+)", text)

    return {
        "work_name": work_name,
        "episode": episode,
        "tags": tags
    }
