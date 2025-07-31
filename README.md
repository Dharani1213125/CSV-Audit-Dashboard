# 📊 AI Training Data Audit System

A Streamlit-based web application that allows data scientists and analysts to audit CSV datasets for quality and readiness before using them in machine learning or statistical analysis.

---

## 🚀 Features

✅ Upload any CSV dataset with automatic encoding detection  
✅ Data preview and label column selection  
✅ Audit results for:
- Missing values
- Duplicate records
- Class imbalance
- Outliers (IQR method)
- Label inconsistencies (case/space mismatch)

✅ Download audit reports as:
- 📄 Section-wise CSV
- 📄 Full CSV summary
- 📄 PDF report (auto-formatted)

✅ Professional UI with a responsive layout and mild blue theme

---

## 🛠️ Tech Stack

| Layer        | Tools Used                   |
|--------------|------------------------------|
| Frontend     | Streamlit, HTML/CSS          |
| Backend      | Python, Pandas, NumPy        |
| Report Export| ReportLab (PDF), Pandas (CSV)|
| Utilities    | Chardet (Encoding detection) |

---

## 📦 Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-username/ai-data-audit-system.git
   cd ai-data-audit-system
