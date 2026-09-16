"""
Customer & Card Analysis — Financial Fraud Detection Dashboard
================================================================

Customer-level insights, card-type breakdowns, card-age distributions,
and device-type patterns.  All statistics are descriptive analytics
computed dynamically from the loaded CSV dataset.
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
    page_title="Customer & Card Analysis — Fraud Detection",
    page_icon="👥",
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

    Returns a DataFrame with numeric fields safely coerced so that
    non-numeric values become NaN rather than raising an error.
    """
    df = pd.read_csv(DATA_CSV)
    df["Transaction_Amount"] = pd.to_numeric(
        df["Transaction_Amount"], errors="coerce"
    )
    df["Card_Age"] = pd.to_numeric(df["Card_Age"], errors="coerce")
    df["Previous_Fraudulent_Activity"] = pd.to_numeric(
        df["Previous_Fraudulent_Activity"], errors="coerce"
    )
    return df


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
page_header(
    "Customer & Card Analysis",
    "Customer-level insights, card type distribution, card age patterns, "
    "and device type breakdown.",
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
st.sidebar.markdown("### 🔍 Customer & Card Filters")

# --- Card type filter ---
card_types = sorted(df["Card_Type"].dropna().unique().tolist())
selected_cards = st.sidebar.multiselect(
    "Card Type",
    options=card_types,
    default=card_types,
)

# --- Device type filter ---
device_types = sorted(df["Device_Type"].dropna().unique().tolist())
selected_devices = st.sidebar.multiselect(
    "Device Type",
    options=device_types,
    default=device_types,
)

# --- Fraud status filter ---
fraud_status_options = ["All", "Fraud", "Legitimate"]
fraud_status = st.sidebar.selectbox("Fraud Status", fraud_status_options)

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df.copy()

filtered = filtered[filtered["Card_Type"].isin(selected_cards)]
filtered = filtered[filtered["Device_Type"].isin(selected_devices)]

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

unique_customers = filtered["User_ID"].nunique()
num_transactions = len(filtered)
fraud_count = int((filtered["Fraud_Label"] == 1).sum())
fraud_rate = (fraud_count / num_transactions * 100) if num_transactions > 0 else 0.0
avg_card_age = filtered["Card_Age"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Unique Customers", f"{unique_customers:,}")
k2.metric("Transactions", f"{num_transactions:,}")
k3.metric("Fraudulent Transactions", f"{fraud_count:,}")
k4.metric("Fraud Rate", f"{fraud_rate:.2f}%")
k5.metric(
    "Avg Card Age",
    f"{avg_card_age:.0f} months" if pd.notna(avg_card_age) else "N/A",
)

st.markdown("")  # spacing

# ===========================================================================
# Card Type Analysis
# ===========================================================================
section_heading("Card Type Analysis")

# --- Transaction counts by Card Type ---
card_txn_counts = (
    filtered["Card_Type"]
    .value_counts()
    .rename_axis("Card Type")
    .reset_index(name="Transactions")
)

col_ct1, col_ct2 = st.columns(2)

with col_ct1:
    st.markdown("**Transactions by Card Type**")
    st.bar_chart(card_txn_counts, x="Card Type", y="Transactions", height=350)

# --- Fraudulent transaction counts by Card Type ---
fraud_by_card = (
    filtered[filtered["Fraud_Label"] == 1]["Card_Type"]
    .value_counts()
    .rename_axis("Card Type")
    .reset_index(name="Fraudulent Transactions")
)

with col_ct2:
    st.markdown("**Fraudulent Transactions by Card Type**")
    if fraud_by_card.empty:
        st.info("No fraudulent transactions in the current selection.")
    else:
        st.bar_chart(
            fraud_by_card,
            x="Card Type",
            y="Fraudulent Transactions",
            height=350,
        )

st.markdown("")  # spacing

# ---------------------------------------------------------------------------
# Fraud Rate by Card Type
# ---------------------------------------------------------------------------
section_heading("Fraud Rate by Card Type")

card_fraud_summary = (
    filtered.groupby("Card_Type", dropna=False)
    .agg(
        Total_Transactions=("Fraud_Label", "count"),
        Fraudulent_Transactions=("Fraud_Label", "sum"),
    )
    .reset_index()
)
card_fraud_summary["Fraud_Rate (%)"] = np.where(
    card_fraud_summary["Total_Transactions"] > 0,
    card_fraud_summary["Fraudulent_Transactions"]
    / card_fraud_summary["Total_Transactions"]
    * 100,
    0.0,
)
card_fraud_summary = card_fraud_summary.rename(columns={"Card_Type": "Card Type"})

col_fr1, col_fr2 = st.columns(2)

with col_fr1:
    st.dataframe(
        card_fraud_summary,
        use_container_width=True,
        hide_index=True,
    )

with col_fr2:
    st.bar_chart(
        card_fraud_summary[["Card Type", "Fraud_Rate (%)"]],
        x="Card Type",
        y="Fraud_Rate (%)",
        height=350,
    )

st.markdown("")  # spacing

# ===========================================================================
# Card Age Analysis
# ===========================================================================
section_heading("Card Age Analysis")

card_age_series = filtered["Card_Age"].dropna()

if card_age_series.empty:
    st.info("No card-age data available for the current selection.")
else:
    # --- Card Age distribution (histogram via binning) ---
    st.markdown("**Card Age Distribution**")

    num_bins = 10
    bin_edges = np.linspace(
        card_age_series.min(), card_age_series.max(), num_bins + 1
    )
    labels = [
        f"{int(bin_edges[i])}–{int(bin_edges[i + 1])}"
        for i in range(len(bin_edges) - 1)
    ]
    filtered_copy = filtered.dropna(subset=["Card_Age"]).copy()
    filtered_copy["Card_Age_Group"] = pd.cut(
        filtered_copy["Card_Age"],
        bins=bin_edges,
        labels=labels,
        include_lowest=True,
    )

    age_dist = (
        filtered_copy["Card_Age_Group"]
        .value_counts()
        .sort_index()
        .rename_axis("Card Age (months)")
        .reset_index(name="Transactions")
    )

    st.bar_chart(age_dist, x="Card Age (months)", y="Transactions", height=350)

    st.markdown("")  # spacing

    # --- Fraud comparison by card-age group ---
    st.markdown("**Fraud Activity by Card Age Group**")

    age_fraud = (
        filtered_copy.groupby("Card_Age_Group", observed=False)
        .agg(
            Total=("Fraud_Label", "count"),
            Fraudulent=("Fraud_Label", "sum"),
        )
        .reset_index()
    )
    age_fraud["Fraud_Rate (%)"] = np.where(
        age_fraud["Total"] > 0,
        age_fraud["Fraudulent"] / age_fraud["Total"] * 100,
        0.0,
    )
    age_fraud = age_fraud.rename(columns={"Card_Age_Group": "Card Age (months)"})

    col_age1, col_age2 = st.columns(2)

    with col_age1:
        st.dataframe(age_fraud, use_container_width=True, hide_index=True)

    with col_age2:
        st.bar_chart(
            age_fraud[["Card Age (months)", "Fraud_Rate (%)"]],
            x="Card Age (months)",
            y="Fraud_Rate (%)",
            height=350,
        )

st.markdown("")  # spacing

# ===========================================================================
# Device Type Analysis
# ===========================================================================
section_heading("Device Type Analysis")

col_dt1, col_dt2 = st.columns(2)

# --- Transaction counts by Device Type ---
device_txn_counts = (
    filtered["Device_Type"]
    .value_counts()
    .rename_axis("Device Type")
    .reset_index(name="Transactions")
)

with col_dt1:
    st.markdown("**Transactions by Device Type**")
    st.bar_chart(device_txn_counts, x="Device Type", y="Transactions", height=350)

# --- Fraud counts by Device Type ---
fraud_by_device = (
    filtered[filtered["Fraud_Label"] == 1]["Device_Type"]
    .value_counts()
    .rename_axis("Device Type")
    .reset_index(name="Fraudulent Transactions")
)

with col_dt2:
    st.markdown("**Fraudulent Transactions by Device Type**")
    if fraud_by_device.empty:
        st.info("No fraudulent transactions in the current selection.")
    else:
        st.bar_chart(
            fraud_by_device,
            x="Device Type",
            y="Fraudulent Transactions",
            height=350,
        )

st.markdown("")  # spacing

# ===========================================================================
# Customer-Level Summary
# ===========================================================================
section_heading("Customer Summary")

customer_summary = (
    filtered.groupby("User_ID", dropna=False)
    .agg(
        Transaction_Count=("Transaction_Amount", "count"),
        Total_Amount=("Transaction_Amount", "sum"),
        Fraudulent_Transactions=("Fraud_Label", "sum"),
    )
    .reset_index()
    .sort_values("Fraudulent_Transactions", ascending=False)
)

customer_summary["Total_Amount"] = customer_summary["Total_Amount"].round(2)

st.caption(
    f"Showing {len(customer_summary):,} customers from the filtered data. "
    "Sorted by number of fraudulent transactions (descending)."
)
st.dataframe(
    customer_summary.head(200),
    use_container_width=True,
    hide_index=True,
    column_config={
        "User_ID": "Customer ID",
        "Transaction_Count": "Transactions",
        "Total_Amount": st.column_config.NumberColumn(
            "Total Amount", format="$%.2f"
        ),
        "Fraudulent_Transactions": "Fraudulent Txns",
    },
)
if len(customer_summary) > 200:
    st.caption(
        f"Displaying the first 200 of {len(customer_summary):,} customers."
    )

st.markdown("")  # spacing

# ===========================================================================
# Filtered Transaction Preview
# ===========================================================================
section_heading("Transaction Preview")

preview_columns = [
    "Transaction_ID",
    "User_ID",
    "Transaction_Amount",
    "Card_Type",
    "Card_Age",
    "Device_Type",
    "Previous_Fraudulent_Activity",
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
