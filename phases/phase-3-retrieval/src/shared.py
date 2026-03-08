from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

# Add phase directories to Python path for imports
_current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_current_dir / "phase-4-orchestration"))

# ── constants ──────────────────────────────────────────────────────────────────
# All 32 Groww AMC funds, organised by category
SCOPE_FUNDS_BY_CATEGORY: dict[str, list[str]] = {
    "📈 Equity": [
        "Groww Nifty Total Market Index Fund",
        "Groww Multicap Fund",
        "Groww Small Cap Fund",
        "Groww Large Cap Fund",
        "Groww Value Fund",
        "Groww ELSS Tax Saver Fund",
        "Groww Banking & Financial Services Fund",
        "Groww Nifty Smallcap 250 Index Fund",
        "Groww Nifty Non-Cyclical Consumer Index Fund",
        "Groww Nifty Next 50 Index Fund",
        "Groww Nifty Midcap 150 Index Fund",
        "Groww Nifty EV & New Age Automotive ETF FoF",
        "Groww Nifty India Defence ETF FoF",
        "Groww Nifty 200 ETF FoF",
        "Groww Nifty 500 Momentum 50 ETF FoF",
        "Groww Nifty India Railways PSU Index Fund",
        "Groww BSE Power ETF FoF",
        "Groww Nifty India Internet ETF FoF",
        "Groww Nifty PSE ETF FoF",
        "Groww Nifty Capital Markets ETF FoF",
        "Groww Arbitrage Fund",
    ],
    "🏦 Debt": [
        "Groww Liquid Fund",
        "Groww Overnight Fund",
        "Groww Short Duration Fund",
        "Groww Dynamic Bond Fund",
        "Groww Gilt Fund",
        "Groww Nifty 1D Rate Liquid ETF",
    ],
    "⚖️ Hybrid": [
        "Groww Aggressive Hybrid Fund",
        "Groww Multi Asset Allocation Fund",
        "Groww Multi Asset Omni FoF",
    ],
    "🪙 Commodities": [
        "Groww Gold ETF FoF",
        "Groww Silver ETF FoF",
    ],
}

# Flat list for backward-compat references
SCOPE_FUNDS: list[str] = [
    fund for funds in SCOPE_FUNDS_BY_CATEGORY.values() for fund in funds
]

@st.cache_resource
def _init_scheduler():
    """Start the APScheduler background job exactly once per process."""
    from src.scheduler import start_scheduler_once
    return start_scheduler_once()

def ensure_scheduler_started():
    """Idempotent call – safe on every Streamlit rerun."""
    return _init_scheduler()
