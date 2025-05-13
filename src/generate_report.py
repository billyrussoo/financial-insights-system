import os
import json
from pathlib import Path
from datetime import datetime

from data_collection.alpha_vantage_client import search_symbol, get_daily_adjusted
from data_collection.newsapi_client import fetch_news_articles
from data_collection.reddit_client import search_reddit
from data_collection.producthunt_client import run_producthunt_client
from data_collection.google_trends_client import run_google_trends_client

from rag_pipeline.embed_store import embed_documents, build_context_chunks_from_keywords, retrieve_top_k_chunks
from rag_pipeline.query_ollama import run_llm
from utils.json_helpers import safe_parse_llm_json
from utils.file_io import save_json
from utils.text_helpers import ensure_directory
from utils.prompt_utils import fill_prompt_template


def clean_previous_data():
    folders = ["articles", "reports/json", "reports/pdf"]
    for folder in folders:
        dir_path = Path(folder)
        if dir_path.exists():
            for f in dir_path.glob("*.json"):
                f.unlink()
            for f in dir_path.glob("*.pdf"):
                f.unlink()
    print("🧹 Cleared previous run data (JSON/PDF).")


def generate_report(persona, interests, company_size, industry, region, role, ticker, language, model="llama3"):
    print(f"🚀 Generating report for: {interests}")

    # Ensure required folders exist
    ensure_directory("articles")
    ensure_directory("reports/json")
    ensure_directory("reports/pdf")

    # Clean old files
    clean_previous_data()

    # 1. Collect & Save Data (News, Reddit, Stock)
    combined_articles = []

    for keyword in interests:
        news_results = fetch_news_articles(keyword)
        if news_results:
            save_json(news_results, f"articles/{keyword}_news.json")
            combined_articles.extend(news_results)

        reddit_results = search_reddit(keyword)
        if reddit_results:
            save_json(reddit_results, f"articles/{keyword}_reddit.json")

        matches = search_symbol(keyword)
        if matches:
            symbol = matches[0]["1. symbol"]
            stock_data = get_daily_adjusted(symbol)
            save_json(stock_data, f"articles/{keyword}_stock.json")

    # 2. Collect Google Trends + Product Hunt
    run_producthunt_client(interests)
    run_google_trends_client(interests)
    ticker_data = get_daily_adjusted(ticker, days=30) if ticker else []
    # 3. Embed content
    all_chunks = build_context_chunks_from_keywords(interests)
    vectorstore = embed_documents(all_chunks)

    # 4. Retrieve Relevant Context
    query_str = f"{', '.join(interests)} {role} financial summary"
    top_chunks = retrieve_top_k_chunks(vectorstore, query=query_str, k=15)
    combined_context = "\n".join(top_chunks)

    # 5. Build Prompt & Run LLM —
    prompt = fill_prompt_template(
        persona=persona,
        context=combined_context,
        keyword=", ".join(interests),
        model=model,
        ticker=ticker,
        stock_data=ticker_data,
        articles=combined_articles
    )

    raw_output = run_llm(prompt)
    response_json, _ = safe_parse_llm_json(raw_output)

    # 6. Save JSON Report
    filename = "_".join(interests).replace(" ", "_")
    json_path = f"reports/json/{filename}_report.json"
    save_json(response_json, json_path)
    print(f"✅ JSON report saved to: {json_path}")

    return {
        "json_report": response_json,
        "text_report": response_json.get("final_summary", "")
    }


# ✅ Standalone Test Run
if __name__ == "__main__":
    test_payload = {
        "feedback": {"response": "", "comment": ""},
        "persona": {
            "name": "Tech Investor",
            "description": "A Tech Investor looking for investment opportunities ",
            "interests": ["Google", "Microsoft", "cloud computing"]
        },
        "companySize": "50-200",
        "industry": "SaaS",
        "region": "North America",
        "role": "VP of Sales",
        "ticker": "AAPL",
        "language": "en"
    }

    result = generate_report(
        persona=test_payload["persona"],
        interests=test_payload["persona"]["interests"],
        company_size=test_payload["companySize"],
        industry=test_payload["industry"],
        region=test_payload["region"],
        role=test_payload["role"],
        ticker=test_payload["ticker"],
        language=test_payload["language"]
    )

    print(json.dumps(result["json_report"], indent=2))
