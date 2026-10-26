<div align="center">

# 📊 EDA Automater
### Automated Exploratory Data Analysis Dashboard

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white">
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white">
<img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge">

**Upload a CSV or Excel file and instantly get data profiling, interactive charts, and plain-language statistical insights. No code, no API key, no internet required.**

</div>

---

# 📖 Overview

Every time an analyst receives a new dataset, the first steps are the same: check the shape, count missing values, look for duplicates, plot distributions, and find correlations. That means writing the same code again and again for every dataset.

> **What if the entire first look at a dataset could be automated?**

**AutoInsight** is a Streamlit web application that does exactly that. Upload a dataset and it builds a complete interactive EDA dashboard on one screen: KPI cards, data quality checks, descriptive statistics, automatic charts, and rule-based insights, with live filtering and export options.

> This is my **Field Project** for TYBSc Data Science.

---

# 🎯 Objectives

- Automate the repetitive first stage of Exploratory Data Analysis.
- Make EDA accessible to people who do not write code.
- Detect data quality problems automatically.
- Choose the right chart for each column type.
- Give **transparent, explainable** insights instead of black-box output.
- Run fully offline, with no API key or paid service.

---

# ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Smart Upload** | Accepts CSV and Excel files with extension validation and friendly error messages. |
| 🧮 **KPI Summary Cards** | Rows, columns, missing values, missing %, duplicate rows and memory usage at a glance. |
| 🧹 **Data Quality Checks** | Missing values per column (table and chart), duplicate rows, constant columns and columns with more than 50% missing values. |
| 📈 **Descriptive Statistics** | Count, mean, median, std, min, quartiles and max for numeric columns, top-5 frequency tables for categorical columns, and a per-column deep-dive. |
| 📊 **Interactive Charts** | Histograms, box plots, bar charts, correlation heatmap, scatter explorer and time-series explorer, all built with Plotly (zoom, hover, pan). |
| 💡 **Rule-Based Insights** | Plain-language statistical findings generated from fixed rules. No AI model, and no causation claims. |
| 🔎 **Live Filters** | Categorical multiselects and numeric range sliders. Every KPI, chart, statistic and insight updates instantly. |
| ⬇️ **Export** | Original CSV, optional cleaned CSV, data quality summary CSV and a self-contained offline HTML report. |

---

# 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Programming language |
| Streamlit | Web application and UI |
| Pandas | Data loading, profiling and all calculations |
| Plotly | Interactive chart generation |
| openpyxl | Reading `.xlsx` files (used by Pandas) |

**Why Plotly instead of Matplotlib or Seaborn?** Plotly charts are interactive out of the box (zoom, hover, pan), which static Matplotlib and Seaborn images do not offer.

---

# 🔄 How It Works

```
Upload CSV / Excel
        │
        ▼
Validate File Extension
        │
        ▼
Load into DataFrame
(fix duplicate / blank column names)
        │
        ▼
Detect Column Types
(numeric / categorical / datetime / boolean)
        │
        ▼
Apply Sidebar Filters
        │
        ▼
KPI Cards
        │
        ▼
┌───────────────┬───────────────┬───────────────┬───────────────┬───────────────┐
Overview     Data Quality    Statistics   Visualizations    Insights
└───────────────┴───────────────┴───────────────┴───────────────┴───────────────┘
        │
        ▼
Export (CSV / Cleaned CSV / HTML Report)
```

---

# 🧠 Column Type Detection

Each column is checked in this order, and the first match wins:

1. **Boolean**: True/False columns
2. **Numeric**: integer and float columns
3. **Datetime**: real datetime columns
4. **Datetime (from text)**: text columns where at least 80% of a 20-value sample parse as dates
5. **Categorical**: everything else

---

# 💡 Rule-Based Insights

Every insight comes from a visible statistical rule, so the output is **explainable and reproducible**.

| Rule | Trigger |
|------|---------|
| Missing values | Columns with missing data, with count and percentage |
| Strong correlation | Pairs with correlation of 0.7 or higher |
| Skewness | Columns with skewness of 1 or higher (left or right) |
| Outliers | Values outside 1.5 × IQR |
| Variance | Highest and lowest variance numeric columns |
| Frequent category | Most common value in categorical columns |

> ⚠️ Correlation does not imply causation. AutoInsight reports statistical association only and never claims one variable causes another.

---

# 📁 Project Structure

```
AutoInsight/
│
├── app.py                  # Main Streamlit app (UI + orchestration)
├── README.md
│
└── modules/
    ├── __init__.py         # Makes 'modules' a Python package
    ├── data_loader.py      # File validation, loading, column-type detection
    ├── profiling.py        # Missing values, dtypes, descriptive statistics
    ├── visualization.py    # Plotly chart-generation functions
    └── insights.py         # Rule-based statistical insights
```

### 🧩 Architecture

| File | Responsibility |
|------|----------------|
| `app.py` | Builds the UI (sidebar, tabs, filters, KPI cards) and connects all modules. Contains no low-level data logic. |
| `data_loader.py` | Validates and reads files, renames duplicate or blank columns, classifies column types, computes KPI values. |
| `profiling.py` | Missing-value summaries, data-type tables, constant and high-missing column flags, descriptive statistics. |
| `visualization.py` | Every Plotly chart. Each function returns `None` instead of crashing if a chart cannot be built. |
| `insights.py` | Generates the plain-language statistical observations. |

`@st.cache_data` is used on expensive operations so that re-runs are fast, and `st.session_state` keeps the loaded dataset and filters between reruns.

---

# 🖥 Using the App

1. **Upload** a CSV or Excel file from the sidebar.
2. Read the **KPI cards** that appear at the top.
3. Explore the tabs:
   - 🗂️ **Overview**: preview, column types, full dataset inspector
   - 🧹 **Data Quality**: missing values, duplicates, constant and high-missing columns
   - 📈 **Statistics**: descriptive statistics, category frequencies, column deep-dive
   - 📊 **Visualizations**: histograms, box plots, bar charts, heatmap, scatter and time-series explorers
   - 💡 **Insights**: automatically generated statistical observations
   - ⬇️ **Export**: downloads and the HTML report
4. Use the **sidebar filters** to narrow the data. Everything updates live.
5. Click **Reset / Replace Dataset** to load a different file.


---

# 🛡 Robustness

- Validates file extensions before reading.
- Handles empty files and datasets with no rows or columns.
- Renames duplicate and blank column names (e.g. `score`, `score_2`).
- Handles numeric-only, categorical-only and mixed datasets with clear messages instead of errors.
- **The original dataset is never modified.** Cleaning is optional and applies only to a separate copy.


---

# ⚠️ Limitations

- Designed for classroom-sized datasets (up to a few hundred thousand rows) on a typical laptop.
- Insights come from six fixed statistical rules. There is no machine learning or prediction.
- The correlation insight reports the strength of the relationship, not its direction.
- The HTML report is a summary (KPIs, quality table, statistics, up to three charts, insights), not a copy of the full app.
- Old `.xls` files need the extra `xlrd` package, which is not in `requirements.txt`. Use `.xlsx` or CSV.
- Dates stored as text in unusual formats may be treated as categorical.

---

# 🚀 Future Improvements

- Statistical hypothesis testing
- Automatic data cleaning suggestions
- PDF report export
- Database connections
- Multi-file upload and dataset comparison
- Optional AI-written summary on top of the rule-based insights

---

# 💡 What I Learned

- Designing an application with a clean separation of concerns
- Building interactive dashboards with Streamlit
- Using Pandas for profiling, type detection and statistics
- Creating interactive visualizations with Plotly
- Writing explainable, rule-based insights (IQR, skewness, correlation)
- Handling edge cases so an app never crashes on unusual data
- Caching and session state in Streamlit

---

# 👨‍💻 Author

### Zidane Raja


Python • Exploratory Data Analysis • Streamlit • Data Visualization

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a star!

</div>
