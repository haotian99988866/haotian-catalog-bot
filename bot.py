import asyncio
import logging
import sys
from telegram import Update
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
logger = logging.getLogger(__name__)

async def main():
    try:
        Config.validate()
        logger.info("✅ Token 验证通过")

        application = ApplicationBuilder().token(Config.BOT_TOKEN).build()

        # 注册处理器 — 顺序不能乱
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("menu", menu))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

        logger.info("✅ Handler 注册完成，开始接收消息...")

        # 官方推荐写法，消除警告+稳定接收
        await application.initialize()
        await application.start()
        
        await application.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "channel_post"]
        )

        logger.info("✅ 机器人在线！发 /start 试试吧")
        
        # 保持运行
        await asyncio.Event().wait()

    except Exception as e:
        logger.error(f"❌ 错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  停止中...")
