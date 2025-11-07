#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה עדכנית - עברית ללא URL encoding כברירת מחדל

גרסה 0.1.7 - עכשיו עברית מוצגת בצורה רגילה ללא צורך בפרמטרים נוספים!
"""

from flask import Flask, request, Response
from yemot_flow import Flow

app = Flask(__name__)
flow = Flow(print_log=True)

@flow.get("")
def welcome(call):
    """עכשיו הקוד פשוט ונקי - עברית עובדת מיד!"""
    
    # 🎉 עכשיו זה עובד ישירות ללא פרמטרים נוספים!
    call.play_message([
        ('text', 'שלום וברכה! ברוכים הבאים למערכת החדשה'),
        ('text', 'עכשיו העברית מוצגת בצורה נכונה'),
        ('text', 'למידע על החברה - הקש 1'),
        ('text', 'לשירות לקוחות - הקש 2'),
        ('text', 'להשארת הודעה - הקש 3')
    ])
    
    # גם read עובד עכשיו עם עברית ללא בעיות
    call.read(
        [('text', 'אנא הקש את בחירתך')],
        val_name="Digits",
        max_digits=1,
        digits_allowed="123",
        sec_wait=10
    )
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/company-info")
    elif digits == "2":
        call.goto("/customer-service")
    elif digits == "3":
        call.goto("/leave-message")
    else:
        call.play_message([('text', 'בחירה לא חוקית. נסה שוב')])
        call.goto("/")

@flow.get("company-info")
def company_info(call):
    """מידע החברה עם טקסט עברי נקי"""
    call.play_message([
        ('text', 'אנחנו חברת yemot-flow'),
        ('text', 'מתמחים בפיתוח מערכות IVR בפייתון'),
        ('text', 'הספרייה מאפשרת כתיבת קוד פשוט ונקי'),
        ('text', 'עכשיו גם עם תמיכה מלאה בעברית!')
    ])
    
    call.read([('text', 'הקש כל מקש לחזרה')], max_digits=1)
    call.goto("/")

@flow.get("customer-service")
def customer_service(call):
    """שירות לקוחות"""
    call.play_message([
        ('text', 'שירות לקוחות'),
        ('text', 'לדיווח בעיה טכנית - הקש 1'),
        ('text', 'לשאלות כלליות - הקש 2'),
        ('text', 'לחזרה לתפריט הראשי - הקש 0')
    ])
    
    call.read([('text', 'בחר אפשרות')], max_digits=1, digits_allowed="012")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/tech-support")
    elif digits == "2":
        call.goto("/general-questions") 
    elif digits == "0":
        call.goto("/")

@flow.get("tech-support")
def tech_support(call):
    """תמיכה טכנית"""
    call.play_message([
        ('text', 'תמיכה טכנית'),
        ('text', 'אנא תאר את הבעיה הטכנית שלך'),
        ('text', 'ההקלטה תתחיל לאחר הצפצוף')
    ])
    
    call.read(
        [('text', 'התחל לתאר את הבעיה')],
        mode="record",
        path="tech_issues",
        file_name=f"issue_{call.call_id}",
        max_length=120  # 2 דקות
    )
    
    call.play_message([
        ('text', 'תודה! הבעיה נרשמה במערכת'),
        ('text', 'מספר הפנייה שלך:'),
        ('digits', call.call_id[-6:]),  # 6 ספרות אחרונות
        ('text', 'נחזור אליך בהקדם')
    ])
    call.goto("/")

@flow.get("general-questions") 
def general_questions(call):
    """שאלות כלליות"""
    call.play_message([
        ('text', 'שאלות כלליות'),
        ('text', 'לשאלות על התחיל - הקש 1'),
        ('text', 'לשאלות על תמחור - הקש 2'),
        ('text', 'לשאלות טכניות - הקש 3'),
        ('text', 'לחזרה - הקש 0')
    ])
    
    call.read([('text', 'בחר נושא')], max_digits=1, digits_allowed="0123")
    
    digits = call.params.get("Digits")
    topics = {
        "1": "להתחיל עם yemot-flow פשוט התקן: pip install yemot-flow",
        "2": "הספרייה חינמית לחלוטין ובקוד פתוח!",
        "3": "לתמיכה טכנית בקר ב-GitHub או פתח issue",
        "0": None  # חזרה
    }
    
    if digits == "0":
        call.goto("/")
    elif digits in topics:
        call.play_message([('text', topics[digits])])
        call.read([('text', 'הקש כל מקש לחזרה')], max_digits=1)
        call.goto("/general-questions")

@flow.get("leave-message") 
def leave_message(call):
    """השארת הודעה כללית"""
    call.play_message([
        ('text', 'השארת הודעה'),
        ('text', 'אנא השאר את הודעתך לאחר הצפצוף'),
        ('text', 'זכור לציין את שמך ומספר הטלפון שלך')
    ])
    
    call.read(
        [('text', 'התחל הקלטת ההודעה')],
        mode="record",
        path="messages", 
        file_name=f"message_{call.call_id}",
        max_length=90,  # דקה וחצי
        save_on_hangup=True
    )
    
    call.play_message([
        ('text', 'תודה רבה!'),
        ('text', 'ההודעה שלך נקלטה בהצלחה'),
        ('text', 'נשמח לחזור אליך בהקדם')
    ])
    call.hangup()

@app.route("/yemot", methods=["GET", "POST"])
def yemot_entry():
    """נקודת כניסה לימות המשיח"""
    response = flow.handle_request(request.values.to_dict())
    return Response(response, mimetype="text/plain; charset=utf-8")

@app.route("/")
def index():
    return """
    <h1>🎉 yemot-flow v0.1.7</h1>
    <h2>עברית ללא URL encoding!</h2>
    
    <h3>מה חדש:</h3>
    <ul>
        <li>✅ עברית מוצגת בצורה נכונה כברירת מחדל</li>
        <li>✅ אין צורך להוסיف url_encode=False</li>
        <li>✅ קוד פשוט ונקי יותר</li>
        <li>✅ תמיכה מלאה בכל התכונות</li>
    </ul>
    
    <h3>דוגמת קוד:</h3>
    <pre><code>call.play_message([('text', 'שלום עולם!')])  # עובד מיד!</code></pre>
    
    <p><strong>API Endpoint:</strong> <code>/yemot</code></p>
    """

if __name__ == "__main__":
    print("🎉 yemot-flow v0.1.7 - עברית ללא URL encoding!")
    print("📞 כוון את ימות המשיח ל: http://localhost:5000/yemot")
    print("✨ עכשיו הכל פועל בצורה טבעית!")
    
    app.run(host="0.0.0.0", port=5000, debug=True)