from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flats")
def flats():
    return jsonify([
        {
            "lat": 53.9023,
            "lng": 27.5619,
            "price": "500 $",
            "contact": "+375 29 123-45-67"
        }
    ])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
