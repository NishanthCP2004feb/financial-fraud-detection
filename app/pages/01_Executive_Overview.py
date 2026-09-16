"""
Executive Overview — Financial Fraud Detection Dashboard
=========================================================

High-level summary of fraud detection metrics, key performance
indicators, and dataset-level descriptive statistics.
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
    page_title="Executive Overview — Fraud Detection",
    page_icon="📊",
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

    Returns a DataFrame with Transaction_Amount coerced to numeric
    (non-numeric values become NaN rather than raising an error).
    """
    df = pd.read_csv(DATA_CSV)
    df["Transaction_Amount"] = pd.to_numeric(
        df["Transaction_Amount"], errors="coerce"
    )
    return df


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
page_header(
    "Executive Overview",
    "High-level summary of fraud detection performance and key metrics.",
)

# Load data
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
# Derive KPI values
# ---------------------------------------------------------------------------
total_transactions = len(df)
fraud_transactions = int((df["Fraud_Label"] == 1).sum())
legit_transactions = int((df["Fraud_Label"] == 0).sum())
fraud_rate = fraud_transactions / total_transactions * 100 if total_transactions else 0.0

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
section_heading("Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(label="Total Transactions", value=f"{total_transactions:,}")
kpi2.metric(label="Fraudulent Transactions", value=f"{fraud_transactions:,}")
kpi3.metric(label="Legitimate Transactions", value=f"{legit_transactions:,}")
kpi4.metric(label="Fraud Rate", value=f"{fraud_rate:.2f}%")

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Fraud Distribution Visualization
# ---------------------------------------------------------------------------
section_heading("Fraud Distribution")

chart_data = (
    df["Fraud_Label"]
    .map({0: "Legitimate", 1: "Fraud"})
    .value_counts()
    .rename_axis("Category")
    .reset_index(name="Count")
)

st.bar_chart(chart_data, x="Category", y="Count", color="Category", height=400)

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Transaction Amount Summary
# ---------------------------------------------------------------------------
section_heading("Transaction Amount Summary")

total_amount = df["Transaction_Amount"].sum()
avg_amount = df["Transaction_Amount"].mean()
avg_fraud_amount = df.loc[df["Fraud_Label"] == 1, "Transaction_Amount"].mean()
avg_legit_amount = df.loc[df["Fraud_Label"] == 0, "Transaction_Amount"].mean()

s1, s2, s3, s4 = st.columns(4)

s1.metric(label="Total Transaction Amount", value=f"${total_amount:,.2f}")
s2.metric(label="Avg Transaction Amount", value=f"${avg_amount:,.2f}")
s3.metric(label="Avg Fraudulent Amount", value=f"${avg_fraud_amount:,.2f}")
s4.metric(label="Avg Legitimate Amount", value=f"${avg_legit_amount:,.2f}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
footer()
