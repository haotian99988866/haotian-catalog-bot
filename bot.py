import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from config import Config
from handlers import start, menu, direct_search, button_handler, channel_listener

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def main():
    Config.validate()
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # 注册处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("✅ 机器人启动成功！")
    
    # 标准写法，兼容所有 Python 版本
    await application.run_polling(close_loop=False)

if __name__ == "__main__":
    asyncio.run(main())
