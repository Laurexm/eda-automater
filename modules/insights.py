"""
insights.py
-------------
Rule-based, purely statistical insight generation. No AI/LLM is used --
every observation below comes directly from Pandas/NumPy calculations,
and is phrased as a statistical observation rather than a causal claim.
"""

import pandas as pd


def generate_insights(df, numeric_cols, categorical_cols, missing_df, max_items_per_category=3):
    """
    Generate a list of plain-language statistical observations about the
    dataset. Each helper degrades gracefully (returns an empty list) if it
    cannot be computed, so the overall function never raises.
    """
    insights = []

    insights.extend(_missing_value_insights(missing_df, max_items_per_category))
    insights.extend(_correlation_insights(df, numeric_cols, max_items_per_category))
    insights.extend(_skewness_insights(df, numeric_cols, max_items_per_category))
    insights.extend(_outlier_insights(df, numeric_cols, max_items_per_category))
    insights.extend(_variance_insights(df, numeric_cols, max_items_per_category))
    insights.extend(_frequent_category_insights(df, categorical_cols, max_items_per_category))

    if not insights:
        insights.append(
            "No notable statistical patterns were detected in the current dataset / filter selection."
        )

    return insights


def _missing_value_insights(missing_df, max_items):
    insights = []
    if missing_df is None or missing_df.empty:
        return insights

    top_missing = missing_df[missing_df["Missing Count"] > 0].head(max_items)
    for _, row in top_missing.iterrows():
        insights.append(
            f"Column '{row['Column']}' has {row['Missing %']}% missing values "
            f"({int(row['Missing Count'])} rows)."
        )
    return insights


def _correlation_insights(df, numeric_cols, max_items):
    insights = []
    if len(numeric_cols) < 2:
        return insights

    try:
        corr = df[numeric_cols].corr(numeric_only=True).abs()
    except Exception:
        return insights

    pairs, seen = [], set()
    for col_a in corr.columns:
        for col_b in corr.columns:
            if col_a == col_b:
                continue
            key = tuple(sorted([col_a, col_b]))
            if key in seen:
                continue
            seen.add(key)
            value = corr.loc[col_a, col_b]
            if pd.notna(value):
                pairs.append((key[0], key[1], value))

    pairs.sort(key=lambda p: p[2], reverse=True)
    strong_pairs = [p for p in pairs if p[2] >= 0.7][:max_items]

    for col_a, col_b, value in strong_pairs:
        insights.append(
            f"'{col_a}' and '{col_b}' show a strong correlation (r = {value:.2f}). "
            f"This reflects a statistical association only, not proof of causation."
        )
    return insights


def _skewness_insights(df, numeric_cols, max_items):
    insights = []
    if not numeric_cols:
        return insights

    results = []
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 3:
            continue
        try:
            skew_value = series.skew()
        except Exception:
            continue
        if pd.notna(skew_value) and abs(skew_value) >= 1:
            results.append((col, skew_value))

    results.sort(key=lambda r: abs(r[1]), reverse=True)
    for col, skew_value in results[:max_items]:
        direction = "right (positively)" if skew_value > 0 else "left (negatively)"
        insights.append(
            f"Column '{col}' is strongly skewed to the {direction} (skewness = {skew_value:.2f})."
        )
    return insights


def _outlier_insights(df, numeric_cols, max_items):
    insights = []
    if not numeric_cols:
        return insights

    results = []
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 4:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower_bound, upper_bound = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_outliers = int(((series < lower_bound) | (series > upper_bound)).sum())
        if n_outliers > 0:
            pct = round(n_outliers / len(series) * 100, 2)
            results.append((col, n_outliers, pct))

    results.sort(key=lambda r: r[1], reverse=True)
    for col, n_outliers, pct in results[:max_items]:
        insights.append(
            f"Column '{col}' has {n_outliers} potential outlier(s) ({pct}% of non-missing values), "
            f"based on the IQR method."
        )
    return insights


def _variance_insights(df, numeric_cols, max_items):
    insights = []
    if len(numeric_cols) < 2:
        return insights

    variances = []
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 2:
            continue
        var = series.var()
        if pd.notna(var):
            variances.append((col, var))

    if len(variances) < 2:
        return insights

    variances.sort(key=lambda v: v[1], reverse=True)
    highest, lowest = variances[0], variances[-1]

    insights.append(
        f"Column '{highest[0]}' has the highest variance among numeric columns "
        f"(variance = {highest[1]:.2f}), indicating relatively spread-out values."
    )
    if lowest[0] != highest[0]:
        insights.append(
            f"Column '{lowest[0]}' has the lowest variance among numeric columns "
            f"(variance = {lowest[1]:.2f}), indicating relatively consistent values."
        )
    return insights[:max_items]


def _frequent_category_insights(df, categorical_cols, max_items):
    insights = []
    if not categorical_cols or len(df) == 0:
        return insights

    for col in categorical_cols[:max_items]:
        value_counts = df[col].value_counts(dropna=True)
        if value_counts.empty:
            continue
        top_value = value_counts.index[0]
        top_count = value_counts.iloc[0]
        pct = round(top_count / len(df) * 100, 2)
        insights.append(
            f"In column '{col}', the most frequent category is '{top_value}' ({pct}% of records)."
        )
    return insights[:max_items]
