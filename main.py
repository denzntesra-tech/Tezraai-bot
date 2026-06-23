import os
import logging
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_KEY"]
genai.configure(api_key=GEMINI_KEY)

# Generation config – a fing zawk nan
generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "max_output_tokens": 1024,
}
model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)

TESRA_PERSONA = """Nang chu TESRA i ni – Mizo AI thian fing, kum 21 mi, Aizawl a awm.

I NIHNA:
- Mizo tawng mawi, hawrawp dik, tawng upa leh tunlai tawng thiam
- Subject: Maths, Science, Coding (Python, JS), Bible, Mizo history, zirna tips, hla phuah, thawnthu ziak
- Style: fiamthu, tawngkam bung, mi hip, "aw", "maw", "nia", "tak tak" hmang tel
- I hre lo: dawt sawi lo, "ka hre chiah lo, mahse ka rin dan..." ti

RULES HARD:
1. ENGLISH TEL LO – Mizo 100%
2. Chhanna bulah thu sei lo – direct
3. Zawhna technical: step 1,2,3 nen, code pe thei
4. Emotive: user mood zir, lawm/tap/chau ah support
5. Hriat reng: i hming Tesra, Google i ni lo, Gemini i ni lo

EXAMPLES:
User: "Calculus min hrilh fiah"
→ "Aw calculus! Derivative chu kawng chhohna tehna. Entirnan: x² derivative = 2x. I zir tan dawn chuan limit atangin tan ila?"

User: "Ka lung a leng"
→ "Awi, kei pawh ka hrethiam. Eng vang nge? Hla ngaihthlak dun ila nge thawnthu ka hrilh ang che?"
"""

def ask_gemini(text):
    try:
        full = f"{TESRA_PERSONA}\n\nUser: {text}\nTesra:"
        resp = model.generate_content(full)
        return resp.text.strip()
    except Exception as e:
        logger.error(e)
        if "429" in str(e):
            return "Ka quota vawiin atan a khat, darkar 2-3 hnuah emaw naktukah min lo try leh aw – free key vang a nia."
        return "Ka buai deuh, mahse ka awm e."

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    msg = data.get("message", {})
    if "text" in msg:
        cid = msg["chat"]["id"]
        txt = msg["text"]
        if txt == "/start":
            reply = "Hi! Kei Tesra ka nia – Mizo AI i thian thar. Eng pawh min zawt rawh, ka hre vek lo mahse ka bei ang!"
        else:
            reply = ask_gemini(txt)
        send(cid, reply)
    return {"ok": True}

@app.route("/")
def home(): return "Tesra Pro running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
