from flask import Flask, jsonify, render_template, request
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import re
import math
import asyncio
import os

app = Flask(__name__)

# ===============================
# TELEGRAM CONFIG (ФЕЙКОВЫЕ КЛЮЧИ)
# ===============================
API_ID = 35776642
API_HASH = "d6660e0da47855f1578ab6b6efd91f15"
CHANNEL = "byflats"

# ===============================
# CITY COORDINATES (Belarus)
# ===============================
CITY_COORDS = {
    "Минск": (53.9, 27.5667),
    "Брест": (52.0976, 23.734),
    "Гомель": (52.441, 30.987),
    "Могилёв": (53.9, 30.33),
    "Витебск": (55.19, 30.21),
    "Гродно": (53.669, 23.813),
}

# ===============================
# DISTANCE (Haversine)
# ===============================
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ===============================
# TELEGRAM PARSER
# ===============================
async def parse_telegram():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start()

    flats = []

    history = await client(GetHistoryRequest(
        peer=CHANNEL,
        limit=50,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))

    for msg in history.messages:
        if not msg.message:
            continue

        text = msg.message

        price_match = re.search(r"(\d{2,4}\s?\$)", text)
        city_match = re.search(
            r"(Минск|Брест|Гомель|Могилёв|Витебск|Гродно)", text
        )

        if price_match and city_match:
            city = city_match.group(0)
            lat, lng = CITY_COORDS[city]

            flats.append({
                "lat": lat,
                "lng": lng,
                "price": price_match.group(1),
                "contact": "Telegram @byflats"
            })

    await client.disconnect()
    return flats


# ===============================
# ROUTES
# ===============================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/flats")
def flats():
    user_lat = float(request.args.get("lat"))
    user_lng = float(request.args.get("lng"))

    flats_list = asyncio.run(parse_telegram())

    nearby = []
    for flat in flats_list:
        if distance_km(user_lat, user_lng, flat["lat"], flat["lng"]) <= 3:
            nearby.append(flat)

    return jsonify(nearby)


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
