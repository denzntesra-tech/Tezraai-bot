import os
import logging
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

# Logging setup – Railway logs ah a lang ang
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not TELEGRAM_TOKEN or not GEMINI_KEY:
    logger.error("TELEGRAM_TOKEN or GEMINI_KEY missing!")
    
# Gemini configure – AQ.Ab... key pawh a thawk
genai.configure(api_key=GEMINI_KEY)

# Model – 1.5-flash a stable
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    logger.info("Gemini model loaded")
except Exception as e:
    logger.error(f"Model init failed: {e}")
    model = None

def ask_gemini(prompt):
    """Gemini call with error logging"""
    if not model:
        return "Model a load theih loh."
    try:
        # Mizo context
        full_prompt = f"I Mizo tawng chauhvin chhang rawh. I hming chu Tesra. Zawhna: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"Ka buai deuh: {str(e)[:150]}"

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=10)
        logger.info(f"Telegram send: {r.status_code}")
    except Exception as e:
        logger.error(f"Telegram send error: {e}")

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    logger.info(f"Incoming: {data}")
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        if user_text.lower() in ["/start", "start"]:
            reply = "Ka hming chu Tesra. Mizo tawngin eng pawh min zawt rawh!"
        else:
            reply = ask_gemini(user_text)
        
        send_telegram(chat_id, reply)
    
    return jsonify({"ok": True})

@app.route("/")
def home():
    return "Tesra bot a nung!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
