from flask import Flask, request, jsonify
import requests
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
PORT = int(os.environ.get("PORT", 8080))
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mizo_bot_2024")

if not WHAPI_TOKEN:
    raise ValueError("WHAPI_TOKEN environment variable required!")

BOT_STATUS = True

def send_whapi_message(to, text):
    to = str(to).replace("@s.whatsapp.net", "").replace("@c.us", "").replace("+", "")
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": to, "body": text}
    try:
        response = requests.post(WHAPI_URL, headers=headers, json=payload, timeout=10)
        return response.json()
    except: return None

def get_mizo_reply(msg):
    msg_lower = msg.lower().strip()
    if msg_lower in ["hi","chibai","hello"]:
        return "Chibai le 🙏 Eng nge ka puih ang che?\n\n*Commands:*\n• price/man\n• grammar"
    elif msg_lower in ["price","man"]:
        return "*TESRA BOT MAN*\n• BASIC ₹399\n• STARTER ₹799\n• PRO ₹1299"
    elif msg_lower == "grammar":
        return "📝 Mizo Grammar: AWM RIH LOH → AWM RIH LOH"
    else:
        return f"Ka dawng e: *{msg}*"

@app.route('/webhook', methods=['POST'])
def webhook():
    global BOT_STATUS
    if not BOT_STATUS: return jsonify({"status":"ignored"}),200
    data = request.get_json(silent=True) or {}
    message = data["messages"][0] if "messages" in data else data.get("message", data)

    # === HEI HI KA SIAM THA ===
    msg_body = ""
    if isinstance(message.get("text"), dict):
        msg_body = message["text"].get("body", "")
    else:
        msg_body = message.get("body", "") or message.get("text", "")

    sender = str(message.get("from","") or message.get("chatId","")).replace("@s.whatsapp.net","").replace("+","")

    logger.info(f"DEBUG sender: {sender} | msg: {msg_body}")
    if not msg_body or not sender: return jsonify({"status":"ignored"}),200

    reply = get_mizo_reply(msg_body)
    send_whapi_message(sender, reply)
    return jsonify({"status":"sent"})

@app.route('/on', methods=['GET','POST'])
def bot_on():
    global BOT_STATUS; BOT_STATUS=True
    return jsonify({"status":"ON"})
@app.route('/')
def home(): return "Bot Active"
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode")=="subscribe" and request.args.get("hub.verify_token")==VERIFY_TOKEN:
        return request.args.get("hub.challenge"),200
    return "Forbidden",403

if __name__=="__main__": app.run(host="0.0.0.0",port=PORT)
