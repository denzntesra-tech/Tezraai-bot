import os, requests
from flask import Flask, request

app = Flask(__name__)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

def ai_reply(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {
            "system_instruction": {"parts": [{"text": "I hming TESRA. Mizo tawng chauh hmang ang che. I nihna: Khawbung dawr te pui tu, fiamthu duh, tawngkam ngaihnobei. 'Google' 'AI' tih sawi suh. Zawhna tawi pawh kimchang takin chhang la, Mizo pangngai in."}]},
            "contents": [{"role": "user", "parts": [{"text": text}]}]
        }
        r = requests.post(url, json=payload, timeout=15)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Ka buai deuh, minute 1 hnuah lo try leh aw"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")
    reply = ai_reply(text)
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  json={"chat_id": chat_id, "text": reply})
    return "ok"

@app.route("/")
def home():
    return "TESRA Telegram Bot running"
