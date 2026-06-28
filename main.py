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

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Railway Variables atangin la vek
GEMINI_KEY = os.environ["GEMINI_KEY"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
NEITU_CHAT_ID = os.environ["NEITU_CHAT_ID"]
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
    # Sheet atangin stock la chhuak. A1: Product, B1: Man, C1: Stock
    data = stock_sheet.get_all_records()
    return data

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
    stock_text = "\n".join([f"{item.get('Product', '')}: ₹{item.get('Man', 0)}, Stock: {item.get('Stock', 0)}" for item in stock_data if item.get('Product')])
    
    return f"""I hming chu Tesra. Mizo dawr AI assistant i ni.

DAWR STOCK TUNAH:
{stock_text}

DAN KHIRH TAK:
1. Mizo tawng chauh hmang. Sap tawng hmang suh.
2. GRAMMAR RULE: I thumal hmasa berah "Chibai!" ti la, a tawp berah "ka puih theih ang che?" ti ZIAH rawh.
   DIK: "Chibai!... ka puih theih ang che?"
   DIK LO: "ka puih theih che ang" - HEI HI HMANG SUH
3. Customer in product a zawh chuan stock en la. Stock 0 a nih chuan "Aw, a zo tawh" ti rawh.
4. Order duh chuan: "I hming leh phone number min lo pe la, kan lo call ang che" ti rawh.
5. Customer in hming + phone a pek chuan: "Aw le, kan lo save e. Kan lo call ang che" ti rawh.
6. "Ka pu/ka pi" tih hi conversation ah vawi 1 chiah hmang rawh. Message tin ah hmang suh.
7. Tlawmngai, polite, dawrkai pangngai ang

Customer: {user_text}
Tesra:"""
def process_message(chat_id, text):
    # Hei hi background ah a kal ang
    try:
        stock_data = get_stock()
        prompt = create_prompt(text, stock_data)
        reply = model.generate_content(prompt).text
        
        # Order detect: hming + phone number a awm chuan
        if "phone" in text.lower() or any(char.isdigit() for char in text):
            import re
            phone_match = re.search(r'\d{10}', text)
            if phone_match:
                for item in stock_data:
                    if item.get('Product','').lower() in text.lower() and int(item.get('Stock', 0)) > 0:
                        update_stock(item['Product'], int(item['Stock']) - 1)
                        log_order(item['Product'], "Customer", phone_match.group())
                        break
        
        send_telegram(chat_id, reply)
    except Exception as e:
        send_telegram(chat_id, "Ka pu, tunah ka buai deuh a. Minute 1 hnuah min lo zawt leh mai dawn em ni?")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        
        send_typing(chat_id)
        
        # Hi/Start ah chuan rang takin reply nghal
        if text.lower() in ['/start', 'hi', 'hello', 'chibai', 'hi tesra']:
            send_telegram(chat_id, "Chibai! Ka hming chu Tesra. Mizo dawr AI assistant ka ni. Eng nge ka puih theih ang che?")
            return "OK", 200
        
        # A dang chu background ah process tir rawh
        Thread(target=process_message, args=(chat_id, text)).start()
    
    # Telegram hnenah "Ka dawng e" ti nghal - Sec 1 pawh tling lo
    return "OK", 200

@app.route("/")
def home():
    return "Tesra Bot Running with Google Sheets"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
