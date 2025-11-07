# 🎉 yemot-flow v0.2.0 - מהפכה בפיתוח IVR!

## 🚀 השוואה: לפני ואחרי

### ❌ **הקוד הישן (v0.1.x) - מסורבל ולא קריא:**

```python
@flow.get("")
def welcome(call):
    # בדיקה ידנית של קלט
    digits = call.params.get("Digits")
    
    if digits:
        # יש קלט - עיבוד
        if digits == "1":
            call.play_message([('text', 'העברתך לחברה')])
        elif digits == "2":
            call.play_message([('text', 'העברתך לתמיכה')])
        else:
            call.play_message([('text', 'בחירה לא חוקית')])
    else:
        # אין קלט - תפריט
        call.read([('text', 'ברוכים הבאים. בחר אפשרות')], 
                 max_digits=1, digits_allowed="12")
```

### ✅ **הקוד החדש (v0.2.0) - פשוט וקריא כמו Node.js:**

```python
@flow.get("")
async def welcome(call):
    # פשוט וישיר!
    choice = await call.read([('text', 'ברוכים הבאים. בחר אפשרות')], 
                            max_digits=1, digits_allowed="12")
    
    if choice == "1":
        call.play_message([('text', 'העברתך לחברה')])
    elif choice == "2": 
        call.play_message([('text', 'העברתך לתמיכה')])
    else:
        call.play_message([('text', 'בחירה לא חוקית')])
```

## 🎯 **התכונות החדשות:**

### 1. **async/await Support** 
```python
# עכשיו זה עובד!
choice = await call.read([('text', 'בחר אפשרות')], max_digits=1)
```

### 2. **לולאות ותנאים טבעיים**
```python
attempts = 0
while attempts < 3:
    pin = await call.read([('text', f'הכנס PIN (ניסיון {attempts+1})')], max_digits=4)
    if validate_pin(pin):
        break
    attempts += 1
```

### 3. **איסוף נתונים פשוט**
```python
name = await call.read([('text', 'מה שמך?')], mode="stt")
age = await call.read([('text', 'מה גילך?')], max_digits=2)
phone = await call.read([('text', 'מה הטלפון שלך?')], max_digits=10)

# עכשיו יש לנו את כל הנתונים!
save_user_data(name, age, phone)
```

### 4. **תמיכה מלאה בכל סוגי הקלט**
```python
# טקסט רגיל
choice = await call.read([('text', 'בחר')], max_digits=1)

# זיהוי דיבור  
name = await call.read([('text', 'אמור שם')], mode="stt", lang="he-IL")

# הקלטה
file_path = await call.read([('text', 'הקלט הודעה')], 
                           mode="record", max_length=60)
```

## 📦 **התקנה:**

```bash
pip install --upgrade yemot-flow>=0.2.0
```

## 📝 **דוגמה מלאה:**

```python
from flask import Flask, request, Response
from yemot_flow import Flow

app = Flask(__name__)
flow = Flow()

@flow.get("")
async def main_menu(call):
    choice = await call.read([
        ('text', 'ברוכים הבאים. לחברה הקש 1, לתמיכה הקש 2')
    ], max_digits=1, digits_allowed="12")
    
    if choice == "1":
        call.goto("/company")
    elif choice == "2":
        call.goto("/support")

@flow.get("support")
async def support(call):
    issue_type = await call.read([
        ('text', 'תמיכה. לבעיה טכנית הקש 1, לשאלה כללית הקש 2')
    ], max_digits=1, digits_allowed="12")
    
    if issue_type == "1":
        # הקלטת תיאור בעיה
        call.play_message([('text', 'תאר את הבעיה לאחר הצפצוף')])
        issue_file = await call.read([('text', 'התחל')], 
                                    mode="record", max_length=120)
        
        call.play_message([('text', 'הבעיה נרשמה. נחזור אליך בהקדם')])
        call.hangup()
        
    elif issue_type == "2":
        call.play_message([('text', 'לשאלות כלליות פנה למייל: info@example.com')])
        call.hangup()

@app.route("/yemot", methods=["GET", "POST"])
def yemot_entry():
    return Response(
        flow.handle_request(request.values.to_dict()),
        mimetype="text/plain; charset=utf-8"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## 🎊 **זהו! עכשיו יש לך ספרייה שפשוטה כמו Node.js!**

- ✅ אין יותר בדיקות `if digits:` מסורבלות
- ✅ אין יותר ניהול state ידני  
- ✅ קוד קריא וטבעי עם async/await
- ✅ תמיכה מלאה בכל תכונות ימות המשיח
- ✅ עובד עם Flask ו-FastAPI
- ✅ תואם לחלוטין עם API הקיים

### 🔄 **Migration מ-v0.1.x:**

הקוד הישן ימשיך לעבוד! אבל מומלץ לעבור לגרסה החדשה:

```python
# ישן
@flow.get("")
def old_way(call):
    digits = call.params.get("Digits")  # מסורבל
    if digits:
        # לוגיקה מורכבת...

# חדש  
@flow.get("")
async def new_way(call):
    choice = await call.read([('text', 'בחר')], max_digits=1)  # פשוט!
    # לוגיקה פשוטה...
```

**יemot-flow v0.2.0 - סוף סוף פיתוח IVR פשוט בפייתון! 🐍✨**