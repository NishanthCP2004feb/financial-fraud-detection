"""
Transaction Analysis — Financial Fraud Detection Dashboard
============================================================

Detailed breakdown of transactions, fraud vs. legitimate
patterns, and distribution analysis.  All statistics are
computed dynamically from the loaded CSV dataset.
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
    page_title="Transaction Analysis — Fraud Detection",
    page_icon="💳",
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
    "Transaction Analysis",
    "Explore transaction patterns, amounts, and fraud distribution.",
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
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 🔍 Transaction Filters")

# --- Fraud status filter ---
fraud_status_options = ["All", "Fraud", "Legitimate"]
fraud_status = st.sidebar.selectbox("Fraud Status", fraud_status_options)

# --- Transaction type filter ---
transaction_types = sorted(df["Transaction_Type"].dropna().unique().tolist())
selected_txn_types = st.sidebar.multiselect(
    "Transaction Type",
    options=transaction_types,
    default=transaction_types,
)

# --- Device type filter ---
device_types = sorted(df["Device_Type"].dropna().unique().tolist())
selected_devices = st.sidebar.multiselect(
    "Device Type",
    options=device_types,
    default=device_types,
)

# --- Card type filter ---
card_types = sorted(df["Card_Type"].dropna().unique().tolist())
selected_cards = st.sidebar.multiselect(
    "Card Type",
    options=card_types,
    default=card_types,
)

# --- Merchant category filter ---
merchant_categories = sorted(df["Merchant_Category"].dropna().unique().tolist())
selected_merchants = st.sidebar.multiselect(
    "Merchant Category",
    options=merchant_categories,
    default=merchant_categories,
)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df.copy()

# Fraud status
if fraud_status == "Fraud":
    filtered = filtered[filtered["Fraud_Label"] == 1]
elif fraud_status == "Legitimate":
    filtered = filtered[filtered["Fraud_Label"] == 0]

# Categorical multi-select filters
filtered = filtered[filtered["Transaction_Type"].isin(selected_txn_types)]
filtered = filtered[filtered["Device_Type"].isin(selected_devices)]
filtered = filtered[filtered["Card_Type"].isin(selected_cards)]
filtered = filtered[filtered["Merchant_Category"].isin(selected_merchants)]

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
total_amount = filtered["Transaction_Amount"].sum()
avg_amount = filtered["Transaction_Amount"].mean()
fraud_count = int((filtered["Fraud_Label"] == 1).sum())
fraud_rate = (fraud_count / num_transactions * 100) if num_transactions > 0 else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Transactions", f"{num_transactions:,}")
k2.metric("Total Amount", f"${total_amount:,.2f}")
k3.metric("Avg Amount", f"${avg_amount:,.2f}")
k4.metric("Fraud Rate", f"{fraud_rate:.2f}%")

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Transaction Amount Distribution
# ---------------------------------------------------------------------------
section_heading("Transaction Amount Distribution")

# Build a simple histogram-style view using st.bar_chart.
# We bin the Transaction_Amount into ranges for readability.
amount_series = filtered["Transaction_Amount"].dropna()

# Create bins (up to 20 equal-width bins)
num_bins = 20
bin_counts = pd.cut(amount_series, bins=num_bins).value_counts().sort_index()
bin_chart_df = pd.DataFrame({
    "Amount Range": [str(interval) for interval in bin_counts.index],
    "Count": bin_counts.values,
})
st.bar_chart(bin_chart_df, x="Amount Range", y="Count", height=400)

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Fraud vs. Legitimate Comparison
# ---------------------------------------------------------------------------
section_heading("Fraud vs. Legitimate Transactions")

fraud_vs_legit = (
    filtered["Fraud_Label"]
    .map({0: "Legitimate", 1: "Fraud"})
    .value_counts()
    .rename_axis("Category")
    .reset_index(name="Count")
)

st.bar_chart(fraud_vs_legit, x="Category", y="Count", color="Category", height=400)

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Transaction Type Analysis
# ---------------------------------------------------------------------------
section_heading("Transaction Type Analysis")

txn_type_counts = (
    filtered["Transaction_Type"]
    .value_counts()
    .rename_axis("Transaction Type")
    .reset_index(name="Count")
)

st.bar_chart(txn_type_counts, x="Transaction Type", y="Count", height=400)

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Filtered Transaction Preview
# ---------------------------------------------------------------------------
section_heading("Transaction Preview")

preview_columns = [
    "Transaction_ID",
    "User_ID",
    "Transaction_Amount",
    "Transaction_Type",
    "Date",
    "Device_Type",
    "Location",
    "Merchant_Category",
    "Card_Type",
    "Fraud_Label",
]

# Only keep columns that actually exist in the dataframe
preview_columns = [c for c in preview_columns if c in filtered.columns]

st.dataframe(
    filtered[preview_columns].head(100),
    use_container_width=True,
    hide_index=True,
)
st.caption(f"Showing up to 100 of {num_transactions:,} filtered transactions.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
footer()
