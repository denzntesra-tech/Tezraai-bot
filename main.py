import os, requests
from flask import Flask, request

app = Flask(__name__)

WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

def ai_reply(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"I hming TESRA. Mizo tawng pangngai, tlanglawn takin chhang rawh. Tawite, fiamthu telh zeuh, thurawn pe thiam takin awm la. English hmang suh. Thu: {text}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 120
            }
        }
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Gemini error:", e)
        return "Ka buai deuh, nakinah min rawn be leh rawh"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["messages"][0]
        chat_id = msg["from"]
        if chat_id.endswith("@g.us"): # group ignore
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
    except Exception as e:
        print("Webhook error:", e)
    return "ok"

@app.route("/")
def home():
    return "TESRA Gemini running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
