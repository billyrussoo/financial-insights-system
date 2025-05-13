# rag_pipeline/report_generator.py

import json
from query_ollama import query_llm
from prompt_builder import build_prompt
from src.utils.file_io import save_json
from src.utils.pdf_generator import create_pdf
from pathlib import Path
from datetime import datetime


def generate_report(persona_name: str, content_paths: list[str], output_basename: str = None):
    """
    Main pipeline function: builds prompt, queries LLM, saves JSON and PDF report.

    Args:
        persona_name (str): Name of the persona file in /personas (without .json).
        content_paths (list): List of article or data files (txt or json).
        output_basename (str, optional): Optional custom output name.
    """
    # Step 1: Build the full prompt
    prompt = build_prompt(persona_name, content_paths)

    # Step 2: Query the local Ollama LLaMA 3 model
    llm_response = query_llm(prompt)

    # Step 3: Parse and validate LLM response
    try:
        report_data = json.loads(llm_response)
    except json.JSONDecodeError:
        print("❌ Error: LLM response could not be parsed as JSON.")
        return

    # Step 4: Define output paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = output_basename or f"{persona_name}_{timestamp}"
    json_path = Path("reports/json") / f"{base_name}.json"
    pdf_path = Path("reports/pdf") / f"{base_name}.pdf"

    # Step 5: Save structured JSON and generate PDF
    save_json(report_data, json_path)
    create_pdf(report_data, pdf_path)

    print(f"✅ Report saved:\n   JSON: {json_path}\n   PDF: {pdf_path}")
