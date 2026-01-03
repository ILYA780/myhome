from flask import Flask, jsonify, render_template

app = Flask(__name__)

FLATS = [
    {"price": "450 $", "address": "Минск, Немига 3", "lat": 53.9, "lng": 27.5667, "link": "#"},
    {"price": "500 $", "address": "Минск, пр. Победителей 10", "lat": 53.92, "lng": 27.55, "link": "#"},
    {"price": "400 $", "address": "Минск, ул. Первомайская 5", "lat": 53.91, "lng": 27.56, "link": "#"},
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
    app.run(host="0.0.0.0", port=port)
