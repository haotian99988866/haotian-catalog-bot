BOT_TOKEN = "在这里填入你的Bot Token"

class Config:
    BOT_TOKEN = BOT_TOKEN

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "在这里填入你的Bot Token":
            raise ValueError("请先在 config.py 中填写你的 BOT_TOKEN")
