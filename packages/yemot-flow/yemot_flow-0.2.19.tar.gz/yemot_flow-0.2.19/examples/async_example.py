#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה חדשה עם async/await - הדרך המודרנית!

התקנה:
pip install yemot-flow flask

הרצה:
python async_example.py

כוון את ימות המשיח לכתובת: http://your-server-ip:5000/yemot
"""

from flask import Flask, request, Response
from yemot_flow import Flow, Call

app = Flask(__name__)
flow = Flow(print_log=True)

@flow.get("")
async def welcome(call: Call):
    """דוגמה פשוטה עם async/await"""
    
    # ברכה ובקשה לשם
    name = await call.read([
        ('text', 'שלום וברכה! ברוכים הבאים למערכת החדשה'),
        ('text', 'אמור את שמך')
    ], mode="stt", val_name="name", lang="he-IL")
    
    # בקשה לגיל
    age = await call.read([
        ('text', f'שלום {name}! כמה אתה בן?')
    ], val_name="age", max_digits=2, digits_allowed="0123456789")
    
    # בחירת שירות
    service = await call.read([
        ('text', f'{name} בן {age}, איזה שירות אתה רוצה?'),
        ('text', 'הקש 1 למידע כללי'),
        ('text', 'הקש 2 לתמיכה טכנית'),
        ('text', 'הקש 3 להזמנת שירות')
    ], val_name="service", max_digits=1, digits_allowed="123")
    
    # טיפול בבחירה
    if service == "1":
        call.play_message([
            ('text', f'{name}, אנחנו חברת טכנולוגיה מתקדמת'),
            ('text', 'מתמחים בפתרונות IVR חכמים עם בינה מלאכותית')
        ])
        
    elif service == "2":
        # בקשה לתיאור הבעיה
        problem = await call.read([
            ('text', 'תאר בקצרה את הבעיה הטכנית')
        ], mode="stt", val_name="problem", lang="he-IL")
        
        call.play_message([
            ('text', f'תודה {name}'),
            ('text', f'רשמנו את הבעיה: {problem}'),
            ('text', 'נציג יחזור אליך תוך 24 שעות')
        ])
        
    elif service == "3":
        # תהליך הזמנה
        await handle_order_process(call, name)
    
    # סיום
    call.play_message([
        ('text', f'תודה {name} על הפנייה!'),
        ('text', 'יום טוב ולהתראות')
    ])
    call.hangup()

async def handle_order_process(call: Call, customer_name: str):
    """תהליך הזמנת שירות"""
    
    # סוג השירות
    service_type = await call.read([
        ('text', 'איזה שירות תרצה להזמין?'),
        ('text', 'הקש 1 לפיתוח אתר'),
        ('text', 'הקש 2 למערכת IVR'),
        ('text', 'הקש 3 לייעוץ טכנולוגי')
    ], val_name="service_type", max_digits=1, digits_allowed="123")
    
    services = {
        "1": "פיתוח אתר",
        "2": "מערכת IVR", 
        "3": "ייעוץ טכנולוגי"
    }
    
    # פרטי התקשרות
    phone = await call.read([
        ('text', f'נבחר שירות: {services[service_type]}'),
        ('text', 'אמור מספר טלפון לחזרה')
    ], mode="stt", val_name="phone", lang="he-IL")
    
    email = await call.read([
        ('text', 'אמור כתובת אימייל')
    ], mode="stt", val_name="email", lang="he-IL")
    
    # אישור פרטים
    call.play_message([
        ('text', f'אישור הזמנה עבור {customer_name}'),
        ('text', f'שירות: {services[service_type]}'),
        ('text', f'טלפון: {phone}'),
        ('text', f'אימייל: {email}'),
        ('text', 'נחזור אליך תוך 48 שעות')
    ])

@flow.get("demo")
async def quick_demo(call: Call):
    """דמו מהיר של יכולות"""
    
    call.play_message([('text', 'דמו מהיר של יכולות המערכת')])
    
    # הקלטה קצרה
    recording = await call.read([
        ('text', 'אמור משהו ונקליט אותו')
    ], mode="record", val_name="demo_recording", max_length=10)
    
    call.play_message([('text', 'תודה! ההקלטה נשמרה')])
    
    # זיהוי דיבור
    speech = await call.read([
        ('text', 'עכשיו אמור משפט ונזהה אותו')
    ], mode="stt", val_name="demo_speech", lang="he-IL")
    
    call.play_message([
        ('text', f'זיהינו: {speech}'),
        ('text', 'סוף הדמו')
    ])
    call.goto("")

@app.route("/yemot", methods=["GET", "POST"]) 
def yemot_entry():
    """נקודת הכניסה"""
    return Response(
        flow.handle_request(request.values.to_dict()),
        mimetype="text/plain; charset=utf-8"
    )

@app.route("/")
def index():
    return """
    <h1>🚀 Yemot Flow - Async/Await Demo</h1>
    <h2>🔗 נקודות כניסה:</h2>
    <ul>
        <li><a href="/yemot?ApiCallId=test1">תפריט ראשי</a></li>
        <li><a href="/yemot?ApiCallId=test2&ApiExtension=demo">דמו מהיר</a></li>
    </ul>
    <p><b>כתובת לימות:</b> <code>/yemot</code></p>
    """

if __name__ == "__main__":
    print("🔥 מערכת async/await פועלת על פורט 5000!")
    print("📞 כתובת לימות: http://your-server:5000/yemot")
    app.run(host="0.0.0.0", port=5000, debug=True)