class Config:
    BOT_TOKEN = "8929187714:AAFUOLvEDvKIvLXQpnT0VVsttH69oE_RdDA"
    
    CHANNEL_ID = -1003920194464
    CHANNEL_ID_EXPECTED = "-1003920194464"
    
    CHANNEL_LINK = "https://t.me/haotianyingyuan"

    @classmethod
    def validate(cls):
        assert cls.BOT_TOKEN and cls.BOT_TOKEN != "换成你的真实TOKEN", "❌ 请先填BOT_TOKEN"
        assert cls.CHANNEL_LINK, "❌ 请填CHANNEL_LINK"
        assert cls.CHANNEL_ID_EXPECTED, "❌ 请填CHANNEL_ID_EXPECTED"
