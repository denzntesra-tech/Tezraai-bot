import os
import logging
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)
GEMINI_KEY = os.environ["GEMINI_KEY"]
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Railway Variables ah i dah tawh: TELEGRAM_TO...
BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]  # I variable hming dik tak dah rawh

# Dawr info chauh dah. Token chu code ah lang tawh lo
DAWR_INFO = {
    "dawr_hming": "Demo Dawr Aizawl",
    "neitu_no": "9862xxxxxx",
    "products": {
        "sana": {"man": "₹2500", "stock": 10},
        "t-shirt mizo": {"man": "₹800", "stock": 20},
        "pheikhawk": {"man": "₹1800", "stock": 5}
    }
}

def create_prompt(user_text):
    return f"""I hming chu Tesra. {DAWR_INFO['dawr_hming']} dawr AI assistant i ni.
Dawr neitu phone: {DAWR_INFO['neitu_no']}
Product: {DAWR_INFO['products']}

DAN:
1. Mizo tawng chauh hmang
2. Customer in product a zawh chuan man leh stock sawi la
3. Order duh chuan: "I hming leh phone no min lo pe la, kan lo call ang che ka pi/ka pu" ti rawh
4. Tawngkam: polite, tawi, fiamthu hret

Customer: {user_text}
Tesra:"""

def send_telegram(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                 json={"chat_id": chat_id, "text": text})

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        
        prompt = create_prompt(text)
        reply = model.generate_content(prompt).text
        
        send_telegram(chat_id, reply)
    return {"ok": True}

@app.route("/")
def home(): return "Tesra Multi-Dawr running"
