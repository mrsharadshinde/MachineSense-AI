#model_predictor.py

import json
from datetime import datetime
import os
import re
import joblib
import pandas as pd
from utils import parse_date, read_completeness_score

#paths 
STRUCTURED_JSON = 'outputs/structured_output.json'
VALIDATION_SUMMARY = 'outputs/validation_summary.txt'
MODEL_PATH = 'models/maintenance_risk_model.pkl'
OUTPUT_FEATURES_FILE = 'outputs/predicted_features.csv'

#load traind model
model = joblib.load(MODEL_PATH)

    
def extract_features():
    issue = []
    # 1) Load JSON data
    with open(STRUCTURED_JSON, 'r', encoding="utf-8") as f:
        data = json.load(f)

    machine_info = data.get('machine_info', {})
    tables = data.get('tables', [])

    # 2) Document completeness from validation_summary.txt
    document_completeness = read_completeness_score()

    # 3) Installation date → machine_age_days
    install_date_str = machine_info.get('Installation Date', '')
    install_date = parse_date(install_date_str)  # parse_date from utils

    today = datetime.today()
    if install_date:
        machine_age_days = (today - install_date).days
    else:
        machine_age_days = 365  # fallback

    # 4) Operating hours: "1216 Hours |" → 1216
    hours_val = machine_info.get('Machine Operating Hours', "")
    hours_val = hours_val.replace("\n", " ").strip()

    # Use regex to extract only digits (more robust)
    match = re.search(r'\d+', hours_val)
    if match:
        try:
            operating_hours = int(match.group(0))
        except ValueError:
            operating_hours = 1000
    else:
        operating_hours = 1000  # fallback

    # 5) Extract warning_count & checklist_items from LAST table (maintenance checklist)
    warning_count = 0
    checklist_items = 0
    
    if tables:
        maintenance_table = tables[-1]  # Last table is the checklist

        rows = {}
        for cell in maintenance_table:
            r = cell.get('row')
            if r is None:
                continue
            rows.setdefault(r, []).append(cell)

        for _, cells in rows.items():
            row_text = " ".join(c.get('text', "") for c in cells)

            # Skip header row: "Component | Condition | Status"
            if "Component" in row_text and "Condition" in row_text:
                continue    

            # Count as checklist entry if the row has any text
            if any(c.get('text', "").strip() for c in cells):
                checklist_items += 1

            # Count warnings
            if "⚠" in row_text:
                warning_count += 1
                issue.append(row_text.strip())

    # 6) Build one-row dataframe for model input with SAME feature names as training
    df = pd.DataFrame([{
        'document_completeness': document_completeness,
        'warning_count': warning_count,
        'checklist_items': checklist_items,
        'machine_age_days': machine_age_days,
        'operating_hours': operating_hours, 
    }])

    # 7) Save features to CSV (for debugging/verification)
    os.makedirs('outputs', exist_ok=True)
    df.to_csv(OUTPUT_FEATURES_FILE, index=False)

    return df, issue

def predict():
    df, issue = extract_features()

    print("Extracted Features:")
    print(df)
    
    #make prediction
    prediction = model.predict(df)[0]
    print(f"Preddicted Risk Level: {prediction}")

    os.makedirs('outputs', exist_ok= True)
    with open('outputs/risk_prediction.txt', 'w', encoding='utf-8') as f:
        f.write(f"Predicted Risk Level: {str(prediction)}\n")
    
    return prediction, issue

if __name__ == "__main__":
    predict()
