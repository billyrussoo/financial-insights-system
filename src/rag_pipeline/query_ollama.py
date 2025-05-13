import os
import re
import json
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()

# Load Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is not set in the environment")

# Initialize LangChain ChatOpenAI for Groq with LLaMA 3
llm = ChatOpenAI(
    openai_api_key=GROQ_API_KEY,
    openai_api_base="https://api.groq.com/openai/v1",
    model_name="llama3-70b-8192",
    temperature=0.3
)

def extract_json_block(text: str) -> str:
    """Extracts the first valid JSON object from a block of text using regex."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None

def run_llm(final_prompt: str) -> dict:
    """
    Sends a prompt to the LLM and returns a parsed JSON dictionary.
    Handles messy LLM output gracefully.
    """
    try:
        messages = [
            SystemMessage(
                content="You are a helpful, concise financial analyst who generates structured JSON reports from data and persona context."
            ),
            HumanMessage(content=final_prompt)
        ]
        response = llm(messages)
        raw_output = response.content

        # Debug: print raw LLM response
        print("\n[🧠 RAW LLM RESPONSE]:\n", raw_output)

        # Try to extract JSON block
        json_block = extract_json_block(raw_output)
        if json_block:
            return json.loads(json_block)
        else:
            print("[⚠️ LLM PARSE WARNING] No valid JSON object found.")
            return {}

    except json.JSONDecodeError as je:
        print("[❌ JSON DECODE ERROR] Failed to parse response as JSON.")
        print("🔎 Raw Output:\n", raw_output)
        return {}

    except Exception as e:
        print(f"[🔥 LLM ERROR] Failed to query Groq LLaMA 3:\n{e}")
        return {}
