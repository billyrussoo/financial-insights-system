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
    print(" Cleared previous run data (JSON/PDF).")

def generate_report(persona, interests, company_size, industry, region, role, ticker, language, model="llama3"):
    print(f" Generating report for: {interests}")

    ensure_directory("articles")
    ensure_directory("reports/json")
    ensure_directory("reports/pdf")
    clean_previous_data()

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

    run_producthunt_client(interests)
    run_google_trends_client(interests)

    ticker_data = []
    for t in ticker:
        data = get_daily_adjusted(t, days=30)
        for entry in data:
            entry["symbol"] = t  # annotate with symbol
            ticker_data.append(entry)

    all_chunks = build_context_chunks_from_keywords(interests)
    vectorstore = embed_documents(all_chunks)

    query_str = f"{', '.join(interests)} {role} financial summary"
    top_chunks = retrieve_top_k_chunks(vectorstore, query=query_str, k=15)
    combined_context = "\n".join(top_chunks)

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

    filename = "_".join(interests).replace(" ", "_")
    json_path = f"reports/json/{filename}_report.json"
    save_json(response_json, json_path)
    print(f"✅ JSON report saved to: {json_path}")

    return {
        "json_report": response_json,
        "text_report": response_json.get("final_summary", "")
    }