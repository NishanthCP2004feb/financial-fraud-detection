"""
Executive Overview — Financial Fraud Detection Dashboard
=========================================================

High-level summary of fraud detection metrics, key performance
indicators, and system health. Full analytics coming in the
next dashboard build-out step.
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
    page_title="Executive Overview — Fraud Detection",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
page_header(
    "Executive Overview",
    "High-level summary of fraud detection performance and key metrics.",
)

coming_soon_placeholder("Executive Overview")

footer()
