from flask import Flask, jsonify, render_template
import requests
import re

app = Flask(__name__)

# Пример координат для городов Беларуси
CITY_COORDS = {
    "Минск": [53.9, 27.5667],
    "Брест": [52.0976, 23.734],
    "Гомель": [52.441, 30.987],
    "Могилёв": [53.9, 30.33],
    "Витебск": [55.19, 30.21],
    "Гродно": [53.669, 23.813],
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flats")
def flats():
    flats_list = []

    # Пример: открытый JSON с канала Telegram через telegra.ph RSS (можно заменить на реальные ссылки)
    channels = [
        "https://t.me/s/nedvizimost_bel",  # замените на реальную RSS/JSON ссылку, если есть
        "https://t.me/s/byflats"
    ]

    for channel in channels:
        try:
            r = requests.get(channel)
            if r.status_code == 200:
                messages = r.text.split("\n")  # упрощенно, парсим текст постов
                for msg in messages:
                    # Находим цены и города через regex
                    price_match = re.search(r"(\d+\s?\$)", msg)
                    city_match = re.search(r"(Минск|Брест|Гомель|Могилёв|Витебск|Гродно)", msg)
                    if price_match and city_match:
                        city = city_match.group(0)
                        price = price_match.group(0)
                        lat, lng = CITY_COORDS[city]
                        flats_list.append({
                            "lat": lat,
                            "lng": lng,
                            "price": price,
                            "contact": "Telegram канал"
                        })
        except Exception as e:
            print(f"Ошибка при парсинге {channel}: {e}")

    # Если не удалось ничего найти — ставим пример
    if not flats_list:
        flats_list.append({
            "lat": 53.9,
            "lng": 27.5667,
            "price": "500 $",
            "contact": "+375 29 123-45-67"
        })

    return jsonify(flats_list)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)


