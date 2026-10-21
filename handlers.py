from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import get_episodes_of_work, get_all_works

# ========== 内联键盘函数 ==========
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
        cb_data = f"play:{work.get('work_name', '')}:{ep}" if ep in uploaded else "noop"
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
            w.get("work_name", "未知"),
            callback_data=f"show_eps:{w.get('work_name', '')}"
        )])
    if not buttons:
        buttons.append([InlineKeyboardButton("暂无数据", callback_data="noop")])
    return InlineKeyboardMarkup(buttons)

# ========== 底部主键盘 ==========
main_reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🎬 全部影片"), KeyboardButton("🔎 搜索")],
        [KeyboardButton("🏷️ 按标签"), KeyboardButton("❓ 帮助")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="输入片名搜索，或点下方按钮"
)

# ========== 消息处理函数 ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🎬 <b>昊天影院目录</b>

欢迎使用👇

• 🎬 全部影片 — 按作品浏览
• 🔎 搜索 — 查找作品
• 🏷️ 按标签 — 按分类筛选
• ❓ 帮助 — 使用说明

直接发片名也能搜索哦！"""
    await update.message.reply_text(text, reply_markup=main_reply_kb, parse_mode="HTML")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def direct_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text.strip()
    if t == "🎬 全部影片":
        works = get_all_works()
        if not works:
            await update.message.reply_text("📭 暂无收录，频道发消息开始收录吧！\n格式：《片名》第X集 #标签")
            return
        await update.message.reply_text(
            f"📋 <b>全部收录（共 {len(works)} 部作品）</b>\n点作品展开集数👇",
            reply_markup=works_list_kb(works),
            parse_mode="HTML"
        )
    elif t == "🔎 搜索":
        await update.message.reply_text("🔍 请直接发片名关键词给我！")
    elif t == "🏷️ 按标签":
        await update.message.reply_text("🏷️ 标签功能开发中，敬请期待！")
    elif t == "❓ 帮助":
        text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《作品名》第X集 #标签1 #标签2
综艺：《综艺名》第X期 #综艺

<b>说明：</b>
▶ 已上传可播放
░ 暂未上传
"""
        await update.message.reply_text(text, parse_mode="HTML")
    else:
        works = get_all_works()
        filtered = [w for w in works if t in w.get("work_name", "")]
        if not filtered:
            await update.message.reply_text(f"🔎 搜索：<b>{t}</b>\n没有找到相关作品", parse_mode="HTML")
            return
        await update.message.reply_text(
            f"🔎 搜索：<b>{t}</b>（找到 {len(filtered)} 部）\n点作品展开集数👇",
            reply_markup=works_list_kb(filtered),
            parse_mode="HTML"
        )

async def channel_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 频道消息监听 — 填入你的原有逻辑
    pass

# ========== 按钮回调处理 ==========
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
            f"📺 <b>{w.get('work_name', wn)}</b> — 共 {w.get('total_episodes', 0)} 集 / 已上传 {w.get('actual_uploaded', 0)} 集\n\n▶=可播放  ░=暂未上传",
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
