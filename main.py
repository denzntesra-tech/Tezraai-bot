import os, requests
from flask import Flask, request

app = Flask(__name__)
WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

def ai_reply(text):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama3-8b-8192",
                  "messages": [{"role":"system","content":"I hming chu TESRA. Mizo tawng chauh hmang la, tawngkam thiam, nelawm leh fiamthu in chhang thin ang che."},
                               {"role":"user","content":text}]}, timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ka buai deuh: {e}"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["messages"][0]
        chat_id = msg["from"]
        # text la chhuak dan hrang hrang
        user_text = msg.get("text", {}).get("body") or msg.get("body") or ""
        if not user_text: return "ok"

        reply = ai_reply(user_text)
        requests.post("https://gate.whapi.cloud/messages/text",
            headers={"Authorization": f"Bearer {WHAPI_TOKEN}"},
            json={"to": chat_id, "body": reply})
    except: pass
    return "ok"
