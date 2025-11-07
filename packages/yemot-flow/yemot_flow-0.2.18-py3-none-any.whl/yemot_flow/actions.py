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
    parts = []
    for m_type, data in messages:
        clean = sanitize_text(data) if remove_invalid_chars else data
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
    if not messages:
        raise ValueError("read requires at least one message")

    m_type, data = messages[0]
    # אפשרות לשלוט בקידוד URL
    should_encode = opts.get("url_encode", False)
    encoded_data = urlencode(data) if should_encode else data
    msg_part = f"{_PREFIX.get(m_type, m_type)}-{encoded_data}"

    yn = lambda v: "yes" if v is True else "no" if v is False else v  # noqa: E731

    # שני שדות ראשונים - עכשיו משתמש בval_name שהועבר
    base = [opts.get("val_name", "val_1"), yn(opts.get("re_enter_if_exists", "no"))]

    if mode == "tap":
        third = ""  # empty → key‑press
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
    else:
        raise ValueError(f"Unsupported read mode: {mode}")

    fields = base + [third] + rest
    return f"read={msg_part}={','.join(map(str, fields))}"


# ---------- go_to_folder ----------

def build_go_to_folder(folder: str) -> str:
    return "go_to_folder=" + (folder if folder == "hangup" or folder.startswith("/") else "/" + folder)


# ---------- combined actions ----------

def build_combined_action(actions: List[str]) -> str:
    """שילוב כמה פעולות עם & ביניהן"""
    return "&".join(actions)

