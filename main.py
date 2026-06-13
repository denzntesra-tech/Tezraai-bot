import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WHAPI_TOKEN = os.environ.get('WHAPI_TOKEN')
WHAPI_URL = 'https://gate.whapi.cloud/messages/text'

@app.route('/__mockup/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data or 'messages' not in data or not data['messages']:
        return jsonify({'status': 'no messages'}), 200

    message = data['messages'][0]
    chat_id = message.get('chat_id')
    text = message.get('text', {}).get('body', '')

    if not chat_id or not text:
        return jsonify({'status': 'missing chat_id or text'}), 200

    payload = {
        'to': chat_id,
        'body': text
    }

    headers = {
        'Authorization': f'Bearer {WHAPI_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.post(WHAPI_URL, json=payload, headers=headers)
    print("Chat ID:", chat_id) # 1. Whapi hnena i thawn number
    print("Whapi status:", response.status_code, response.text) # 2. Error en nan
    return jsonify({'status': 'sent', 'whapi_status': response.status_code}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
