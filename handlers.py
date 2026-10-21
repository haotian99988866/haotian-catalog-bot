from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import get_episodes_of_work, get_all_works, add_or_update_work
import logging
import re

logger = logging.getLogger(__name__)

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
    if not isinstance(uploaded, list):
        uploaded = []
    buttons = []
    row = []
    for ep in range(1, total + 1):
        if ep in uploaded:
            text = f"{ep}"
            cb_data = f"play:{work.get('work_name', '')}:{ep}"
        else:
            text = f"{ep}"
            cb_data = "noop"
        row.append(InlineKeyboardButton(text, callback_data=cb_data))
        if len(row) >= 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("返回", callback_data="list_page:1")])
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

# 汉字数字转阿拉伯数字
chinese_num_map = {
    "零":0,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10,
    "十一":11,"十二":12,"十三":13,"十四":14,"十五":15,"十六":16,"十七":17,"十八":18,"十九":19,"二十":20
}
def chinese_to_num(s):
    if s.isdigit():
        return int(s)
    if s in chinese_num_map:
        return chinese_num_map[s]
    return None

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
    
    # 优先处理底部按钮指令，不要当成搜索关键词
    if t == "🎬 全部影片" or t == "全部影片":
        works = get_all_works()
        if not works:
            await update.message.reply_text("暂无收录，频道发消息开始收录吧！\n格式：《片名》第X集 #标签")
            return
        await update.message.reply_text(
            f"📋 <b>全部收录（共 {len(works)} 部作品）</b>\n点作品展开集数👇",
            reply_markup=works_list_kb(works),
            parse_mode="HTML"
        )
        return
    elif t == "🔎 搜索" or t == "搜索":
        await update.message.reply_text("请直接发片名关键词给我！")
        return
    elif t == "🏷️ 按标签" or t == "按标签":
        await update.message.reply_text("标签功能开发中，敬请期待！")
        return
    elif t == "❓ 帮助" or t == "帮助":
        text = """📖 <b>使用帮助</b>

<b>收录格式：</b>
《作品名》第X集 #标签1 #标签2
支持写法：《片名》第4集 / 《片名》第四集 / 《片名》第四集04

<b>播放：</b>
点击蓝色数字集数即可播放
"""
        await update.message.reply_text(text, parse_mode="HTML")
        return
    
    # 真正的关键词搜索
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
    text = ""
    if update.channel_post:
        text = update.channel_post.text or update.channel_post.caption or ""
    
    text = text.strip()
    if not text:
        return

    logger.info(f"📥 收到频道消息: {text}")

    # 匹配：《片名》第[汉字/数字][集/期][数字后缀]
    match = re.search(r"《\s*(.+?)\s*》\s*第\s*([一二三四五六七八九十\d]+)\s*(?:集|期)\s*(\d+)?", text)
    
    if not match:
        logger.info("⚠️  未匹配到收录格式")
        return

    name = match.group(1).strip()
    num_part = match.group(2).strip()
    suffix_num = match.group(3)

    # 优先用后缀数字，否则转换汉字数字
    if suffix_num:
        episode = int(suffix_num)
    else:
        episode = chinese_to_num(num_part)
        if not episode:
            logger.info(f"⚠️  集数解析失败: {num_part}")
            return

    # 更新数据库 — 确保已上传列表正确追加并去重
    existing = get_episodes_of_work(name)
    if existing:
        uploaded = existing["uploaded_list"] + [episode]
        total = max(existing["total_episodes"], episode)
    else:
        uploaded = [episode]
        total = episode
    
    uploaded = sorted(set(uploaded))
    add_or_update_work(name, total, uploaded)
    
    reply_text = f"✅ 已收录：《{name}》第{episode}集\n📊 已收录 {len(uploaded)} 集"
    await update.effective_chat.send_message(reply_text)
    logger.info(f"✅ 收录成功: 《{name}》第{episode}集")

# ========== 按钮回调处理 ==========
async def button_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    try:
        await q.answer()
    except Exception:
        return

    d = q.data

    if d == "noop":
        await q.answer("该集暂未上传", show_alert=True)
        return

    if d.startswith("play:"):
        _, work_name, ep_str = d.split(":", 2)
        ep = int(ep_str)
        await q.answer(f"正在播放：{work_name} 第{ep}集", show_alert=True)
        return

    if d.startswith("show_eps:"):
        wn = d.split(":", 1)[1]
        w = get_episodes_of_work(wn)
        if not w:
            await q.answer("该作品不存在", show_alert=True)
            return
        uploaded = w.get("uploaded_list", [])
        if not isinstance(uploaded, list):
            uploaded = []
        await q.edit_message_text(
            f"📺 <b>{w.get('work_name', wn)}</b> — 共 {w.get('total_episodes', 0)} 集 / 已上传 {len(uploaded)} 集\n\n点击数字播放",
            reply_markup=episodes_kb(w),
            parse_mode="HTML"
        )

    elif d.startswith("list_page:"):
        works = get_all_works()
        await q.edit_message_text(
            f"📋 <b>全部收录</b>\n共 {len(works)} 部作品",
            reply_markup=works_list_kb(works),
            parse_mode="HTML"
        )

    elif d == "all_movies":
        works = get_all_works()
        if not works:
            text = "暂无收录，频道发消息开始收录吧！"
        else:
            text = f"全部影片 — 共 {len(works)} 部作品"
        await q.edit_message_text(text, reply_markup=works_list_kb(works, 1), parse_mode="HTML")

    elif d == "search":
        await q.edit_message_text("请输入片名搜索：", reply_markup=main_kb(), parse_mode="HTML")

    elif d == "by_tag":
        await q.edit_message_text("请选择标签：", reply_markup=main_kb(), parse_mode="HTML")

    elif d == "help":
        help_text = """使用说明：
格式：《片名》第X集
支持：《片名》第四集 / 《片名》第四集04
点击数字集数即可播放
"""
        await q.edit_message_text(help_text, reply_markup=main_kb(), parse_mode="HTML")
