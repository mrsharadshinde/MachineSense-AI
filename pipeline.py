import os
from analyze_pdf_kv import run_extraction
from validate_maintenance import run_validation 
from model_predictor import predict
from maintenance_report_generator import generate_report

def run_pipeline(pdf_path: str):
    '''
    End-to-end pipeline to process a maintenance report PDF
    1) Extract key-values and tables from PDF
    2) Validate extracted data
    3) Predict maintenance risk
    4) Generate PDF report
    '''
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Input PDF file not found: {pdf_path}")
    
    print("\n🚀 Running MachineSense AI pipeline")
    print(f"Input PDF: {pdf_path}")

    # Step 1: Extract structured data from PDF
    print("\nStep 1: Extracting data from PDF...")
    json_path = run_extraction(pdf_path)

    # Step 2: Validate extracted data
    print("\nStep 2: Validating extracted data...")
    completeness_score, health_score = run_validation(structured_json_path=json_path)

    # Step 3: Predict maintenance risk
    print("\nStep 3: Predicting maintenance risk with Ai...")
    risk_label, _issues = predict()

    print(f"\nGenerating final AI report...")
    report_path = generate_report()

    return {
        "json_path": json_path,
        "completeness_score": completeness_score,
        "health_score": health_score,
        "risk_label": risk_label,
        "report_path": report_path,
    }

if __name__ == "__main__":
    sample_pdf = "sample_docs/maintenance_report_sample2.pdf"
    results = run_pipeline(sample_pdf)
    print("\nPipeline completed. Results:")
