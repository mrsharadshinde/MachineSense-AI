# MachineSense AI – Industrial Maintenance Intelligence

An end-to-end AI system that:
- Extracts asset & maintenance data from unstructured PDF reports (OEM docs, checklists)
- Validates critical fields and computes document completeness & maintenance health score
- Predicts machine risk level (Good / Moderate / Poor) using a trained ML model
- Generates a professional PDF maintenance report
- Provides a Django web UI where users can upload maintenance PDFs and download AI-generated reports

---

## 🔧 Tech Stack

- **Backend**: Python, Django
- **AI/ML**: scikit-learn (RandomForest), pandas, numpy
- **Document AI**: Azure Document Intelligence (Form Recognizer)
- **Reporting**: ReportLab (PDF generation), Matplotlib (charts)
- **Frontend**: Bootstrap 5 (simple responsive UI)

---

## 🚀 Features

- PDF upload via web UI
- Azure-powered extraction of key-value pairs and tables
- Rule-based validation of required fields (dates, serial numbers, intervals, etc.)
- Computation of:
  - Document Completeness Score
  - Maintenance Health Score (from checklist warnings)
- ML model to classify risk: `Good`, `Moderate`, `Poor`
- AI-generated suggestions for components needing attention (e.g. CNC fan filter, cooling pump)
- Final PDF maintenance summary report with:
  - Machine info table
  - Validation summary table
  - Risk assessment
  - Health chart
  - Actionable suggestions

---

## 🧩 Architecture Workflow

1. **User uploads PDF** via Django UI
2. **Azure Document Intelligence** extracts key-values & tables → `structured_output.json`
3. **Validation module**:
   - Checks required fields (Installation Date, Maintenance Interval, etc.)
   - Counts checklist warnings (⚠) and computes health score
   - Writes `validation_summary.txt`
4. **ML model**:
   - Reads features (completeness, age, warnings, items, operating hours)
   - Predicts risk level (Good/Moderate/Poor)
   - Saves risk label
5. **Report Generator**:
   - Combines machine info + validation + ML output + suggestions
   - Creates `maintenance_report_YYYYMMDD_HHMMSS.pdf`
6. **UI**:
   - Shows risk, scores, and download button for the PDF

---

## 🛠 How to Run Locally

```bash
# 1. Clone repo
git clone https://github.com/<your-username>/Basic-ML.git
cd MachineSense-AI

# 2. Create & activate virtual env
python -m venv venv
venv\Scripts\activate   # on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set Azure credentials (in environment or .env)
AZURE_FORM_RECOGNIZER_ENDPOINT=...
AZURE_FORM_RECOGNIZER_KEY=...

# 5. Run Django server
python manage.py runserver

#6 project structure
MachineSense-AI/
│── analyze_pdf_kv.py
│── validate_maintenance.py
│── model_predictor.py
│── maintenance_report_generator.py
│── pipeline.py
│── manage.py
│── requirements.txt
│── README.md
│── outputs/           (generated reports & json)
│── uploads/           (uploaded PDFs)
│── maintenance/       (Django app)
│   ├── templates/
│   └── views.py
