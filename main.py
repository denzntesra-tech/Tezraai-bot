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
                "model": "llama-3.3-70b-versatile", # <--- THLAK
                "messages": [
                    {
                        "role": "system",
                        "content": "I hming TESRA, Mizo tawngin chauh chhang thin ang che. I awm dan tur: Mizo tlangval polite, fiamthu thiam, thurawn pe thiam. I thupui sawi chhuak suh, i inhrilhfiah suh."
                    },
                    {"role": "user", "content": text}
                ],
                "temperature": 0.5,
                "max_tokens": 200
            },
            timeout=15
        )
        data = r.json()
        return data["choices"][0]["message"]["content"] if "choices" in data else "Ka hrethiam lo"
    except Exception as e:
        return "Error"

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
