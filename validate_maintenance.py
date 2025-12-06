# validate_maintenance.py 

import json 
from datetime import datetime 
from utils import is_invalid_value, parse_date
import os

structured_Json_path = "output/structured_output.json"

#2) Try to parse dates safely (return None if format unknown)


def run_validation(structured_json_path:str = "outputs/structured_output.json", 
                   summary_output_path: str = "outputs/validation_summary.txt"):
    # 3) Load the JSON 
    with open(structured_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    
    machine_info = data.get("machine_info", {})
    tables = data.get("tables", [])

    print("\n---- Validating Machine Info ----")

    #4) define required fields and their types 
    required_fields = [
        "Machine Model",
        "Serial Number",
        "Installation Date", 
        "Customer Site", 
        "Maintanance Interval ",
        "Inspection Date", 
        "Next Due Date",
        "Machine Operating Hours",

    ]

    #check if there is any mistake 
    missing_fields = []
    for field in required_fields:
        value = machine_info.get(field)
        if is_invalid_value(value):
            missing_fields.append(field)
            print(f"Missing or Invalid : {field}")
        else:
            print(f"ok : {field}: {value}")


    #5) Basic Completness Score
    total_fields = len(required_fields)
    valid_fields = total_fields - len(missing_fields)
    completeness_score = round((valid_fields / total_fields) * 100, 2)

    print(f"\n Document Completeness Score: {completeness_score}%")

    #6) date sanity checks
    insp_date = parse_date(machine_info.get("Inspection Date"))
    next_due_date = parse_date(machine_info.get("Next Due Date"))

    if insp_date and next_due_date:
        if next_due_date <= insp_date:
            print("Warning: Next Due Date is before or same as Instpection Date ")
        else:
            print("Date checks passed ")
    else:
        print("Date check : Could not parse one or both dates ")

    #7) Maintanance checklist health form tables (simple count of ⚠)
    warning_count = 0
    total_items = 0

    for table in tables:
        # each table is a list of cell dicts: {"row", "col", "text"}
        # We look for rows that contain a status cell with '⚠'
        # We will roughly assume: if any cell in the row has ⚠, we count that as a warning item.
        # First, group cells by row

        rows = {} 
        for cell in table:
            r = cell["row"]
            rows.setdefault(r, []).append(cell)
        
        for r, cells in rows.items():
            row_text = " ".join([c["text"] for c in cells])
            #skip header rows
            if "Component" in row_text or "Field" in row_text or "Attribute" in row_text:
                continue
            if any(c["text"] for c in cells):
                total_items += 1
            if "⚠" in row_text:
                warning_count += 1

    print(f"\nMaintanance Checklist Health")
    print(f"Total Items Checked: {total_items}")
    print(f"total Warnings Found: {warning_count}")

    if total_items > 0:
        health_score = round((1-warning_count/ total_items) * 100, 2)
        print(f"Maintanance Health Score: {health_score}%")
    else:
        print("No items found in maintanance checklist tables.")

    os.makedirs("outputs", exist_ok=True)
    #8) Save validation summary to a content file
    with open(summary_output_path, "w") as f:
        f.write(f"Document completeness score: {completeness_score}%\n")
        f.write(f"Warnings found: {warning_count}\n")
        f.write(f"Checklist items inspected: {total_items}\n")
        if total_items > 0:
            f.write(f"Maintanance Health Score: {health_score}%\n")
        else:
            f.write("No items found in maintanance checklist tables.\n")
    
    print(f"\nValidation summary saved to {summary_output_path}")
    return completeness_score, health_score

if __name__ == "__main__":
    run_validation()
