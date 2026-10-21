BOT_TOKEN = "8929187714:AAFUOLvEDvKIvLXQpnT0VVsttH69oE_RdDA"

class Config:
    BOT_TOKEN = BOT_TOKEN

    @classmethod
    def validate(cls):
        # 只检查是否为空，不再硬编码对比
        if not cls.BOT_TOKEN or len(cls.BOT_TOKEN) < 30:
            raise ValueError("请先在 config.py 中填写正确的 BOT_TOKEN")
