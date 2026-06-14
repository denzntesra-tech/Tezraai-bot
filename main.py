from flask import Flask, request, jsonify
import requests
import os
import logging
from dotenv import load_dotenv
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== CONFIG ====================
WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
PORT = int(os.environ.get("PORT", 8080))
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mizo_bot_2024")

if not WHAPI_TOKEN:
    raise ValueError("WHAPI_TOKEN environment variable required!")

BOT_STATUS = True # Bot on/off switch

# ==================== FUNCTIONS ====================
def send_whapi_message(to, text):
    """Whapi hmangin message thawnna"""
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"to": to, "body": text}
    try:
        response = requests.post(WHAPI_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Message thawnchhuah: {to}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Thawn a tlawk lo: {e}")
        return None

def get_mizo_reply(msg):
    """Mizo tawng in auto reply siamna - Pricing V4.3"""
    msg_lower = msg.lower().strip()

    if msg_lower in ["hi", "chibai", "hello"]:
        return "Chibai le 🙏 Eng nge ka puih ang che?\n\n*Commands:*\n• price/man - Dawrkai man enna\n• grammar - Grammar diktanna"

    elif msg_lower in ["price", "man", "man enna"]:
        return """*TESRA DAWRKAI BOT MAN - THLA TIN* 💰

*1. BASIC - ₹399/thla*
Auto Reply chauh. Hman chhin nan

*2. STARTER - ₹799/thla* ⭐ *Tam ber in an hmang*
Auto Reply + Reminder + Zan Order + Sheet. Dawrkai tan a tawk

*3. PRO - ₹1299/thla* 🔥
Voice + Customer hriatna + VIP Support. Dawr lian tan

*Mahse* tun thla sign up hmasa 10 tan chuan Starter kha ₹599/thla chauh in ka pe ang che ✅
I tan Option 2 hi a tawk ber ang em?"""

    elif msg_lower == "grammar":
        return "📝 *Mizo Grammar Diktanna:*\n\n❌ AWM RIH LO → ✅ AWM RIH LO\n❌ THEI LO → ✅ THEI RIH LO A, MAHSE...\n❌ KA LO → ✅ KA LA\n❌ TIH TAWP → ✅ TIH TAWP TA"

    else:
        return f"Ka dawng e: *{msg}*\n\n'price' emaw 'grammar' tih type rawh."

# ==================== ROUTES ====================
@app.route('/')
def home():
    status = "ON ✅" if BOT_STATUS else "OFF ❌"
    return f"TESRA Mizo WhatsApp Bot - Status: {status}"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """WhatsApp webhook verification"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified")
        return challenge, 200
    return "Forbidden", 403

@app.route('/on', methods=['POST'])
def bot_on():
    global BOT_STATUS
    BOT_STATUS = True
    logger.info("Bot ON")
    return jsonify({"status": "ON", "message": "Bot chhuak leh ta e ✅"})

@app.route('/off', methods=['POST'])
def bot_off():
    global BOT_STATUS
    BOT_STATUS = False
    logger.info("Bot OFF")
    return jsonify({"status": "OFF", "message": "Bot off ta e ❌"})

@app.route('/webhook', methods=['POST'])
def webhook():
    global BOT_STATUS

    if not BOT_STATUS:
        return jsonify({"status": "ignored", "reason": "Bot off a ni"})

    data = request.get_json(silent=True) or {}

    # Message lak chhuah
    message = {}
    if "messages" in data and isinstance(data["messages"], list):
        message = data["messages"][0]
    elif "message" in data:
        message = data["message"]
    else:
        message = data

    # LOOP TIHTAWP - 1. Keimahni reply chu ignore - A him zawk
    if str(message.get("from_me")).lower() == "true":
        return jsonify({"status": "ignored", "reason": "Kei mahni reply"})

    msg_body = message.get("body", "") or message.get("text", "")
    msg_body_lower = msg_body.lower().strip()

    # LOOP TIHTAWP - 2. Echo: leh Ka dawng e: chu ignore hmasa ber
    if msg_body_lower.startswith("echo:") or msg_body_lower.startswith("ka dawng e:"):
        return jsonify({"status": "ignored", "reason": "Echo/Loop message"})

    sender = message.get("from", "") or message.get("chat_id", "")

    if not msg_body or not sender:
        return jsonify({"status": "ignored", "reason": "Data incomplete"})

    # Process leh reply
    reply_text = get_mizo_reply(msg_body)
    send_whapi_message(sender, reply_text)
    return jsonify({"status": "sent", "to": sender, "reply": reply_text})

# ==================== RUN ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
