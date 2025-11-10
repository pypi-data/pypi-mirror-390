# ================================================================
# File: yemot_flow/actions.py
# ================================================================
"""Builders – המרת פקודות לטקסט API של ימות."""
from __future__ import annotations

from typing import List, Tuple

from .utils import sanitize_text, urlencode

Message = Tuple[str, str]

_PREFIX = {
    "text": "t",
    "file": "f",
    "speech": "s",
    "digits": "d",
    "number": "n",
    "alpha": "a",
}


# ---------- id_list_message ----------

def build_id_list_message(messages: List[Message], *, remove_invalid_chars: bool | None = None, url_encode: bool = False) -> str:
    """
    בניית הודעת id_list_message לימות המשיח
    
    Args:
        messages: רשימת הודעות [(type, content), ...]
        remove_invalid_chars: האם לנקות תווים אסורים מתוכן ההודעות בלבד
        url_encode: האם לקודד URL
        
    Returns:
        מחרוזת API מוכנה לשליחה
        
    Note: הניקוי מתבצע רק על תוכן ההודעות (content), לא על הפרמטרים הטכניים
    """
    parts = []
    for m_type, data in messages:
        # ברירת מחדל - מנקה תווים אלא אם נאמר אחרת (רק מתוכן ההודעה!)
        should_clean = remove_invalid_chars if remove_invalid_chars is not None else True
        clean = sanitize_text(data, should_clean) if should_clean else data
        encoded_data = urlencode(clean) if url_encode else clean
        parts.append(f"{_PREFIX.get(m_type, m_type)}-{encoded_data}")
    return "id_list_message=" + ".".join(parts)


# ---------- read (tap / record / stt) ----------

def build_read(
    messages: List[Message],
    *,
    mode: str = "tap",
    **opts,
) -> str:
    """
    בניית פקודת read לקבלת קלט מהמשתמש
    
    Args:
        messages: הודעות להשמעה לפני הקלט
        mode: סוג הקלט (tap/record/stt)
        **opts: פרמטרים טכניים נוספים
        
    Returns:
        מחרוזת API מוכנה לשליחה
        
    Important: הניקוי מתבצע רק על תוכן ההודעות למשתמש,
               הפרמטרים הטכניים נשמרים בדיוק כמו שהם!
    """
    if not messages:
        raise ValueError("read requires at least one message")

    m_type, data = messages[0]
    # ניקוי טקסט ברירת מחדל - רק על תוכן ההודעה למשתמש!
    should_clean = opts.get("remove_invalid_chars", True)
    clean_data = sanitize_text(data, should_clean) if should_clean else data
    # אפשרות לשלוט בקידוד URL
    should_encode = opts.get("url_encode", False)
    encoded_data = urlencode(clean_data) if should_encode else clean_data
    msg_part = f"{_PREFIX.get(m_type, m_type)}-{encoded_data}"

    yn = lambda v: "yes" if v is True else "no" if v is False else v  # noqa: E731

    # שני שדות ראשונים - עכשיו משתמש בval_name שהועבר
    base = [opts.get("val_name", "val_1"), yn(opts.get("re_enter_if_exists", "no"))]

    if mode == "tap":
        # tap - השדה השלישי מושמט לגמרי (לא ריק!)
        rest = [
            opts.get("max_digits", "*"),
            opts.get("min_digits", 1),
            opts.get("sec_wait", 7),
            opts.get("typing_playback_mode", "NO"),
            yn(opts.get("block_asterisk_key", "no")),
            yn(opts.get("block_zero_key", "no")),
            opts.get("replace_char", "*/"),
            opts.get("digits_allowed", ""),
            opts.get("amount_attempts", 3),
            yn(opts.get("allow_empty", "no")),
            opts.get("empty_val", "None"),
            yn(opts.get("block_change_keyboard", "no")),
        ]
        fields = base + rest  # ללא שדה שלישי
    elif mode == "record":
        third = "record"
        rest = [
            opts.get("path", ""),
            opts.get("file_name", ""),
            yn(opts.get("no_confirm_menu", "no")),
            yn(opts.get("save_on_hangup", "no")),
            yn(opts.get("append_to_existing_file", "no")),
            opts.get("min_length", ""),
            opts.get("max_length", ""),
        ]
        fields = base + [third] + rest  # עם שדה שלישי
    elif mode == "stt":
        third = "voice"
        rest = [
            opts.get("lang", ""),
            yn(opts.get("block_typing", "no")),
            opts.get("max_digits", ""),
            yn(opts.get("use_records_recognition_engine", "no")),
            opts.get("quiet_max", ""),
            opts.get("length_max", ""),
        ]
        fields = base + [third] + rest  # עם שדה שלישי
    else:
        raise ValueError(f"Unsupported read mode: {mode}")

    # חשוב: שומרים על שדות ריקים עם str() מפורש
    fields_str = [str(field) for field in fields]
    return f"read={msg_part}={','.join(fields_str)}"


# ---------- go_to_folder ----------

def build_go_to_folder(folder: str) -> str:
    return "go_to_folder=" + (folder if folder == "hangup" or folder.startswith("/") else "/" + folder)


# ---------- combined actions ----------

def build_combined_action(actions: List[str]) -> str:
    """שילוב כמה פעולות עם & ביניהן"""
    return "&".join(actions)

