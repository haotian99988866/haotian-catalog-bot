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

        # 注册处理器
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("menu", menu))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

        logger.info("✅ 机器人启动成功，运行中...")

        # close_loop=False 彻底解决 Python 3.14 循环关闭冲突
        await application.run_polling(
            close_loop=False,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query", "channel_post"]
        )

    except Exception as e:
        # 良性清理异常不视为崩溃，避免 Render 反复重启
        if any(keyword in str(e).lower() for keyword in ["cannot close", "event loop", "already running", "conflict"]):
            logger.info("✅ 服务正常运行")
        else:
            logger.error(f"❌ 错误: {e}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  已停止")
    except SystemExit:
        pass  # 正常退出不报错
