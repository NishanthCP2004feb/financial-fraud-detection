"""
Time Analysis — Financial Fraud Detection Dashboard
=====================================================

Temporal trends in fraudulent activity — daily, monthly,
and day-of-week patterns.  All statistics are descriptive
analytics computed dynamically from the loaded CSV dataset.

No model inference or prediction is performed on this page.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Project root resolution
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ui import footer, page_header, section_heading  # noqa: E402

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Time Analysis — Fraud Detection",
    page_icon="🕐",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Dataset path (project-root-relative)
# ---------------------------------------------------------------------------
DATA_CSV = PROJECT_ROOT / "data" / "raw" / "synthetic_fraud_dataset1 (1).csv"


# ---------------------------------------------------------------------------
# Cached data loader
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading dataset …")
def load_dataset() -> pd.DataFrame:
    """Load the raw fraud dataset and safely parse the Date column.

    Returns a DataFrame with *Date* parsed via ``pd.to_datetime``
    (``errors='coerce'``) so that invalid/missing values become ``NaT``
    rather than raising an error.
    """
    df = pd.read_csv(DATA_CSV)
    df["Transaction_Amount"] = pd.to_numeric(
        df["Transaction_Amount"], errors="coerce"
    )
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
page_header(
    "Time Analysis",
    "Temporal trends and seasonality in fraud detection data.",
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
try:
    df = load_dataset()
except FileNotFoundError:
    st.error(
        "Dataset file not found. Please ensure the CSV exists at "
        f"`{DATA_CSV.relative_to(PROJECT_ROOT)}`.",
        icon="🚨",
    )
    footer()
    st.stop()

# ---------------------------------------------------------------------------
# Separate valid-date rows (keep originals untouched)
# ---------------------------------------------------------------------------
df_valid = df.dropna(subset=["Date"]).copy()

if df_valid.empty:
    st.error(
        "No valid dates found in the dataset. "
        "Cannot perform time-based analysis.",
        icon="🚨",
    )
    footer()
    st.stop()

# Report any dropped rows so the user is aware
invalid_date_count = len(df) - len(df_valid)
if invalid_date_count > 0:
    st.warning(
        f"{invalid_date_count:,} row(s) with missing or invalid dates "
        "were excluded from this analysis.",
        icon="⚠️",
    )

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 🕐 Time Analysis Filters")

# --- Date range filter (derived from data) ---
min_date = df_valid["Date"].min().date()
max_date = df_valid["Date"].max().date()

start_date = st.sidebar.date_input(
    "Start Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
)
end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
)

if start_date > end_date:
    st.sidebar.error("Start Date must be on or before End Date.")

# --- Fraud status filter ---
fraud_status_options = ["All", "Fraud", "Legitimate"]
fraud_status = st.sidebar.selectbox("Fraud Status", fraud_status_options)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df_valid[
    (df_valid["Date"].dt.date >= start_date)
    & (df_valid["Date"].dt.date <= end_date)
].copy()

if fraud_status == "Fraud":
    filtered = filtered[filtered["Fraud_Label"] == 1]
elif fraud_status == "Legitimate":
    filtered = filtered[filtered["Fraud_Label"] == 0]

# ---------------------------------------------------------------------------
# Empty-result guard
# ---------------------------------------------------------------------------
if filtered.empty:
    st.warning(
        "No transactions match the selected filters. "
        "Please adjust the filters in the sidebar.",
        icon="⚠️",
    )
    footer()
    st.stop()

# ---------------------------------------------------------------------------
# KPI metrics (computed from filtered data)
# ---------------------------------------------------------------------------
section_heading("Key Metrics")

num_transactions = len(filtered)
fraud_count = int((filtered["Fraud_Label"] == 1).sum())
fraud_rate = (fraud_count / num_transactions * 100) if num_transactions > 0 else 0.0
total_amount = filtered["Transaction_Amount"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Transactions", f"{num_transactions:,}")
k2.metric("Fraudulent Transactions", f"{fraud_count:,}")
k3.metric("Fraud Rate", f"{fraud_rate:.2f}%")
k4.metric("Total Transaction Amount", f"${total_amount:,.2f}")

st.markdown("")  # spacing

# ===========================================================================
# Daily Transaction Trend
# ===========================================================================
section_heading("Daily Transaction Trend")

daily_txn = (
    filtered.groupby(filtered["Date"].dt.date)
    .size()
    .rename_axis("Date")
    .reset_index(name="Transactions")
)
daily_txn["Date"] = pd.to_datetime(daily_txn["Date"])

st.line_chart(daily_txn, x="Date", y="Transactions", height=350)

st.markdown("")  # spacing

# ===========================================================================
# Daily Fraud Trend
# ===========================================================================
section_heading("Daily Fraud Trend")

fraud_only = filtered[filtered["Fraud_Label"] == 1]

if fraud_only.empty:
    st.info("No fraudulent transactions in the current selection.")
else:
    daily_fraud = (
        fraud_only.groupby(fraud_only["Date"].dt.date)
        .size()
        .rename_axis("Date")
        .reset_index(name="Fraudulent Transactions")
    )
    daily_fraud["Date"] = pd.to_datetime(daily_fraud["Date"])

    st.line_chart(
        daily_fraud, x="Date", y="Fraudulent Transactions", height=350
    )

st.markdown("")  # spacing

# ===========================================================================
# Monthly Analysis
# ===========================================================================
section_heading("Monthly Analysis")

filtered_monthly = filtered.copy()
filtered_monthly["Month"] = filtered_monthly["Date"].dt.to_period("M")

monthly_summary = (
    filtered_monthly.groupby("Month")
    .agg(
        Total_Transactions=("Fraud_Label", "count"),
        Fraudulent_Transactions=("Fraud_Label", "sum"),
    )
    .reset_index()
)
monthly_summary["Fraud_Rate (%)"] = np.where(
    monthly_summary["Total_Transactions"] > 0,
    monthly_summary["Fraudulent_Transactions"]
    / monthly_summary["Total_Transactions"]
    * 100,
    0.0,
)
# Convert Period to string for display / charting
monthly_summary["Month"] = monthly_summary["Month"].astype(str)

col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown("**Monthly Transaction & Fraud Counts**")
    st.bar_chart(
        monthly_summary,
        x="Month",
        y=["Total_Transactions", "Fraudulent_Transactions"],
        height=350,
    )

with col_m2:
    st.markdown("**Monthly Fraud Rate**")
    st.bar_chart(
        monthly_summary[["Month", "Fraud_Rate (%)"]],
        x="Month",
        y="Fraud_Rate (%)",
        height=350,
    )

st.markdown("**Monthly Summary Table**")
st.dataframe(
    monthly_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Month": "Month",
        "Total_Transactions": "Total Transactions",
        "Fraudulent_Transactions": "Fraudulent Transactions",
        "Fraud_Rate (%)": st.column_config.NumberColumn(
            "Fraud Rate (%)", format="%.2f"
        ),
    },
)

st.markdown("")  # spacing

# ===========================================================================
# Day-of-Week Analysis
# ===========================================================================
section_heading("Day-of-Week Analysis")

DOW_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

filtered_dow = filtered.copy()
filtered_dow["Day_of_Week"] = filtered_dow["Date"].dt.day_name()

dow_summary = (
    filtered_dow.groupby("Day_of_Week")
    .agg(
        Transactions=("Fraud_Label", "count"),
        Fraudulent_Transactions=("Fraud_Label", "sum"),
    )
    .reindex(DOW_ORDER)
    .fillna(0)
    .astype({"Transactions": int, "Fraudulent_Transactions": int})
    .reset_index()
)

col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown("**Transactions by Day of Week**")
    st.bar_chart(
        dow_summary,
        x="Day_of_Week",
        y="Transactions",
        height=350,
    )

with col_d2:
    st.markdown("**Fraudulent Transactions by Day of Week**")
    st.bar_chart(
        dow_summary,
        x="Day_of_Week",
        y="Fraudulent_Transactions",
        height=350,
    )

st.markdown("")  # spacing

# ===========================================================================
# Fraud Rate by Day of Week
# ===========================================================================
section_heading("Fraud Rate by Day of Week")

dow_summary["Fraud_Rate (%)"] = np.where(
    dow_summary["Transactions"] > 0,
    dow_summary["Fraudulent_Transactions"] / dow_summary["Transactions"] * 100,
    0.0,
)

col_fr1, col_fr2 = st.columns(2)

with col_fr1:
    st.bar_chart(
        dow_summary[["Day_of_Week", "Fraud_Rate (%)"]],
        x="Day_of_Week",
        y="Fraud_Rate (%)",
        height=350,
    )

with col_fr2:
    st.dataframe(
        dow_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Day_of_Week": "Day of Week",
            "Transactions": "Total Transactions",
            "Fraudulent_Transactions": "Fraudulent Transactions",
            "Fraud_Rate (%)": st.column_config.NumberColumn(
                "Fraud Rate (%)", format="%.2f"
            ),
        },
    )

st.markdown("")  # spacing

# ===========================================================================
# Compact Time Summary Table
# ===========================================================================
section_heading("Time Summary")

date_range_days = (filtered["Date"].max() - filtered["Date"].min()).days + 1
peak_day = daily_txn.loc[daily_txn["Transactions"].idxmax(), "Date"]
avg_daily_txn = daily_txn["Transactions"].mean()

# Peak fraud day (if fraud exists)
if not fraud_only.empty:
    daily_fraud_full = (
        fraud_only.groupby(fraud_only["Date"].dt.date)
        .size()
        .rename_axis("Date")
        .reset_index(name="Fraudulent Transactions")
    )
    peak_fraud_day = daily_fraud_full.loc[
        daily_fraud_full["Fraudulent Transactions"].idxmax(), "Date"
    ]
    peak_fraud_day_str = str(peak_fraud_day)
    avg_daily_fraud = daily_fraud_full["Fraudulent Transactions"].mean()
else:
    peak_fraud_day_str = "N/A"
    avg_daily_fraud = 0.0

# Day with highest fraud rate
if dow_summary["Fraud_Rate (%)"].max() > 0:
    highest_fraud_rate_day = dow_summary.loc[
        dow_summary["Fraud_Rate (%)"].idxmax(), "Day_of_Week"
    ]
else:
    highest_fraud_rate_day = "N/A"

summary_data = {
    "Metric": [
        "Date Range",
        "Total Days Covered",
        "Total Transactions",
        "Total Fraudulent Transactions",
        "Overall Fraud Rate",
        "Total Transaction Amount",
        "Avg Daily Transactions",
        "Avg Daily Fraudulent Transactions",
        "Peak Transaction Day",
        "Peak Fraud Day",
        "Highest Fraud Rate Day (by Day of Week)",
    ],
    "Value": [
        f"{start_date} to {end_date}",
        f"{date_range_days:,}",
        f"{num_transactions:,}",
        f"{fraud_count:,}",
        f"{fraud_rate:.2f}%",
        f"${total_amount:,.2f}",
        f"{avg_daily_txn:,.1f}",
        f"{avg_daily_fraud:,.1f}",
        str(peak_day.date()) if hasattr(peak_day, "date") else str(peak_day),
        peak_fraud_day_str,
        highest_fraud_rate_day,
    ],
}

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
footer()
