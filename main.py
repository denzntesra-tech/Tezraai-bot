from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"

def ai_reply(msg):
    if not GROQ_KEY:
        return "AI key a awm lo"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "Nang chu Mizo tawng chauh hmang AI assistant i ni. Polite leh fel takin, tawngkam mawiin chhang ang che. I hming chu TESRA."},
            {"role": "user", "content": msg}
        ],
        "temperature": 0.7
    }
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "Ka buai deuh, han sawi nawn teh"

def send_whatsapp(to, text):
    to = str(to).replace("+", "")
    payload = {"to": to, "body": text}
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}"}
    requests.post(WHAPI_URL, headers=headers, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json() or {}
    msg_data = data.get("messages", [{}])[0] if "messages" in data else data
    msg = ""
    if isinstance(msg_data.get("text"), dict):
        msg = msg_data["text"].get("body", "")
    else:
        msg = msg_data.get("body", "")
    sender = str(msg_data.get("from", "")).replace("+", "")

    if msg and sender:
        reply = ai_reply(msg)
        send_whatsapp(sender, reply)
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return "TESRA AI Bot Running"
