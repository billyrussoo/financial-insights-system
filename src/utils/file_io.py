import json
from pathlib import Path

def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_text(filepath):
    return Path(filepath).read_text(encoding="utf-8")

def write_text(filepath, text):
    Path(filepath).write_text(text, encoding="utf-8")
