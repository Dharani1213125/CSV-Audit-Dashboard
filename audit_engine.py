import pandas as pd
import numpy as np

def run_audit(df, label_col):
    results = {}

    results['missing_values'] = df.isnull().sum().reset_index()
    results['missing_values'].columns = ['Column', 'Missing Count']

    results['duplicate_rows'] = df[df.duplicated()]

    if label_col in df.columns:
        results['class_distribution'] = df[label_col].value_counts().reset_index()
        results['class_distribution'].columns = ['Label', 'Count']

    outliers = []
    for col in df.select_dtypes(include=np.number).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        mask = (df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)
        outlier_rows = df[mask]
        if not outlier_rows.empty:
            outliers.append(outlier_rows)
    results['outliers'] = pd.concat(outliers) if outliers else pd.DataFrame()

    if df[label_col].dtype == 'object':
        normalized = df[label_col].astype(str).str.strip().str.lower()
        inconsistency_df = normalized.value_counts().reset_index()
        inconsistency_df.columns = ['Normalized Label', 'Count']
        results['label_inconsistencies'] = inconsistency_df

    constant_cols = [col for col in df.columns if df[col].nunique() == 1]
    results['constant_columns'] = pd.DataFrame({'Column': constant_cols})

    high_card = [col for col in df.select_dtypes(include='object').columns if df[col].nunique() > 50]
    results['high_cardinality'] = pd.DataFrame({'Column': high_card})

    mixed_type = []
    for col in df.columns:
        if df[col].map(type).nunique() > 1:
            mixed_type.append(col)
    results['mixed_type_columns'] = pd.DataFrame({'Column': mixed_type})

    return results

# ✅ Add this to support Health Score
def calculate_score(df, audit_result):
    score = 100

    if audit_result.get('missing_values') is not None:
        if audit_result['missing_values']['Missing Count'].sum() > 0:
            score -= 15

    if audit_result.get('duplicate_rows') is not None:
        if not audit_result['duplicate_rows'].empty:
            score -= 15

    if audit_result.get('outliers') is not None:
        if not audit_result['outliers'].empty:
            score -= 10

    if audit_result.get('constant_columns') is not None:
        if not audit_result['constant_columns'].empty:
            score -= 10

    if audit_result.get('high_cardinality') is not None:
        if not audit_result['high_cardinality'].empty:
            score -= 10

    if audit_result.get('mixed_type_columns') is not None:
        if not audit_result['mixed_type_columns'].empty:
            score -= 10

    return max(score, 0)
