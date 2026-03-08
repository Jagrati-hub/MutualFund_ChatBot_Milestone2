from __future__ import annotations

import streamlit as st
import sys
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Admin - Groww MF Assistant",
    page_icon="🛠",
    layout="wide",
)

# Add phase directories to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "phase-4-orchestration"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "phase-3-retrieval"))

from src.scheduler import run_pipeline_once
from src.shared import ensure_scheduler_started, SCOPE_FUNDS_BY_CATEGORY

# Dark theme CSS
st.markdown("""
<style>
.stApp {
    background: #0f172a;
    color: #e2e8f0;
}

.admin-header {
    background: #1e293b;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    border: 1px solid #334155;
}

.admin-title {
    font-size: 2rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0;
}

.status-card {
    background: #1e293b;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #334155;
    margin-bottom: 1rem;
}

.status-dot {
    height: 10px;
    width: 10px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.status-dot.off {
    background: #ef4444;
}

.stButton > button {
    background: #3b82f6 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 1.5rem !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background: #2563eb !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="admin-header"><h1 class="admin-title">🛠 Admin Dashboard</h1></div>', unsafe_allow_html=True)

# Ensure scheduler is started
scheduler = ensure_scheduler_started()
from src.scheduler import SCHEDULER_JOB_ID

# System Status
st.markdown('<div class="status-card">', unsafe_allow_html=True)
st.subheader("System Status")

col1, col2 = st.columns(2)

with col1:
    if hasattr(scheduler, "running") and scheduler.running:
        st.markdown('<div style="display:flex; align-items:center;"><span class="status-dot"></span><span style="color:#10b981; font-weight:600;">Scheduler Active</span></div>', unsafe_allow_html=True)
        job = scheduler.get_job(SCHEDULER_JOB_ID)
        if job and job.next_run_time:
            st.caption(f"Next run: {job.next_run_time.strftime('%d %b %Y, %H:%M %Z')}")
    else:
        st.markdown('<div style="display:flex; align-items:center;"><span class="status-dot off"></span><span style="color:#ef4444; font-weight:600;">Scheduler Inactive</span></div>', unsafe_allow_html=True)

with col2:
    st.metric("Total Funds", len([f for funds in SCOPE_FUNDS_BY_CATEGORY.values() for f in funds]))

st.markdown('</div>', unsafe_allow_html=True)

# Actions
st.markdown('<div class="status-card">', unsafe_allow_html=True)
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Run Pipeline Now", use_container_width=True):
        with st.status("Running scraper + ingestor...", expanded=True) as status:
            try:
                st.write("Fetching latest data from Groww...")
                run_pipeline_once()
                st.write("Ingestion complete!")
                status.update(label="Pipeline completed successfully!", state="complete", expanded=False)
                st.success("✅ Data updated!")
            except Exception as e:
                status.update(label=f"Pipeline failed: {e}", state="error")
                st.error(f"❌ Error: {e}")

with col2:
    if st.button("🔄 Restart Scheduler", use_container_width=True):
        st.info("Scheduler restart requires app restart")

with col3:
    if st.button("📊 View Logs", use_container_width=True):
        st.info("Log viewer coming soon")

st.markdown('</div>', unsafe_allow_html=True)

# Fund Categories
st.markdown('<div class="status-card">', unsafe_allow_html=True)
st.subheader("Fund Categories")

for category, funds in SCOPE_FUNDS_BY_CATEGORY.items():
    with st.expander(f"{category} ({len(funds)} funds)"):
        for fund in sorted(funds):
            st.write(f"• {fund}")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Admin Dashboard • Groww Mutual Fund Assistant")
