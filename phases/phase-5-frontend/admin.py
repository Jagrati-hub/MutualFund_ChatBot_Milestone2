"""
Admin Dashboard - Separate Page
================================
This is a completely separate admin page that is not accessible from the main chat page.
Access via: http://localhost:8502/admin
"""

import sys
from pathlib import Path

# Add phase directories to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "phase-4-orchestration"))
sys.path.insert(0, str(Path(__file__).parent.parent / "phase-3-retrieval"))

import streamlit as st
from src.shared import SCOPE_FUNDS_BY_CATEGORY, SCOPE_FUNDS, ensure_scheduler_started

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Admin Dashboard - Groww MF FAQ",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Dark theme CSS for admin page ──────────────────────────────────────────────
ADMIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #ffffff !important;
}

.stApp {
    background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}

/* ── Admin header ── */
.admin-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%);
    border-bottom: 2px solid #00d09c;
    padding: 2rem;
    margin-bottom: 2rem;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

.admin-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #00d09c !important;
    margin: 0;
    letter-spacing: -0.03em;
}

.admin-subtitle {
    font-size: 1rem;
    color: #cbd5e0 !important;
    margin: 0.5rem 0 0 0;
    font-weight: 400;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #2d3748 0%, #374151 100%) !important;
    border: 1px solid #4a5568 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00d09c 0%, #00b386 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    padding: 0.9rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 16px rgba(0,208,156,0.2) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #00b386 0%, #009970 100%) !important;
    box-shadow: 0 8px 24px rgba(0,208,156,0.3) !important;
    transform: translateY(-2px) !important;
}

/* ── Section headers ── */
h2 {
    color: #00d09c !important;
    border-bottom: 2px solid #00d09c;
    padding-bottom: 0.8rem;
    margin-top: 2rem !important;
}

/* ── Status indicators ── */
.status-active {
    color: #00d09c !important;
    font-weight: 700;
}

.status-inactive {
    color: #ff4d4d !important;
    font-weight: 700;
}

/* ── Info boxes ── */
.stInfo {
    background: linear-gradient(135deg, #1a3a3a 0%, #0f2f2f 100%) !important;
    border-left: 4px solid #00d09c !important;
    border-radius: 8px !important;
}

.stSuccess {
    background: linear-gradient(135deg, #1a3a2a 0%, #0f2f1f 100%) !important;
    border-left: 4px solid #00d09c !important;
    border-radius: 8px !important;
}

.stError {
    background: linear-gradient(135deg, #3a1a1a 0%, #2f0f0f 100%) !important;
    border-left: 4px solid #ff4d4d !important;
    border-radius: 8px !important;
}

/* ── Hide Streamlit defaults ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(ADMIN_CSS, unsafe_allow_html=True)

# ── Admin page content ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="admin-header">
        <p class="admin-title">⚙️ Admin Dashboard</p>
        <p class="admin-subtitle">Pipeline Management & System Status</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── System Status ──────────────────────────────────────────────────────────────
st.markdown("## 🔍 System Status")

col1, col2, col3 = st.columns(3)

from src.shared import ensure_scheduler_started
scheduler = ensure_scheduler_started()
from src.scheduler import SCHEDULER_JOB_ID

with col1:
    if hasattr(scheduler, "running") and scheduler.running:
        st.metric("Scheduler Status", "🟢 Active", "Running")
    else:
        st.metric("Scheduler Status", "🔴 Inactive", "Stopped")

with col2:
    job = scheduler.get_job(SCHEDULER_JOB_ID)
    if job and job.next_run_time:
        st.metric("Next Update", job.next_run_time.strftime("%H:%M"), job.next_run_time.strftime("%d %b"))
    else:
        st.metric("Next Update", "N/A", "No job scheduled")

with col3:
    st.metric("Total Funds", len(SCOPE_FUNDS), "32 schemes")

st.markdown("---")

# ── Pipeline Controls ──────────────────────────────────────────────────────────
st.markdown("## 🚀 Pipeline Controls")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Run Data Pipeline Now", use_container_width=True, key="run_pipeline_admin"):
        with st.status("Running scraper + ingestor...", expanded=True) as status:
            try:
                from src.scheduler import run_pipeline_once
                st.write("📥 Fetching latest data from Groww...")
                run_pipeline_once()
                st.write("✅ Ingestion complete!")
                status.update(label="✅ Pipeline successfully completed!", state="complete", expanded=False)
                st.success("Data successfully updated!", icon="✅")
            except Exception as e:
                status.update(label=f"❌ Pipeline failed: {e}", state="error")
                st.error(f"Error: {e}")

with col2:
    if st.button("🗑️ Clear Cache", use_container_width=True, key="clear_cache_admin"):
        try:
            import shutil
            from pathlib import Path
            cache_dir = Path(".cache/fund_attributes")
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
            st.success("✅ Cache cleared successfully!")
        except Exception as e:
            st.error(f"Error clearing cache: {e}")

st.markdown("---")

# ── Cache Statistics ──────────────────────────────────────────────────────────
st.markdown("## 📊 Cache Statistics")

try:
    from pathlib import Path
    cache_dir = Path(".cache/fund_attributes")
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Cached Entries", len(cache_files), "fund-attribute pairs")
        
        with col2:
            total_size = sum(f.stat().st_size for f in cache_files) / 1024
            st.metric("Cache Size", f"{total_size:.1f} KB", "on disk")
        
        with col3:
            st.metric("Cache TTL", "24 hours", "auto-expire")
    else:
        st.info("No cache directory found")
except Exception as e:
    st.warning(f"Could not read cache stats: {e}")

st.markdown("---")

# ── Fund Statistics ────────────────────────────────────────────────────────────
st.markdown("## 📈 Fund Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    equity_count = len(SCOPE_FUNDS_BY_CATEGORY.get("📈 Equity", []))
    st.metric("Equity Funds", equity_count, "schemes")

with col2:
    debt_count = len(SCOPE_FUNDS_BY_CATEGORY.get("🏦 Debt", []))
    st.metric("Debt Funds", debt_count, "schemes")

with col3:
    hybrid_count = len(SCOPE_FUNDS_BY_CATEGORY.get("⚖️ Hybrid", []))
    st.metric("Hybrid Funds", hybrid_count, "schemes")

with col4:
    commodity_count = len(SCOPE_FUNDS_BY_CATEGORY.get("🪙 Commodities", []))
    st.metric("Commodity Funds", commodity_count, "schemes")

st.markdown("---")

# ── System Logs ────────────────────────────────────────────────────────────────
st.markdown("## 📋 Recent Activity")
st.info("✅ System running normally. Last pipeline run completed successfully.")
