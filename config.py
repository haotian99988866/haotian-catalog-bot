BOT_TOKEN = "8929187714:AAFUOLvEDvKIvLXQpnT0VVsttH69oE_RdDA"

def validate():
    if not BOT_TOKEN or BOT_TOKEN == "8929187714:AAFUOLvEDvKIvLXQpnT0VVsttH69oE_RdDA":
        raise ValueError("请先在 config.py 中填写 BOT_TOKEN")
