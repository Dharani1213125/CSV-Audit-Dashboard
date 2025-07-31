import streamlit as st
import pandas as pd
import chardet
import io
import matplotlib.pyplot as plt
import seaborn as sns
from audit_engine import run_audit, calculate_score
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

st.set_page_config(page_title="CSV Audit Dashboard", layout="wide")

# =======================
# 🎨 Custom CSS
# =======================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    background-color: #e6f0fa !important;
}
.title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    color: #1a508b;
    margin: 1em 0;
}
.section {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: none;
}
[data-testid="stSidebar"] {
    background-color: #1a508b !important;
    color: white;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
.center-upload {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
}
.stButton>button, .stDownloadButton>button {
    background-color: #1a508b;
    color: white;
    border-radius: 8px;
    padding: 0.5em 1.2em;
    font-weight: bold;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to", ["📝 Data Audit", "📊 Visualization Tool", "📈 Health Score"])

st.markdown("<div class='title'>📊 AI Training Data Audit System 📊</div>", unsafe_allow_html=True)

# File Upload
st.markdown('<div class="center-upload">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📎 Upload your dataset", type=["csv", "xlsx", "json"], key="fileUploader")
st.markdown('</div>', unsafe_allow_html=True)

df = None
if uploaded_file:
    uploaded_file.seek(0)
    rawdata = uploaded_file.read()
    encoding = chardet.detect(rawdata)["encoding"]
    uploaded_file.seek(0)
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding=encoding)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            df = pd.read_json(uploaded_file)
    except Exception as e:
        st.error(f"❌ Failed to load file. Error: {e}")

# PDF Generator
def generate_pdf_report(audit_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("AI Training Data Audit Report", styles['Title']))
    elements.append(Spacer(1, 12))

    for section, data in audit_data.items():
        elements.append(Paragraph(section.replace('_', ' ').title(), styles['Heading2']))
        if isinstance(data, pd.DataFrame) and not data.empty:
            table_data = [data.columns.tolist()] + data.astype(str).values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
        elif isinstance(data, pd.DataFrame):
            elements.append(Paragraph("No data found.", styles['Normal']))
        else:
            elements.append(Paragraph(str(data), styles['Normal']))
        elements.append(Spacer(1, 24))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ============= PAGE: Data Audit =============
if page == "📝 Data Audit":
    if df is not None and not df.empty:
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🔍 Preview of Uploaded Data")
        st.dataframe(df.head())

        possible_labels = [col for col in df.columns if df[col].nunique() <= 10 and df[col].dtype == 'object']
        auto_label = possible_labels[0] if possible_labels else df.columns[0]
        label_col = st.selectbox("Choose the label/target column:", df.columns, index=df.columns.get_loc(auto_label))
        st.markdown("</div>", unsafe_allow_html=True)

        if label_col:
            st.markdown("<div class='section'>", unsafe_allow_html=True)
            st.subheader("🧠 Running Data Audit...")

            try:
                audit_result = run_audit(df, label_col)
                st.success("✅ Audit completed successfully.")
                full_report_csv = pd.DataFrame()

                for section, result_df in audit_result.items():
                    if isinstance(result_df, pd.DataFrame) and not result_df.empty:
                        st.markdown(f"#### 📌 {section.replace('_', ' ').title()}")
                        st.dataframe(result_df)

                        csv_data = result_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"⬇️ Download {section} as CSV",
                            data=csv_data,
                            file_name=f"{section}.csv",
                            mime="text/csv",
                            key=f"csv_{section}"
                        )

                        full_report_csv = pd.concat([
                            full_report_csv,
                            pd.DataFrame({section: [""]}),
                            result_df,
                            pd.DataFrame({section: [""]})
                        ], ignore_index=True)

                if not full_report_csv.empty:
                    combined_csv = full_report_csv.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Download Full Audit Report as CSV",
                        data=combined_csv,
                        file_name="full_audit_report.csv",
                        mime="text/csv"
                    )

                # PDF Button
                pdf_buffer = generate_pdf_report(audit_result)
                st.download_button(
                    label="⬇️ Download Full Audit Report as PDF",
                    data=pdf_buffer,
                    file_name="full_audit_report.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"❌ Audit failed: {e}")

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("📎 Please upload a dataset to begin.")

# ============= PAGE: Visualization =============
elif page == "📊 Visualization Tool":
    if df is not None and not df.empty:
        st.subheader("📈 Visualizations")

        possible_label_cols = [col for col in df.columns if df[col].nunique() <= 10]
        if possible_label_cols:
            vis_label = st.selectbox("Select column for class distribution:", possible_label_cols)
            dist_df = df[vis_label].value_counts().reset_index()
            dist_df.columns = ['Label', 'Count']
            fig1, ax1 = plt.subplots(figsize=(3, 3))
            ax1.pie(dist_df['Count'], labels=dist_df['Label'], autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)

        num_cols = df.select_dtypes(include='number')
        if not num_cols.empty and num_cols.shape[1] > 1:
            st.write("🔗 Correlation Heatmap")
            fig2, ax2 = plt.subplots(figsize=(5, 3))
            sns.heatmap(num_cols.corr(), annot=True, cmap='coolwarm', ax=ax2)
            st.pyplot(fig2)

        st.write("📦 Boxplots for Numerical Columns")
        for col in num_cols.columns:
            fig3, ax3 = plt.subplots(figsize=(4, 2))
            sns.boxplot(x=df[col], ax=ax3)
            st.pyplot(fig3)
    else:
        st.warning("📎 Please upload a dataset to visualize.")

# ============= PAGE: Health Score =============
elif page == "📈 Health Score":
    if df is not None and not df.empty:
        possible_labels = [col for col in df.columns if df[col].nunique() <= 10 and df[col].dtype == 'object']
        auto_label = possible_labels[0] if possible_labels else df.columns[0]
        label_col = st.selectbox("Choose label column for scoring:", df.columns, index=df.columns.get_loc(auto_label), key="score_label")

        audit_result = run_audit(df, label_col)
        score = calculate_score(df, audit_result)
        st.markdown(f"""
            <div class='section'>
                <h2 style='color:#1a508b;'>📊 Dataset Health Score</h2>
                <h1 style='font-size:64px; color:#28a745;'>{score}/100</h1>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("📎 Please upload a dataset to calculate health score.")
