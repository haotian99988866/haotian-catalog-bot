from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import (
    get_all_shows, search_shows, get_shows_by_tag,
    add_show, show_exists
)
from parsers import parse_message_text
from config import Config


# 生成主菜单按钮
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📺 全部影片", callback_data="list_all"),
            InlineKeyboardButton("🔍 搜索", callback_data="search")
        ],
        [
            InlineKeyboardButton("🏷️ 按标签浏览", callback_data="tags"),
            InlineKeyboardButton("ℹ️ 使用帮助", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# 生成影片列表按钮（分页）
def shows_keyboard(shows, page=1, per_page=10):
    total = len(shows)
    total_pages = (total + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    page_shows = shows[start:end]
    
    keyboard = []
    for idx, show in enumerate(page_shows, start + 1):
        keyboard.append([
            InlineKeyboardButton(
                f"{idx}. {show['title']}",
                callback_data=f"show_detail:{show['id']}"
            )
        ])
    
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"page:{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"page:{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard) if keyboard else None


# 主菜单
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🎬 <b>昊天影院目录</b>

欢迎使用！请选择功能：

• 全部影片 — 查看所有收录内容
• 搜索 — 按片名查找
• 按标签浏览 — 按分类筛选
• 使用帮助 — 查看说明

也可以直接发片名搜索哦！"""
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


# 开始
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)


# 帮助
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《影片名》日期 #标签1 #标签2

<b>搜索方式：</b>
• 直接发片名关键词
• 点「搜索」按钮输入
• 点「按标签浏览」筛选

<b>频道链接：</b>
{link}""".format(link=Config.CHANNEL_LINK)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


# 列出全部
async def list_shows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shows = get_all_shows()
    if not shows:
        text = "📭 暂无收录内容，频道发一条消息开始收录吧！"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
        ]])
        await update.message.reply_text(text, reply_markup=keyboard)
        return
    
    text = f"📋 <b>全部收录（共 {len(shows)} 部）</b>"
    await update.message.reply_text(text, reply_markup=shows_keyboard(shows), parse_mode="HTML")


# 搜索命令
async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔍 直接告诉我片名", callback_data="search_prompt")
    ]])
    await update.message.reply_text(
        "🔍 请告诉我要搜索的片名关键词：",
        reply_markup=keyboard
    )


# 直接搜索（私聊发关键词）
async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.strip()
    shows = search_shows(keyword)
    
    if not shows:
        text = f"🔍 搜索：<b>{keyword}</b>\n\n没有找到相关影片"
    else:
        text = f"🔍 搜索：<b>{keyword}</b>（找到 {len(shows)} 部）"
    
    keyboard = shows_keyboard(shows) if shows else InlineKeyboardMarkup([[
        InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
    ]])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


# 频道消息监听
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


# 按钮回调处理
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "main_menu":
        text = """🎬 <b>昊天影院目录</b>

欢迎使用！请选择功能：

• 全部影片 — 查看所有收录内容
• 搜索 — 按片名查找
• 按标签浏览 — 按分类筛选
• 使用帮助 — 查看说明

也可以直接发片名搜索哦！"""
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")
    
    elif data == "list_all":
        shows = get_all_shows()
        if not shows:
            text = "📭 暂无收录内容，频道发一条消息开始收录吧！"
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
            ]])
        else:
            text = f"📋 <b>全部收录（共 {len(shows)} 部）</b>"
            keyboard = shows_keyboard(shows)
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
    
    elif data == "search":
        await query.edit_message_text(
            "🔍 请直接发片名关键词给我，我帮你找！",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
            ]])
        )
    
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
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
        ]])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
    
    elif data == "help":
        text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《影片名》日期 #标签1 #标签2

<b>搜索方式：</b>
• 直接发片名关键词
• 点「搜索」按钮输入
• 点「按标签浏览」筛选

<b>频道链接：</b>
{link}""".format(link=Config.CHANNEL_LINK)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 返回主菜单", callback_data="main_menu")
        ]])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
    
    elif data.startswith("page:"):
        page = int(data.split(":")[1])
        shows = get_all_shows()
        keyboard = shows_keyboard(shows, page)
        await query.edit_message_reply_markup(reply_markup=keyboard)
