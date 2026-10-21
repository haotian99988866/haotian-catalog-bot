from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import (
    init_db, add_episode, update_message_id_if_exists,
    get_all_works, get_episodes_of_work, search_works_by_keyword
)
from parsers import parse_message_text
from config import Config

init_db()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🎬 全部影片"), KeyboardButton("🔎 搜索")],
        [KeyboardButton("🏷️ 按标签"), KeyboardButton("❓ 帮助")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="输入片名搜索，或点下方按钮"
)

def build_jump_url(mid: int) -> str:
    return f"{Config.CHANNEL_LINK.rstrip('/')}/{mid}"

def works_list_kb(works, page=1, per_page=8):
    total = len(works)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    page_works = works[start:start + per_page]
    kb = []
    for w in page_works:
        t = w["main_type"]
        kb.append([InlineKeyboardButton(
            f"📺 {w['work_name']} ({w['total_episodes']}{t} / 已上传{w['actual_uploaded']})",
            callback_data=f"show_eps:{w['work_name']}"
        )])
    nav = []
    if page > 1: nav.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"list_page:{page-1}"))
    if page < total_pages: nav.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"list_page:{page+1}"))
    if nav: kb.append(nav)
    return InlineKeyboardMarkup(kb) if kb else None

def episodes_kb(wdata, from_page=1):
    kb = []
    for e in wdata["episodes"]:
        if e["has_link"]:
            kb.append([InlineKeyboardButton(
                f"▶ {e['episode']}",
                url=build_jump_url(e["message_id"])
            )])
        else:
            kb.append([InlineKeyboardButton(
                f"⬜ {e['episode']}（暂未上传）",
                callback_data="noop"
            )])
    kb.append([InlineKeyboardButton("⬅️ 返回作品列表", callback_data=f"back_to_list:{from_page}")])
    return InlineKeyboardMarkup(kb)

async def send_menu_kb(u: Update, t: str):
    await u.message.reply_text(t, reply_markup=main_keyboard, parse_mode="HTML")

async def menu(u: Update, c: ContextTypes.DEFAULT_TYPE):
    text = """🎬 <b>昊天影院目录</b>

欢迎使用👇

• 🎬 全部影片 — 按作品浏览，显示总集/期数
• 🔎 搜索 — 查找作品
• 🏷️ 按标签 — 按分类筛选
• ❓ 帮助 — 使用说明

直接发片名也能搜索哦！"""
    await send_menu_kb(u, text)

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await menu(u, c)

async def list_shows(u: Update, c: ContextTypes.DEFAULT_TYPE):
    works = get_all_works()
    if not works:
        await send_menu_kb(u, "📭 暂无收录，频道发消息开始收录吧！\n格式：《片名》第X集 #标签\n综艺用：《综艺名》第X期 #标签")
        return
    await u.message.reply_text(
        "📋 <b>全部收录</b>\n点作品展开列表👇\n⬜=暂未上传  ▶=可播放",
        reply_markup=works_list_kb(works),
        parse_mode="HTML"
    )

async def search_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await send_menu_kb(u, "🔎 请直接发片名关键词给我！")

async def search_work(u: Update, c: ContextTypes.DEFAULT_TYPE, kw=None):
    if not kw: return await search_cmd(u, c)
    works = search_works_by_keyword(kw)
    if not works:
        await send_menu_kb(u, f"🔎 搜索：<b>{kw}</b>\n\n没有找到相关作品")
        return
    await u.message.reply_text(
        f"🔎 搜索：<b>{kw}</b>（找到 {len(works)} 部）\n点作品展开列表👇",
        reply_markup=works_list_kb(works),
        parse_mode="HTML"
    )

async def tags_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await send_menu_kb(u, "🏷️ 标签功能开发中，敬请期待！")

async def help_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await send_menu_kb(u, f"""📖 <b>使用帮助</b>

<b>收录格式：</b>
电视剧/动漫：《片名》第5集 #标签
综艺：《综艺名》第3期 #综艺

<b>显示说明：</b>
▶ 第X集/期 = 已上传，可直接跳转
⬜ 第X集/期（暂未上传）= 占位，待补

<b>频道链接：</b>
{Config.CHANNEL_LINK}""")

async def channel_listener(u: Update, c: ContextTypes.DEFAULT_TYPE):
    msg = u.channel_post
    if not msg or str(msg.chat.id) != str(Config.CHANNEL_ID_EXPECTED): return
    parsed = parse_message_text(msg.text or msg.caption or "")
    if not parsed: return
    wn, ep = parsed["work_name"], parsed["episode"]
    if update_message_id_if_exists(wn, ep, msg.message_id):
        print(f"🔄 更新链接：{wn} - {ep}")
        return
    add_episode(wn, ep, parsed.get("tags", []), msg.message_id)
    print(f"✅ 已收录：{wn} - {ep}")

async def direct_search(u: Update, c: ContextTypes.DEFAULT_TYPE):
    t = u.message.text.strip()
    if t == "🎬 全部影片": await list_shows(u, c)
    elif t == "🔎 搜索": await search_cmd(u, c)
    elif t == "🏷️ 按标签": await tags_cmd(u, c)
    elif t == "❓ 帮助": await help_cmd(u, c)
    else: await search_work(u, c, kw=t)

async def button_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    try: await q.answer()
    except: return
    d = q.data
    if d == "noop":
        await q.answer("该集/期暂未上传", show_alert=True)
        return
    if d.startswith("show_eps:"):
        wn = d.split(":", 1)[1]
        w = get_episodes_of_work(wn)
        if not w: await q.answer("该作品不存在", show_alert=True); return
        t = w["main_type"]
        await q.edit_message_text(
            f"📺 <b>{wn}</b> — 共 {w['total_episodes']}{t} / 已上传 {w['actual_uploaded']}{t}\n▶=可播放  ⬜=暂未上传",
            reply_markup=episodes_kb(w),
            parse_mode="HTML"
        )
    elif d.startswith("list_page:"):
        page = int(d.split(":")[1])
        await q.edit_message_text(
            "📋 <b>全部收录</b>\n点作品展开列表👇",
            reply_markup=works_list_kb(get_all_works(), page),
            parse_mode="HTML"
        )
    elif d.startswith("back_to_list:"):
        page = int(d.split(":")[1])
        await q.edit_message_text(
            "📋 <b>全部收录</b>\n点作品展开列表👇",
            reply_markup=works_list_kb(get_all_works(), page),
            parse_mode="HTML"
        )
