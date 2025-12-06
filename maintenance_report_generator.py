# maintenance_report_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable,Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

import json
import os
import matplotlib.pyplot as plt

from utils import is_invalid_value, format_display_text
from src.suggestion_engine import generate_suggestions


STRUCTURED_JSON_PATH = "outputs/structured_output.json"
OUTPUT_REPORT_PATH = "outputs/maintenance_report.pdf"
VALIDATION_SUMMARY_PATH = "outputs/validation_summary.txt"
RISK_PREDICTION_PATH = "outputs/risk_prediction.txt"
HEALTH_CHART_PATH = "outputs/health_chart.png"


# 1) Load JSON
def load_data():
    with open(STRUCTURED_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# 2) Validation summary lines
def extract_summary_from_validation():
    lines = []
    if not os.path.exists(VALIDATION_SUMMARY_PATH):
        return lines
    with open(VALIDATION_SUMMARY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.strip())
    return lines


# 3) Health score from validation_summary.txt
def extract_health_score():
    if not os.path.exists(VALIDATION_SUMMARY_PATH):
        return None
    with open(VALIDATION_SUMMARY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if "maintanance health score" in line.lower():
                parts = line.split(":")
                if len(parts) >= 2:
                    val = parts[1].strip().replace("%", "")
                    try:
                        return float(val)
                    except ValueError:
                        return None
    return None


# 4) Completeness score for chart
def extract_completeness_score():
    if not os.path.exists(VALIDATION_SUMMARY_PATH):
        return None
    with open(VALIDATION_SUMMARY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if "document completeness score" in line.lower():
                parts = line.split(":")
                if len(parts) >= 2:
                    val = parts[1].strip().replace("%", "")
                    try:
                        return float(val)
                    except ValueError:
                        return None
    return None


# 5) Read risk label from file (created by model_predictor.py)
def read_risk_label():
    if not os.path.exists(RISK_PREDICTION_PATH):
        return "Unknown"
    with open(RISK_PREDICTION_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


# 6) Extract components needing attention (⚠) from last table
def get_attention_items(data: dict):
    tables = data.get("tables", [])
    attention_items = []

    if not tables:
        return attention_items

    maintenance_table = tables[-1]  # last table is checklist

    rows = {}
    for cell in maintenance_table:
        r = cell.get("row")
        if r is None:
            continue
        rows.setdefault(r, []).append(cell)

    for _, cells in rows.items():
        row_text = " ".join(c.get("text", "") for c in cells)
        # skip header
        if "Component" in row_text and "Condition" in row_text:
            continue
        if "⚠" in row_text:
            comp_name = None
            for c in cells:
                if c.get("column") == 0:
                    comp_name = c.get("text", "").strip()
                    break
            if comp_name:
                attention_items.append(comp_name)

    return attention_items


# 7) Create a small bar chart for completeness vs health
def create_health_chart(completeness, health_score, out_path=HEALTH_CHART_PATH):
    if completeness is None or health_score is None:
        return
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    metrics = ["Completeness", "Health"]
    values = [completeness, health_score]

    plt.figure(figsize=(4, 3))
    plt.ylim(0, 100)
    plt.bar(metrics, values)
    plt.ylabel("Score (%)")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


# 8) Build the PDF
def generate_pdf_report(machine_info, validation_data, health_score, risk_label, attention_items, suggestions):
    doc = SimpleDocTemplate(OUTPUT_REPORT_PATH, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

  
    # Header / Branding
    story.append(Paragraph("<b>MachineSense AI</b>", styles["Title"]))
    story.append(Paragraph("Predictive & Preventive Maintenance Intelligence System"))
    story.append(Spacer(1, 15))

    story.append(HRFlowable(width="100%", thickness=1, color="black"))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Maintenance Analysis Report</b>", styles["Heading2"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Machine Information</b>", styles["Heading2"]))

    machine_rows = [["Field", "Value"]]  # table header

    for key, value in machine_info.items():
        if not is_invalid_value(str(value)):
            machine_rows.append([key, format_display_text(str(value))])

    machine_table = Table(machine_rows, colWidths=[180, 330])

    machine_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C5D9F1")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
]))

    story.append(machine_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Validation Summary</b>", styles["Heading2"]))

    if validation_data:

    # Build table rows with header first
        summary_rows = [["Check", "Status"]]

        for line in validation_data:
            if ":" in line:
                parts = line.split(":", 1)
                summary_rows.append([parts[0].strip(), parts[1].strip()])
            else:
                summary_rows.append(["Summary", line.strip()])
        # Create table 
        summary_table = Table(summary_rows, colWidths=[220, 290])

        # Style the table
        summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2DCDB")),  # Light red header
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F9E8E7")]),
        ]))

        story.append(summary_table)

    else:
        story.append(Paragraph("No validation summary available.", styles["Normal"]))

    story.append(Spacer(1, 15))
    # Health score
    story.append(Paragraph("<b>Maintenance Health Score</b>", styles["Heading2"]))
    if health_score is not None:
        story.append(Paragraph(f"Score: {health_score} %", styles["Normal"]))
    else:
        story.append(Paragraph("Score: N/A", styles["Normal"]))
    story.append(Spacer(1, 15))

    # Chart
    if os.path.exists(HEALTH_CHART_PATH):
        story.append(Paragraph("<b>Health Overview</b>", styles["Heading2"]))
        story.append(Image(HEALTH_CHART_PATH, width=300, height=200))
        story.append(Spacer(1, 15))

    # Risk section
    story.append(Paragraph("<b>Machine Risk Assessment (ML)</b>", styles["Heading2"]))
    story.append(Paragraph(f"<b>{risk_label}</b>", styles["Normal"]))
    story.append(Spacer(1, 10))

    # Attention items
    story.append(Paragraph("<b>Components Needing Immediate Attention</b>", styles["Heading2"]))
    if attention_items:
        for comp in attention_items:
            story.append(Paragraph(f"⚠ {comp}", styles["Normal"]))
    else:
        story.append(Paragraph("No critical components detected in this cycle.", styles["Normal"]))
    story.append(Spacer(1, 15))

    # Suggestions
    story.append(Paragraph("<b>AI Maintenance Suggestions</b>", styles["Heading2"]))
    if suggestions:
        for s in suggestions:
            story.append(Paragraph("• " + s, styles["Normal"]))
    else:
        story.append(Paragraph("No suggestions available.", styles["Normal"]))
    story.append(Spacer(1, 15))

    # Footer
    story.append(Paragraph(
        "Report automatically generated by MachineSense AI using Azure Document Intelligence, "
        "rule-based validation and ML-based risk prediction.",
        styles["Italic"]
    ))

    doc.build(story)
    print(f"PDF report generated: {OUTPUT_REPORT_PATH}")

def generate_report()->str:
    print("Generating MachineSense AI maintenance PDF report...")

    data = load_data()
    machine_info = data.get("machine_info", {})

    validation_summary = extract_summary_from_validation()
    health_score = extract_health_score()
    completeness_score = extract_completeness_score()

    # Make chart
    create_health_chart(completeness_score, health_score)

    # Read risk label from risk_prediction.txt (created earlier by model_predictor.py)
    risk_label = read_risk_label()

    # Get attention items from checklist table
    attention_items = get_attention_items(data)

    # Generate suggestions
    suggestions = generate_suggestions(attention_items, risk_label)

    # Generate final PDF
    generate_pdf_report(
        machine_info,
        validation_summary,
        health_score,
        risk_label,
        attention_items,
        suggestions
    )
    print("Report generation completed.")
    return OUTPUT_REPORT_PATH
# 9) Orchestrate
if __name__ == "__main__":
       generate_report()
