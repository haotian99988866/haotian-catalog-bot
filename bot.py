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
    
    # 频道新消息监听
    app.add_handler(MessageHandler(UpdateType.CHANNEL_POST, channel_listener))
    
    # 私聊直接搜索
    app.add_handler(MessageHandler(UpdateType.MESSAGE & ~filters.COMMAND, direct_search))
    
    print("=" * 50)
    print("✅ 昊天影院目录机器人已启动！")
    print(f"📺 监听频道ID: {Config.CHANNEL_ID}")
    print(f"🔗 频道链接: {Config.CHANNEL_LINK}")
    print("=" * 50)
    
    # ⚠️ 关键：直接调用，不包 asyncio.run()
    app.run_polling()


if __name__ == "__main__":
    # 干净的入口，不额外包装
    main()
