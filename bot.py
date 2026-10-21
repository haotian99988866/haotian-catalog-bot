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

    # 注册顺序固定
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

    print("✅ 机器人启动成功！")
    await application.run_polling(
        close_loop=False,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️  机器人已停止")
    except RuntimeError as e:
        if "event loop" in str(e).lower():
            print("✅ 服务运行中")
        else:
            print(f"⚠️  异常: {e}")
