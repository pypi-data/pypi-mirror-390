#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
הדרך החדשה והנכונה - async/await כמו Node.js!
"""

from flask import Flask, request, Response
from src.yemot_flow import Flow, Call
app = Flask(__name__)
flow = Flow(print_log=True)

@flow.get("")
async def welcome(call: Call):
    """נקודת בדיקה פשוטה - הדרך הפשוטה שביקשת!"""
    
    # הדרך הפשוטה - בדיוק כמו שרצית!
    print("🎯 מתחיל רצף קלטים פשוט")
    
    test_input1 = await call.read([('text', 'אנא הקש 1')], val_name="test_input1", max_digits=1, digits_allowed="1")
    print(f"✅ קיבלתי קלט 1: {test_input1}")
    
    test_input2 = await call.read([('text', 'אנא הקש 2')], val_name="test_input2", max_digits=1, digits_allowed="2")  
    print(f"✅ קיבלתי קלט 2: {test_input2}")
    
    test_input3 = await call.read([('text', 'אנא הקש 3')], val_name="test_input3", max_digits=1, digits_allowed="3")
    print(f"✅ קיבלתי קלט 3: {test_input3}")
    
    print(f"🎉 סיימתי! כל הקלטים: {test_input1}, {test_input2}, {test_input3}")
    
    # הודעה אחרונה וחזרה לתפריט
    call.play_message([('text', f'תודה על הבדיקה! קלטת: {test_input1}, {test_input2}, {test_input3}')])
    call.goto("")


@app.route("/yemot", methods=["GET", "POST"])
def yemot_entry():
    """נקודת הכניסה לקריאות מימות המשיח"""
    return Response(
        flow.handle_request(request.values.to_dict()),
        mimetype="text/plain; charset=utf-8"
    )
@app.route("/")
def index():
    return """
    <h1>🤖 Yemot Flow + AI - המערכת החכמה!</h1>
    
    <h2>✨ תכונות מתקדמות:</h2>
    <ul>
        <li><strong>🔄 המשך שיחה</strong> - ממשיך מהשיחה הקודמת עם העוזר</li>
        <li><strong>🆕 שיחה חדשה</strong> - מתחיל שיחה טרייה</li>
        <li><strong>📋 סיכום האחרון</strong> - סקירה של הנושא הקודם</li>
    </ul>
    
    <h2>🧠 העוזר החכם המתקדם:</h2>
    <p><strong>שיחה רציפה</strong> - המערכת זוכרת וממשיכה שיחות!</p>
    <ul>
        <li><strong>זיכרון שיחות</strong> - זוכר מה שדיברתם</li>
        <li><strong>שאלות המשך</strong> - מציע המשכים רלוונטיים</li>
        <li><strong>סיכומים</strong> - מסכם נושאים שנדונו</li>
        <li><strong>הקשר שמור</strong> - כל שיחה חדשה מתבססת על הקודמת</li>
    </ul>
    
    <h2>📞 בדיקות:</h2>
    <ul>
        <li><a href="/yemot?ApiCallId=test123">תפריט ראשי</a></li>
        <li><a href="/yemot?ApiCallId=test456&ApiExtension=ai_chat">עוזר חכם</a></li>
        <li><a href="/yemot?ApiCallId=test789&ApiExtension=sales">מכירות</a></li>
    </ul>
    
    <p><strong>📍 נתיב:</strong> <code>/yemot</code></p>
    <p><strong>⚠️ דרישה:</strong> Codex CLI מותקן ומחובר לחשבון ChatGPT Plus</p>
    """

if __name__ == "__main__":
    
    # בדיקה מהירה של Codex בהפעלה
    
    app.run(host="0.0.0.0", port=5011, debug=True)