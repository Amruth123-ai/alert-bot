import requests


BOT_TOKEN = "7683947813:AAH2xwTnh2jutZVamkIiHSzw4LEz_yvK6N8"
CHAT_ID   = "-5040188162"
MESSAGE = "Hello from Python!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": MESSAGE
}

response = requests.post(url, json=payload)

print(response.json())



