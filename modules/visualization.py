"""
visualization.py
----------------
Type-aware, interactive chart generation for AutoInsight.

All chart functions return a Plotly Figure or None. The module supports:
- Continuous numeric columns: histograms and box plots
- Discrete / ordinal numeric columns: frequency bar charts
- Categorical and boolean columns: frequency bar charts
- Numeric relationships: correlation heatmap and scatter plot
- Datetime + numeric columns: time-series line chart
"""

import pandas as pd
import plotly.express as px


# Numeric columns with a small number of distinct values are usually discrete
# scores, ratings, counts, or ordinal scales rather than continuous measures.
DEFAULT_DISCRETE_UNIQUE_LIMIT = 15


def is_discrete_numeric(df, column, unique_limit=DEFAULT_DISCRETE_UNIQUE_LIMIT):
    """Return True when a numeric column looks discrete / ordinal."""
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return False

    values = df[column].dropna()
    if values.empty:
        return False

    integer_like = ((values % 1) == 0).all()
    return bool(integer_like and values.nunique() <= unique_limit)


def plot_missing_values(missing_df):
    """Bar chart of missing-value counts per column (only columns with >0 missing)."""
    if missing_df is None or missing_df.empty:
        return None

    data = missing_df.loc[missing_df["Missing Count"] > 0].copy()
    if data.empty:
        return None

    fig = px.bar(
        data,
        x="Column",
        y="Missing Count",
        text="Missing %",
        title="Missing Values by Column",
        labels={"Missing Count": "Missing Count", "Column": "Column"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(xaxis_tickangle=-40, margin=dict(t=60, b=40), height=400)
    return fig


def plot_histogram(df, column, bins=30):
    """
    Plot a numeric distribution.

    Low-cardinality integer-like columns (e.g. 1–5 ratings) are shown as
    frequency bars, avoiding misleading continuous-looking histograms.
    Other numeric columns use a histogram.
    """
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return None

    series = df[column].dropna()
    if series.empty:
        return None

    if is_discrete_numeric(df, column):
        counts = series.value_counts().sort_index().rename_axis(column).reset_index(name="Count")
        fig = px.bar(
            counts,
            x=column,
            y="Count",
            text="Count",
            title=f"Frequency of {column} (Discrete Numeric)",
            labels={column: column, "Count": "Frequency"},
        )
        fig.update_traces(textposition="outside")
        fig.update_xaxes(type="category")
    else:
        fig = px.histogram(
            df,
            x=column,
            nbins=bins,
            title=f"Distribution of {column}",
            labels={column: column},
        )

    fig.update_layout(margin=dict(t=60, b=40), height=380)
    return fig


def plot_boxplot(df, column):
    """Box plot for a numeric column to show spread and potential outliers."""
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return None

    series = df[column].dropna()
    if series.empty:
        return None

    fig = px.box(df, y=column, title=f"Box Plot of {column}", points="outliers")
    fig.update_layout(margin=dict(t=60, b=40), height=380)
    return fig


def plot_discrete_numeric_chart(df, column, top_n=30):
    """Frequency bar chart for discrete / ordinal numeric columns."""
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return None

    series = df[column].dropna()
    if series.empty:
        return None

    counts = series.value_counts().sort_index().head(top_n)
    if counts.empty:
        return None

    chart_data = counts.rename_axis(column).reset_index(name="Count")
    fig = px.bar(
        chart_data,
        x=column,
        y="Count",
        text="Count",
        title=f"Frequency of {column}",
        labels={column: column, "Count": "Frequency"},
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(type="category")
    fig.update_layout(margin=dict(t=60, b=40), height=380)
    return fig


def plot_bar_chart(df, column, top_n=15):
    """Bar chart of the most frequent values in a categorical / boolean column."""
    if column not in df.columns:
        return None

    value_counts = df[column].value_counts(dropna=True).head(top_n)
    if value_counts.empty:
        return None

    chart_data = pd.DataFrame({
        "Category": value_counts.index.astype(str),
        "Count": value_counts.values,
    })
    fig = px.bar(
        chart_data,
        x="Category",
        y="Count",
        text="Count",
        title=f"Top {min(top_n, len(value_counts))} Categories in {column}",
        labels={"Category": column, "Count": "Count"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-40, margin=dict(t=60, b=40), height=380)
    return fig


def plot_correlation_heatmap(df, numeric_cols):
    """Correlation heatmap for numeric columns (requires at least two)."""
    valid_cols = [
        col for col in numeric_cols
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col])
    ]
    if len(valid_cols) < 2:
        return None

    corr = df[valid_cols].corr(numeric_only=True)
    if corr.empty or corr.isna().all().all():
        return None

    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Heatmap (Numeric Columns)",
        aspect="auto",
    )
    fig.update_layout(margin=dict(t=60, b=40), height=450)
    return fig


def plot_scatter(df, x_col, y_col, color_col=None):
    """Scatter plot between two numeric columns, optionally colored by a third."""
    if x_col not in df.columns or y_col not in df.columns:
        return None
    if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
        return None

    subset = df[[x_col, y_col]].dropna()
    if subset.empty:
        return None

    color_arg = color_col if color_col in df.columns else None
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_arg,
        title=f"{y_col} vs {x_col}",
        opacity=0.7,
    )
    fig.update_layout(margin=dict(t=60, b=40), height=420)
    return fig


def plot_time_series(df, date_col, value_col, agg="mean"):
    """Line plot of a numeric value aggregated by day over a datetime column."""
    if date_col not in df.columns or value_col not in df.columns:
        return None
    if not pd.api.types.is_numeric_dtype(df[value_col]):
        return None

    temp = df[[date_col, value_col]].copy()
    if not pd.api.types.is_datetime64_any_dtype(temp[date_col]):
        temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")

    temp = temp.dropna()
    if temp.empty:
        return None

    temp = temp.sort_values(date_col)
    try:
        grouped = (
            temp.groupby(pd.Grouper(key=date_col, freq="D"))[value_col]
            .agg(agg)
            .dropna()
            .reset_index()
        )
    except (TypeError, ValueError, KeyError):
        return None

    if grouped.empty:
        return None

    fig = px.line(
        grouped,
        x=date_col,
        y=value_col,
        title=f"{value_col} Over Time (by {date_col})",
    )
    fig.update_layout(margin=dict(t=60, b=40), height=400)
    return fig
