#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
דוגמה מינימליסטית לבדיקה מהירה

התקנה:
pip install yemot-flow flask

הרצה:
python minimal_example.py

כוון את ימות המשיח לכתובת: http://your-server-ip:5000/yemot
"""

from flask import Flask, request, Response
from yemot_flow import Flow

app = Flask(__name__)
flow = Flow(print_log=True)

@flow.get("")
def hello_world(call):
    """דוגמה פשוטה ביותר"""
    call.play_message([
        ("text", "שלום עולם!"),
        ("text", "זו דוגמה פשוטה לימות פלו"),
        ("text", "הקש 1 לשמיעה שוב או כל מקש אחר לסיום")
    ])
    
    call.read([("text", "הקש מקש")], max_digits=1)
    
    if call.params.get("Digits") == "1":
        call.goto("/")  # חזרה להתחלה
    else:
        call.play_message([("text", "להתראות!")])
        call.hangup()

@app.route("/yemot", methods=["GET", "POST"])
def yemot_endpoint():
    return Response(
        flow.handle_request(request.values.to_dict()),
        mimetype="text/plain; charset=utf-8"
    )

@app.route("/")
def index():
    return "<h1>Minimal Yemot Flow Example</h1><p>Running on /yemot</p>"

if __name__ == "__main__":
    print("🚀 Minimal example running on http://localhost:5000/yemot")
    app.run(host="0.0.0.0", port=5000, debug=True)