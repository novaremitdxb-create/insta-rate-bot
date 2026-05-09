from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = "jay_verify_123"
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")

def get_rate():
    url = "https://open.er-api.com/v6/latest/AED"
    data = requests.get(url, timeout=10).json()
    live_rate = data["rates"]["INR"]
    return round(live_rate - 0.08, 2)

def send_reply(recipient_id, message):
    url = "https://graph.facebook.com/v22.0/me/messages"

    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message
        }
    }

    requests.post(url, json=payload, headers=headers, timeout=10)

@app.route("/")
def home():
    return "Bot running"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge

    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(data)

    try:
        if "entry" in data:
            for entry in data["entry"]:
                if "messaging" in entry:
                    for event in entry["messaging"]:
                        sender_id = event["sender"]["id"]

                        if "message" in event and "text" in event["message"]:
                            message_text = event["message"]["text"].lower()

                            if "rate" in message_text:
                                rate = get_rate()
                                reply = f"Current AED to INR transfer rate is = ₹{rate} per AED"
                                send_reply(sender_id, reply)

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200

if __name__ == "__main__":
    app.run()
