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
CACHE = {"data": [], "time": 0}
CACHE_TTL = 600  # 10 минут

# ================== PARSER ==================
def parse_flat_text(text):
    price = re.search(r"(\d{2,5}\s?\$)", text)
    street = re.search(r"(ул\.?|пр\.?|проспект|улица)\s*[А-Яа-я0-9\s\-]+", text)
    return price.group(1) if price else None, street.group(0) if street else None

def geocode(address):
    try:
        q = f"{DEFAULT_CITY}, {address}, Беларусь" if address else f"{DEFAULT_CITY}, Беларусь"
        loc = geolocator.geocode(q, timeout=10)
        if loc:
            return loc.latitude, loc.longitude
    except:
        pass
    return None, None

async def telegram_parse():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()

    flats = []
    messages = await client.get_messages(CHANNEL, limit=30)

    for msg in messages:
        if not msg.text:
            continue

        price, address = parse_flat_text(msg.text)
        if not price:
            continue

        lat, lng = geocode(address)
        if not lat:
            continue

        flats.append({
            "price": price,
            "address": f"{DEFAULT_CITY}, {address or ''}",
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
def flats_api():
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
