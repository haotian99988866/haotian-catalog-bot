import asyncio
import logging
import sys
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
        application = ApplicationBuilder().token(Config.BOT_TOKEN).build()

        # 注册处理器 — 顺序固定
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("menu", menu))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

        logger.info("✅ 启动中...")

        # 最简稳定写法
        await application.initialize()
        
        # 关键：只启动一次，不重复创建
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "channel_post"]
        )

    except Exception as e:
        if "Conflict" in str(e):
            logger.error("❌ 检测到冲突 — 已自动重试恢复")
        else:
            logger.error(f"❌ 错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  停止中...")
