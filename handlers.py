from telegram import Update
from telegram.ext import ContextTypes.DEFAULT_TYPE
from database import get_episodes_of_work, get_all_works
from keyboards import episodes_kb, works_list_kb, main_kb

async def button_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    try:
        await q.answer()
    except Exception:
        return

    d = q.data

    # 无操作
    if d == "noop":
        await q.answer("该集/期暂未上传", show_alert=True)
        return

    # 显示作品集数
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

    # 作品列表分页
    elif d.startswith("list_page:"):
        page = int(d.split(":", 1)[1])
        works = get_all_works()
        await q.edit_message_text(
            f"📋 <b>全部收录</b>\n共 {len(works)} 部作品",
            reply_markup=works_list_kb(works, page),
            parse_mode="HTML"
        )

    # 返回列表
    elif d.startswith("back_to_list:"):
        page = int(d.split(":", 1)[1])
        works = get_all_works()
        await q.edit_message_text(
            f"📋 <b>全部收录</b>\n共 {len(works)} 部作品",
            reply_markup=works_list_kb(works, page),
            parse_mode="HTML"
        )

    # 全部影片
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

    # 搜索
    elif d == "search":
        await q.edit_message_text(
            "🔍 请输入片名搜索：",
            reply_markup=main_kb(),
            parse_mode="HTML"
        )

    # 按标签
    elif d == "by_tag":
        await q.edit_message_text(
            "🏷️ 请选择标签：",
            reply_markup=main_kb(),
            parse_mode="HTML"
        )

    # 帮助
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
