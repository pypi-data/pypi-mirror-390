#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה מתקדמת - מערכת הזמנות למסעדה

התכונות המודגמות:
- תפריטים מורכבים עם מעבר בין רמות
- איסוף פרטי לקוח (טלפון, כתובת)
- חישובי מחירים
- אישור הזמנה
- שמירת נתונים (במציאות - למסד נתונים)

התקנה:
pip install yemot-flow flask

הרצה:
python restaurant_ordering_system.py
"""

from flask import Flask, request, Response
from yemot_flow import Flow
import json
import os
from datetime import datetime

app = Flask(__name__)
flow = Flow(print_log=True, timeout=60000)  # דקה timeout

# תפריט המסעדה (במציאות יבוא ממסד נתונים)
MENU = {
    "main_dishes": {
        "name": "מנות עיקריות",
        "items": {
            "1": {"name": "שניצל עוף", "price": 45},
            "2": {"name": "סטייק בקר", "price": 85},
            "3": {"name": "דג סלמון", "price": 65},
            "4": {"name": "פסטה ברוטב עגבניות", "price": 35}
        }
    },
    "appetizers": {
        "name": "מנות ראשונות", 
        "items": {
            "1": {"name": "חומוס עם פיתה", "price": 18},
            "2": {"name": "סלט יווני", "price": 25},
            "3": {"name": "מרק בצל", "price": 22}
        }
    },
    "desserts": {
        "name": "קינוחים",
        "items": {
            "1": {"name": "טירמיסו", "price": 28},
            "2": {"name": "עוגת שוקולד", "price": 32},
            "3": {"name": "פנקוק", "price": 24}
        }
    }
}

def save_order(order_data):
    """שמירת הזמנה לקובץ (במציאות - למסד נתונים)"""
    orders_dir = "orders"
    os.makedirs(orders_dir, exist_ok=True)
    
    filename = f"{orders_dir}/order_{order_data['call_id']}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(order_data, f, ensure_ascii=False, indent=2)
    
    return filename

def get_order_total(items):
    """חישוב סכום ההזמנה"""
    total = 0
    for category, category_items in items.items():
        for item_id, quantity in category_items.items():
            if category in MENU and item_id in MENU[category]["items"]:
                price = MENU[category]["items"][item_id]["price"]
                total += price * quantity
    return total

@flow.get("")
def welcome(call):
    """עמוד פתיחה"""
    # אתחול הזמנה חדשה
    if not hasattr(call, 'order'):
        call.order = {
            "items": {"main_dishes": {}, "appetizers": {}, "desserts": {}},
            "customer": {},
            "total": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    call.play_message([
        ("text", "ברוכים הבאים למסעדת הטעמים"),
        ("text", "למעבר להזמנה - הקש 1"),
        ("text", "לשמיעת שעות פעילות - הקש 2"),
        ("text", "לכתובת המסעדה - הקש 3")
    ])
    
    call.read([("text", "בחר אפשרות")], max_digits=1, digits_allowed="123")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/order-menu")
    elif digits == "2":
        call.goto("/hours")
    elif digits == "3":
        call.goto("/address")

@flow.get("hours")
def opening_hours(call):
    """שעות פעילות"""
    call.play_message([
        ("text", "שעות הפעילות שלנו"),
        ("text", "ראשון עד חמישי מ12:00 עד 23:00"),
        ("text", "שישי מ12:00 עד 15:00"),
        ("text", "מוצאי שבת מ21:00 עד 24:00"),
        ("text", "לחזרה לתפריט הראשי - הקש כל מקש")
    ])
    
    call.read([("text", "הקש כל מקש")], max_digits=1)
    call.goto("/")

@flow.get("address")
def restaurant_address(call):
    """כתובת המסעדה"""
    call.play_message([
        ("text", "כתובתנו: רחוב הרצל 25 תל אביב"),
        ("text", "טלפון הזמנות: 03-1234567"),
        ("text", "לחזרה - הקש כל מקש")
    ])
    
    call.read([("text", "הקש כל מקש")], max_digits=1)
    call.goto("/")

@flow.get("order-menu")
def order_main_menu(call):
    """תפריט הזמנה ראשי"""
    call.play_message([
        ("text", "תפריט הזמנות"),
        ("text", "למנות עיקריות - הקש 1"),
        ("text", "למנות ראשונות - הקש 2"), 
        ("text", "לקינוחים - הקש 3"),
        ("text", "לסיכום ההזמנה - הקש 8"),
        ("text", "לביטול - הקש 9")
    ])
    
    call.read([("text", "בחר קטגוריה")], max_digits=1, digits_allowed="12389")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/menu/main_dishes")
    elif digits == "2":
        call.goto("/menu/appetizers")
    elif digits == "3":
        call.goto("/menu/desserts")
    elif digits == "8":
        call.goto("/order-summary")
    elif digits == "9":
        call.goto("/cancel-order")

@flow.get("menu/main_dishes")
def main_dishes_menu(call):
    """תפריט מנות עיקריות"""
    display_category_menu(call, "main_dishes")

@flow.get("menu/appetizers")
def appetizers_menu(call):
    """תפריט מנות ראשונות"""
    display_category_menu(call, "appetizers")

@flow.get("menu/desserts") 
def desserts_menu(call):
    """תפריט קינוחים"""
    display_category_menu(call, "desserts")

def display_category_menu(call, category):
    """הצגת תפריט לפי קטגוריה"""
    menu_data = MENU[category]
    
    messages = [("text", menu_data["name"])]
    
    for item_id, item_info in menu_data["items"].items():
        messages.append(("text", f"להזמנת {item_info['name']} במחיר {item_info['price']} שקל - הקש {item_id}"))
    
    messages.append(("text", "לחזרה לתפריט הקודם - הקש 0"))
    
    call.play_message(messages)
    
    allowed_digits = "0" + "".join(menu_data["items"].keys())
    call.read([("text", "בחר מנה")], max_digits=1, digits_allowed=allowed_digits)
    
    digits = call.params.get("Digits")
    if digits == "0":
        call.goto("/order-menu")
    elif digits in menu_data["items"]:
        # שמירת הבחירה במשתנה זמני
        call.selected_category = category
        call.selected_item = digits
        call.goto("/select-quantity")

@flow.get("select-quantity")
def select_quantity(call):
    """בחירת כמות"""
    category = getattr(call, 'selected_category', '')
    item_id = getattr(call, 'selected_item', '')
    
    if not category or not item_id:
        call.goto("/order-menu")
        return
    
    item_info = MENU[category]["items"][item_id]
    
    call.play_message([
        ("text", f"בחרת {item_info['name']}"),
        ("text", f"מחיר יחידה: {item_info['price']} שקל"),
        ("text", "כמה יחידות תרצה? הקש מספר מ1 עד 9")
    ])
    
    call.read([("text", "הקש כמות")], max_digits=1, digits_allowed="123456789")
    
    quantity = int(call.params.get("Digits", "0"))
    if quantity > 0:
        # הוספה להזמנה
        if not hasattr(call, 'order'):
            call.order = {"items": {"main_dishes": {}, "appetizers": {}, "desserts": {}}}
        
        call.order["items"][category][item_id] = quantity
        
        total_price = item_info['price'] * quantity
        call.play_message([
            ("text", f"נוסף להזמנה: {quantity} {item_info['name']}"),
            ("text", f"סכום: {total_price} שקל"),
            ("text", "להמשך הזמנה - הקש 1"),
            ("text", "לסיום - הקש 2")
        ])
        
        call.read([("text", "המשך או סיים")], max_digits=1, digits_allowed="12")
        
        next_action = call.params.get("Digits")
        if next_action == "1":
            call.goto("/order-menu")
        else:
            call.goto("/order-summary")

@flow.get("order-summary")
def order_summary(call):
    """סיכום הזמנה"""
    if not hasattr(call, 'order') or not any(call.order["items"].values()):
        call.play_message([("text", "לא נבחרו מנות. חוזר לתפריט")])
        call.goto("/order-menu")
        return
    
    # חישוב סכום כולל
    total = 0
    messages = [("text", "סיכום ההזמנה שלך:")]
    
    for category, items in call.order["items"].items():
        if items:
            category_name = MENU[category]["name"]
            messages.append(("text", category_name))
            
            for item_id, quantity in items.items():
                item_info = MENU[category]["items"][item_id]
                item_total = item_info["price"] * quantity
                total += item_total
                
                messages.append(("text", f"{quantity} {item_info['name']} - {item_total} שקל"))
    
    call.order["total"] = total
    messages.extend([
        ("text", f"סכום כולל: {total} שקל"),
        ("text", "לאישור ההזמנה - הקש 1"),
        ("text", "לחזרה לעריכה - הקש 2"),
        ("text", "לביטול - הקש 9")
    ])
    
    call.play_message(messages)
    call.read([("text", "בחר פעולה")], max_digits=1, digits_allowed="129")
    
    digits = call.params.get("Digits")
    if digits == "1":
        call.goto("/customer-details")
    elif digits == "2":
        call.goto("/order-menu")
    elif digits == "9":
        call.goto("/cancel-order")

@flow.get("customer-details")
def get_customer_details(call):
    """קבלת פרטי לקוח"""
    call.play_message([
        ("text", "כדי להשלים את ההזמנה נדרשים פרטיך"),
        ("text", "אנא הקלד את מספר הטלפון שלך ולחץ סולמית")
    ])
    
    call.read(
        [("text", "הקלד טלפון ולחץ סולמית")], 
        max_digits=15,
        min_digits=9,
        replace_char="#",
        sec_wait=15
    )
    
    phone = call.params.get("Digits", "")
    if len(phone) >= 9:
        call.order["customer"]["phone"] = phone
        call.goto("/get-address")
    else:
        call.play_message([("text", "מספר לא תקין. נסה שוב")])
        call.goto("/customer-details")

@flow.get("get-address")
def get_address(call):
    """קבלת כתובת"""
    call.play_message([("text", "אנא הקלט את כתובתך לאחר הצפצוף")])
    
    call.read(
        [("text", "התחל הקלטה")],
        mode="record",
        path="addresses",
        file_name=f"address_{call.call_id}",
        max_length=30,  # 30 שניות
        save_on_hangup=True
    )
    
    call.order["customer"]["address_file"] = f"address_{call.call_id}"
    call.goto("/confirm-order")

@flow.get("confirm-order")
def confirm_order(call):
    """אישור הזמנה סופי"""
    phone = call.order["customer"].get("phone", "")
    total = call.order.get("total", 0)
    
    call.play_message([
        ("text", "אישור הזמנה"),
        ("text", f"טלפון: {phone}"),
        ("text", f"סכום כולל: {total} שקל"),
        ("text", "ההזמנה תגיע תוך 45 דקות"),
        ("text", "לאישור סופי - הקש 1"),
        ("text", "לביטול - הקש 2")
    ])
    
    call.read([("text", "אשר או בטל")], max_digits=1, digits_allowed="12")
    
    digits = call.params.get("Digits")
    if digits == "1":
        # שמירת ההזמנה
        call.order["call_id"] = call.call_id
        call.order["status"] = "confirmed"
        call.order["confirmed_at"] = datetime.now().isoformat()
        
        order_file = save_order(call.order)
        order_number = call.call_id[-6:]  # 6 ספרות אחרונות
        
        call.play_message([
            ("text", "ההזמנה אושרה בהצלחה!"),
            ("text", f"מספר הזמנה: {order_number}"),
            ("text", "תודה שהזמנת אצלנו!")
        ])
        call.hangup()
    else:
        call.goto("/cancel-order")

@flow.get("cancel-order")
def cancel_order(call):
    """ביטול הזמנה"""
    call.play_message([
        ("text", "ההזמנה בוטלה"),
        ("text", "תודה שפנית אלינו!"),
        ("text", "נשמח לראותך בפעם הבאה")
    ])
    call.hangup()

@app.route("/yemot", methods=["GET", "POST"])
def yemot_entry():
    """נקודת כניסה לימות המשיח"""
    resp = flow.handle_request(request.values.to_dict())
    return Response(resp, mimetype="text/plain; charset=utf-8")

@app.route("/")
def index():
    return """
    <h1>🍽️ מערכת הזמנות למסעדה</h1>
    <p>מערכת הזמנות מתקדמת עם yemot-flow</p>
    <h3>תכונות:</h3>
    <ul>
        <li>תפריט מנות מלא</li>
        <li>בחירת כמויות</li>
        <li>חישוב מחירים</li>
        <li>איסוף פרטי לקוח</li>
        <li>אישור הזמנה</li>
    </ul>
    """

@app.route("/orders")
def list_orders():
    """רשימת הזמנות (לניהול)"""
    orders_dir = "orders"
    if not os.path.exists(orders_dir):
        return {"orders": []}
    
    orders = []
    for filename in os.listdir(orders_dir):
        if filename.endswith('.json'):
            with open(f"{orders_dir}/{filename}", 'r', encoding='utf-8') as f:
                order = json.load(f)
                orders.append(order)
    
    return {"orders": orders}

if __name__ == "__main__":
    print("🍽️ מפעיל מערכת הזמנות למסעדה")
    print("📞 כוון את ימות המשיח לכתובת: http://your-server-ip:5000/yemot")
    print("💻 רשימת הזמנות: http://localhost:5000/orders")
    
    app.run(host="0.0.0.0", port=5000, debug=True)