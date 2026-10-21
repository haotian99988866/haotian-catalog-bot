BOT_TOKEN = "8929187714:AAFUOLvEDvKIvLXQpnT0VVsttH69oE_RdDA"

class Config:
    BOT_TOKEN = BOT_TOKEN

    @classmethod
    def validate(cls):
        token = cls.BOT_TOKEN.strip()
        if not token or len(token) < 30 or ":" not in token:
            raise ValueError("BOT_TOKEN 格式不正确或未填写")
