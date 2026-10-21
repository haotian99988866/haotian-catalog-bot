import re

def parse_message_text(text: str) -> dict:
    if not text: return None
    m = re.search(r"《([^》]+)》", text)
    if not m: return None
    full = m.group(1).strip()
    epm = re.search(r"\s+(第\s*\d+\s*(?:集|期|季|部)|[上下]部)\s*$", full)
    if epm:
        work = re.sub(r"\s+第\s*\d+\s*(?:集|期|季|部)\s*$", "", full).strip()
        work = re.sub(r"\s+[上下]部\s*$", "", work).strip()
        ep = epm.group(1)
    else:
        work = full
        ep = "第1集"
    tags = re.findall(r"#(\w+)", text)
    return {"work_name": work, "episode": ep, "tags": tags}
