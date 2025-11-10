#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה בסיסית לשימוש ב-yemot-flow עם Flask

התקנה:
pip install yemot-flow flask

הרצה:
python flask_basic_example.py

כוון את ימות המשיח לכתובת: http://your-server-ip:5000/yemot
"""

from flask import Flask, request, Response
from yemot_flow import Flow

app = Flask(__name__)
flow = Flow(print_log=True)

@flow.get("")
def welcome(call):
    """שלוחה ראשית - ברוכים הבאים"""
    call.play_message([
        ("text", "שלום וברכה! ברוכים הבאים למערכת הדוגמה"),
        ("text", "להמשך לתפריט הראשי - הקש 1"),
        ("text", "לסיום השיחה - הקש 9")
    ])
    
    call.read([("text", "הקש את בחירתך")], max_digits=1, digits_allowed="19")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/main-menu")
    elif digits == "9":
        call.goto("/goodbye")
    else:
        call.play_message([("text", "בחירה לא חוקית")])
        call.goto("/")

@flow.get("main-menu")
def main_menu(call):
    """תפריט ראשי"""
    call.play_message([
        ("text", "תפריט ראשי"),
        ("text", "לקבלת מידע על החברה - הקש 1"),
        ("text", "לשירות לקוחות - הקש 2"), 
        ("text", "להשארת הודעה - הקש 3"),
        ("text", "לחזרה לתפריט הקודם - הקש 0")
    ])
    
    call.read([("text", "בחר מהתפריט")], max_digits=1, digits_allowed="0123")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/company-info")
    elif digits == "2":
        call.goto("/customer-service")
    elif digits == "3":
        call.goto("/leave-message")
    elif digits == "0":
        call.goto("/")

@flow.get("company-info")
def company_info(call):
    """מידע על החברה"""
    call.play_message([
        ("text", "אנחנו חברת טכנולוגיה המתמחה בפתרונות IVR"),
        ("text", "נוסדנו בשנת 2024 ואנו משרתים לקוחות בכל הארץ"),
        ("text", "להמשך - הקש כל מקש")
    ])
    
    call.read([("text", "הקש כל מקש להמשך")], max_digits=1)
    call.goto("/main-menu")

@flow.get("customer-service") 
def customer_service(call):
    """שירות לקוחות"""
    call.play_message([
        ("text", "שירות לקוחות"),
        ("text", "אנא השאר את פרטיך ונחזור אליך בהקדם"),
        ("text", "לרגע...")
    ])
    
    # כאן אפשר להוסיף לוגיקה של העברה לנציג או טופס פרטים
    call.play_message([("text", "כרגע כל הנציגים עסוקים. אנא נסה מאוחר יותר")])
    call.goto("/main-menu")

@flow.get("leave-message")
def leave_message(call):
    """השארת הודעה"""
    call.play_message([("text", "אנא השאר הודעה לאחר הצפצוף")])
    
    call.read(
        [("text", "החל הקלטה")], 
        mode="record",
        path="messages",
        file_name=f"message_{call.call_id}",
        save_on_hangup=True,
        max_length=60
    )
    
    call.play_message([("text", "תודה! ההודעה נקלטה בהצלחה")])
    call.goto("/main-menu")

@flow.get("goodbye")
def goodbye(call):
    """הודעת סיום"""
    call.play_message([
        ("text", "תודה שהתקשרת!"),
        ("text", "יום טוב ולהתראות")
    ])
    call.hangup()

@app.route("/yemot", methods=["GET", "POST"])
def yemot_entry():
    """נקודת הכניסה לקריאות מימות המשיח"""
    resp = flow.handle_request(request.values.to_dict())
    return Response(resp, mimetype="text/plain; charset=utf-8")

@app.route("/")
def index():
    """דף בית פשוט"""
    return """
    <h1>Yemot Flow - Flask Example</h1>
    <p>המערכת פועלת!</p>
    <p>כוון את ימות המשיח לכתובת: <code>/yemot</code></p>
    """

if __name__ == "__main__":
    print("🚀 מפעיל שרת Flask על פורט 5000")
    print("📞 כוון את ימות המשיח לכתובת: http://your-server-ip:5000/yemot")
    app.run(host="0.0.0.0", port=5000, debug=True)