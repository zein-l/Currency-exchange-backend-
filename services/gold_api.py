import yfinance as yf

def get_gold_price():
    try:
        gold = yf.Ticker("GC=F")  # Gold Futures
        history = gold.history(period="1d")

        if history is None or history.empty:
            raise Exception("Gold price history is empty.")

        price = history['Close'].iloc[-1]

        return {
            "symbol": "GC=F",
            "currency": "USD",
            "price": round(price, 2)
        }

    except Exception as e:
        raise Exception(f"Error fetching gold price: {str(e)}")

from datetime import date, timedelta

def get_historical_gold_prices(days=7):
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        gold = yf.Ticker("GC=F")
        history = gold.history(start=start_date, end=end_date)

        if history is None or history.empty:
            raise Exception("No gold price history found.")

        prices = {
            str(idx.date()): round(val, 2)
            for idx, val in history["Close"].items()
        }

        return {
            "symbol": "GC=F",
            "currency": "USD",
            "start_date": str(start_date),
            "end_date": str(end_date),
            "prices": prices
        }

    except Exception as e:
        raise Exception(f"Error fetching gold history: {str(e)}")
