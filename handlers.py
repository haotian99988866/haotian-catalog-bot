from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import (
    get_all_shows,
    search_shows,
    get_shows_by_tags,
    add_show,
    show_exists,
    update_message_id
)
from parsers import parse_message_text
from config import Config


# ===== 底部固定键盘 =====
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("🎬 全部影片"),
            KeyboardButton("🔎 搜索")
        ],
        [
            KeyboardButton("🏷️ 按标签"),
            KeyboardButton("❓ 帮助")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="输入片名搜索，或点下方按钮"
)


# ✅ 修复：手机端兼容的跳转链接
def build_jump_url(message_id: int) -> str:
    # 格式：https://t.me/c/频道ID/消息ID （全平台兼容）
    base = Config.CHANNEL_LINK
    if base.endswith("/"):
        return f"{base}{message_id}"
    return f"{base}/{message_id}"


# 影片列表
def shows_keyboard(shows, page=1, per_page=10):
    total = len(shows)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    page_shows = shows[start:end]

    keyboard = []
    for idx, show in enumerate(page_shows, start + 1):
        if show.get("message_id"):
            jump_url = build_jump_url(show["message_id"])
            keyboard.append([
                InlineKeyboardButton(f"▶ {idx}. {show['title']}", url=jump_url)
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(f"📂 {idx}. {show['title']}", callback_data="no_link")
            ])

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"page:{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"page:{page+1}"))
    if nav_row:
        keyboard.append(nav_row)

    return InlineKeyboardMarkup(keyboard) if keyboard else None


# ✅ 每次交互都重发键盘，清除聊天后自动恢复
async def send_menu_with_kb(update: Update, text: str):
    await update.message.reply_text(
        text,
        reply_markup=main_keyboard,
        parse_mode="HTML"
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🎬 <b>昊天影院目录</b>

欢迎使用！片名直接点跳转观看👇

• 🎬 全部影片 — 查看所有收录
• 🔎 搜索 — 按片名查找
• 🏷️ 按标签 — 按分类筛选
• ❓ 帮助 — 使用说明

也可以直接发片名搜索哦！"""
    await send_menu_with_kb(update, text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《片名》日期 #标签1 #标签2

<b>链接说明：</b>
• 片名直接点 → 全平台（手机/电脑）直接跳转
• 暂无链接 → 频道重发该内容自动补全

<b>频道链接：</b>
{link}""".format(link=Config.CHANNEL_LINK)
    await send_menu_with_kb(update, text)


async def list_shows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_all_shows()
    if not shows:
        await send_menu_with_kb(update, "📭 暂无收录，频道发消息开始收录吧！")
        return

    text = f"📋 <b>全部收录（共 {len(shows)} 部）</b>\n片名直接点跳转观看👇"
    await update.message.reply_text(
        text,
        reply_markup=shows_keyboard(shows),
        parse_mode="HTML"
    )


async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_menu_with_kb(update, "🔎 请直接发片名关键词给我！")


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

    await send_menu_with_kb(update, text)


# 底部按钮 + 搜索
async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text.strip()

    if text_input == "🎬 全部影片":
        await list_shows(update, context)
        return
    if text_input == "🔎 搜索":
        await search_cmd(update, context)
        return
    if text_input == "🏷️ 按标签":
        await tags_cmd(update, context)
        return
    if text_input == "❓ 帮助":
        await help_cmd(update, context)
        return

    shows = search_shows(text_input)
    if not shows:
        text = f"🔎 搜索：<b>{text_input}</b>\n\n没有找到相关影片"
        await send_menu_with_kb(update, text)
    else:
        text = f"🔎 搜索：<b>{text_input}</b>（找到 {len(shows)} 部）\n片名直接点跳转👇"
        await update.message.reply_text(
            text,
            reply_markup=shows_keyboard(shows),
            parse_mode="HTML"
        )


async def channel_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg or msg.chat.id != Config.CHANNEL_ID:
        return

    parsed = parse_message_text(msg.text or msg.caption or "")
    if not parsed:
        return

    title = parsed["title"]
    if show_exists(title):
        update_message_id(title, msg.message_id)
        print(f"🔄 补全链接：{title}")
        return

    add_show(title, parsed.get("tags", []), msg.message_id)
    print(f"✅ 已收录：{title}")


# 内联按钮处理
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        return

    data = query.data

    if data == "no_link":
        await query.answer(
            text="暂无链接 → 频道重发该内容即可补全 ✅",
            show_alert=True
        )
        return

    if data == "list_all":
        shows = get_all_shows()
        if not shows:
            text = "📭 暂无收录内容"
            keyboard = None
        else:
            text = f"📋 <b>全部收录（共 {len(shows)} 部）</b>\n片名直接点跳转👇"
            keyboard = shows_keyboard(shows)
        try:
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception:
            pass
        return

    if data.startswith("page:"):
        page = int(data.split(":")[1])
        shows = get_all_shows()
        keyboard = shows_keyboard(shows, page)
        try:
            await query.edit_message_reply_markup(reply_markup=keyboard)
        except Exception:
            pass
        return
