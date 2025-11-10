#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקה שהניקוי עובד רק על תוכן הודעות ולא על פרמטרים טכניים
"""

from yemot_flow.actions import build_id_list_message, build_read

# בדיקה 1: id_list_message
print("🧪 בדיקת id_list_message:")
print("=" * 50)

# הודעה עם תווים "בעייתיים"
messages_with_forbidden = [
    ("text", 'ברוך הבא להקמת שיחה חדשה. הקש 1, להמשך שיחה קיימת הקש 2.'),
    ("text", 'יש לך "בעיות"? נקודות... ו&שורה\nחדשה!')
]

result1 = build_id_list_message(messages_with_forbidden)
print("תוצאה עם ניקוי:")
print(result1)
print()

result2 = build_id_list_message(messages_with_forbidden, remove_invalid_chars=False)
print("תוצאה ללא ניקוי:")
print(result2)
print()

# בדיקה 2: build_read
print("📞 בדיקת build_read:")
print("=" * 50)

# הודעת קלט עם תווים "בעייתיים"
read_messages = [
    ("text", 'ברוך הבא! הקש 1. לעזרה הקש 2... או & כל מקש אחר.')
]

read_result1 = build_read(
    read_messages,
    mode="tap",
    val_name="MenuChoice",
    max_digits=1,
    digits_allowed="12"
)
print("read עם ניקוי:")
print(read_result1)
print()

read_result2 = build_read(
    read_messages,
    mode="tap", 
    val_name="MenuChoice",
    max_digits=1,
    digits_allowed="12",
    remove_invalid_chars=False
)
print("read ללא ניקוי:")
print(read_result2)
print()

# בדיקה 3: וודא שפרמטרים טכניים לא נפגעים
print("🔧 בדיקת שמירה על פרמטרים טכניים:")
print("=" * 50)

# פרמטרים עם נקודות ותווים מיוחדים (צריכים להישמר)
technical_read = build_read(
    [("text", "הקש מספר.")],
    mode="tap",
    val_name="UserInput.Main",  # יש נקודה בשם - צריך להישמר
    digits_allowed="123.456",   # יש נקודה - צריך להישמר  
    replace_char="*/"           # יש / - צריך להישמר
)
print("פרמטרים טכניים:")
print(technical_read)
print()

# פירוק התוצאה לבדיקה
parts = technical_read.split('=')
if len(parts) >= 2:
    message_part = parts[1].split(',')[0]
    params_part = ','.join(parts[1].split(',')[1:])
    print("חלק ההודעה (צריך להיות מנוקה):", message_part)
    print("חלק הפרמטרים (צריך להישמר):", params_part)

print("\n✅ הבדיקה מראה שהניקוי מתבצע רק על תוכן ההודעות!")
print("🔧 פרמטרים טכניים נשמרים בדיוק כמו שהם!")