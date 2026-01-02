from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

# API с квартирами (пока демо-данные)
@app.route("/api/flats")
def flats():
    return jsonify([
        {
            "lat": 53.9023,
            "lng": 27.5619,
            "price": "500 $",
            "contact": "+375 29 123-45-67"
        },
        {
            "lat": 53.9100,
            "lng": 27.5400,
            "price": "650 $",
            "contact": "+375 33 987-65-43"
        }
    ])

if __name__ == "__main__":
    app.run(debug=True)