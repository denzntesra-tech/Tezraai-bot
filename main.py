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
def send_typing(chat_id):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction",
                 json={"chat_id": chat_id, "action": "typing"})
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

DAN KHIRH TAK:
1. Mizo tawng chauh hmang. Sap tawng hman phal lo.
2. GRAMMAR RULE: I thumal hmasa berah "Chibai!" ti la, a tawp berah "ka puih theih ang che?" ti ZIAH rawh.
   DIK: "Chibai!... ka puih theih ang che?"
   DIK LO: "ka puih theih che ang" - HEI HI HMANG SUH
3. Customer in product a zawh chuan: "Aw, kan nei e! [Product] man chu ₹[price] a ni e. Stock [stock] kan la nei. I order duh em?"
4. Order duh chuan: "I hming leh phone number min lo pe la, kan lo call ang che"
5. "Ka pu/ka pi" tih hi conversation ah vawi 1 chiah hmang rawh. Message tin ah hmang suh.
6. Tawngkam: polite, tawi, dawrkai pangngai ang

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

        send_typing(chat_id)  # Gemini call hmaah hian dah rawh
        
        prompt = create_prompt(text)
        try:
            reply = model.generate_content(prompt).text
        except Exception as e:
            if "429" in str(e):
                reply = "Tunah chuan ka buai deuh a, minute 1 hnuah min lo zawt leh mai dawn em ni? Ka inthlahrung hle mai"
            else:
                reply = "Tihpalh, ka system a buai deuh. Nakkinah min lo be leh dawn nia."
        
        send_telegram(chat_id, reply)
        
    return {"ok": True}

@app.route("/")
def home(): return "Tesra Multi-Dawr running"
