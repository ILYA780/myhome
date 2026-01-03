from flask import Flask, jsonify, render_template
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio
import re

app = Flask(__name__)

API_ID = 31174726
API_HASH = "16bd530d2cffe0b722620fac49585fd0"
SESSION = "session"  # session.session
CHANNEL_USERNAME = "byflats"

# Асинхронная функция для получения квартир
async def get_flats():
    flats_list = []
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()

    try:
        channel = await client.get_entity(CHANNEL_USERNAME)
        history = await client(GetHistoryRequest(
            peer=channel,
            limit=20,  # последние 20 сообщений
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        for msg in history.messages:
    text = msg.message or ""
    
    # Цена через regex, если есть
    price_match = re.search(r"(\d+\s?\$)", text)
    price = price_match.group(0) if price_match else "Цена не указана"
    
    # Адрес через regex, если есть
    address_match = re.search(r"(?i)(ул\.|улица|проспект|пер\.|наб\.|дом)\s[^\n,]+", text)
    address = address_match.group(0) if address_match else "Адрес не указан"
    
    flats_list.append({
        "price": price,
        "address": address,
        "lat": None,
        "lng": None,
        "link": f"https://t.me/{CHANNEL_USERNAME}/{msg.id}"
    })

    except Exception as e:
        print("Ошибка при парсинге:", e)

    finally:
        await client.disconnect()

    if not flats_list:
        flats_list.append({
            "price": "500 $",
            "address": "Минск, примерная улица",
            "lat": 53.9,
            "lng": 27.5667,
            "link": "#"
        })

    return flats_list

# Роут для страницы
@app.route("/")
def index():
    return render_template("index.html")

# Роут для JSON
@app.route("/api/flats")
def flats():
    flats_list = asyncio.run(get_flats())
    return jsonify(flats_list)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
