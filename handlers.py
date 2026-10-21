from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, filters
from telegram.ext.filters import UpdateType  # 新版过滤器

from database import get_all_shows, get_episodes, search_videos, save_video
from parsers import parse_message_text, extract_tags
from config import Config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🎬 昊天影院 · 检索机器人

/menu — 完整目录
/search 剧名 — 搜索
/list — 全部剧名
/help — 使用帮助
直接发剧名也可以搜索！
    """)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
📖 使用说明：
• /menu 浏览全部剧集
• /search 爱情公寓 搜索
• 点击集数 → 直接跳转频道观看
• 新视频发布自动收录
    """)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_all_shows()
    if not shows:
        await update.message.reply_text("📂 暂无收录内容")
        return
    kb = []
    for name, cnt in shows:
        if name:
            kb.append([InlineKeyboardButton(f"📺 {name} ({cnt}集)", callback_data=f"show:{name}")])
    await update.message.reply_text("📋 请选择：", reply_markup=InlineKeyboardMarkup(kb))


async def list_shows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_all_shows()
    text = "📂 全部剧名：\n\n"
    for i, (name, cnt) in enumerate(shows, 1):
        text += f"{i}. {name} — {cnt}集\n"
    await update.message.reply_text(text)


async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法：/search 爱情公寓")
        return
    keyword = " ".join(context.args)
    await show_search_results(update, keyword)


async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.startswith("/"):
        await show_search_results(update, text)


async def show_search_results(update: Update, keyword: str):
    results = search_videos(keyword)
    if not results:
        await update.message.reply_text(f"🔍 未找到「{keyword}」相关内容")
        return

    from collections import defaultdict
    grouped = defaultdict(list)
    for r in results:
        grouped[r[2]].append(r)

    kb = []
    for name in grouped:
        kb.append([InlineKeyboardButton(
            f"📺 {name} ({len(grouped[name])}集)",
            callback_data=f"show:{name}"
        )])
    await update.message.reply_text(
        f"🔍 搜索「{keyword}」找到 {len(results)} 条结果：",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("show:"):
        show_name = data.replace("show:", "")
        episodes = get_episodes(show_name)

        kb, row = [], []
        for ep in episodes:
            msg_id = ep[0]
            ep_label = f"第{ep[3]}集" if ep[3] else f"集{msg_id}"
            row.append(InlineKeyboardButton(ep_label, url=f"{Config.CHANNEL_LINK}/{msg_id}"))
            if len(row) == 4:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        kb.append([InlineKeyboardButton("◀ 返回", callback_data="back")])

        await query.edit_message_text(
            f"📺 {show_name}（共{len(episodes)}集）\n点击集数直接跳转观看",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data == "back":
        shows = get_all_shows()
        kb = []
        for name, cnt in shows:
            if name:
                kb.append([InlineKeyboardButton(f"📺 {name} ({cnt}集)", callback_data=f"show:{name}")])
        await query.edit_message_text("📋 请选择：", reply_markup=InlineKeyboardMarkup(kb))


async def channel_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """监听频道新消息并自动收录"""
    if update.channel_post and update.channel_post.chat.id == Config.CHANNEL_ID:
        msg = update.channel_post
        text = msg.text or msg.caption or ""
        parsed = parse_message_text(text)
        tags = extract_tags(text)

        if parsed["show_name"]:
            save_video(
                msg_id=msg.message_id,
                title=parsed["title"] or "",
                show_name=parsed["show_name"],
                season=parsed["season"],
                episode=parsed["episode"],
                tags=tags
            )
            print(f"✅ 自动收录: {parsed['show_name']} 第{parsed['episode']}集")