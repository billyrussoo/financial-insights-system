import os
import faiss
import json
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from data_collection.reddit_client import get_social_trends
from utils.text_helpers import chunk_text
from utils.file_io import load_json
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize embedding model path
model = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDINGS_DIR = Path("embeddings")
INDEX_PATH = os.path.join(EMBEDDINGS_DIR, "index.faiss")
DOCS_PATH = os.path.join(EMBEDDINGS_DIR, "docs.pkl")


def load_reddit_chunks(keyword: str) -> List[str]:
    path = Path("articles") / f"{keyword}_reddit.json"
    chunks = []
    if path.exists():
        data = load_json(path)
        for post in data:
            title = post.get("title", "")
            body = post.get("body", "")
            chunks.append(f"[Reddit Post]\n{title}\n{body}")
    return chunks


def load_reddit_trends(keyword: str) -> List[str]:
    summaries = get_social_trends([keyword])
    trend_chunks = []
    for trend in summaries:
        text = (
            f"[Social Trend Summary for '{trend['keyword']}']\n"
            f"Post Count: {trend['post_count']}\n"
            f"Average Score: {trend['average_score']}\n"
            f"Top Posts:\n- " + "\n- ".join(trend["top_titles"])
        )
        trend_chunks.append(text)
    return trend_chunks


def load_news_chunks(keyword: str) -> List[str]:
    path = Path("articles") / f"{keyword}_news.json"
    chunks = []
    if path.exists():
        data = load_json(path)
        for article in data:
            title = article.get("title", "")
            full_text = article.get("content", "")
            chunks.append(f"[News Article]\n{title}\n{full_text}")
    return chunks


def load_stock_chunks(keyword: str) -> List[str]:
    path = Path("articles") / f"{keyword}_stock.json"
    chunks = []
    if path.exists():
        data = load_json(path)
        if isinstance(data, list):
            stock_text = json.dumps(data[:10], indent=2)
            chunks.append(f"[Stock Data]\n{stock_text}")
    return chunks

def load_google_trends_chunks(keyword: str) -> List[str]:
    folder = Path("articles")
    chunks = []

    for timeframe in ["same_day", "weekly"]:
        filename = f"google_trends_{keyword.lower()}_{timeframe}.json"
        path = folder / filename

        if not path.exists():
            continue

        data = load_json(path)
        trend_summary = data.get("trend_summary", "")
        regions = data.get("top_regions", [])
        print(f"[DEBUG] regions: {regions}")
        if isinstance(regions, list) and all(isinstance(r, dict) for r in regions):
            region_text = ", ".join(f"{r['region']} ({r['score']})" for r in regions)
        else:
            print("[WARNING] Invalid region format, skipping region chunk.")
            region_text = "No regional data available."

        chunk = f"[Google Trends - {timeframe.upper()}]\n{trend_summary}\nTop Regions: {region_text}"
        chunks.append(chunk)

    return chunks

def load_producthunt_chunks(keyword: str) -> List[str]:
    path = Path("articles") / f"{keyword}_producthunt.json"
    chunks = []
    if path.exists():
        data = load_json(path)
        for item in data:
            name = item.get("name", "")
            tagline = item.get("tagline", "")
            url = item.get("url", "")
            chunks.append(f"[Product Hunt]\n{name}\n{tagline}\n{url}")
    return chunks


def build_context_chunks_from_keywords(keywords: List[str]) -> List[str]:
    all_chunks = []
    for keyword in keywords:
        all_chunks.extend(load_reddit_chunks(keyword))
        all_chunks.extend(load_reddit_trends(keyword))
        all_chunks.extend(load_news_chunks(keyword))
        all_chunks.extend(load_stock_chunks(keyword))
        all_chunks.extend(load_producthunt_chunks(keyword))
        all_chunks.extend(load_google_trends_chunks(keyword))
    return all_chunks


def embed_documents(docs: List[str]):
    """Embeds and stores documents into FAISS index and returns vectorstore."""
    if not os.path.exists(EMBEDDINGS_DIR):
        os.makedirs(EMBEDDINGS_DIR)

    all_chunks = []
    langchain_docs = []
    for doc in docs:
        chunks = chunk_text(doc)
        all_chunks.extend(chunks)
        langchain_docs.extend([Document(page_content=chunk) for chunk in chunks])

    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(langchain_docs, embeddings_model)
    vectorstore.save_local(str(EMBEDDINGS_DIR))
    print(f"[✅] Embedded {len(all_chunks)} chunks and saved to {INDEX_PATH}")
    return vectorstore


def load_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(
        folder_path=str(EMBEDDINGS_DIR),
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )
    return vectorstore


def retrieve_top_k_chunks(vectorstore, query: str, k: int = 5) -> List[str]:
    retriever = vectorstore.as_retriever(search_type="mmr", k=k)
    docs = retriever.get_relevant_documents(query)
    print("\n[📂] Retrieved Documents from FAISS:")
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i + 1} ---")
        print(doc.page_content[:1000])
    return [doc.page_content for doc in docs]


def embed_from_json(data: Dict):
    """Entry point: receives {'interests': [...]} and embeds all content."""
    interests = data.get("interests", [])
    print(f"[ℹ️] Embedding content for: {interests}")
    chunks = build_context_chunks_from_keywords(interests)
    if not chunks:
        print("[⚠️] No content found to embed.")
        return
    embed_documents(chunks)
