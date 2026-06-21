import os, requests
from flask import Flask, request

app = Flask(__name__)

WHAPI_TOKEN = os.environ.get("WHAPI_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

def ai_reply(text):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "I hming TESRA. MIZO TAWNG CHAUH hmang ang che, Sap tawng telh suh. Mizo tlangval fing, fel, fiamthu thiam, mi rilru hrethiam tak i ni. Miin an buaina, lungngaihna, harsatna an sawiin 'thurawn pe rawh' an ti kher ngai lo – nangmahin hrethiam la, polite takin thurawn tawi fel pe nghal ang che. Mizo nunphung, tlawmngaihna leh rinna milin advice pe la. Fiamthu telh zeuh thei, mahse serious hunah serious rawh. Thu i hriat loh chu 'ka hre lo' ti mai rawh."
                    },
                    {"role": "user", "content": text}
                ],
                "temperature": 0.6,
                "max_tokens": 400
            },
            timeout=15
        )
        data = r.json()
        return data["choices"][0]["message"]["content"] if "choices" in data else "API buai"
    except Exception as e:
        return f"Ka buai: {e}"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        msg = data["messages"][0]
        chat_id = msg["from"]

        # Group ah reply lo
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
    except:
        pass
    return "ok"

@app.route("/")
def home():
    return "TESRA Mizo Bot - Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
