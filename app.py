from flask import Flask, jsonify, render_template
import re
import time
import asyncio
from telethon import TelegramClient
from geopy.geocoders import Nominatim

app = Flask(__name__)

# ================== TELEGRAM ==================
API_ID = 35776642
API_HASH = "d6660e0da47855f1578ab6b6efd91f15"
CHANNEL = "byflats"

# ================== GEOCODER ==================
geolocator = Nominatim(user_agent="myhome")
DEFAULT_CITY = "Минск"

# ================== CACHE ==================
CACHE = {
    "data": [],
    "time": 0
}
CACHE_TTL = 600  # 10 минут

# ================== PARSER ==================
def parse_price(text):
    match = re.search(r"(\d{2,5}\s?\$)", text)
    return match.group(1) if match else None

def parse_address(text):
    # Берём любую строку, где упоминается Минск
    match = re.search(r"(Минск[^\n]*)", text)
    return match.group(1) if match else None

def geocode_address(address):
    if not address:
        return None, None
    try:
        query = f"{address}, Беларусь"
        location = geolocator.geocode(query, timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print("Geocode error:", e)
    return None, None

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
        lat, lng = geocode_address(address)

        flats.append({
            "price": price,
            "address": address or "Адрес не указан",
            "lat": lat,
            "lng": lng,
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

# ================== START ==================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
