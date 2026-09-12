"""
Geographic Analysis — Financial Fraud Detection Dashboard
==========================================================

Geographic distribution of fraud activity, regional patterns,
and location-based insights. Full analytics coming in the
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
    page_title="Geographic Analysis — Fraud Detection",
    page_icon="🌐",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
page_header(
    "Geographic Analysis",
    "Regional fraud distribution and location-based pattern analysis.",
)

coming_soon_placeholder("Geographic Analysis")

footer()
