# -*- coding: utf-8 -*-
# remote/mention_manager.py
#
# مدیریت منشن تکی و گروهی با پذیرش آیدی عددی و @username
# - بدون parse_mode (نه HTML و نه Markdown)
# - تولید «منشن واقعی» با استفاده از entities (TEXT_LINK → tg://user?id=...)
# - سازگار با هندلرهای main.py شما:
#     set_mention_cmd(message, config.spam_config)
#     remove_mention_cmd(message, config.spam_config)
#     toggle_mention_cmd(message, config.spam_config)
#     group_mention_cmd(message, config.spam_config)
#
# نکته مهم: برای منشن واقعی، باید هنگام send_message علاوه بر text، entities هم پاس داده شود.
# این فایل هم خروجی ساده‌ی رشته‌ای می‌دهد (get_active_mentions) و هم خروجی متن+entities
# (get_active_mentions_with_entities). اسپمر/سایر بخش‌ها برای منشن واقعی باید دومی را مصرف کنند.
import html
import re
import logging
from typing import List, Tuple, Dict, Any, Iterable,Optional
from ..core.config import spam_config 
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import UsernameNotOccupied
logger = logging.getLogger(__name__)

def _normalize_id_token(tok: str) -> int | None:
    """
    نرمال‌سازی ورودی ID:
      - اعداد (مثبت/منفی) → همان int
      - '@username' یا 't.me/...' قابل تبدیل به ID عددی نیستند اینجا (مدیریت در لایه‌ی commands).
    """
    if tok is None:
        return None
    t = str(tok).strip()
    # فقط عدد را می‌پذیریم ( -100... هم مجاز )
    if t and (t.lstrip("-").isdigit()):
        try:
            return int(t)
        except Exception:
            return None
    return None


def _add_many_preserve_order(dst: List[int], ids: Iterable[int]) -> Tuple[int, int]:
    """
    افزودن چند ID با حفظ ترتیب و جلوگیری از تکرار.
    خروجی: (added_count, skipped_count)
    """
    added = 0
    skipped = 0
    exist = set(dst)
    for i in ids:
        try:
            ii = int(i)
        except Exception:
            skipped += 1
            continue
        if ii in exist:
            skipped += 1
            continue
        dst.append(ii)
        exist.add(ii)
        added += 1
    return added, skipped


def _remove_many(dst: List[int], ids: Iterable[int]) -> Tuple[int, int]:
    """
    حذف یک/چند ID از لیست. اگر نبود، شمرده می‌شود به عنوان skipped.
    خروجی: (removed_count, skipped_count)
    """
    removed = 0
    skipped = 0
    s = set(dst)
    for i in ids:
        try:
            ii = int(i)
        except Exception:
            skipped += 1
            continue
        if ii in s:
            # حذف تمام رخدادها (به‌صورت ایمن)
            dst[:] = [x for x in dst if x != ii]
            s.discard(ii)
            removed += 1
        else:
            skipped += 1
    return removed, skipped
async def _resolve_one_token_to_id(client: Client, token: str) -> Optional[int]:
    """
    token را به chat/user id عددی تبدیل می‌کند:
      - "me" → id خود اکانت
      - "-100..." یا عدد → همان int
      - "@username" یا "t.me/username" → get_chat → id
    اگر نتوانست، None.
    """
    if token is None:
        return None
    t = token.strip()
    if not t:
        return None

    # me
    if t.lower() == "me":
        me = await client.get_me()
        return int(me.id)

    # عدد
    if re.fullmatch(r"-?\d+", t):
        try:
            return int(t)
        except Exception:
            return None

    # username / لینک
    username = t
    if username.startswith("@"):
        username = username[1:]
    if "t.me/" in username.lower():
        username = re.sub(r"^https?://t\.me/", "", username, flags=re.IGNORECASE).strip("/")

    try:
        ch = await client.get_chat(username)
        return int(ch.id)
    except (UsernameNotOccupied, Exception):
        return None


async def _resolve_many_tokens_to_ids(client: Client, tokens: List[str]) -> List[int]:
    """لیست توکن‌ها را به لیست ID عددی تبدیل می‌کند (تبدیل‌های ناموفق حذف می‌شوند)."""
    out: List[int] = []
    for tok in tokens:
        cid = await _resolve_one_token_to_id(client, tok)
        if cid is not None:
            out.append(cid)
    return out
# -------------------------------
# ✍️ تنظیم متن منشن
# -------------------------------
async def set_mention_text(text: str) -> str:
    if not (text or "").strip():
        return "❌ متن منشن نمی‌تواند خالی باشد."
    spam_config["textMen"] = text.strip()
    logger.info(f"✅ Mention text set: {text.strip()}")
    return "✅ متن منشن تنظیم شد."


# -------------------------------
# 🆔 تنظیم شناسه کاربر برای منشن «تکی»
# -------------------------------
async def set_mention_user(user_id: int) -> str:
    try:
        uid = int(user_id)
    except Exception:
        return "❌ شناسه کاربر معتبر نیست."
    spam_config["useridMen"] = uid
    logger.info(f"✅ Mention target set: {uid}")
    return f"✅ کاربر {uid} برای منشن تنظیم شد."


# -------------------------------
# ⚙️ فعال / غیرفعال کردن منشن «تکی»
# -------------------------------
async def toggle_mention(enable: bool) -> str:
    spam_config["is_menshen"] = bool(enable)
    logger.info(f"🔄 Single mention {'enabled' if enable else 'disabled'}.")
    return "✅ منشن تکی فعال شد." if enable else "🛑 منشن تکی غیرفعال شد."


# -------------------------------
# 🔁 فعال / غیرفعال کردن منشن «گروهی»
# -------------------------------
async def toggle_group_mention(enable: bool) -> str:
    spam_config["group_menshen"] = bool(enable)
    logger.info(f"🔄 Group mention {'enabled' if enable else 'disabled'}.")
    return "✅ منشن گروهی فعال شد." if enable else "🛑 منشن گروهی غیرفعال شد."


# -------------------------------
# 👥 افزودن گروه‌ها (چند ID یکجا)
#   مثال: /mention_gps id1 id2 id3 ...
#   نکته: اینجا فقط ID عددی را می‌پذیریم؛ ریـزولوشن username در لایه‌ی command انجام شود.
# -------------------------------
async def add_groups_by_ids(*ids: int | str) -> str:
    groups: List[int] = spam_config["group_ids"]

    # نرمال‌سازی فقط IDهای عددی
    norm = []
    for t in ids:
        n = _normalize_id_token(str(t))
        if n is not None:
            norm.append(n)

    if not norm:
        return "❌ هیچ شناسهٔ معتبری دریافت نشد."

    added, skipped = _add_many_preserve_order(groups, norm)
    logger.info(f"✅ Group IDs added: +{added} / skipped:{skipped} → total:{len(groups)}")
    if added and not spam_config.get("group_menshen", False):
        # اگر کاربر گروهی را روشن نکرده باشد، راهنمایی کوچکی بدهیم (اختیاری)
        return f"✅ {added} شناسه افزوده شد. ℹ️ برای استفاده، منشن گروهی را فعال کنید."
    return f"✅ {added} شناسه افزوده شد. {'(برخی تکراری/نامعتبر بودند.)' if skipped else ''}".strip()


# -------------------------------
# 📥 افزودن از روی ریپلای
#   (ID کاربر ریپلای‌شده را به لیست group_ids اضافه می‌کند)
# -------------------------------
async def add_group_from_reply(user_id: int) -> str:
    try:
        uid = int(user_id)
    except Exception:
        return "❌ شناسهٔ ریپلای معتبر نیست."

    groups: List[int] = spam_config["group_ids"]
    added, skipped = _add_many_preserve_order(groups, [uid])
    logger.info(f"✅ Group add from reply: +{added} (uid={uid}) → total:{len(groups)}")
    return "✅ شناسهٔ کاربرِ ریپلای به لیست منشن گروهی اضافه شد." if added else "ℹ️ این شناسه قبلاً در لیست بود."


# -------------------------------
# ❌ حذف یک یا چند ID از group_ids
#   مثال: /mention_del id1 id2 ...
# -------------------------------
async def remove_groups_by_ids(*ids: int | str) -> str:
    groups: List[int] = spam_config["group_ids"]

    norm = []
    for t in ids:
        n = _normalize_id_token(str(t))
        if n is not None:
            norm.append(n)

    if not norm:
        return "❌ هیچ شناسهٔ معتبری برای حذف دریافت نشد."

    removed, skipped = _remove_many(groups, norm)
    logger.info(f"🗑️ Group IDs removed: -{removed} / skipped:{skipped} → total:{len(groups)}")
    if removed:
        if skipped:
            return f"🗑️ {removed} شناسه حذف شد. (برخی یافت نشدند.)"
        return f"🗑️ {removed} شناسه حذف شد."
    return "ℹ️ هیچ‌کدام از شناسه‌ها در لیست نبود."


# -------------------------------
# 🧹 پاکسازی کامل گروه‌های منشن
# -------------------------------
async def clear_groups() -> str:
    spam_config["group_ids"] = []
    logger.info("🧹 All group mention IDs cleared.")
    return "🧹 تمام گروه‌های منشن پاک شدند."


# -------------------------------
# 📊 وضعیت فعلی منشن
# -------------------------------
async def mention_status() -> str: 
    text = spam_config["textMen"]
    user_id = spam_config["useridMen"]
    single_enabled = bool(spam_config["is_menshen"])
    group_enabled = bool(spam_config["group_menshen"])
    groups = list(spam_config["group_ids"])

    msg = (
        "📋 **وضعیت منشن:**\n"
        f"💬 متن منشن: {text or '—'}\n"
        f"🎯 کاربر تکی: `{user_id or '—'}` — {'✅' if single_enabled else '❌'}\n"
        f"👥 گروهی فعال: {'✅' if group_enabled else '❌'}\n"
        f"📦 تعداد شناسه‌های گروهی: {len(groups)}\n"
    )

    if groups:
        msg += "\n🗂 **لیست گروهی (به ترتیب):**\n"
        msg += "\n".join([f"{i+1}. `{gid}`" for i, gid in enumerate(groups)])

    logger.info("📊 Mention status displayed.")
    return msg

def make_mention_html(user_id: int, text: str) -> str:
    """ساخت منشن HTML تلگرام به یک کاربر."""
    return f'<a href="tg://user?id={int(user_id)}">{html.escape(text or str(user_id))}</a>'
