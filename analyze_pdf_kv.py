from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
import os 
from utils import  normalize_extracted_text

#------------------ Azure form recognizer key Configuration ---------------------------
ENDPOINT = "Insert your endpoint here"
KEY = "Insert your key here"
#-----------------------------------------------------------

OUTPUT_PATH = "outputs/structured_output.json"

def run_extraction(pdf_path: str, output_json_path: str = OUTPUT_PATH):
    os.makedirs("outputs", exist_ok=True)

    client = DocumentAnalysisClient(
        endpoint=ENDPOINT,
        credential = AzureKeyCredential(KEY)
    )

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-document", document=f)

        result = poller.result()


    #---------- Print key-value pairs----------------
    machine_info = {}
    print("---- Key-Value Pairs ----")
    for kv in result.key_value_pairs:
        key = normalize_extracted_text(kv.key.content) if kv.key else None
        value = normalize_extracted_text(kv.value.content) if kv.value else None

        if key:
            machine_info[key] = value
            print(f"{key}: {value}")
    
    #........parse table into python list--------------
    tables_data = []
    print("----- table -----")
    for table in result.tables:
        print("new table")
        table_rows = {}
        # try to detect headers 
        headers = []
        for cell in table.cells:
            if cell.row_index == 0:
                headers.append(normalize_extracted_text(cell.content))
            r,c = cell.row_index, cell.column_index
            text = normalize_extracted_text(cell.content)
            print(f"cell[{r},{c}] = {text}")

        # keep table parsing simple for now 
        tables_data.append([
            {
            "row": cell.row_index,
            "column": cell.column_index,
            "text": normalize_extracted_text(cell.content)
            }
            for cell in table.cells
        ])

    #----------combine into one structure object ----------------
    data = {
        "machine_info": machine_info,
        "tables": tables_data,
    }

    #save JSON output for later use (DB/API/ML)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(data , f,  indent= 2, ensure_ascii= False)
    
    print(f"Structured output saved to {output_json_path}")

    return output_json_path



if __name__ == "__main__":
    sample_pdf = "sample_docs/maintenance_report_sample2.pdf"
    run_extraction(sample_pdf)
