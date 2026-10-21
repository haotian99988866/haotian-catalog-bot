import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1003920194464"))
    CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/c/3920194464")
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("请在 .env 文件中设置 BOT_TOKEN")
        if not cls.CHANNEL_LINK:
            raise ValueError("请在 .env 文件中设置 CHANNEL_LINK")