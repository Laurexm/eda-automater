"""

AutoInsight - Automated Exploratory Data Analysis Dashboard.

"""

import pandas as pd
import streamlit as st

from modules import data_loader, profiling, visualization, insights



# Page config and styling
st.set_page_config(
    page_title="AutoInsight | Automated EDA",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    .app-title { font-size: 2.1rem; font-weight: 700; margin-bottom: 0; color: #1f2937; }
    .app-subtitle { font-size: 1.0rem; color: #6b7280; margin-top: 0.1rem; margin-bottom: 1.2rem; }

    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 14px 16px 10px 16px;
    }
    div[data-testid="stMetricLabel"] { font-weight: 600; color: #4b5563; }

    .section-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }

    .insight-item {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        border-radius: 6px;
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.55rem;
        font-size: 0.93rem;
        color: #1f2937;
    }
    /* Fix KPI labels and values in Streamlit dark mode */
    div[data-testid="stMetric"] {
        background-color: #f8fafc !important;
        color: #1f2937 !important;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label *,
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] *,
    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] * {
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;

    .stTabs [data-baseweb="tab"] { font-weight: 600; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# HTML REPORT BUILDER
def build_html_report(df, basic_info, quality_summary, numeric_cols, categorical_cols, insights_list, file_name):
    """
    Build a single, self-contained HTML report string containing KPIs,
    data quality info, descriptive statistics, a couple of key charts,
    and the generated insights. Plotly.js is embedded inline once so the
    report works fully offline after download.
    """
    desc_stats = profiling.get_descriptive_stats(df, numeric_cols)

    # Build up to two key charts as embeddable HTML snippets
    chart_html_blocks = []
    first_chart = True

    missing_fig = visualization.plot_missing_values(profiling.get_missing_value_summary(df))
    if missing_fig:
        chart_html_blocks.append(
            missing_fig.to_html(full_html=False, include_plotlyjs=(True if first_chart else False))
        )
        first_chart = False

    if len(numeric_cols) >= 2:
        heatmap_fig = visualization.plot_correlation_heatmap(df, numeric_cols)
        if heatmap_fig:
            chart_html_blocks.append(
                heatmap_fig.to_html(full_html=False, include_plotlyjs=(True if first_chart else False))
            )
            first_chart = False

    if numeric_cols:
        hist_fig = visualization.plot_histogram(df, numeric_cols[0])
        if hist_fig:
            chart_html_blocks.append(
                hist_fig.to_html(full_html=False, include_plotlyjs=(True if first_chart else False))
            )
            first_chart = False

    # If no charts were generated at all, still make sure plotly isn't referenced
    charts_section = "".join(chart_html_blocks) if chart_html_blocks else "<p>No charts available for this dataset.</p>"

    insights_html = "".join([f"<li>{item}</li>" for item in insights_list])

    quality_table_html = quality_summary["table"].to_html(index=False, border=0)
    stats_table_html = desc_stats.to_html(index=False, border=0) if not desc_stats.empty else "<p>No numeric columns available.</p>"

    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>AutoInsight Report - {file_name}</title>
        <style>
            body {{ font-family: Arial, Helvetica, sans-serif; margin: 40px; color: #1f2937; }}
            h1 {{ color: #111827; }}
            h2 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 6px; margin-top: 40px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
            th, td {{ border: 1px solid #e5e7eb; padding: 6px 10px; text-align: left; font-size: 0.9rem; }}
            th {{ background-color: #f3f4f6; }}
            .kpi-row {{ display: flex; gap: 20px; margin-top: 10px; flex-wrap: wrap; }}
            .kpi-box {{ background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px 18px; min-width: 140px; }}
            .kpi-value {{ font-size: 1.4rem; font-weight: bold; }}
            ul.insights li {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <h1>AutoInsight Report</h1>
        <p><b>Dataset:</b> {file_name}</p>

        <h2>KPI Summary</h2>
        <div class="kpi-row">
            <div class="kpi-box">Rows<br><span class="kpi-value">{basic_info['rows']:,}</span></div>
            <div class="kpi-box">Columns<br><span class="kpi-value">{basic_info['columns']:,}</span></div>
            <div class="kpi-box">Missing Values<br><span class="kpi-value">{basic_info['missing_values']:,}</span></div>
            <div class="kpi-box">Missing %<br><span class="kpi-value">{basic_info['missing_pct']}%</span></div>
            <div class="kpi-box">Duplicate Rows<br><span class="kpi-value">{basic_info['duplicate_rows']:,}</span></div>
            <div class="kpi-box">Memory (MB)<br><span class="kpi-value">{basic_info['memory_usage_mb']}</span></div>
        </div>

        <h2>Data Quality Summary</h2>
        {quality_table_html}

        <h2>Descriptive Statistics (Numeric Columns)</h2>
        {stats_table_html}

        <h2>Key Charts</h2>
        {charts_section}

        <h2>Automated Insights</h2>
        <ul class="insights">{insights_html}</ul>

        <p style="margin-top:40px; color:#9ca3af; font-size:0.8rem;">
            Generated by AutoInsight. Insights are rule-based statistical observations, not causal conclusions.
        </p>
    </body>
    </html>
    """
    return html_template


# SESSION STATE INITIALIZATION
def init_session_state():
    defaults = {
        "df": None,
        "file_name": None,
        "file_signature": None,
        "reset_filters_flag": False,
        "uploader_version": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
init_session_state()


def reset_dataset():
    """Clear all dataset-related session state so the user can upload a new file."""
    for key in ["df", "file_name", "file_signature"]:
        st.session_state[key] = None
    # Bump the uploader's key so the file_uploader widget itself is reset too --
    # otherwise it keeps holding the old file and silently reloads it on rerun.
    st.session_state.uploader_version += 1
    # Clear any filter widget state
    for key in list(st.session_state.keys()):
        if key.startswith("filter_"):
            del st.session_state[key]


def reset_filters():
    """Clear only the filter widgets, keeping the loaded dataset intact."""
    for key in list(st.session_state.keys()):
        if key.startswith("filter_"):
            del st.session_state[key]


# SIDEBAR: UPLOAD & CONTROLS
with st.sidebar:
    st.markdown("### 📁 Dataset")
    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Maximum recommended size: ~200 MB for smooth performance on a laptop.",
        key=f"uploader_{st.session_state.uploader_version}",
    )

    if uploaded_file is not None:
        is_valid, message = data_loader.validate_file(uploaded_file)
        if not is_valid:
            st.error(message)
        else:
            file_bytes = uploaded_file.getvalue()
            signature = (uploaded_file.name, len(file_bytes))

            if signature != st.session_state.file_signature:
                df, error = data_loader.load_dataset(file_bytes, uploaded_file.name)
                if error:
                    st.error(error)
                else:
                    st.session_state.df = df
                    st.session_state.file_name = uploaded_file.name
                    st.session_state.file_signature = signature
                    reset_filters()
                    st.success(f"Loaded '{uploaded_file.name}'")

    if st.session_state.df is not None:
        st.markdown(f"**Current file:** `{st.session_state.file_name}`")
        if st.button("🔄 Reset / Replace Dataset", use_container_width=True):
            reset_dataset()
            st.rerun()

    st.divider()

    if st.session_state.df is not None:
        st.markdown("### 🔎 Filters")
        st.caption("Filters apply to charts, statistics, and insights below. The original dataset is never modified.")
        if st.button("↺ Reset Filters", use_container_width=True):
            reset_filters()
            st.rerun()

    st.divider()
    st.markdown("### ⚙️ Chart Settings")
    max_charts = st.slider(
        "Max auto-charts per chart type", min_value=1, max_value=8, value=4,
        help="Limits how many histograms / box plots / bar charts are generated automatically, to keep the app fast.",
    )


# EMPTY STATE
df_original = st.session_state.df  # read once; reused below to avoid any check/use mismatch

if df_original is None:
    st.markdown('<p class="app-title">📊 AutoInsight</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Automated Exploratory Data Analysis</p>', unsafe_allow_html=True)
    st.info("👈 Upload a CSV or Excel (.xlsx) file from the sidebar to get started.")
    st.markdown("""
    **What AutoInsight does for you:**
    - Profiles your dataset automatically (rows, columns, missing values, duplicates)
    - Generates relevant charts based on each column's data type
    - Surfaces rule-based statistical observations (no AI guessing involved)
    - Lets you filter, explore, and export your results
    """)
    st.stop()


# LOAD DATA & APPLY FILTERS
column_types = data_loader.detect_column_types(df_original)
numeric_cols = column_types["numeric"]
categorical_cols = column_types["categorical"]
datetime_cols = column_types["datetime"]
boolean_cols = column_types["boolean"]

df_filtered = df_original.copy()

with st.sidebar:
    if categorical_cols:
        with st.expander("Categorical filters", expanded=False):
            for col in categorical_cols[:8]:
                options = sorted(df_original[col].dropna().astype(str).unique().tolist())
                if 1 < len(options) <= 200:
                    selected = st.multiselect(
                        col, options=options, default=options, key=f"filter_{col}"
                    )
                    if selected and len(selected) < len(options):
                        df_filtered = df_filtered[df_filtered[col].astype(str).isin(selected)]

    if numeric_cols:
        with st.expander("Numeric range filters", expanded=False):
            for col in numeric_cols[:8]:
                series = df_original[col].dropna()
                if series.empty:
                    continue
                col_min, col_max = float(series.min()), float(series.max())
                if col_min == col_max:
                    continue
                selected_range = st.slider(
                    col, min_value=col_min, max_value=col_max,
                    value=(col_min, col_max), key=f"filter_{col}"
                )
                df_filtered = df_filtered[
                    df_filtered[col].between(selected_range[0], selected_range[1]) | df_filtered[col].isna()
                ]

n_filtered_rows = len(df_filtered)
n_total_rows = len(df_original)


# HEADER
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown('<p class="app-title">AutoInsight</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Automated Exploratory Data Analysis</p>', unsafe_allow_html=True)
with header_col2:
    st.markdown(f"<div style='text-align:right; padding-top: 1.2rem; color:#6b7280;'>File: <b>{st.session_state.file_name}</b></div>", unsafe_allow_html=True)

if n_filtered_rows != n_total_rows:
    st.caption(f"Showing **{n_filtered_rows:,}** of **{n_total_rows:,}** rows after filters (charts & stats below use the filtered data).")


# KPI SUMMARY CARDS
basic_info = data_loader.get_basic_info(df_filtered)

kpi_cols = st.columns(6)
kpi_cols[0].metric("Rows", f"{basic_info['rows']:,}")
kpi_cols[1].metric("Columns", f"{basic_info['columns']:,}")
kpi_cols[2].metric("Missing Values", f"{basic_info['missing_values']:,}")
kpi_cols[3].metric("Missing %", f"{basic_info['missing_pct']}%")
kpi_cols[4].metric("Duplicate Rows", f"{basic_info['duplicate_rows']:,}")
kpi_cols[5].metric("Memory Usage", f"{basic_info['memory_usage_mb']} MB")

st.write("")


# TABS
tab_overview, tab_quality, tab_stats, tab_viz, tab_insights, tab_export = st.tabs(
    ["🗂️ Overview", "🧹 Data Quality", "📈 Statistics", "📊 Visualizations", "💡 Insights", "⬇️ Export"]
)

# ---------------- OVERVIEW ----------------
with tab_overview:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.subheader("Dataset Preview")
        n_preview = st.slider("Rows to preview", 5, 20, 8, key="preview_rows")
        st.dataframe(df_filtered.head(n_preview), use_container_width=True)

        with st.expander("🔍 Inspect full dataset"):
            st.dataframe(df_filtered, use_container_width=True, height=420)

    with col_b:
        st.subheader("Column Type Counts")
        type_counts = pd.DataFrame({
            "Type": ["Numeric", "Categorical", "Datetime", "Boolean"],
            "Count": [len(numeric_cols), len(categorical_cols), len(datetime_cols), len(boolean_cols)],
        })
        st.dataframe(type_counts, use_container_width=True, hide_index=True)

        st.subheader("Data Quality Snapshot")
        st.write(f"- **Duplicate rows:** {basic_info['duplicate_rows']:,}")
        st.write(f"- **Total missing values:** {basic_info['missing_values']:,}")
        st.write(f"- **Missing %:** {basic_info['missing_pct']}%")

    st.subheader("Column Names & Inferred Types")
    dtype_df = profiling.get_dtype_summary(df_filtered)
    st.dataframe(dtype_df, use_container_width=True, hide_index=True)


# DATA QUALITY 
with tab_quality:
    quality_summary = profiling.get_data_quality_summary(df_filtered)

    q_col1, q_col2 = st.columns([1, 1])
    with q_col1:
        st.subheader("Missing Values by Column")
        st.dataframe(quality_summary["table"], use_container_width=True, hide_index=True)
    with q_col2:
        st.subheader("Missing Value Chart")
        missing_fig = visualization.plot_missing_values(profiling.get_missing_value_summary(df_filtered))
        if missing_fig:
            st.plotly_chart(missing_fig, use_container_width=True)
        else:
            st.success("No missing values detected in the current selection. ✅")

    st.divider()
    flag_col1, flag_col2, flag_col3 = st.columns(3)
    flag_col1.metric("Duplicate Rows", quality_summary["duplicate_rows"])
    flag_col2.metric("Constant Columns", len(quality_summary["constant_columns"]))
    flag_col3.metric("High-Missingness Columns (>50%)", len(quality_summary["high_missing_columns"]))

    if quality_summary["constant_columns"]:
        st.warning(f"Constant columns (only one unique value): {', '.join(quality_summary['constant_columns'])}")
    if quality_summary["high_missing_columns"]:
        st.warning(f"Columns with >50% missing values: {', '.join(quality_summary['high_missing_columns'])}")
    st.caption("Note: these are flags for your attention only. AutoInsight never modifies your original dataset automatically.")


# STATISTICS 
with tab_stats:
    st.subheader("Numeric Descriptive Statistics")
    if numeric_cols:
        desc_stats = profiling.get_descriptive_stats(df_filtered, numeric_cols)
        st.dataframe(desc_stats, use_container_width=True, hide_index=True)
    else:
        st.info("No numeric columns detected in this dataset.")

    st.divider()
    st.subheader("Categorical Frequency Summary")
    if categorical_cols:
        cat_summaries = profiling.get_categorical_summary(df_filtered, categorical_cols)
        selected_cat_col = st.selectbox("Select a categorical column to inspect", categorical_cols)
        if selected_cat_col in cat_summaries:
            st.dataframe(cat_summaries[selected_cat_col], use_container_width=True, hide_index=True)
        else:
            st.info("No values available for this column in the current selection.")
    else:
        st.info("No categorical columns detected in this dataset.")

    st.divider()
    st.subheader("Column Deep-Dive")
    all_cols = df_filtered.columns.tolist()
    deep_dive_col = st.selectbox("Select any column for detailed inspection", all_cols, key="deep_dive")
    dd_series = df_filtered[deep_dive_col]
    dd1, dd2, dd3, dd4 = st.columns(4)
    dd1.metric("Non-null Count", int(dd_series.notna().sum()))
    dd2.metric("Missing Count", int(dd_series.isna().sum()))
    dd3.metric("Unique Values", int(dd_series.nunique(dropna=True)))
    if deep_dive_col in numeric_cols:
        dd4.metric("Mean", round(float(dd_series.mean()), 3) if dd_series.notna().any() else "N/A")
    else:
        mode_vals = dd_series.mode(dropna=True)
        dd4.metric("Most Frequent", str(mode_vals.iloc[0]) if not mode_vals.empty else "N/A")


# VISUALIZATIONS 
with tab_viz:
    st.caption(f"Showing up to {max_charts} charts per chart type (adjust in the sidebar under 'Chart Settings').")

    # Numeric distributions
    if numeric_cols:
        st.subheader("Numeric Distributions")
        selected_numeric = st.multiselect(
            "Columns to plot (histograms & box plots)",
            numeric_cols, default=numeric_cols[:max_charts], max_selections=max_charts,
        )
        grid_cols = st.columns(2)
        for i, col in enumerate(selected_numeric):
            hist_fig = visualization.plot_histogram(df_filtered, col)
            with grid_cols[i % 2]:
                if hist_fig:
                    st.plotly_chart(hist_fig, use_container_width=True)
                else:
                    st.info(f"Could not generate a histogram for '{col}'.")

        grid_cols2 = st.columns(2)
        for i, col in enumerate(selected_numeric):
            box_fig = visualization.plot_boxplot(df_filtered, col)
            with grid_cols2[i % 2]:
                if box_fig:
                    st.plotly_chart(box_fig, use_container_width=True)
                else:
                    st.info(f"Could not generate a box plot for '{col}'.")
        st.divider()

    # Categorical frequencies
    if categorical_cols:
        st.subheader("Categorical Frequencies")
        selected_categorical = st.multiselect(
            "Columns to plot (bar charts)",
            categorical_cols, default=categorical_cols[:max_charts], max_selections=max_charts,
        )
        grid_cols3 = st.columns(2)
        for i, col in enumerate(selected_categorical):
            bar_fig = visualization.plot_bar_chart(df_filtered, col)
            with grid_cols3[i % 2]:
                if bar_fig:
                    st.plotly_chart(bar_fig, use_container_width=True)
                else:
                    st.info(f"Could not generate a bar chart for '{col}'.")
        st.divider()

    # Correlation heatmap
    if len(numeric_cols) >= 2:
        st.subheader("Correlation Heatmap")
        heatmap_fig = visualization.plot_correlation_heatmap(df_filtered, numeric_cols)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        else:
            st.info("Not enough numeric variation to compute a correlation heatmap.")
        st.divider()

    # Scatter plot
    if len(numeric_cols) >= 2:
        st.subheader("Scatter Plot Explorer")
        sc1, sc2, sc3 = st.columns(3)
        x_col = sc1.selectbox("X-axis", numeric_cols, index=0, key="scatter_x")
        y_default_index = 1 if len(numeric_cols) > 1 else 0
        y_col = sc2.selectbox("Y-axis", numeric_cols, index=y_default_index, key="scatter_y")
        color_options = ["(none)"] + categorical_cols + boolean_cols
        color_choice = sc3.selectbox("Color by (optional)", color_options, key="scatter_color")
        color_col = None if color_choice == "(none)" else color_choice

        scatter_fig = visualization.plot_scatter(df_filtered, x_col, y_col, color_col)
        if scatter_fig:
            st.plotly_chart(scatter_fig, use_container_width=True)
        else:
            st.info("Could not generate a scatter plot for the selected columns.")
        st.divider()

    # Time series
    if datetime_cols and numeric_cols:
        st.subheader("Time Series Explorer")
        ts1, ts2 = st.columns(2)
        date_col = ts1.selectbox("Datetime column", datetime_cols, key="ts_date")
        value_col = ts2.selectbox("Numeric column", numeric_cols, key="ts_value")
        ts_fig = visualization.plot_time_series(df_filtered, date_col, value_col)
        if ts_fig:
            st.plotly_chart(ts_fig, use_container_width=True)
        else:
            st.info("Could not generate a time-series chart for the selected columns.")

    if not numeric_cols and not categorical_cols and not datetime_cols:
        st.info("No plottable columns were detected in this dataset.")


# INSIGHTS 
with tab_insights:
    st.subheader("Automated Statistical Insights")
    st.caption("These are rule-based observations calculated directly from your data. No AI model is used to generate them, and they never claim causation.")

    missing_summary_for_insights = profiling.get_missing_value_summary(df_filtered)
    generated_insights = insights.generate_insights(
        df_filtered, numeric_cols, categorical_cols, missing_summary_for_insights
    )

    for item in generated_insights:
        st.markdown(f'<div class="insight-item">💡 {item}</div>', unsafe_allow_html=True)


# EXPORT 
with tab_export:
    st.subheader("Export Options")

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        st.markdown("**Original Dataset**")
        st.download_button(
            "⬇️ Download Original Dataset (CSV)",
            data=df_original.to_csv(index=False).encode("utf-8"),
            file_name=f"original_{st.session_state.file_name.rsplit('.', 1)[0]}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("**Data Quality Summary**")
        quality_csv = profiling.get_data_quality_summary(df_filtered)["table"].to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Data Quality Summary (CSV)",
            data=quality_csv,
            file_name="data_quality_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp_col2:
        st.markdown("**Cleaned Dataset (optional)**")
        st.caption("Cleaning is never applied automatically. Choose operations below, then download.")
        drop_dupes = st.checkbox("Drop duplicate rows")
        drop_na_rows = st.checkbox("Drop rows with any missing values")
        drop_constant = st.checkbox("Drop constant columns")

        cleaned_df = df_original.copy()
        if drop_dupes:
            cleaned_df = cleaned_df.drop_duplicates()
        if drop_na_rows:
            cleaned_df = cleaned_df.dropna()
        if drop_constant:
            constant_cols_all = profiling.get_constant_columns(df_original)
            cleaned_df = cleaned_df.drop(columns=constant_cols_all, errors="ignore")

        any_cleaning_selected = drop_dupes or drop_na_rows or drop_constant
        st.download_button(
            "⬇️ Download Cleaned Dataset (CSV)",
            data=cleaned_df.to_csv(index=False).encode("utf-8"),
            file_name=f"cleaned_{st.session_state.file_name.rsplit('.', 1)[0]}.csv",
            mime="text/csv",
            disabled=not any_cleaning_selected,
            use_container_width=True,
        )
        if not any_cleaning_selected:
            st.caption("Select at least one cleaning operation to enable this download.")
        else:
            st.caption(f"Cleaned dataset shape: {cleaned_df.shape[0]:,} rows x {cleaned_df.shape[1]:,} columns")

    st.divider()
    st.markdown("**Full HTML Report**")
    st.caption("Generates a self-contained HTML file with KPIs, data quality, statistics, key charts, and insights. Works fully offline once downloaded.")

    if st.button("🧾 Generate HTML Report"):
        with st.spinner("Building report..."):
            report_html = build_html_report(
                df_filtered, basic_info, quality_summary,
                numeric_cols, categorical_cols, generated_insights,
                st.session_state.file_name,
            )
            st.session_state["report_html"] = report_html
        st.success("Report ready below.")

    if st.session_state.get("report_html"):
        st.download_button(
            "⬇️ Download HTML Report",
            data=st.session_state["report_html"].encode("utf-8"),
            file_name="autoinsight_report.html",
            mime="text/html",
            use_container_width=True,
        )
