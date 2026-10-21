from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import (
    get_all_shows,
    search_shows,
    get_shows_by_tags,
    add_show,
    show_exists
)
from parsers import parse_message_text
from config import Config


# ===== 底部固定键盘 =====
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("📺 全部影片"),
            KeyboardButton("🔍 搜索")
        ],
        [
            KeyboardButton("🏷️ 按标签"),
            KeyboardButton("ℹ️ 帮助")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


# 影片列表 —— 直接跳转，无详情页，去掉返回主菜单
def shows_keyboard(shows, page=1, per_page=10):
    total = len(shows)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    page_shows = shows[start:end]

    keyboard = []
    for idx, show in enumerate(page_shows, start + 1):
        if show.get("message_id"):
            jump_url = f"{Config.CHANNEL_LINK}?single&msg={show['message_id']}"
            keyboard.append([
                InlineKeyboardButton(f"{idx}. {show['title']}", url=jump_url)
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(f"{idx}. {show['title']} (暂无链接)", callback_data="no_link")
            ])

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"page:{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"page:{page+1}"))
    if nav_row:
        keyboard.append(nav_row)

    # ✅ 去掉了「返回主菜单」按钮
    return InlineKeyboardMarkup(keyboard) if keyboard else None


# 主菜单
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🎬 <b>昊天影院目录</b>

欢迎使用！片名直接跳转观看👇

• 📺 全部影片 — 查看所有收录内容
• 🔍 搜索 — 按片名查找
• 🏷️ 按标签 — 按分类筛选
• ℹ️ 帮助 — 查看说明

也可以直接发片名搜索哦！"""
    await update.message.reply_text(
        text,
        reply_markup=main_keyboard,
        parse_mode="HTML"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《影片名》日期 #标签1 #标签2

<b>使用方式：</b>
• 直接发片名关键词搜索
• 片名直接点就跳转观看

<b>频道链接：</b>
{link}""".format(link=Config.CHANNEL_LINK)
    await update.message.reply_text(text, parse_mode="HTML")


async def list_shows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_all_shows()
    if not shows:
        text = "📭 暂无收录内容，频道发一条消息开始收录吧！"
        await update.message.reply_text(text)
        return

    text = f"📋 <b>全部收录（共 {len(shows)} 部）</b>\n片名直接点👇"
    await update.message.reply_text(
        text,
        reply_markup=shows_keyboard(shows),
        parse_mode="HTML"
    )


async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 请直接发片名关键词给我，我帮你找！")


async def tags_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_all_shows()
    all_tags = {}
    for show in shows:
        for tag in show.get("tags", []):
            all_tags[tag] = all_tags.get(tag, 0) + 1

    if not all_tags:
        text = "🏷️ 暂无标签内容"
    else:
        text = "🏷️ <b>按标签筛选</b>\n\n"
        for tag, count in sorted(all_tags.items()):
            text += f"#{tag}  ({count}部)\n"

    await update.message.reply_text(text, parse_mode="HTML")


# 优先响应底部按钮
async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text.strip()

    if text_input == "📺 全部影片":
        await list_shows(update, context)
        return
    if text_input == "🔍 搜索":
        await search_cmd(update, context)
        return
    if text_input == "🏷️ 按标签":
        await tags_cmd(update, context)
        return
    if text_input == "ℹ️ 帮助":
        await help_cmd(update, context)
        return

    shows = search_shows(text_input)
    if not shows:
        reply_text = f"🔍 搜索：<b>{text_input}</b>\n\n没有找到相关影片"
        keyboard = None
    else:
        reply_text = f"🔍 搜索：<b>{text_input}</b>（找到 {len(shows)} 部）\n片名直接点👇"
        keyboard = shows_keyboard(shows)

    await update.message.reply_text(
        reply_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def channel_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg or msg.chat.id != Config.CHANNEL_ID:
        return

    parsed = parse_message_text(msg.text or msg.caption or "")
    if not parsed:
        return

    if show_exists(parsed["title"]):
        return

    add_show(parsed["title"], parsed.get("tags", []), msg.message_id)
    print(f"✅ 已收录：{parsed['title']}")


# 内联按钮处理 —— 彻底移除 show_detail，不再出现详情页
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        text = """🎬 <b>昊天影院目录</b>

请选择功能："""
        await query.edit_message_text(text, parse_mode="HTML")

    elif data == "list_all":
        shows = get_all_shows()
        if not shows:
            text = "📭 暂无收录内容，频道发一条消息开始收录吧！"
            keyboard = None
        else:
            text = f"📋 <b>全部收录（共 {len(shows)} 部）</b>\n片名直接点👇"
            keyboard = shows_keyboard(shows)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

    elif data == "no_link":
        await query.answer(text="暂无链接，重新收录此内容即可", show_alert=True)

    elif data == "search":
        await query.edit_message_text("🔍 请直接发片名关键词给我，我帮你找！", parse_mode="HTML")

    elif data == "tags":
        shows = get_all_shows()
        all_tags = {}
        for show in shows:
            for tag in show.get("tags", []):
                all_tags[tag] = all_tags.get(tag, 0) + 1

        if not all_tags:
            text = "🏷️ 暂无标签内容"
        else:
            text = "🏷️ <b>按标签筛选</b>\n\n"
            for tag, count in sorted(all_tags.items()):
                text += f"#{tag}  ({count}部)\n"
        await query.edit_message_text(text, parse_mode="HTML")

    elif data == "help":
        text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《影片名》日期 #标签1 #标签2"""
        await query.edit_message_text(text, parse_mode="HTML")

    elif data.startswith("page:"):
        page = int(data.split(":")[1])
        shows = get_all_shows()
        keyboard = shows_keyboard(shows, page)
        await query.edit_message_reply_markup(reply_markup=keyboard)
