import os
import json
from pathlib import Path
from datetime import datetime

from data_collection.alpha_vantage_client import search_symbol, get_daily_adjusted
from data_collection.newsapi_client import fetch_news_articles
from data_collection.reddit_client import search_reddit

from rag_pipeline.embed_store import embed_documents, retrieve_top_k_chunks
from rag_pipeline.embed_store import build_context_chunks
from rag_pipeline.prompt_builder import build_prompt
from rag_pipeline.query_ollama import run_llm

from utils.file_io import save_json, load_json
from utils.text_helpers import ensure_directory
from utils.prompt_utils import fill_prompt_template

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from textwrap import wrap

ARTICLES_DIR = Path("articles/")
REPORTS_JSON_DIR = Path("reports/json/")
REPORTS_PDF_DIR = Path("reports/pdf/")
PROMPT_TEMPLATE_PATH = Path("src/rag_pipeline/prompt.txt")


def generate_combined_report(keywords: list, model: str = "llama3"):
    print(f"\n🔍 Generating combined report for: {', '.join(keywords)}")

    ensure_directory(ARTICLES_DIR)
    ensure_directory(REPORTS_JSON_DIR)
    ensure_directory(REPORTS_PDF_DIR)

    all_chunks = []

    for keyword in keywords:
        # 1. News
        news_results = fetch_news_articles(keyword)
        if news_results:
            news_path = ARTICLES_DIR / f"{keyword}_news.json"
            save_json(news_results, news_path)
            print(f"📰 Saved news results to: {news_path}")

        # 2. Reddit
        reddit_results = search_reddit(keyword)
        if reddit_results:
            reddit_path = ARTICLES_DIR / f"{keyword}_reddit.json"
            save_json(reddit_results, reddit_path)
            print(f"👾 Saved Reddit results to: {reddit_path}")

        # 3. Stocks
        matches = search_symbol(keyword)
        if matches:
            symbol = matches[0].get("1. symbol")
            time_series_data = get_daily_adjusted(symbol)
            stock_path = ARTICLES_DIR / f"{keyword}_stock.json"
            save_json(time_series_data, stock_path)
            print(f"📈 Saved Alpha Vantage data to: {stock_path}")

    # 4. Build Combined Context Chunks (across all keywords)
    for keyword in keywords:
        chunks = build_context_chunks(keyword)
        all_chunks.extend(chunks)

    if not all_chunks:
        print("❌ No content available for embedding from any keyword.")
        return

    # 5. Embed all combined content
    vectorstore = embed_documents(all_chunks)
    if vectorstore is None:
        print("❌ Failed to create vectorstore. Aborting.")
        return

    # 6. Retrieve top chunks using combined query
    combined_query = ", ".join(keywords) + " financial summary"
    top_chunks = retrieve_top_k_chunks(vectorstore, query=combined_query, k=10)
    combined_context = "\n".join(top_chunks)

    # 7. Build Prompt
    BASE_DIR = Path(__file__).resolve().parent.parent
    persona_file = BASE_DIR / "personas" / "sales_exec.json"
    persona_data = load_json(str(persona_file))
    final_prompt = fill_prompt_template(persona_data, combined_context, combined_query)

    # 8. Query LLM
    llm_response = run_llm(final_prompt, model=model)

    # 9. Save JSON Report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"combined_report_{timestamp}"
    json_path = REPORTS_JSON_DIR / f"{filename}.json"
    save_json(llm_response, json_path)
    print(f"✅ Saved JSON report: {json_path}")

    # 10. Generate PDF Report
    generate_pdf_report(llm_response, filename)


def generate_pdf_report(report_data, filename):
    pdf_path = f"reports/pdf/{filename}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=LETTER)
    width, height = LETTER
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Combined Financial Report")
    y -= 30

    c.setFont("Helvetica", 11)
    for section, content in report_data.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{section.replace('_', ' ').title()}:")
        y -= 18
        c.setFont("Helvetica", 10)

        if isinstance(content, dict):
            for k, v in content.items():
                for line in wrap(f"{k}: {v}", width=100):
                    c.drawString(60, y, line)
                    y -= 14
        elif isinstance(content, list):
            for item in content:
                for line in wrap(str(item), width=100):
                    c.drawString(60, y, line)
                    y -= 14
        else:
            for line in wrap(str(content), width=100):
                c.drawString(60, y, line)
                y -= 14

        y -= 10
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    c.save()
    print(f"📄 PDF report saved to: {pdf_path}")


if __name__ == "__main__":
    input_str = input("Enter up to 3 keywords separated by commas: ")
    keywords = [k.strip() for k in input_str.split(",") if k.strip()][:3]
    generate_combined_report(keywords)