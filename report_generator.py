import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os

def generate_csv_report(results, csv_path):
    """
    Save each result DataFrame to a single CSV file by appending section headers.
    """
    with open(csv_path, 'w', encoding='utf-8') as f:
        for section, df in results.items():
            f.write(f"--- {section.upper()} ---\n")
            if isinstance(df, pd.DataFrame) and not df.empty:
                df.to_csv(f, index=False)
            else:
                f.write("No data found\n")
            f.write("\n\n")


def generate_pdf_report(results, pdf_path):
    """
    Create a basic PDF summary report with section names and summary stats.
    """
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "AI Training Data Audit Summary Report")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 40

    for section, df in results.items():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"{section.replace('_', ' ').title()}")
        y -= 20
        c.setFont("Helvetica", 11)

        if isinstance(df, pd.DataFrame) and not df.empty:
            summary = df.head(3).to_string(index=False)
            for line in summary.split('\n'):
                if y < 100:
                    c.showPage()
                    y = height - 50
                c.drawString(60, y, line)
                y -= 15
        else:
            c.drawString(60, y, "No data found")
            y -= 20

        y -= 20

    c.save()
