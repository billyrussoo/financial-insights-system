# src/utils/text_helpers.py

import re
import os


def read_time(text: str, words_per_minute: int = 200) -> str:
    words = len(re.findall(r'\w+', text))
    minutes = words / words_per_minute
    return f"{max(1, round(minutes))} min read"


def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def chunk_text(text: str, max_chunk_size: int = 500) -> list[str]:
    """
    Splits long text into overlapping chunks for embedding.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_chunk_size):
        chunk = words[i:i + max_chunk_size]
        chunks.append(' '.join(chunk))
    return chunks


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)
