from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Фиктивные квартиры для теста
FLATS = [
    {"price": "450 $", "address": "Минск, Немига 3", "lat": None, "lng": None, "link": "#"},
    {"price": "500 $", "address": "Минск, пр. Победителей 10", "lat": None, "lng": None, "link": "#"},
    {"price": "400 $", "address": "Минск, ул. Первомайская 5", "lat": None, "lng": None, "link": "#"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flats")
def flats():
    return jsonify(FLATS)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
