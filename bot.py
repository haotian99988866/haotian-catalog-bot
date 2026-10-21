import asyncio
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from telegram.ext.filters import UpdateType
from config import Config
from database import init_db
from handlers import (
    start, help_cmd, menu, list_shows,
    search_cmd, direct_search, button_handler, channel_listener
)


async def main():
    Config.validate()
    init_db()
    
    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("list", list_shows))
    app.add_handler(CommandHandler("help", help_cmd))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(UpdateType.CHANNEL_POST, channel_listener))
    app.add_handler(MessageHandler(UpdateType.MESSAGE & ~filters.COMMAND, direct_search))
    
    print("=" * 50)
    print("✅ 昊天影院目录机器人已启动！")
    print(f"📺 监听频道ID: {Config.CHANNEL_ID}")
    print(f"🔗 频道链接: {Config.CHANNEL_LINK}")
    print("=" * 50)
    
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
