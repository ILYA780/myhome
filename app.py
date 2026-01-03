from flask import Flask, jsonify, render_template
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel
import asyncio
import re

app = Flask(__name__)

# Твои Telegram API
API_ID = 35776642
API_HASH = "d6660e0da47855f1578ab6b6efd91f15"
SESSION = "session"  # файл session.session

CHANNEL_USERNAME = "byflats"  # канал для парсинга

# Асинхронная функция для получения последних 20 сообщений с канала
async def get_flats():
    flats_list = []

    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()

    try:
        channel = await client.get_entity(CHANNEL_USERNAME)
        history = await client(GetHistoryRequest(
            peer=channel,
            limit=20,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))
        for msg in history.messages:
            text = msg.message or ""
            price_match = re.search(r"(\d+\s?\$)", text)
            address_match = re.search(r"(?i)(ул\.|улица|проспект|пер\.|наб\.|дом)\s[^\n,]+", text)
            if price_match:
                price = price_match.group(0)
            else:
                price = "Цена не указана"
            if address_match:
                address = address_match.group(0)
            else:
                address = "Адрес не указан"
            flats_list.append({
                "price": price,
                "address": address,
                "lat": None,  # координаты пока нет
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

# Роут для карты
@app.route("/")
def index():
    return render_template("index.html")

# Роут для JSON квартир
@app.route("/api/flats")
def flats():
    flats_list = asyncio.run(get_flats())
    return jsonify(flats_list)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
