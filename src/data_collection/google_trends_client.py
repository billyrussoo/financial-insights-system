import os
import time
import json
import pandas as pd
from typing import List, Dict
from pytrends.request import TrendReq

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Ensure articles folder exists
ARTICLES_DIR = os.path.join(os.path.dirname(__file__), "../articles")
os.makedirs(ARTICLES_DIR, exist_ok=True)

def fetch_trend_data(keyword, timeframe, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            pytrends.build_payload([keyword], timeframe=timeframe)
            df = pytrends.interest_over_time()
            if not df.empty:
                df = df.reset_index()[['date', keyword]]
            else:
                df = pd.DataFrame(columns=['date', keyword])
            return df
        except Exception as e:
            print(f"❌ Attempt {attempt} failed for trend data: {e}")
            time.sleep(attempt * 5)
    return pd.DataFrame(columns=['date', keyword])

def fetch_interest_by_region(keyword, timeframe, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            pytrends.build_payload([keyword], timeframe=timeframe)
            df = pytrends.interest_by_region()
            if not df.empty:
                df = df.sort_values(by=keyword, ascending=False).reset_index()
            else:
                df = pd.DataFrame(columns=['geoName', keyword])
            return df
        except Exception as e:
            print(f"❌ Attempt {attempt} failed for region data: {e}")
            time.sleep(attempt * 5)
    return pd.DataFrame(columns=['geoName', keyword])

def summarize_trend_data(trend_df: pd.DataFrame, keyword: str) -> Dict:
    if trend_df.empty:
        return {"summary": f"No trend data available for '{keyword}'."}

    max_value = trend_df[keyword].max()
    min_value = trend_df[keyword].min()
    mean_value = trend_df[keyword].mean()

    max_time = trend_df.loc[trend_df[keyword].idxmax()]['date']
    min_time = trend_df.loc[trend_df[keyword].idxmin()]['date']

    return {
        "summary": (
            f"Search interest for '{keyword}' averaged {mean_value:.1f}. "
            f"Peak at {max_time} ({max_value}), lowest at {min_time} ({min_value})."
        )
    }

def summarize_region_data(region_df: pd.DataFrame, keyword: str, top_n: int = 5) -> Dict:
    if region_df.empty or keyword not in region_df.columns:
        return {"top_regions": "No regional data available."}

    top_regions = region_df.head(top_n)
    region_info = [
        {"region": row["geoName"], "score": int(row[keyword])}
        for _, row in top_regions.iterrows()
    ]
    return {"top_regions": region_info}

def save_summary_json(keyword: str, timeframe_label: str, data: Dict):
    filename = f"google_trends_{keyword.lower()}_{timeframe_label}.json"
    path = os.path.join(ARTICLES_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved: {filename}")

def run_google_trends_client(keywords: List[str]):
    timeframes = {
        "same_day": "now 1-d",
        "weekly": "now 7-d"
    }

    for keyword in keywords:
        for label, timeframe in timeframes.items():
            trend_data = fetch_trend_data(keyword, timeframe)
            region_data = fetch_interest_by_region(keyword, timeframe)

            trend_summary = summarize_trend_data(trend_data, keyword)
            region_summary = summarize_region_data(region_data, keyword)

            combined = {
                "type": "google_trends_summary",
                "keyword": keyword,
                "timeframe": label,
                "trend_summary": trend_summary["summary"],
                "top_regions": region_summary.get("top_regions", [])
            }

            save_summary_json(keyword, label, combined)
            time.sleep(5)

# Example standalone test
if __name__ == "__main__":
    run_google_trends_client(["USA", "China", "Tariff"])
