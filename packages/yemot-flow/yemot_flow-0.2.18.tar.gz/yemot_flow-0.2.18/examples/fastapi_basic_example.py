#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה בסיסית לשימוש ב-yemot-flow עם FastAPI

התקנה:
pip install yemot-flow fastapi uvicorn

הרצה:
uvicorn fastapi_basic_example:app --host 0.0.0.0 --port 8000 --reload

כוון את ימות המשיח לכתובת: http://your-server-ip:8000/yemot
"""

from fastapi import FastAPI, Request, Response
from yemot_flow import Flow

app = FastAPI(
    title="Yemot Flow FastAPI Example",
    description="דוגמה לשימוש בספריית yemot-flow עם FastAPI",
    version="1.0.0"
)

flow = Flow(print_log=True, timeout=45000)  # 45 שניות timeout

@flow.get("")
def welcome(call):
    """דף הבית - ברוכים הבאים"""
    call.play_message([
        ("text", "ברוכים הבאים למערכת FastAPI המתקדמת"),
        ("text", "למידע על השירותים שלנו - הקש 1"),
        ("text", "לתמיכה טכנית - הקש 2"),
        ("text", "לביטול - הקש כוכבית")
    ])
    
    call.read(
        [("text", "אנא בחר אפשרות")], 
        max_digits=1, 
        digits_allowed="12*",
        sec_wait=10
    )
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/services")
    elif digits == "2":
        call.goto("/support")
    elif digits == "*":
        call.goto("/cancel")
    else:
        call.play_message([("text", "לא הובנה בחירתך")])
        call.goto("/")

@flow.get("services")
def services_menu(call):
    """תפריט שירותים"""
    call.play_message([
        ("text", "שירותי החברה"),
        ("text", "לפיתוח אפליקציות - הקש 1"),
        ("text", "לייעוץ טכנולוגי - הקש 2"),
        ("text", "למערכות IVR - הקש 3"),
        ("text", "לחזרה - הקש 0")
    ])
    
    call.read([("text", "בחר שירות")], max_digits=1, digits_allowed="0123")
    
    digits = call.params.get("Digits")
    routes = {
        "1": "/service-development",
        "2": "/service-consulting", 
        "3": "/service-ivr",
        "0": "/"
    }
    
    if digits in routes:
        call.goto(routes[digits])
    else:
        call.goto("/services")

@flow.get("service-development")
def service_development(call):
    """שירות פיתוח"""
    call.play_message([
        ("text", "פיתוח אפליקציות מותאמות אישית"),
        ("text", "אנו מפתחים אפליקציות ווב ומובייל מתקדמות"),
        ("text", "לקביעת פגישה - הקש 1"),
        ("text", "למידע נוסף - הקש 2"),
        ("text", "לחזרה - הקש 0")
    ])
    
    call.read([("text", "מה תרצה לעשות")], max_digits=1, digits_allowed="012")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/schedule-meeting")
    elif digits == "2":
        call.goto("/more-info")
    elif digits == "0":
        call.goto("/services")

@flow.get("service-consulting")
def service_consulting(call):
    """שירות ייעוץ"""
    call.play_message([
        ("text", "ייעוץ טכנולוגי מקצועי"),
        ("text", "אנו מספקים ייעוץ בתחומי הטכנולוגיה המתקדמים ביותר"),
        ("text", "לייעוץ חינם - הקש 1"),
        ("text", "לחזרה - הקש 0")
    ])
    
    call.read([("text", "בחר אפשרות")], max_digits=1, digits_allowed="01")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/free-consultation")
    elif digits == "0":
        call.goto("/services")

@flow.get("service-ivr") 
def service_ivr(call):
    """שירות IVR"""
    call.play_message([
        ("text", "פתרונות IVR מתקדמים"),
        ("text", "בניית מערכות מענה אוטומטי חכמות ויעילות"),
        ("text", "כמו המערכת שאתה מקשיב לה כרגע!"),
        ("text", "לדוגמה - הקש 1"), 
        ("text", "לחזרה - הקש 0")
    ])
    
    call.read([("text", "בחר אפשרות")], max_digits=1, digits_allowed="01")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/ivr-demo")
    elif digits == "0":
        call.goto("/services")

@flow.get("support")
def support_menu(call):
    """תפריט תמיכה"""
    call.play_message([
        ("text", "תמיכה טכנית"),
        ("text", "לדיווח על תקלה - הקש 1"),
        ("text", "לשאלות כלליות - הקש 2"),
        ("text", "לחזרה - הקש 0")
    ])
    
    call.read([("text", "איך נוכל לעזור")], max_digits=1, digits_allowed="012")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/report-issue")
    elif digits == "2":
        call.goto("/general-questions")
    elif digits == "0":
        call.goto("/")

@flow.get("schedule-meeting")
def schedule_meeting(call):
    """קביעת פגישה"""
    call.play_message([
        ("text", "קביעת פגישה"),
        ("text", "אנא השאר את הפרטים שלך: שם, טלפון ונושא הפגישה")
    ])
    
    call.read(
        [("text", "התחל הקלטה לאחר הצפצוף")],
        mode="record",
        path="meetings",
        file_name=f"meeting_request_{call.call_id}",
        max_length=120,  # 2 דקות
        save_on_hangup=True
    )
    
    call.play_message([
        ("text", "תודה! פרטיך נקלטו"),
        ("text", "נחזור אליך תוך 24 שעות")
    ])
    call.goto("/")

@flow.get("ivr-demo")
def ivr_demo(call):
    """דוגמת IVR אינטראקטיבית"""
    call.play_message([
        ("text", "זוהי דוגמה לאפשרויות IVR מתקדמות"),
        ("text", "אמור את המילה 'שלום' וננסה לזהות אותה")
    ])
    
    call.read(
        [("text", "דבר עכשיו")],
        mode="stt",  # Speech to Text
        lang="he-IL",
        quiet_max=3,
        length_max=10
    )
    
    recognized_text = call.params.get("Digits", "").lower()
    if "שלום" in recognized_text:
        call.play_message([("text", "מצוין! זיהינו את המילה שלום")])
    else:
        call.play_message([("text", "לא הצלחנו לזהות. נסה שוב")])
    
    call.goto("/services")

@flow.get("report-issue")
def report_issue(call):
    """דיווח תקלה"""
    call.play_message([
        ("text", "דיווח תקלה"),
        ("text", "אנא תאר את התקלה בפירוט")
    ])
    
    call.read(
        [("text", "התחל תיאור התקלה")],
        mode="record", 
        path="issues",
        file_name=f"issue_{call.call_id}",
        max_length=180,  # 3 דקות
        save_on_hangup=True
    )
    
    call.play_message([
        ("text", "התקלה תועברה למחלקה הטכנית"),
        ("text", "מספר הפנייה שלך הוא"),
        ("digits", call.call_id[-4:])  # 4 ספרות אחרונות
    ])
    call.goto("/")

@flow.get("cancel")
def cancel(call):
    """ביטול השיחה"""
    call.play_message([("text", "השיחה מבוטלת. תודה ולהתראות")])
    call.hangup()

@app.api_route("/yemot", methods=["GET", "POST"])
async def yemot_endpoint(request: Request):
    """נקודת הכניסה לקריאות מימות המשיח"""
    # קבלת הפרמטרים מ-GET או POST
    if request.method == "POST":
        form = await request.form()
        params = dict(form)
    else:
        params = dict(request.query_params)
    
    # עיבוד הבקשה
    response_text = flow.handle_request(params)
    
    return Response(
        content=response_text,
        media_type="text/plain; charset=utf-8"
    )

@app.get("/")
def root():
    """דף בית עם מידע על ה-API"""
    return {
        "message": "Yemot Flow FastAPI Example",
        "status": "running",
        "yemot_endpoint": "/yemot",
        "docs": "/docs"
    }

@app.get("/status")
def status():
    """סטטוס המערכת"""
    return {
        "active_calls": len(flow.active_calls),
        "timeout_ms": flow.timeout_ms,
        "routes": list(flow.routes.keys())
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 מפעיל שרת FastAPI על פורט 8000")
    print("📞 כוון את ימות המשיח לכתובת: http://your-server-ip:8000/yemot") 
    print("📚 תיעוד API זמין בכתובת: http://localhost:8000/docs")
    
    uvicorn.run(
        "fastapi_basic_example:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )