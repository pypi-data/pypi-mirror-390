# -*- coding: utf-8 -*-
# File: SBself/core/final_text.py
#
# متن نهایی = متن پایه + کپشن (طبق همین کانفیگ فعلی) + منشن‌ها
# ⚠️ برای رندر درست منشن‌ها، پیام را با parse_mode="HTML" ارسال کن.

import random
import re
from typing import List, Optional, Union
from .text_manager import get_spam_texts
from ..core.config import spam_config
from .mention_manager import make_mention_html  # سازنده‌ی <a href="tg://user?id=...">label</a> 

try:
    # فقط برای تشخیص اینکه base از نوع Message است یا نه
    from pyrogram.types import Message as _PyroMessage  # type: ignore
except Exception:
    _PyroMessage = None  # type: ignore


# =========================
# متن تصادفی (از AllConfig["text"]["lines"])
# =========================
def get_random_text() -> str:
    """
    متن تصادفی را از spam_config["text_list"] یا get_spam_texts() می‌گیرد.
    اگر لیست خالی بود، رشته‌ای پیش‌فرض برمی‌گرداند تا خروجی build_final_text هیچ‌وقت خالی نباشد.
    """
    try:
        txt = get_spam_texts()
        if not txt or not str(txt).strip():
            raise ValueError("Empty spam text list.")
        return str(txt).strip()
    except Exception:
        # متن پیش‌فرض در صورت خالی بودن لیست
        return "Default test message from get_random_text()"

# =========================
# کپشن از کانفیگ (وقتی base=Message نیست)
# منبع: AllConfig["text"]["caption"]
# سوییچ: AllConfig["spammer"]["caption_on"] یا وقتی caption خالی نباشه
# =========================
def _caption_from_config() -> str:
    caption = spam_config["caption"]
    return f"\n{caption}"


# =========================
# نرمال‌سازی ورودی‌های منشن
# =========================
_USERNAME_RE = re.compile(r"[A-Za-z0-9_]{3,}")

def _normalize_user_id(val) -> Optional[int]:
    """اگر ورودی عددی باشد به int برمی‌گرداند، وگرنه None."""
    try:
        s = str(val).strip().lstrip("@")
        return int(s)
    except Exception:
        return None

def _normalize_username(val) -> Optional[str]:
    """اگر ورودی username معتبر باشد (با/بی‌@)، برمی‌گرداند؛ وگرنه None."""
    try:
        s = str(val).strip().lstrip("@")
        if not s:
            return None
        return s if _USERNAME_RE.fullmatch(s) else None
    except Exception:
        return None

def _make_username_link_html(username: str, label_text: str) -> str:
    """
    برای username لینک وب می‌سازیم تا در HTML کلیک‌پذیر باشد.
    اگر label_text خالی بود، خودِ @username نمایش داده می‌شود.
    """
    visible = (label_text or "").strip() or f"@{username}"
    return f'<a href="https://t.me/{username}">{visible}</a>'


# =========================
# ساخت منشن‌ها از AllConfig["mention"]
# کلیدها: textMen, useridMen, is_menshen, group_menshen, group_ids
# =========================
def build_mentions() -> str:
    """
    قوانین:
      - اگر مقدار عددی (ID) بود → tg://user?id=... با لیبل textMen (یا "mention")
      - اگر username بود → https://t.me/username با لیبل textMen؛
        اگر textMen خالی بود، خودِ @username نمایش داده می‌شود.
    خروجی:
      - "" اگر چیزی نبود
      - "\n" + " ".join(parts) در غیر این صورت
    """
    parts: List[str] = []

    label_cfg = spam_config["textMen"].strip()
    default_label = label_cfg or "mention"

    # تکی
    single_val = spam_config["useridMen"]
    if spam_config["is_menshen"] and single_val:
        uid = _normalize_user_id(single_val)
        if uid is not None:
            parts.append(make_mention_html(uid, default_label))
        else:
            uname = _normalize_username(single_val)
            if uname:
                parts.append(_make_username_link_html(uname, label_cfg))

    # گروهی
    if spam_config["group_menshen"] and spam_config["group_ids"]:
        for gid in spam_config["group_ids"]:
            uid = _normalize_user_id(gid)
            if uid is not None:
                parts.append(make_mention_html(uid, default_label))
            else:
                uname = _normalize_username(gid)
                if uname:
                    parts.append(_make_username_link_html(uname, label_cfg))

    return ("\n" + " ".join(parts)) if parts else ""


# =========================
# استخراج متن/کپشن از Message
# =========================
def _extract_from_message(msg) -> tuple[str, str]:
    """
    از Message، متن پایه و کپشنِ پیام را استخراج می‌کند.
    base_text: caption اگر بود؛ وگرنه text؛ وگرنه ""
    msg_caption: جداگانه خالی است (چون cap را در base می‌ریزیم تا دوباره‌کاری نشود)
    """
    base_text = ""
    msg_caption = ""
    try:
        cap = (getattr(msg, "caption", None) or "").strip()
        txt = (getattr(msg, "text", None) or "").strip()
        base_text = cap or txt or ""
        msg_caption = ""
    except Exception:
        pass
    return base_text, msg_caption


# =========================
# مونتاژ نهایی (متن + کپشن + منشن)
# =========================
def build_final_text(base: Optional[Union[str, object]] = None) -> str:
    """
    ترتیب:
      1) متن پایه:
         - اگر base=Message → caption یا text پیام
         - اگر base=str → همان
         - اگر base=None → یک متن تصادفی از text.lines
      2) کپشن:
         - اگر base=Message → کپشن پیام قبلاً در base_text لحاظ شده (چیزی اضافه نمی‌کنیم)
         - در غیر این صورت، از text.caption (در صورت فعال بودن/وجود) اضافه می‌شود
      3) منشن‌ها از mention.*
    خروجی: رشتهٔ HTML (برای ارسال با parse_mode="HTML")
    """
    msg_given = (_PyroMessage is not None and isinstance(base, _PyroMessage))

    if msg_given:
        base_text, msg_caption = _extract_from_message(base)
        caption_part = msg_caption  # عمداً خالی؛ cap در base_text لحاظ شده
    else:
        base_text = (str(base).strip() if isinstance(base, str) else "") or get_random_text()
        caption_part = _caption_from_config()

    if not base_text:
        return ""

    mentions_part = build_mentions()
    return "".join([base_text, caption_part, mentions_part])
