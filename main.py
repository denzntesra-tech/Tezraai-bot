import os
import logging
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

app = Flask(__name__)
GEMINI_KEY = os.environ["GEMINI_KEY"]
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# DAWR 1-NA: Hei hi i customer hmasa ber tur info
DAWR_LIST = {
    "TUNA_I_BOT_TOKEN_DAH_LA": {
        "dawr_hming": "Demo Dawr Aizawl",
        "neitu_no": "9862xxxxxx",  # Dawr neitu WhatsApp no
        "products": {
            "sana": {"man": "₹2500", "stock": 10},
            "t-shirt mizo": {"man": "₹800", "stock": 20},
            "pheikhawk": {"man": "₹1800", "stock": 5}
        }
    }
}

def create_prompt(bot_token, user_text):
    dawr = DAWR_LIST.get(bot_token)
    if not dawr: return "Setup la zo lo, neitu be rawh."
    
    return f"""I hming chu Tesra. {dawr['dawr_hming']} dawr AI assistant i ni.
Dawr neitu phone: {dawr['neitu_no']}
Product: {dawr['products']}

DAN:
1. Mizo tawng chauh hmang
2. Customer in product a zawh chuan man leh stock sawi la
3. Order duh chuan: "I hming leh phone no min lo pe la, kan lo call ang che ka pi/ka pu" ti rawh
4. Tawngkam: polite, tawi, fiamthu hret

Customer: {user_text}
Tesra:"""

def send_telegram(bot_token, chat_id, text):
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                 json={"chat_id": chat_id, "text": text})

@app.route("/<bot_token>", methods=["POST"])
def webhook(bot_token):
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        
        prompt = create_prompt(bot_token, text)
        reply = model.generate_content(prompt).text
        
        send_telegram(bot_token, chat_id, reply)
        
        # Dawr neitu hnenah order notification thawn belh duh chuan hetah
    return {"ok": True}

@app.route("/")
def home(): return "Tesra Multi-Dawr running"
