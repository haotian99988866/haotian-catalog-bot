BOT_TOKEN = "8929187714:AAFUOLvEDvKIvLXQpnT0VVsttH69oE_RdDA"

class Config:
    BOT_TOKEN = BOT_TOKEN

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "8929187714:AAFUOLvEDvKIvLXQpnT0VVsttH69oE_RdDA":
            raise ValueError("请先在 config.py 中填写你的 BOT_TOKEN")
