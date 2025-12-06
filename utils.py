#utils.py 
from datetime import datetime
VALIDATION_SUMMARY = 'outputs/validation_summary.txt'
import os 
def is_invalid_value(value: str) -> bool:
    if value is None:
        return True
    v = value.strip()
    if v == "":
        return True
    if v in [":", ":unselected:", "|"]:
        return True
    return False

def normalize_extracted_text(text: str) -> str:
    if not text:
        return ""
    return (
        text.replace(":selected", "")
            .replace("\n", "")
            .strip()
    )

def format_display_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("|", "").strip()

# Try to parse dates safely (return None if format unknown)
def parse_date(date_str: str):
    if not date_str or is_invalid_value(date_str):
        return None
    for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

#load validation summary and extract completeness score
def read_completeness_score():
    if not os.path.exists(VALIDATION_SUMMARY):
        return None
    try:
        with open(VALIDATION_SUMMARY, "r", encoding="utf-8") as f:
            for line in f:
                if "document completeness score" in line.lower():
                    # Example line: "Document completeness score: 87.5%"
                    score = line.split(":")[1].strip().replace("%","")
                    try:
                        return float(score)
                    except ValueError:
                        return None
        return None
    except FileNotFoundError:
        return None