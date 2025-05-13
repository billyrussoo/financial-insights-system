import json
import re
from typing import Tuple, Any
from ast import literal_eval
def clean_llm_json_string(raw: str) -> str:
    """
    Heuristically clean malformed LLM JSON strings.
    This includes:
    - Fixing bad keys or unquoted values
    - Replacing illegal trailing commas
    - Escaping quotes
    """
    # Remove invalid trailing commas
    raw = re.sub(r",(\s*[}\]])", r"\1", raw)

    # Fix known malformed keys or fragments
    raw = re.sub(r'("Why this article matters: ")([^"]+)', r'"summary": "\2"', raw)

    # Replace entries like:  "AAPL -1.8%, MSFT +2.2%" (not a key-value pair)
    raw = re.sub(r'"QUICK CONTEXT":\s*{\s*"([^"]+)"\s*}', r'"QUICK CONTEXT": {"stock_movement": "\1"}', raw)

    return raw

def safe_parse_llm_json(raw):
    # If raw is already a dict, just return it
    if isinstance(raw, dict):
        return raw, False

    # Try to parse as-is
    try:
        return json.loads(raw), False
    except json.JSONDecodeError as e:
        print("[❌ JSON DECODE ERROR] Failed to parse response as JSON.")

        # 🔧 Attempt to auto-fix common issues
        fixed_raw = raw

        # Fix trailing commas (optional enhancement)
        fixed_raw = re.sub(r",\s*([}\]])", r"\1", fixed_raw)

        # Fix missing closing curly brace in lists
        fixed_raw = re.sub(r'("summary":\s*".+?")\s*\]', r'\1}\n]', fixed_raw, flags=re.DOTALL)

        try:
            return json.loads(fixed_raw), True
        except Exception as inner_e:
            print(f"[❌ Fallback parsing failed] {inner_e}")
            return {}, True

