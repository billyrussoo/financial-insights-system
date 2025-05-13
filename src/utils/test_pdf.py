from pdf_generator import create_pdf

sample_json = {
    "title": "Test Report",
    "sections": [
        {"heading": "Overview", "content": "This is a test overview."},
        {"heading": "Details", "content": "These are some test details."}
    ]
}

output_path = "test_output.pdf"
create_pdf(sample_json, output_path)
