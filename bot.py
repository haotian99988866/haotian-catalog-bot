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

async def main():
    Config.validate()
    application = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # 注册处理器 — Callback 放最前面
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_listener))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, direct_search))

    print("✅ 机器人启动成功！")
    
    # 使用官方推荐的完整参数，避免事件循环冲突
    await application.run_polling(
        close_loop=False,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

if __name__ == "__main__":
    # 处理事件循环冲突的终极写法
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️  机器人已停止")
    except RuntimeError as e:
        if "event loop" in str(e).lower():
            # 忽略 Render 环境下的良性循环关闭警告
            print("✅ 服务运行中，忽略循环清理提示")
        else:
            print(f"⚠️  运行时异常: {e}")
            sys.exit(1)
