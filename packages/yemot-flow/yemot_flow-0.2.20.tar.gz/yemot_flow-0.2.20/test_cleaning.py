#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקה מהירה של ניקוי טקסט
"""

from yemot_flow.utils import sanitize_text, clean_speech_text, validate_phone_number

# בדיקות ניקוי טקסט
test_cases = [
    'טקסט עם "גרשיים"',
    'נקודות...רבות', 
    'קו & מיוחד',
    'שורה\nחדשה',
    'רווחים    רבים',
    'פסיקים,,,רבים',
    'הכל ביחד: "שלום"...עולם & שורה\nחדשה!'
]

print("🧹 בדיקת ניקוי טקסט:")
print("=" * 50)

for i, test in enumerate(test_cases, 1):
    cleaned = sanitize_text(test)
    print(f"{i}. מקור:  '{test}'")
    print(f"   נוקה:  '{cleaned}'")
    print()

# בדיקות ניקוי דיבור
print("🗣️ בדיקת ניקוי דיבור:")
print("=" * 50)

speech_cases = [
    "אה שלום אמ אני קוראים לי אההה יוסי",
    "אוף המספר שלי הוא נו חמישה חמש שמונה",
    "אמממ אני אוהב אוקיי פיצה ממש טעימה",
]

for i, speech in enumerate(speech_cases, 1):
    cleaned = clean_speech_text(speech)
    further_cleaned = sanitize_text(cleaned)
    print(f"{i}. מקור:     '{speech}'")
    print(f"   ללא מילוי: '{cleaned}'")
    print(f"   סופי:     '{further_cleaned}'")
    print()

# בדיקות מספרי טלפון
print("📞 בדיקת מספרי טלפון:")
print("=" * 50)

phone_cases = [
    "חמש שמונה שלוש אחד שתיים שלוש ארבע",
    "050-1234567",
    "שלוש אפס תשע - מליון מאתיים",
    "058-123-4567",
    "123",  # קצר מדי
    "תשע שמונה שבע שש חמש ארבע שלוש שתיים אחד אפס תשע",  # ארוך מדי
]

for i, phone in enumerate(phone_cases, 1):
    cleaned = validate_phone_number(phone)
    print(f"{i}. מקור: '{phone}'")
    print(f"   נוקה: '{cleaned}' {'✅' if cleaned else '❌'}")
    print()

print("🎯 הסיום - כל הבדיקות הושלמו!")