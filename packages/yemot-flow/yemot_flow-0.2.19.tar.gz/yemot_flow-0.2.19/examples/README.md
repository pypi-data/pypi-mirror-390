# דוגמאות לשימוש ב-yemot-flow

תיקיה זו מכילה דוגמאות מעשיות לשימוש בספריית `yemot-flow` לבניית מערכות IVR.

## 🎉 חדש בגרסה 0.1.7!
**עברית ללא URL encoding כברירת מחדל!** עכשיו אפשר לכתוב:
```python
call.play_message([('text', 'שלום וברכה!')])  # עובד מיד!
```

## 📁 קבצי הדוגמאות

### 1. `flask_basic_example.py`
**דוגמה בסיסית עם Flask**
- תפריט פשוט עם ניווט בין עמודים
- הצגת מידע על החברה
- שירות לקוחות
- הקלטת הודעות
- הדגמה של פונקציות בסיסיות

```bash
# התקנה והרצה
pip install yemot-flow flask
python flask_basic_example.py
```

### 2. `fastapi_basic_example.py`  
**דוגמה בסיסית עם FastAPI**
- תפריט מתקדם יותר
- דוגמה לזיהוי דיבור (STT)
- הקלטת הודעות והודעות קול
- API מתועד אוטומטית
- endpoint לבדיקת סטטוס

```bash
# התקנה והרצה
pip install yemot-flow fastapi uvicorn
uvicorn fastapi_basic_example:app --host 0.0.0.0 --port 8000
```

### 3. `hebrew_no_encoding_example.py` ⭐ **חדש!**
**דוגמה מעודכנת - עברית ללא קידוד**
- עברית מוצגת בצורה נכונה כברירת מחדל
- קוד פשוט ונקי יותר
- תפריטים מלאים בעברית
- הדגמת כל התכונות החדשות

```bash
# התקנה והרצה
pip install yemot-flow flask
python hebrew_no_encoding_example.py
```

### 4. `restaurant_ordering_system.py`
**מערכת הזמנות מתקדמת למסעדה**
- תפריט מנות מלא (ראשונות, עיקריות, קינוחים)
- בחירת כמויות ומחירים
- איסוף פרטי לקוח (טלפון וכתובת)
- חישוב סכומים אוטומטי
- שמירת הזמנות לקבצים
- אישור הזמנה סופי

```bash
# התקנה והרצה
pip install yemot-flow flask
python restaurant_ordering_system.py
```

## 🚀 הוראות הפעלה כלליות

### שלב 1: התקנת התלויות
```bash
# עבור Flask
pip install yemot-flow flask

# עבור FastAPI  
pip install yemot-flow fastapi uvicorn
```

### שלב 2: הרצת הדוגמה
```bash
# Flask (פורט 5000)
python flask_basic_example.py

# FastAPI (פורט 8000)
uvicorn fastapi_basic_example:app --host 0.0.0.0 --port 8000

# מערכת מסעדה (פורט 5000)
python restaurant_ordering_system.py
```

### שלב 3: הגדרה בימות המשיח
1. כנס לממשק ניהול ימות המשיח
2. צור שלוחה חדשה או ערוך קיימת
3. הגדר את כתובת ה-API:
   - Flask: `http://your-server-ip:5000/yemot`
   - FastAPI: `http://your-server-ip:8000/yemot`

## 📋 תכונות מודגמות

### תכונות בסיסיות
- ✅ הצגת הודעות (`play_message`)
- ✅ קבלת קלט מהמשתמש (`read`)
- ✅ ניווט בין עמודים (`goto`)
- ✅ סיום שיחות (`hangup`)

### תכונות מתקדמות
- ✅ הקלטת הודעות קול (`mode="record"`)
- ✅ זיהוי דיבור (`mode="stt"`)
- ✅ ניהול מצב שיחה (session state)
- ✅ חישובים ולוגיקה עסקית
- ✅ שמירת נתונים לקבצים

### אפשרויות תצורה
- ✅ timeout מותאם אישית
- ✅ הגדרת ספרות מורשות
- ✅ זמן המתנה לקלט
- ✅ הודעות שגיאה מותאמות

## 🛠️ התאמות והרחבות

### הוספת תפריטים חדשים
```python
@flow.get("new-menu")
def new_menu(call):
    call.play_message([("text", "תפריט חדש")])
    # הוסף לוגיקה כאן
    call.goto("/main-menu")
```

### שמירה למסד נתונים
במקום שמירה לקבצים, אפשר להתחבר למסד נתונים:
```python
import sqlite3

def save_to_db(data):
    conn = sqlite3.connect('database.db')
    # הכנס נתונים למסד
    conn.close()
```

### הוספת אימות
```python
@flow.get("protected-area")
def protected_area(call):
    # בדיקת הרשאות
    if not is_authorized(call.params.get("CallerID")):
        call.goto("/unauthorized")
        return
    
    # תוכן מוגן
    call.play_message([("text", "אזור מוגן")])
```

## 🔧 פתרון בעיות נפוצות

### השרת לא עונה
- ודא שהשרת רץ על הפורט הנכון
- בדוק שהfirewall מאפשר תנועה על הפורט
- ודא שכתובת ה-IP נכונה בהגדרות ימות

### שיחות מתנתקות
- הגדל את ה-timeout במחלקת Flow
- ודא שהשרת יציב ולא נופל
- בדוק לוגים לזיהוי שגיאות

### קלט לא נקרא נכון  
- ודא שהגדרת `digits_allowed` נכונה
- בדוק את זמן ההמתנה (`sec_wait`)
- וודא שההודעות ברורות למשתמש

## 📞 יצירת קשר ותמיכה

לשאלות ובעיות:
- פתח Issue ב-GitHub
- בדוק את התיעוד הרשמי
- עיין בדוגמאות נוספות בקהילת ימות המשיח

---

**בהצלחה בבניית המערכת שלך! 🎉**