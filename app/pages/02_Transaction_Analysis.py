"""
Transaction Analysis — Financial Fraud Detection Dashboard
============================================================

Detailed breakdown of transactions, fraud vs. legitimate
patterns, and distribution analysis. Full analytics coming
in the next dashboard build-out step.
"""

import sys
from pathlib import Path

import streamlit as st

# Project root resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ui import coming_soon_placeholder, footer, page_header  # noqa: E402

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Transaction Analysis — Fraud Detection",
    page_icon="💳",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
page_header(
    "Transaction Analysis",
    "Explore transaction patterns, amounts, and fraud distribution.",
)

coming_soon_placeholder("Transaction Analysis")

footer()
