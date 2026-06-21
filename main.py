import os, requests
from flask import Flask, request

app = Flask(__name__)

WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# === AI REPLY FUNCTION ===
def ai_reply(text):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "I hming chu TESRA. Mizo tawng chauh hmang la, tawngkam nelawm, tawi fel leh fiamthu telh zeuh zeuh in chhang ang che."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.7
            },
            timeout=15
        )
        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"Groq error: {data.get('error',{}).get('message','API key dik lo')}"
    except Exception as e:
        return f"Ka buai: {e}"

# === WEBHOOK ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["messages"][0]
        chat_id = msg["from"] # mi mal:...@s.whatsapp.net | group:...@g.us

        # GROUP AH REPLY LO
        if chat_id.endswith("@g.us"):
            return "ok"

        user_text = msg.get("text", {}).get("body") or msg.get("body") or ""
        if not user_text:
            return "ok"

        reply = ai_reply(user_text)

        requests.post(
            "https://gate.whapi.cloud/messages/text",
            headers={"Authorization": f"Bearer {WHAPI_TOKEN}"},
            json={"to": chat_id, "body": reply}
        )
    except Exception:
        pass
    return "ok"

@app.route("/")
def home():
    return "TESRA Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
