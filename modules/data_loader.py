"""
data_loader.py
----------------
Handles dataset loading, file validation, and column-type detection
for the AutoInsight application.
"""

import io
import pandas as pd
import streamlit as st


ALLOWED_EXTENSIONS = ["csv", "xlsx", "xls"]


def validate_file(uploaded_file):
    """
    Validate that the uploaded file has an allowed extension.

    Returns:
        (is_valid: bool, message: str)
    """
    if uploaded_file is None:
        return False, "No file uploaded."

    file_name = uploaded_file.name
    extension = file_name.split(".")[-1].lower() if "." in file_name else ""

    if extension not in ALLOWED_EXTENSIONS:
        return False, (
            f"Unsupported file type '.{extension}'. "
            f"Please upload a CSV or Excel (.xlsx/.xls) file."
        )
    return True, "Valid file."


def _deduplicate_columns(columns):
    """Rename duplicate column names by appending a numeric suffix."""
    seen = {}
    new_columns = []
    for col in columns:
        col_str = str(col).strip() if str(col).strip() else "Unnamed"
        if col_str not in seen:
            seen[col_str] = 0
            new_columns.append(col_str)
        else:
            seen[col_str] += 1
            new_columns.append(f"{col_str}_{seen[col_str] + 1}")
    return new_columns


@st.cache_data(show_spinner="Reading dataset...")
def load_dataset(file_bytes, file_name):
    """
    Load a dataset from raw bytes into a Pandas DataFrame.

    Cached on (file_bytes, file_name): re-uploading the exact same file
    will not trigger a re-read or re-computation.

    Returns:
        (df, error_message) -- df is None if loading failed.
    """
    extension = file_name.split(".")[-1].lower()

    try:
        buffer = io.BytesIO(file_bytes)

        if extension == "csv":
            df = pd.read_csv(buffer)
        elif extension == "xlsx":
            df = pd.read_excel(buffer, engine="openpyxl")
        elif extension == "xls":
            df = pd.read_excel(buffer)
        else:
            return None, f"Unsupported file type '.{extension}'."

        if df is None or df.shape[1] == 0:
            return None, "The uploaded file has no columns and cannot be analyzed."

        if df.shape[0] == 0:
            return None, "The uploaded file has no data rows to analyze."

        # Handle duplicate / blank column names safely
        df.columns = _deduplicate_columns(df.columns)

        return df, None

    except Exception as exc:
        return None, f"Could not read the file. Details: {exc}"


@st.cache_data(show_spinner=False)
def detect_column_types(df):
    """
    Classify each column into numeric, categorical, datetime, or boolean.
    Also attempts to detect datetime values stored as text/object columns.

    Returns:
        dict with keys 'numeric', 'categorical', 'datetime', 'boolean',
        each mapping to a list of column names.
    """
    numeric_cols, categorical_cols, datetime_cols, boolean_cols = [], [], [], []

    for col in df.columns:
        series = df[col]

        if pd.api.types.is_bool_dtype(series):
            boolean_cols.append(col)
        elif pd.api.types.is_numeric_dtype(series):
            numeric_cols.append(col)
        elif pd.api.types.is_datetime64_any_dtype(series):
            datetime_cols.append(col)
        elif _looks_like_datetime(series):
            datetime_cols.append(col)
        else:
            categorical_cols.append(col)

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "datetime": datetime_cols,
        "boolean": boolean_cols,
    }


def _looks_like_datetime(series, sample_size=20, min_success_ratio=0.8):
    """
    Heuristic: sample a handful of non-null values from an object/string
    column and see if most of them parse as dates. Prevents misclassifying
    plain text columns as dates.
    """
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
        return False

    non_null = series.dropna()
    if non_null.empty or len(non_null) < 3:
        return False

    sample_size = min(sample_size, len(non_null))
    sample = non_null.sample(sample_size, random_state=42)

    success = 0
    for value in sample:
        try:
            # errors='raise' ensures we only count clean parses
            pd.to_datetime(value, errors="raise")
            success += 1
        except (ValueError, TypeError):
            continue

    return (success / sample_size) >= min_success_ratio


def get_basic_info(df):
    """Return a dict of high-level KPI values used by the summary cards."""
    n_rows, n_cols = df.shape
    total_missing = int(df.isna().sum().sum())
    total_cells = max(n_rows * n_cols, 1)
    missing_pct = round((total_missing / total_cells) * 100, 2)
    duplicate_rows = int(df.duplicated().sum())
    memory_usage_mb = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2)

    return {
        "rows": n_rows,
        "columns": n_cols,
        "missing_values": total_missing,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "memory_usage_mb": memory_usage_mb,
    }
