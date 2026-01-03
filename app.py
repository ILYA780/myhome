from flask import Flask, jsonify, render_template
import asyncio
import re
from telethon import TelegramClient
from geopy.geocoders import Nominatim
import time

app = Flask(__name__)

API_ID = 35776642
API_HASH = "d6660e0da47855f1578ab6b6efd91f15"
CHANNEL = "byflats"

geolocator = Nominatim(user_agent="myhome")
DEFAULT_CITY = "Минск"

CACHE = {"flats": [], "time": 0}
CACHE_TTL = 600  # 10 минут

def parse_flat_text(text):
    price = re.search(r"(\d{2,5}\s?\$)", text)
    street = re.search(r"(ул\.?|пр\.?|проспект|улица)\s*[А-Яа-я0-9\s\-]+", text)
    return {
        "price": price.group(1) if price else None,
        "address": street.group(0) if street else None
    }

def geocode_address(address):
    query = f"{DEFAULT_CITY}, {address}, Беларусь" if address else f"{DEFAULT_CITY}, Беларусь"
    location = geolocator.geocode(query)
    if location:
        return location.latitude, location.longitude
    return None, None

async def fetch_flats_from_telegram():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()

    flats = []
    messages = await client.get_messages(CHANNEL, limit=20)  # последние 20 сообщений

    for msg in messages:
        if not msg.text:
            continue
        data = parse_flat_text(msg.text)
        if not data["price"]:
            continue
        lat, lng = geocode_address(data.get("address", ""))
        flats.append({
            "lat": lat,
            "lng": lng,
            "price": data["price"],
            "contact": "Telegram @byflats",
            "link": f"https://t.me/byflats/{msg.id}",
            "address": f"{DEFAULT_CITY}, {data.get('address', '')}"
        })
    await client.disconnect()
    return flats

@app.route("/")
def index():
    now = time.time()
    if CACHE["flats"] and (now - CACHE["time"] < CACHE_TTL):
        flats = CACHE["flats"]
    else:
        flats = asyncio.run(fetch_flats_from_telegram())
        CACHE["flats"] = flats
        CACHE["time"] = now
    return render_template("index.html", flats=flats)
