from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)

# Бесплатный геокодер OSM
def geocode(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code == 200 and r.json():
        data = r.json()[0]
        return float(data["lat"]), float(data["lon"])
    return None, None

# Функция парсинга канала через открытый HTML
def parse_channel(url):
    flats = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        messages = soup.find_all("div", class_="tgme_widget_message_text")[:20]  # последние 20 сообщений
        for msg in messages:
            text = msg.get_text()

            # Цена (пример: 500 $, 1200 USD)
            price_match = re.search(r"\d+\s?\$|\d+\s?USD", text)
            price = price_match.group(0) if price_match else "Цена не указана"

            # Контакт (телефон)
            contact_match = re.search(r"\+?\d{11,12}", text)
            contact = contact_match.group(0) if contact_match else "Контакт не указан"

            # Адрес (ищем город + остальное)
            address_match = re.search(r"(Минск|Брест|Гомель|Могилёв|Витебск|Гродно).+", text)
            if address_match:
                address = address_match.group(0)
                lat, lng = geocode(address)
                time.sleep(1)  # чтобы не перегружать Nominatim
                if lat and lng:
                    flats.append({
                        "lat": lat,
                        "lng": lng,
                        "price": price,
                        "contact": contact,
                        "address": address
                    })
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
    return flats

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flats")
def get_flats():
    channels = [
        "https://t.me/s/byflats",
        "https://t.me/s/minskroomby",
        "https://t.me/s/nedvizimost_bel"
    ]
    all_flats = []
    for channel in channels:
        all_flats.extend(parse_channel(channel))
    return jsonify(all_flats)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)