import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import requests
import re

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Railway Variables atangin la vek
GEMINI_KEY = os.environ["GEMINI_KEY"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
NEITU_CHAT_ID = os.environ.get("NEITU_CHAT_ID", "")
STOCK_SHEET_ID = os.environ["STOCK_SHEET_ID"]
COMMANDS_SHEET_ID = os.environ["COMMANDS_SHEET_ID"]
GOOGLE_CREDS = json.loads(os.environ["GOOGLE_CREDS"])

# Gemini Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Google Sheets Setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_info(GOOGLE_CREDS, scopes=SCOPES)
gc = gspread.authorize(creds)
stock_sheet = gc.open_by_key(STOCK_SHEET_ID).sheet1
commands_sheet = gc.open_by_key(COMMANDS_SHEET_ID).sheet1

def send_telegram(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text})

def send_typing(chat_id):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendChatAction",
        json={"chat_id": chat_id, "action": "typing"})

def get_stock():
    records = stock_sheet.get_all_records()
    cleaned = []
    for r in records:
        cleaned.append({k.strip(): v for k, v in r.items()})
    return cleaned

def update_stock(product_name, new_stock):
    # Stock update
    records = stock_sheet.get_all_records()
    for i, row in enumerate(records, start=2):  # row 1 = header
        if row.get('Product', '').lower() == product_name.lower():
            stock_sheet.update_cell(i, 3, new_stock)  # Column C = Stock
            return True
    return False

def log_order(product, customer_name, phone):
    # Commands sheet ah order log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commands_sheet.append_row([timestamp, product, customer_name, phone, "ORDER THAR"])

def create_prompt(user_text, stock_data):
    stock_detail = "\n".join([
        f"{item.get('Product')}: Rs.{item.get('Man', 0)}, stock {item.get('Stock', 0)}"
        for item in stock_data if item.get('Product')
    ])
    stock_names = ", ".join([item.get('Product') for item in stock_data if item.get('Product')])

    return f"""You are Tesra, a friendly Mizo shop assistant in Mizoram, India.

INSTRUCTIONS:
- Always reply to the customer IN MIZO only. Natural, colloquial Mizo.
- Talk like a real human shopkeeper, short and warm.
- When asked "what do you have?", just list names: "Sana, Pheikhawk, Kawr, Momo leh Bawnghnute kan nei e. Eng ber nge i duh ang?"
- Only give exact price/stock numbers when asked for a specific item.
- NEVER end every message with "Eng tin nge ka puih theih ang che?". Use "I duh em?", "Eng ber nge ni ang?", "A dang en duh em?" – vary, or just stop.
- Do NOT repeat "Stock X a la awm e" for every item.
- Keep replies to 1-3 sentences.

CURRENT SHOP INVENTORY:
{stock_detail}

Available: {stock_names}

Customer message: {user_text}

Reply in natural Mizo:
"""
def process_message(chat_id, text):
    # Hei hi background ah a kal ang
    try:
        # Greeting – Gemini call hma in, fix sa
        is_greeting = text.lower().strip() in ['/start', 'hi', 'hello', 'chibai']
        if is_greeting:
            send_telegram(chat_id, "Chibai! Ka hming chu Tesra. Eng tin nge ka puih theih ang che?")
            return

        stock_data = get_stock()
        prompt = create_prompt(text, stock_data)
        reply = model.generate_content(prompt).text

        # ====== Grammar force fix ======
        reply = reply.replace("angche", "ang che")
        reply = reply.replace("Angche", "Ang che")
        reply = reply.replace("Engtin", "Eng tin")
        reply = reply.replace("Eng nge", "Eng tin nge")
        reply = reply.replace("Enge", "Eng tin nge")
        reply = reply.replace("Ka pu", "").replace("Ka pi", "")
        reply = reply.replace("ka pu", "").replace("ka pi", "")
        # Gemini Mizo tisual fix
        reply = reply.replace("ih theih", "ka puih theih")
        reply = reply.replace("ihtheih", "ka puih theih")
        # Chibai spam – greeting lo ah chuan paih
        reply = reply.replace("Chibai!", "").strip()
        reply = " ".join(reply.split())
        # ==============================

        # Order detect: hming + phone number a awm chuan
        if "phone" in text.lower() or any(char.isdigit() for char in text):
            phone_match = re.search(r'\d{10}', text)
            if phone_match:
                for item in stock_data:
                    if item.get('Product', '').lower() in text.lower() and int(item.get('Stock', 0)) > 0:
                        update_stock(item['Product'], int(item['Stock']) - 1)
                        log_order(item['Product'], "Customer", phone_match.group())
                        break

        send_telegram(chat_id, reply)
    except Exception as e:
        logging.error(e)
        send_telegram(chat_id, "Ih aw, tunah ka buai deuh a. Minute 1 hnuah min lo zawt leh mai dawn em ni?")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        send_typing(chat_id)
        Thread(target=process_message, args=(chat_id, text)).start()
    return "OK", 200

@app.route("/")
def home():
    return "Tesra Bot Running with Google Sheets"
    
@app.route("/debug")
def debug():
    try:
        data = get_stock()
        return jsonify({
            "sheet_id": STOCK_SHEET_ID,
            "rows": len(data),
            "headers": list(data[0].keys()) if data else [],
            "first_row": data[0] if data else None
        })
    except Exception as e:
        return jsonify({"error": str(e), "sheet_id": STOCK_SHEET_ID}), 500
