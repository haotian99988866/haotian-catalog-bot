from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ApplicationHandler
from database import get_episodes_of_work, get_all_works

# ========== 键盘函数 ==========
def main_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📂 全部影片", callback_data="all_movies"),
            InlineKeyboardButton("🔍 搜索", callback_data="search")
        ],
        [
            InlineKeyboardButton("🏷️ 按标签", callback_data="by_tag"),
            InlineKeyboardButton("❓ 帮助", callback_data="help")
        ]
    ])

def episodes_kb(work):
    total = work.get("total_episodes", 0)
    uploaded = work.get("uploaded_list", [])
    buttons = []
    row = []
    for ep in range(1, total + 1):
        text = f"{ep}" if ep in uploaded else f"{ep} ░"
        cb_data = f"play:{work['name']}:{ep}" if ep in uploaded else "noop"
        row.append(InlineKeyboardButton(text, callback_data=cb_data))
        if len(row) >= 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("◀ 返回", callback_data="list_page:1")])
    return InlineKeyboardMarkup(buttons)

def works_list_kb(works, page=1):
    buttons = []
    for w in works:
        buttons.append([InlineKeyboardButton(
            w.get("name", "未知"),
            callback_data=f"show_eps:{w.get('name', '')}"
        )])
    if not buttons:
        buttons.append([InlineKeyboardButton("暂无数据", callback_data="noop")])
    return InlineKeyboardMarkup(buttons)

# ========== 按钮主处理函数 ==========
async def button_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    try:
        await q.answer()
    except Exception:
        return

    d = q.data

    if d == "noop":
        await q.answer("该集/期暂未上传", show_alert=True)
        return

    if d.startswith("show_eps:"):
        wn = d.split(":", 1)[1]
        w = get_episodes_of_work(wn)
        if not w:
            await q.answer("该作品不存在", show_alert=True)
            return
        await q.edit_message_text(
            f"📺 <b>{w['name']}</b> — 共 {w['total_episodes']} 集 / 已上传 {w['actual_uploaded']} 集\n\n▶=可播放  ░=暂未上传",
            reply_markup=episodes_kb(w),
            parse_mode="HTML"
        )

    elif d.startswith("list_page:"):
        page = int(d.split(":", 1)[1])
        works = get_all_works()
        await q.edit_message_text(
            f"📋 <b>全部收录</b>\n共 {len(works)} 部作品",
            reply_markup=works_list_kb(works, page),
            parse_mode="HTML"
        )

    elif d.startswith("back_to_list:"):
        page = int(d.split(":", 1)[1])
        works = get_all_works()
        await q.edit_message_text(
            f"📋 <b>全部收录</b>\n共 {len(works)} 部作品",
            reply_markup=works_list_kb(works, page),
            parse_mode="HTML"
        )

    elif d == "all_movies":
        works = get_all_works()
        if not works:
            text = "📂 <b>全部影片</b>\n暂无收录，频道发消息开始收录吧！"
        else:
            text = f"📂 <b>全部影片</b>\n共 {len(works)} 部作品"
        await q.edit_message_text(
            text,
            reply_markup=works_list_kb(works, 1),
            parse_mode="HTML"
        )

    elif d == "search":
        await q.edit_message_text(
            "🔍 请输入片名搜索：",
            reply_markup=main_kb(),
            parse_mode="HTML"
        )

    elif d == "by_tag":
        await q.edit_message_text(
            "🏷️ 请选择标签：",
            reply_markup=main_kb(),
            parse_mode="HTML"
        )

    elif d == "help":
        help_text = """📖 使用说明：
格式：《片名》第X集 #标签
综艺：《综艺名》第X期 #标签
"""
        await q.edit_message_text(
            help_text,
            reply_markup=main_kb(),
            parse_mode="HTML"
        )
