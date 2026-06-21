import os, requests
from flask import Flask, request

app = Flask(__name__)
WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

def ai_reply(text):
    try:
        # System prompt awm lo – a leak thei lo
        prompt = f"Mizo tawng chauh hmang la, tawite leh fiamthu in chhang rawh. I hming TESRA. Thu: {text}"
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 150
            },
            timeout=15
        )
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Ka buai deuh"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["messages"][0]
        chat_id = msg["from"]
        if chat_id.endswith("@g.us"): return "ok"
        user_text = msg.get("text", {}).get("body") or ""
        if not user_text: return "ok"
        reply = ai_reply(user_text)
        requests.post("https://gate.whapi.cloud/messages/text",
            headers={"Authorization": f"Bearer {WHAPI_TOKEN}"},
            json={"to": chat_id, "body": reply})
    except: pass
    return "ok"

@app.route("/")
def home(): return "TESRA running"
if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
