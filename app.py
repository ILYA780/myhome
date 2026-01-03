from flask import Flask, jsonify, render_template
import re
import time
import asyncio
from telethon import TelegramClient

app = Flask(__name__)

API_ID = 35776642
API_HASH = "d6660e0da47855f1578ab6b6efd91f15"
CHANNEL = "byflats"

CACHE = {"data": [], "time": 0}
CACHE_TTL = 600  # 10 минут

# ================== PARSER ==================
def parse_price(text):
    # Ищем ЛЮБОЕ число 2–5 цифр
    match = re.search(r"\b(\d{2,5})\b", text)
    return match.group(1) if match else None

def parse_address(text):
    match = re.search(r"(Минск[^\n]*)", text)
    return match.group(1) if match else "Минск"

async def telegram_parse():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()

    flats = []
    messages = await client.get_messages(CHANNEL, limit=30)

    for msg in messages:
        if not msg.text:
            continue

        price = parse_price(msg.text)
        if not price:
            continue

        address = parse_address(msg.text)

        flats.append({
            "price": price,
            "address": address,
            "lat": None,
            "lng": None,
            "link": f"https://t.me/byflats/{msg.id}"
        })

    await client.disconnect()
    return flats

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flats")
def api_flats():
    now = time.time()

    if CACHE["data"] and now - CACHE["time"] < CACHE_TTL:
        return jsonify(CACHE["data"])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(telegram_parse())
    loop.close()

    CACHE["data"] = data
    CACHE["time"] = now

    return jsonify(data)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
