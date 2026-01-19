from flask import Flask, render_template, request
import requests
import os
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

analyzer = SentimentIntensityAnalyzer()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    company = request.form["company"]
    symbol = request.form["symbol"]

    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")["Close"][0]

    url = f"https://newsapi.org/v2/everything?q={company}&apiKey={NEWS_API_KEY}"
    news = requests.get(url).json()

    score = 0
    headlines = []

    for article in news["articles"][:5]:
        title = article["title"]
        headlines.append(title)
        score += analyzer.polarity_scores(title)["compound"]

    score /= 5

    if score > 0.05:
        recommendation = "BUY"
    elif score < -0.05:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return render_template(
        "result.html",
        company=company,
        symbol=symbol,
        price=round(price, 2),
        headlines=headlines,
        recommendation=recommendation
    )

if __name__ == "__main__":
    app.run()
