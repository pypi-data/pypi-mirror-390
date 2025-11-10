# ================================================================
# File: yemot_flow/utils.py
# ================================================================
"""Utilities."""
from __future__ import annotations

import time
import urllib.parse
import re

# תווים אסורים שיוחלפו בפסיק - רק בטקסט של הודעות למשתמש
FORBIDDEN_REPLACE_WITH_COMMA = ".'&\n\r\t"

# תווים שיימחקו לגמרי (גרשיים) - רק בטקסט של הודעות למשתמש  
FORBIDDEN_DELETE = '\"'

def now_ms() -> int:
    return int(time.time() * 1000)


def urlencode(text: str) -> str:
    return urllib.parse.quote_plus(text, encoding="utf-8")


def sanitize_text(text: str, remove_invalid_chars: bool = True) -> str:
    """
    ניקוי טקסט לשליחה לימות המשיח - רק עבור תוכן הודעות למשתמש
    
    Args:
        text: הטקסט לניקוי (תוכן הודעות בלבד, לא פרמטרים טכניים)
        remove_invalid_chars: האם להחיל ניקוי תווים
        
    Returns:
        טקסט נקי לשליחה לימות
        
    Rules (חלים רק על תוכן הודעות):
        - תווים .'&\n\r\t מוחלפים בפסיק
        - גרשיים " נמחקים לגמרי
        - שורות חדשות מרובות מתכווצות לפסיק אחד
        
    Note: פונקציה זו משמשת רק לניקוי תוכן הודעות טקסט למשתמש,
          לא לפרמטרים טכניים של API.
    """
    if not remove_invalid_chars:
        return text
        
    if not text:
        return ""
    
    # החלפה בפסיק - רק בתוכן הודעות
    for ch in FORBIDDEN_REPLACE_WITH_COMMA:
        text = text.replace(ch, ",")
    
    # מחיקת גרשיים - רק בתוכן הודעות
    for ch in FORBIDDEN_DELETE:
        text = text.replace(ch, "")
    
    # ניקוי פסיקים מרובים ורווחים
    text = re.sub(r',+', ',', text)  # פסיקים מרובים לפסיק אחד
    text = re.sub(r'\s+', ' ', text)  # רווחים מרובים לרווח אחד
    text = text.strip(' ,')  # הסרת פסיקים ורווחים מההתחלה והסוף
    
    return text


def clean_speech_text(text: str) -> str:
    """
    ניקוי מיוחד לטקסט שחוזר מזיהוי דיבור
    
    Args:
        text: טקסט שחזר מSTT
        
    Returns:
        טקסט נקי ומעוצב
    """
    if not text:
        return ""
    
    # הסרת מילות מילוי נפוצות
    filler_words = [
        "אה", "אהה", "אההה", "אמ", "אממ", "אמממ",
        "הה", "ההה", "אוף", "נו", "אוקיי", "okay"
    ]
    
    words = text.split()
    cleaned_words = [word for word in words if word.lower() not in filler_words]
    
    return " ".join(cleaned_words)


def validate_phone_number(phone: str) -> str:
    """
    ניקוי וואלידציה למספר טלפון
    
    Args:
        phone: מספר טלפון גולמי
        
    Returns:
        מספר טלפון מנוקה או מחרוזת ריקה אם לא תקין
    """
    if not phone:
        return ""
    
    # הסרת כל מה שלא ספרות או מקף
    phone = re.sub(r'[^\d-]', '', phone)
    
    # הסרת מקפים מיותרים
    phone = phone.strip('-')
    
    # בדיקת אורך סביר (7-15 ספרות)
    digits_only = re.sub(r'[^\d]', '', phone)
    if len(digits_only) < 7 or len(digits_only) > 15:
        return ""
    
    return phone