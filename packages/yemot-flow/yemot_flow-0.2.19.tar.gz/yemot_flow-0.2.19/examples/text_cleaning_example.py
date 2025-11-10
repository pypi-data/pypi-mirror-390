#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה לניקוי תווים אוטומטי

התקנה:
pip install yemot-flow flask

הרצה:
python text_cleaning_example.py
"""

from flask import Flask, request, Response
from yemot_flow import Flow, Call

app = Flask(__name__)
flow = Flow(print_log=True)

@flow.get("")
async def text_cleaning_demo(call: Call):
    """דמו לניקוי תווים אוטומטי"""
    
    call.play_message([
        ('text', 'ברוכים הבאים לדמו ניקוי טקסט!'),
        ('text', 'המערכת תנקה אוטומטיט תווים אסורים')
    ])
    
    # דוגמה 1: זיהוי דיבור עם ניקוי אוטומטי
    name = await call.read([
        ('text', 'אמור את שמך המלא')
    ], mode="stt", val_name="name", lang="he-IL")
    
    # הטקסט כבר נוקה אוטומטית מ:
    # - מילות מילוי (אה, אמ, נו וכו')
    # - תווים אסורים (גרשיים, נקודות וכו')
    
    call.play_message([
        ('text', f'שלום {name}!')
    ])
    
    # דוגמה 2: הודעות עם תווים "בעייתיים"
    problematic_text = 'טקסט עם "גרשיים" ונקודות... וקו & וגם \n שורה חדשה'
    
    call.play_message([
        ('text', 'עכשיו נשלח הודעה עם תווים בעייתיים'),
        ('text', problematic_text)  # יתוקן אוטומטית!
    ])
    
    # דוגמה 3: כתובת עם תווים מיוחדים
    address = await call.read([
        ('text', 'אמור את כתובתך')
    ], mode="stt", val_name="address", lang="he-IL")
    
    call.play_message([
        ('text', f'הכתובת שלך: {address}')  # נוקה אוטומטית
    ])
    
    # דוגמה 4: הצגת ההבדל
    call.play_message([
        ('text', 'הטקסט נוקה מגרשיים, נקודות הוחלפו בפסיקים'),
        ('text', 'שורות חדשות הוחלפו בפסיקים'),
        ('text', 'הכל מוכן לשליחה לימות!')
    ])
    
    call.hangup()

@flow.get("manual")
async def manual_cleaning_demo(call: Call):
    """דמו לניקוי ידני"""
    
    # בדיקה עם ניקוי מבוטל
    call.play_message([
        ('text', 'זה טקסט ללא ניקוי'),
    ], remove_invalid_chars=False)  # ללא ניקוי
    
    # בדיקה עם ניקוי מפורש
    call.play_message([
        ('text', 'זה טקסט עם ניקוי מפורש'),
    ], remove_invalid_chars=True)  # עם ניקוי
    
    call.hangup()

@flow.get("test")
async def test_cleaning(call: Call):
    """בדיקות ניקוי"""
    
    test_texts = [
        'טקסט עם "גרשיים"',
        'נקודות...רבות',
        'קו & מיוחד',
        'שורה\nחדשה',
        'רווחים    רבים',
        'פסיקים,,,רבים',
        'הכל ביחד: "שלום"...עולם & שורה\nחדשה!'
    ]
    
    for i, text in enumerate(test_texts, 1):
        call.play_message([
            ('text', f'בדיקה {i}'),
            ('text', text)  # יתוקן אוטומטית
        ])
    
    call.hangup()

@app.route("/yemot", methods=["GET", "POST"])
def yemot_entry():
    return Response(
        flow.handle_request(request.values.to_dict()),
        mimetype="text/plain; charset=utf-8"
    )

@app.route("/")
def index():
    return """
    <h1>🧹 Yemot Flow - Text Cleaning Demo</h1>
    
    <h2>🔗 נקודות כניסה:</h2>
    <ul>
        <li><a href="/yemot?ApiCallId=test1">דמו ניקוי אוטומטי</a></li>
        <li><a href="/yemot?ApiCallId=test2&ApiExtension=manual">דמו ניקוי ידני</a></li>
        <li><a href="/yemot?ApiCallId=test3&ApiExtension=test">בדיקות ניקוי</a></li>
    </ul>
    
    <h2>🛠️ מה המערכת מנקה:</h2>
    <ul>
        <li><strong>גרשיים ("):</strong> נמחקים לגמרי</li>
        <li><strong>נקודות (.):</strong> מוחלפים בפסיק</li>
        <li><strong>קו (&):</strong> מוחלף בפסיק</li>
        <li><strong>שורות חדשות:</strong> מוחלפים בפסיק</li>
        <li><strong>רווחים מרובים:</strong> מתכווצים לרווח אחד</li>
        <li><strong>פסיקים מרובים:</strong> מתכווצים לפסיק אחד</li>
    </ul>
    
    <p><b>כתובת לימות:</b> <code>/yemot</code></p>
    """

if __name__ == "__main__":
    print("🧹 מערכת ניקוי טקסט אוטומטית פועלת על פורט 5000!")
    print("📞 כתובת לימות: http://your-server:5000/yemot")
    app.run(host="0.0.0.0", port=5000, debug=True)