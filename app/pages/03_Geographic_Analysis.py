"""
Geographic Analysis — Financial Fraud Detection Dashboard
==========================================================

Geographic distribution of fraud activity, location-based
patterns, and regional transaction insights.  All statistics
are computed dynamically from the loaded CSV dataset.
"""

import sys
from pathlib import Path

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
    page_title="Geographic Analysis — Fraud Detection",
    page_icon="🌐",
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
    """Load the raw fraud dataset from CSV.

    Returns a DataFrame with Transaction_Amount safely coerced to numeric.
    """
    df = pd.read_csv(DATA_CSV)
    df["Transaction_Amount"] = pd.to_numeric(
        df["Transaction_Amount"], errors="coerce"
    )
    return df


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
page_header(
    "Geographic Analysis",
    "Regional fraud distribution and location-based pattern analysis.",
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
# Handle missing Location values
# ---------------------------------------------------------------------------
df["Location"] = df["Location"].fillna("Unknown")

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 🌐 Geographic Filters")

locations = sorted(df["Location"].unique().tolist())

selected_locations = st.sidebar.multiselect(
    "Location",
    options=locations,
    default=locations,
)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df[df["Location"].isin(selected_locations)]

# ---------------------------------------------------------------------------
# Empty-result guard
# ---------------------------------------------------------------------------
if filtered.empty:
    st.warning(
        "No transactions match the selected filters. "
        "Please adjust the Location selection in the sidebar.",
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

# ---------------------------------------------------------------------------
# Fraud Distribution by Location
# ---------------------------------------------------------------------------
section_heading("Fraudulent Transactions by Location")

fraud_by_loc = (
    filtered[filtered["Fraud_Label"] == 1]
    .groupby("Location", as_index=False)
    .size()
    .rename(columns={"size": "Fraud Count"})
    .sort_values("Fraud Count", ascending=False)
)

if fraud_by_loc.empty:
    st.info("No fraudulent transactions found for the selected locations.", icon="ℹ️")
else:
    st.bar_chart(fraud_by_loc, x="Location", y="Fraud Count", height=400)

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Fraud Rate by Location
# ---------------------------------------------------------------------------
section_heading("Fraud Rate by Location")

loc_stats = (
    filtered.groupby("Location", as_index=False)
    .agg(
        Total_Transactions=("Fraud_Label", "count"),
        Fraudulent_Transactions=("Fraud_Label", "sum"),
    )
)
loc_stats["Fraudulent_Transactions"] = loc_stats["Fraudulent_Transactions"].astype(int)
loc_stats["Fraud_Rate"] = loc_stats.apply(
    lambda row: (
        row["Fraudulent_Transactions"] / row["Total_Transactions"] * 100
        if row["Total_Transactions"] > 0
        else 0.0
    ),
    axis=1,
)
loc_stats = loc_stats.sort_values("Fraud_Rate", ascending=False)

# Display as a bar chart
fraud_rate_chart = loc_stats[["Location", "Fraud_Rate"]].copy()
fraud_rate_chart = fraud_rate_chart.rename(columns={"Fraud_Rate": "Fraud Rate (%)"})
st.bar_chart(fraud_rate_chart, x="Location", y="Fraud Rate (%)", height=400)

# Also show a supporting table
st.dataframe(
    loc_stats.rename(
        columns={
            "Total_Transactions": "Total Transactions",
            "Fraudulent_Transactions": "Fraudulent Transactions",
            "Fraud_Rate": "Fraud Rate (%)",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Transaction Amount by Location
# ---------------------------------------------------------------------------
section_heading("Transaction Amount by Location")

amount_by_loc = (
    filtered.groupby("Location", as_index=False)
    .agg(
        Total_Amount=("Transaction_Amount", "sum"),
        Avg_Amount=("Transaction_Amount", "mean"),
    )
    .sort_values("Total_Amount", ascending=False)
)

col_total, col_avg = st.columns(2)

with col_total:
    st.markdown("**Total Transaction Amount**")
    chart_total = amount_by_loc[["Location", "Total_Amount"]].rename(
        columns={"Total_Amount": "Total Amount ($)"}
    )
    st.bar_chart(chart_total, x="Location", y="Total Amount ($)", height=350)

with col_avg:
    st.markdown("**Average Transaction Amount**")
    chart_avg = amount_by_loc[["Location", "Avg_Amount"]].rename(
        columns={"Avg_Amount": "Avg Amount ($)"}
    )
    st.bar_chart(chart_avg, x="Location", y="Avg Amount ($)", height=350)

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Geographic Summary Table
# ---------------------------------------------------------------------------
section_heading("Geographic Summary")

summary = (
    filtered.groupby("Location", as_index=False)
    .agg(
        Total_Transactions=("Fraud_Label", "count"),
        Fraudulent_Transactions=("Fraud_Label", "sum"),
        Total_Transaction_Amount=("Transaction_Amount", "sum"),
    )
)
summary["Fraudulent_Transactions"] = summary["Fraudulent_Transactions"].astype(int)
summary["Fraud_Rate"] = summary.apply(
    lambda row: (
        row["Fraudulent_Transactions"] / row["Total_Transactions"] * 100
        if row["Total_Transactions"] > 0
        else 0.0
    ),
    axis=1,
)

# Reorder and rename for display
summary = summary[
    [
        "Location",
        "Total_Transactions",
        "Fraudulent_Transactions",
        "Fraud_Rate",
        "Total_Transaction_Amount",
    ]
].sort_values("Total_Transactions", ascending=False)

st.dataframe(
    summary.rename(
        columns={
            "Total_Transactions": "Total Transactions",
            "Fraudulent_Transactions": "Fraudulent Transactions",
            "Fraud_Rate": "Fraud Rate (%)",
            "Total_Transaction_Amount": "Total Transaction Amount ($)",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
footer()
