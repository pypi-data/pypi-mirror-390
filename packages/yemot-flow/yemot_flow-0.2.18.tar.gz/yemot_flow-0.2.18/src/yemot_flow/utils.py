# ================================================================
# File: yemot_flow/utils.py
# ================================================================
"""Utilities."""
from __future__ import annotations

import time
import urllib.parse

FORBIDDEN = ".-'\"&"

def now_ms() -> int:
    return int(time.time() * 1000)


def urlencode(text: str) -> str:
    return urllib.parse.quote_plus(text, encoding="utf-8")


def sanitize_text(text: str) -> str:
    for ch in FORBIDDEN:
        text = text.replace(ch, "")
    return text