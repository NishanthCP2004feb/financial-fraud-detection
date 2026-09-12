"""
Shared UI helpers for the Financial Fraud Detection Dashboard.
================================================================

Provides consistent styling and layout components used across
all dashboard pages. Keep this module lightweight — it should
contain only reusable presentation helpers, not business logic.
"""

import sys
import streamlit as st

# ---------------------------------------------------------------------------
# Application constants
# ---------------------------------------------------------------------------
APP_TITLE = "Financial Fraud Detection System"
APP_VERSION = "0.2.0"

# Page definitions used for navigation reference
PAGES = {
    "overview": {"title": "Executive Overview", "icon": "📊"},
    "transactions": {"title": "Transaction Analysis", "icon": "💳"},
    "geographic": {"title": "Geographic Analysis", "icon": "🌐"},
    "customer_card": {"title": "Customer & Card Analysis", "icon": "👥"},
    "time": {"title": "Time Analysis", "icon": "🕐"},
    "model": {"title": "Model Performance", "icon": "⚙️"},
}


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
def page_header(title: str, description: str = "") -> None:
    """
    Render a consistent page header with title and optional description.

    Parameters
    ----------
    title : str
        The page heading text.
    description : str, optional
        A brief subtitle shown below the heading.
    """
    st.markdown(
        f"<h2 style='margin-bottom: 0.2rem;'>{title}</h2>",
        unsafe_allow_html=True,
    )
    if description:
        st.markdown(
            f"<p style='color: #6c757d; margin-top: 0;'>{description}</p>",
            unsafe_allow_html=True,
        )
    st.divider()


# ---------------------------------------------------------------------------
# Section heading
# ---------------------------------------------------------------------------
def section_heading(title: str) -> None:
    """Render a styled section heading within a page."""
    st.markdown(f"### {title}")


# ---------------------------------------------------------------------------
# Status indicator
# ---------------------------------------------------------------------------
def status_indicator(label: str, status: str, detail: str = "") -> None:
    """
    Display a status badge with optional detail text.

    Parameters
    ----------
    label : str
        What the status describes (e.g. "Model", "Dataset").
    status : str
        One of "ok", "warning", "error".
    detail : str, optional
        Additional context shown beside the status.
    """
    icons = {"ok": "🟢", "warning": "🟡", "error": "🔴"}
    icon = icons.get(status, "⚪")
    text = f"{icon} **{label}**"
    if detail:
        text += f" — {detail}"
    st.markdown(text)


# ---------------------------------------------------------------------------
# Placeholder for pages under construction
# ---------------------------------------------------------------------------
def coming_soon_placeholder(page_name: str) -> None:
    """
    Render a clean placeholder message for pages not yet implemented.

    Parameters
    ----------
    page_name : str
        The name of the page section (used in the message).
    """
    st.info(
        f"**{page_name}** analytics will be available in the next dashboard update.",
        icon="🔜",
    )
    st.caption("This section is part of the planned dashboard build-out.")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def footer() -> None:
    """Render a consistent page footer with version and runtime info."""
    st.divider()
    st.caption(
        f"{APP_TITLE} v{APP_VERSION}  ·  "
        f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}  ·  "
        f"Streamlit {st.__version__}"
    )
