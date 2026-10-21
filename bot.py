from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from telegram.ext.filters import UpdateType  # 新版过滤器

from config import Config
from database import init_db
from handlers import (
    start, help_cmd, menu, list_shows,
    search_cmd, direct_search, button_handler, channel_listener
)

def main():
    # 初始化配置与数据库
    Config.validate()
    init_db()
    
    # 创建应用
    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()
    
    # 注册命令处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("list", list_shows))
    app.add_handler(CommandHandler("help", help_cmd))
    
    # 按钮回调
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # ✅ 新版写法：频道新消息监听
    app.add_handler(MessageHandler(UpdateType.CHANNEL_POST, channel_listener))
    
    # ✅ 新版写法：私聊直接搜索
    app.add_handler(MessageHandler(UpdateType.MESSAGE & ~filters.COMMAND, direct_search))
    
    print("=" * 50)
    print("✅ 昊天影院目录机器人已启动！")
    print(f"📺 监听频道ID: {Config.CHANNEL_ID}")
    print(f"🔗 频道链接: {Config.CHANNEL_LINK}")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⚠️  机器人已停止")
