from datetime import datetime
import os
import json

def format_further_reading(articles: list) -> str:
    """
    Formats the top 2 articles as a JSON string to inject directly into the FURTHER READING field.
    """
    formatted = []
    for a in articles[:2]:  # Only take top 2 as per the prompt structure
        formatted.append({
            "title": a.get("title", "No title"),
            "link": a.get("url", "#"),
            "summary": a.get("description", "") or a.get("summary", "Relevant to today’s market movements.")
        })
    return json.dumps(formatted, ensure_ascii=False)

def format_stock_data_for_prompt(data: list) -> str:
    """
    Converts 30-day stock data into a plain string format for LLM context.
    """
    if not data:
        return "No recent stock performance data available."

    summary_lines = []
    for entry in data:
        summary_lines.append(
            f"{entry['date']}: Open={entry['open']}, Close={entry['close']}, Volume={entry['volume']}"
        )
    return "Recent 30-day stock performance:\n" + "\n".join(summary_lines)

def fill_prompt_template(
    persona: dict,
    context: str,
    keyword: str,
    model: str = "llama3",
    ticker: str = "N/A",
    articles: list = None,
    stock_data: list = None
) -> str:
    """
    Loads the prompt template and fills it with persona details, context, news articles, and stock performance data.
    """
    template_path = os.path.join(os.path.dirname(__file__), "..", "rag_pipeline", "prompt.txt")

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    further_reading = format_further_reading(articles or [])
    ticker_insight = format_stock_data_for_prompt(stock_data or [])

    return template.format(
        persona_name=persona.get("name", ""),
        persona_description=persona.get("description", ""),
        role=persona.get("role", ""),
        industry=persona.get("industry", ""),
        region=persona.get("region", ""),
        companySize=persona.get("companySize", ""),
        language=persona.get("language", "English"),
        keyword=keyword,
        date=datetime.now().strftime("%Y-%m-%d"),
        context=context,
        model=model,
        ticker=ticker,
        further_reading=further_reading,
        ticker_insight=ticker_insight
    )
