from flask import Flask, render_template, request
import requests
import os
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

analyzer = SentimentIntensityAnalyzer()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        company = request.form["company"]
        symbol = request.form["symbol"]

        # -------- STOCK PRICE SAFE FETCH --------
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            price = "N/A"
        else:
            price = round(hist["Close"].iloc[-1], 2)

        # -------- NEWS FETCH SAFE --------
        url = f"https://newsapi.org/v2/everything?q={company}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        articles = data.get("articles", [])

        if not articles:
            headlines = ["No news found"]
            recommendation = "HOLD"
        else:
            sentiment_score = 0
            headlines = []

            for article in articles[:5]:
                title = article.get("title", "")
                if title:
                    score = analyzer.polarity_scores(title)["compound"]
                    sentiment_score += score
                    headlines.append(title)

            sentiment_score /= len(headlines)

            if sentiment_score > 0.05:
                recommendation = "BUY"
            elif sentiment_score < -0.05:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"

        return render_template(
            "result.html",
            company=company,
            symbol=symbol,
            price=price,
            headlines=headlines,
            recommendation=recommendation
        )

    except Exception as e:
        return f"ERROR OCCURRED: {e}"


if __name__ == "__main__":
    app.run(debug=True)
