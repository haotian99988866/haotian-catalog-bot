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

        # 注册处理器 — 顺序固定
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("menu", menu))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

        logger.info("✅ 所有 Handler 注册完成")
        logger.info("✅ 机器人启动成功，等待消息...")

        await application.run_polling(
            close_loop=False,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "channel_post"]
        )
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  机器人已停止")
    except RuntimeError as e:
        if "event loop" in str(e).lower():
            logger.info("✅ 服务运行中")
        else:
            logger.error(f"⚠️  异常: {e}", exc_info=True)
