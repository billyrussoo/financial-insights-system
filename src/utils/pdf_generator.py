from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap

def generate_pdf_report(report_data: dict, keyword: str):
    ensure_directory(REPORTS_PDF_DIR)
    pdf_path = REPORTS_PDF_DIR / f"{keyword}_report.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"📄 Financial Report: {keyword}")
    y -= 40

    c.setFont("Helvetica", 10)
    for section, content in report_data.items():
        if y < 100:
            c.showPage()
            y = height - 50

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, section.replace("_", " ").title())
        y -= 20

        c.setFont("Helvetica", 10)
        wrapped_lines = wrap(content, width=90)  # Wrap long text
        for line in wrapped_lines:
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(60, y, line)
            y -= 15
        y -= 10  # Extra spacing between sections

    c.save()
    print(f"📄 PDF report saved to: {pdf_path}")
