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

def main():
    Config.validate()
    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ 机器人启动成功！")
    app.run_polling()

if __name__ == "__main__":
    main()
