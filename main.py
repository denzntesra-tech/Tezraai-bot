import os
import requests
from flask import Flask, request

app = Flask(__name__)

WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

def ai_reply(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {
            "system_instruction": {
                "parts": [{"text": "Nang hi TESRA, Mizo tlangval fel leh fiamthu duh tak i ni. Mizo tawng pangngai chauh hmang la. I siamtu chu Sterling. 'Google' tih sawi suh. Tawite, polite, mi biak nuam takin chhang rawh."}]
            },
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0.85, "maxOutputTokens": 500, "topP": 0.9}
        }
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()
        print("GEMINI:", data)
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Ka limit a full rih, darkar 1 hnuah lo try leh aw"
    except Exception as e:
        print("AI Error:", e)
        return "Ka buai deuh"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    if "messages" not in data:
        return "ok"
    msg = data["messages"][0]
    chat_id = msg["from"]
    if chat_id.endswith("@g.us"):
        return "ok"
    user_text = msg.get("text", {}).get("body", "")
    if not user_text:
        return "ok"
    reply = ai_reply(user_text)
    requests.post(
        "https://gate.whapi.cloud/messages/text",
        headers={"Authorization": f"Bearer {WHAPI_TOKEN}"},
        json={"to": chat_id, "body": reply}
    )
    return "ok"

@app.route("/")
def home():
    return "TESRA running"
