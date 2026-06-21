import os, requests, json
from flask import Flask, request

app = Flask(__name__)
WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

def ai_reply(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"Nang hi TESRA i ni. Mizo tawng chauh hmang la, tawite leh pangngai takin chhang rawh: {text}"}]}],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}
            ]
        }
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()
        # debug log
        print("GEMINI RAW:", json.dumps(data)[:500])
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Gemini key dik lo / limit zo"
    except Exception as e:
        print("Error:", e)
        return "Ka buai deuh"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json or {}
        if "messages" not in data:
            return "ok" # WHAPI status ping a nih chuan ignore
        msg = data["messages"][0]
        chat_id = msg["from"]
        if chat_id.endswith("@g.us"):
            return "ok"
        user_text = msg.get("text", {}).get("body", "")
        if not user_text:
            return "ok"
        reply = ai_reply(user_text)
        requests.post("https://gate.whapi.cloud/messages/text",
            headers={"Authorization": f"Bearer {WHAPI_TOKEN}"},
            json={"to": chat_id, "body": reply})
    except Exception as e:
        print("Webhook err:", e)
    return "ok"

@app.route("/")
def home(): return "TESRA OK"
