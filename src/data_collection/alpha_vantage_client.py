import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

def search_symbol(keyword):
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keyword,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    try:
        data = response.json()
        return data.get("bestMatches", [])
    except Exception as e:
        print("Error parsing symbol search:", e)
        return []

def get_daily_adjusted(symbol, days=30):
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "compact",  # max ~100 most recent days
        "datatype": "json",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        print(f"❌ Error fetching data for {symbol}")
        return []

    try:
        data = response.json()
        time_series = data.get("Time Series (Daily)", {})
        formatted_data = []
        for date, values in list(time_series.items())[:days]:  # Grab up to `days` entries
            formatted_data.append({
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "adjusted_close": float(values["5. adjusted close"]),
                "volume": int(values["6. volume"])
            })
        return formatted_data
    except Exception as e:
        print("❌ Failed to parse daily data:", e)
        return []

# Standalone test if needed
if __name__ == "__main__":
    keyword = input("Enter company name or ticker: ").strip()
    matches = search_symbol(keyword)
    if not matches:
        print("No matches found.")
    else:
        symbol = matches[0]["1. symbol"]
        name = matches[0]["2. name"]
        print(f"\n📊 Top Match: {name} ({symbol})")
        data = get_daily_adjusted(symbol, days=30)
        for entry in data:
            print(entry)
        time.sleep(1)
