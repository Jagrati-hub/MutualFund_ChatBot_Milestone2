from __future__ import annotations
import streamlit as st
import time
from typing import Any
from src.scheduler import start_scheduler_once, run_pipeline_once

# Hardcoded credentials
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Admin Login")
        with st.form("login_form"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if user == ADMIN_USER and password == ADMIN_PASS:
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        return False
    return True

def render_admin_page():
    # Page setup
    st.set_page_config(page_title="Admin Panel - Groww MF", page_icon="⚙️", layout="wide")
    
    # Check Auth
    if not check_login():
        st.stop()

    st.title("⚙️ Admin Dashboard")
    st.markdown("Manage the data pipeline and monitor the scheduler from here.")
    st.markdown("---")

    # Import dependencies from shared module
    from src.shared import SCOPE_FUNDS_BY_CATEGORY, SCOPE_FUNDS, ensure_scheduler_started

    scheduler = ensure_scheduler_started()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🕐 Scheduler Status")
        if scheduler and scheduler.running:
            st.success("Scheduler is **running**", icon="✅")
            try:
                job = scheduler.get_job("daily_scrape_and_ingest")
                if job and job.next_run_time:
                    st.info(f"Next scheduled run: **{job.next_run_time.strftime('%d %b %Y, %I:%M %p %Z')}**")
            except Exception as e:
                st.error(f"Error fetching job: {e}")
        else:
            st.warning("Scheduler not running", icon="⚠️")
        
        st.markdown("---")
        st.subheader("🔄 Manual Pipeline Control")
        st.caption("Trigger an immediate scrape + ingest cycle.")
        if st.button("▶ Run Pipeline Now", use_container_width=True):
            with st.spinner("Running scrape → ingest pipeline..."):
                try:
                    run_pipeline_once()
                    st.success("Pipeline completed successfully!", icon="✅")
                except Exception as exc:
                    st.error(f"Pipeline failed: {exc}", icon="❌")

    with col2:
        st.subheader("🗂️ In-Scope Funds")
        st.caption(f"{len(SCOPE_FUNDS)} funds across 4 categories")
        for category, funds in SCOPE_FUNDS_BY_CATEGORY.items():
            with st.expander(f"{category} ({len(funds)})", expanded=False):
                for fund in funds:
                    st.markdown(f"- {fund}")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

if __name__ == "__main__":
    render_admin_page()
