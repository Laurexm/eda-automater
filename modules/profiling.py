"""
profiling.py
--------------
Data profiling utilities: missing-value analysis, duplicate detection,
data type summaries, and descriptive statistics.
"""

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def get_missing_value_summary(df):
    """Return a DataFrame with missing count and percentage for every column."""
    missing_count = df.isna().sum()
    n_rows = len(df)
    missing_pct = (missing_count / n_rows * 100).round(2) if n_rows > 0 else missing_count * 0

    summary = pd.DataFrame({
        "Column": missing_count.index,
        "Missing Count": missing_count.values,
        "Missing %": missing_pct.values,
    })
    summary = summary.sort_values("Missing Count", ascending=False).reset_index(drop=True)
    return summary


@st.cache_data(show_spinner=False)
def get_dtype_summary(df):
    """Return a DataFrame summarizing each column's inferred data type."""
    return pd.DataFrame({
        "Column": df.columns,
        "Data Type": [str(dt) for dt in df.dtypes],
    })


def get_constant_columns(df):
    """Return column names that contain only a single unique value (ignoring NaNs)."""
    constant_cols = []
    for col in df.columns:
        if df[col].nunique(dropna=True) <= 1:
            constant_cols.append(col)
    return constant_cols


def get_high_missing_columns(df, threshold=50.0):
    """Return column names whose missing percentage exceeds the given threshold."""
    if len(df) == 0:
        return []
    missing_pct = df.isna().sum() / len(df) * 100
    return missing_pct[missing_pct > threshold].index.tolist()


def get_data_quality_summary(df):
    """
    Build a consolidated data-quality table combining missing values,
    data types, constant-column flags, and high-missingness flags.

    Returns:
        dict with keys: 'table' (DataFrame), 'duplicate_rows' (int),
        'constant_columns' (list), 'high_missing_columns' (list).
    """
    duplicate_rows = int(df.duplicated().sum())
    constant_cols = get_constant_columns(df)
    high_missing_cols = get_high_missing_columns(df)

    missing_df = get_missing_value_summary(df)
    dtype_df = get_dtype_summary(df)

    quality_df = missing_df.merge(dtype_df, on="Column", how="left")
    quality_df["Constant Column"] = quality_df["Column"].isin(constant_cols)
    quality_df["High Missingness (>50%)"] = quality_df["Column"].isin(high_missing_cols)

    return {
        "table": quality_df,
        "duplicate_rows": duplicate_rows,
        "constant_columns": constant_cols,
        "high_missing_columns": high_missing_cols,
    }


@st.cache_data(show_spinner=False)
def get_descriptive_stats(df, numeric_cols):
    """
    Return descriptive statistics (count, mean, median, std, min, quartiles, max)
    for the given numeric columns. Returns an empty DataFrame if none exist.
    """
    if not numeric_cols:
        return pd.DataFrame()

    stats = df[numeric_cols].describe().T
    stats["median"] = df[numeric_cols].median()

    ordered_cols = ["count", "mean", "median", "std", "min", "25%", "50%", "75%", "max"]
    ordered_cols = [c for c in ordered_cols if c in stats.columns]
    stats = stats[ordered_cols].round(3)
    stats.index.name = "Column"
    return stats.reset_index()


@st.cache_data(show_spinner=False)
def get_categorical_summary(df, categorical_cols, top_n=5):
    """
    Return a dict mapping each categorical column name to a small frequency
    table (top N most common values, counts, and percentages).
    """
    summaries = {}
    n_rows = len(df)
    for col in categorical_cols:
        value_counts = df[col].value_counts(dropna=True).head(top_n)
        if value_counts.empty:
            continue
        freq_df = pd.DataFrame({
            "Value": value_counts.index.astype(str),
            "Count": value_counts.values,
            "Percentage": (value_counts.values / n_rows * 100).round(2) if n_rows > 0 else 0,
        })
        summaries[col] = freq_df
    return summaries
