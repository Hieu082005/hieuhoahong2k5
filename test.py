from dotenv import load_dotenv
import os
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": "😆 Test gửi tin nhắn từ Android VPS thành công!"
}

r = requests.post(url, data=data)

print(r.text)
