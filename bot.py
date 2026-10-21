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
    Config.validate()
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # 注册处理器 — 顺序固定
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

    logger.info("✅ 机器人启动成功！")

    # 关键：close_loop=False 禁止内部关闭循环，彻底消除冲突
    await application.run_polling(
        close_loop=False,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query", "channel_post"]
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  停止中...")
    except RuntimeError as e:
        # 只忽略"循环运行中"这类良性清理提示，其他异常仍报错
        if "event loop" in str(e).lower() or "Cannot close" in str(e):
            logger.info("✅ 服务正常运行中")
        else:
            logger.error(f"❌ 异常: {e}", exc_info=True)
            sys.exit(1)
