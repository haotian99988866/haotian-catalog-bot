from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import (
    init_db,
    add_episode,
    update_message_id_if_exists,
    get_all_works,
    get_episodes_of_work,
    search_works_by_keyword
)
from parsers import parse_message_text
from config import Config


# 初始化数据库
init_db()


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


# 生成跳转链接
def build_jump_url(message_id: int) -> str:
    base = Config.CHANNEL_LINK.rstrip("/")
    return f"{base}/{message_id}"


# 作品列表入口 — 显示总集数
def works_list_keyboard(works, page=1, per_page=8):
    total = len(works)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    page_works = works[start:end]

    keyboard = []
    for idx, work in enumerate(page_works, start + 1):
        keyboard.append([
            InlineKeyboardButton(
                f"📺 {work['work_name']} ({work['total_episodes']}集)",
                callback_data=f"show_eps:{work['work_name']}"
            )
        ])

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"list_page:{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"list_page:{page+1}"))
    if nav_row:
        keyboard.append(nav_row)

    return InlineKeyboardMarkup(keyboard) if keyboard else None


# 集数列表 — 点哪集跳哪集
def episodes_keyboard(work_data, from_page=1):
    eps = work_data["episodes"]
    
    # 智能排序：数字优先
    def ep_sort_key(e):
        import re
        nums = re.findall(r"\d+", e["episode"])
        return int(nums[0]) if nums else 99999
    
    eps.sort(key=ep_sort_key)

    keyboard = []
    for ep in eps:
        url = build_jump_url(ep["message_id"])
        keyboard.append([
            InlineKeyboardButton(f"▶ {ep['episode']}", url=url)
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ 返回作品列表", callback_data=f"back_to_list:{from_page}")
    ])
    return InlineKeyboardMarkup(keyboard)


async def send_menu_kb(update: Update, text: str):
    await update.message.reply_text(
        text,
        reply_markup=main_keyboard,
        parse_mode="HTML"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🎬 <b>昊天影院目录</b>

欢迎使用👇

• 🎬 全部影片 — 按作品浏览，显示总集数
• 🔎 搜索 — 查找作品，展开选择集数
• 🏷️ 按标签 — 按分类筛选
• ❓ 帮助 — 使用说明

直接发片名也能搜索哦！"""
    await send_menu_kb(update, text)


async def list_all_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    works = get_all_works()
    if not works:
        await send_menu_kb(update, "📭 暂无收录，频道发消息开始收录吧！")
        return

    text = f"📋 <b>全部收录（共 {len(works)} 部作品）</b>\n点作品展开集数👇"
    await update.message.reply_text(
        text,
        reply_markup=works_list_keyboard(works),
        parse_mode="HTML"
    )


async def search_work(update: Update, context: ContextTypes.DEFAULT_TYPE, keyword=None):
    if not keyword:
        await send_menu_kb(update, "🔎 请直接发片名关键词给我！")
        return

    works = search_works_by_keyword(keyword)
    if not works:
        text = f"🔎 搜索：<b>{keyword}</b>\n\n没有找到相关作品"
        await send_menu_kb(update, text)
        return

    text = f"🔎 搜索：<b>{keyword}</b>（找到 {len(works)} 部）\n点作品展开集数👇"
    await update.message.reply_text(
        text,
        reply_markup=works_list_keyboard(works),
        parse_mode="HTML"
    )


async def tags_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_menu_kb(update, "🏷️ 标签功能开发中，敬请期待！")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《作品名》第X集 #标签1 #标签2

<b>浏览方式：</b>
• 点作品 → 展开全部集数
• 点对应集数 → 直接跳转播放
• 手机/电脑端都正常打开

<b>频道链接：</b>
{link}""".format(link=Config.CHANNEL_LINK)
    await send_menu_kb(update, text)


# 频道监听收录
async def channel_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg or str(msg.chat.id) != Config.CHANNEL_ID_EXPECTED:
        return

    parsed = parse_message_text(msg.text or msg.caption or "")
    if not parsed:
        return

    work_name = parsed["work_name"]
    episode = parsed["episode"]
    msg_id = msg.message_id

    if update_message_id_if_exists(work_name, episode, msg_id):
        print(f"🔄 更新链接：{work_name} - {episode}")
        return

    add_episode(work_name, episode, parsed.get("tags", []), msg_id)
    print(f"✅ 已收录：{work_name} - {episode}")


# 底部按钮 + 文本搜索
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🎬 全部影片":
        await list_all_works(update, context)
        return
    if text == "🔎 搜索":
        await search_work(update, context)
        return
    if text == "🏷️ 按标签":
        await tags_cmd(update, context)
        return
    if text == "❓ 帮助":
        await help_cmd(update, context)
        return

    await search_work(update, context, keyword=text)


# 内联按钮处理
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        return

    data = query.data

    # 展开集数列表
    if data.startswith("show_eps:"):
        work_name = data.split(":", 1)[1]
        work = get_episodes_of_work(work_name)
        if not work:
            await query.answer("该作品不存在", show_alert=True)
            return

        text = f"📺 <b>{work_name}</b> — 共 {work['total_episodes']} 集\n点集数直接跳转👇"
        await query.edit_message_text(
            text,
            reply_markup=episodes_keyboard(work),
            parse_mode="HTML"
        )
        return

    # 翻页 — 作品列表
    if data.startswith("list_page:"):
        page = int(data.split(":")[1])
        works = get_all_works()
        text = f"📋 <b>全部收录</b>\n点作品展开集数👇"
        await query.edit_message_text(
            text,
            reply_markup=works_list_keyboard(works, page),
            parse_mode="HTML"
        )
        return

    # 返回作品列表
    if data.startswith("back_to_list:"):
        page = int(data.split(":")[1])
        works = get_all_works()
        text = f"📋 <b>全部收录</b>\n点作品展开集数👇"
        await query.edit_message_text(
            text,
            reply_markup=works_list_keyboard(works, page),
            parse_mode="HTML"
        )
        return
