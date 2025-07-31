from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import pandas as pd
from audit_engine import run_audit
from report_generator import generate_csv_report, generate_pdf_report

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    label_col = request.form.get('label')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to read CSV: {str(e)}"}), 500

    # Run audit
    audit_results = run_audit(df, label_col)

    # Generate reports
    csv_path = os.path.join(REPORT_FOLDER, 'audit_report.csv')
    pdf_path = os.path.join(REPORT_FOLDER, 'audit_report.pdf')

    generate_csv_report(audit_results, csv_path)
    generate_pdf_report(audit_results, pdf_path)

    return jsonify({
        "csv_report": f"/download/csv",
        "pdf_report": f"/download/pdf"
    })

@app.route('/download/csv')
def download_csv():
    return send_file(os.path.join(REPORT_FOLDER, 'audit_report.csv'), as_attachment=True)

@app.route('/download/pdf')
def download_pdf():
    return send_file(os.path.join(REPORT_FOLDER, 'audit_report.pdf'), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
