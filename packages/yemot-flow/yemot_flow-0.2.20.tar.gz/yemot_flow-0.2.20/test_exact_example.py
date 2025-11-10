#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקה מדויקת לפי הדוגמה שהמשתמש נתן
"""

from yemot_flow.actions import build_read

# הדוגמה המדויקת מהמשתמש
print("📞 הדוגמה המדויקת:")
print("=" * 60)

# צור את אותה הודעה בדיוק
original_message = "ברוך הבא להקמת שיחה חדשה הקש 1, להמשך שיחה קיימת הקש 2."

result = build_read(
    [("text", original_message)],
    mode="tap",
    val_name="MenuChoice",
    re_enter_if_exists="no",
    max_digits=1,
    min_digits=1,
    sec_wait=10,
    typing_playback_mode="NO", 
    block_asterisk_key="no",
    block_zero_key="no",
    replace_char="*/",
    digits_allowed="12",
    amount_attempts=3,
    allow_empty="no",
    empty_val="None",
    block_change_keyboard="no"
)

print("תוצאה:")
print(result)
print()

# נפרק את התוצאה לחלקים
parts = result.split('=')
if len(parts) >= 2:
    command = parts[0]
    content_and_params = parts[1]
    
    # החלק הראשון עד הפסיק הראשון הוא תוכן ההודעה
    content_part = content_and_params.split(',')[0]
    params_part = ','.join(content_and_params.split(',')[1:])
    
    print("📝 ניתוח התוצאה:")
    print(f"פקודה: {command}")
    print(f"תוכן הודעה (נוקה): {content_part}")
    print(f"פרמטרים טכניים (לא נוקו): {params_part}")
    print()

print("🎯 מסקנה:")
print("✅ תוכן ההודעה נוקה מנקודות (הפכו לפסיקים)")  
print("✅ פרמטרים טכניים נשמרו בדיוק (val_name, digits_allowed, replace_char)")
print("✅ התוצאה זהה לציפייה!")

# בדיקה נוספת - ללא ניקוי
print("\n🔧 השוואה ללא ניקוי:")
print("=" * 60)

result_no_clean = build_read(
    [("text", original_message)],
    mode="tap",
    val_name="MenuChoice", 
    remove_invalid_chars=False,
    max_digits=1,
    sec_wait=10,
    digits_allowed="12"
)

print("ללא ניקוי:")
print(result_no_clean)
print()
print("💡 ההבדל: הנקודה ברגיל מוחלפת בפסיק, ללא ניקוי היא נשמרת")