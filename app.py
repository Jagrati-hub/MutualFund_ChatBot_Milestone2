from __future__ import annotations

# Phase 5 – Frontend (Streamlit App)
# ====================================
# Groww Mutual Fund FAQ Assistant — Premium Chat UI
#
# Responsibilities:
# - On app load, idempotently start the background APScheduler via
#   `start_scheduler_once()` (wrapped in `st.cache_resource` so it only
#   runs once per process, not on every Streamlit rerun).
# - Render a polished chat interface:
#     • Title bar with logo emoji and scope disclaimer pill.
#     • 3 quick-start example question buttons.
#     • Scrollable chat history preserving the full session.
#     • Chat input box at the bottom.
# - For every user query:
#     • Call `rag_engine.validate_query()` as a guardrail.
#     • If BLOCKED → display the default refusal from `system_prompt.md`
#       with a warning banner (no LLM call is made).
#     • If ALLOWED  → call `rag_engine.answer()` and display:
#         – The ≤3-sentence factual answer.
#         – A clickable "Source" link for the citation URL.
# - Sidebar with Admin controls:
#     • Next scheduled run time.
#     • Manual "Run Pipeline Now" trigger.
#     • A status / log area.

import time
from datetime import datetime
from typing import Any, Dict

import streamlit as st

# ── page config must be the VERY FIRST Streamlit call ─────────────────────────
st.set_page_config(
    page_title="Groww MF FAQ Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.scheduler import start_scheduler_once, run_pipeline_once
from src import rag_engine

# ── Playwright Installation (Automatic for Streamlit Cloud) ──────────────────
def _ensure_playwright_installed():
    """Check and install playwright browsers if missing."""
    import subprocess
    try:
        import playwright
    except ImportError:
        return # Should be in requirements.txt
    
    # We check a flag to avoid repeated attempts
    if "playwright_ready" not in st.session_state:
        try:
            # Install chromium
            subprocess.run(["playwright", "install", "chromium"], check=True)
            st.session_state.playwright_ready = True
        except Exception as e:
            st.warning(f"Note: Playwright browser installation failed or skipped: {e}")

_ensure_playwright_installed()

# ── constants ──────────────────────────────────────────────────────────────────
EXAMPLE_QUERIES: list[str] = [
    "What is the investment objective of the Groww ELSS Tax Saver Fund?",
    "What is the expense ratio of the Groww Nifty Total Market Index Fund?",
    "Is the Groww Liquid Fund suitable for short-term parking of funds?",
]

from src.shared import SCOPE_FUNDS_BY_CATEGORY, SCOPE_FUNDS, ensure_scheduler_started
CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #262c3a !important; /* Unified dark text for all elements */
}

/* ── App background (Clean Groww-style) ── */
.stApp {
    background-color: #f7f9fc; /* Slightly deeper than pure white */
    background-image: radial-gradient(#d1d9e6 0.5px, transparent 0.5px);
    background-size: 20px 20px; /* Subtle dot pattern to reduce "flat white" look */
}

/* ── Main container ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 850px;
}

/* ── Header hero area (Groww Mint Gradient) ── */
.hero-header {
    background: linear-gradient(135deg, #00d09c 0%, #00b386 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,208,156,0.15);
    position: relative;
    overflow: hidden;
    text-align: center;
}
.hero-header::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -10%;
    width: 50%;
    height: 200%;
    background: rgba(255,255,255,0.08);
    transform: rotate(25deg);
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff !important; /* Keep white on green header */
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.9) !important;
    margin: 0;
    font-weight: 400;
}

/* ── Scope disclaimer pill ── */
.scope-pill {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 100px;
    padding: 0.4rem 1.2rem;
    font-size: 0.8rem;
    color: #ffffff !important;
    margin-top: 1.2rem;
    backdrop-filter: blur(4px);
    font-weight: 500;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #5c6a8b;
    margin-bottom: 0.8rem;
    padding-left: 0.4rem;
}

/* ── Example question buttons ── */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: #ffffff;
    border: 1px solid #d1dae6;
    border-radius: 100px;
    color: #262c3a !important;
    font-size: 0.85rem;
    padding: 0.6rem 1.2rem;
    width: 100%;
    text-align: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    height: auto;
    min-height: 3.5rem;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: #f0fffb;
    border-color: #00d09c;
    color: #00d09c !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,208,156,0.15);
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 20px !important;
    margin-bottom: 1.5rem !important;
    padding: 1.2rem 1.5rem !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05) !important;
}

/* User bubble (Soft Blue) */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: #e9efff !important;
    border: 1px solid #c8d7ff !important;
    margin-left: 10% !important;
}

/* Assistant bubble (Soft Mint) */
[data-testid="stChatMessage"][data-testid*="assistant"],
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #e6f9f4 !important;
    border: 1px solid #b7e9dc !important;
    margin-right: 10% !important;
}

/* ── Text within bubbles ── */
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
    color: #1a202c !important;
    line-height: 1.6;
}

/* ── Citation & Recency Bar ── */
.assistant-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(0, 208, 156, 0.15);
    align-items: center;
}

.citation-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #00d09c;
    color: #ffffff !important;
    border-radius: 100px;
    padding: 0.4rem 1.2rem;
    font-size: 0.9rem !important;
    text-decoration: none !important;
    transition: all 0.2s ease;
    font-weight: 600;
}
.citation-link:hover {
    background: #00b386;
    box-shadow: 0 4px 12px rgba(0,208,156,0.25);
}

.data-recency {
    font-size: 0.75rem;
    color: #4a5568 !important;
    font-weight: 600;
    margin: 0;
}

/* ── Message timestamps ── */
.message-timestamp {
    font-size: 0.7rem;
    color: #718096 !important;
    margin-top: 0.5rem;
    display: block;
    text-align: right;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #eef2f6 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #00d09c;
    border: none;
    border-radius: 12px;
    color: #ffffff;
    font-weight: 600;
    padding: 0.75rem 1rem;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #00b386;
    box-shadow: 0 4px 12px rgba(0,208,156,0.2);
}

/* ── Chat input (Centered & Floating feel) ── */
[data-testid="stChatInput"] {
    border: 1px solid #e5eef5 !important;
    border-radius: 100px !important;
    background: #ffffff !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
}

/* ── Admin Status Dots ── */
.status-dot {
    height: 10px;
    width: 10px;
    background-color: #00d09c;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
}
.status-dot.off {
    background-color: #ff4d4d;
}

/* ── Hide Streamlit defaults ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Query handler ──────────────────────────────────────────────────────────────
def handle_query(user_query: str) -> Dict[str, Any]:
    """
    Entry point for all incoming user queries.

    1. Run guardrails via `rag_engine.validate_query()`.
    2. If allowed, call `rag_engine.answer()`.
    3. Return a uniform dict with keys:
       blocked, reason, answer, citation_url.
    """
    is_allowed, reason = rag_engine.validate_query(user_query)
    if not is_allowed:
        refusal = reason or rag_engine.get_default_refusal()
        return {
            "blocked": True,
            "reason": reason,
            "answer": refusal,
            "citation_url": None,
        }
    try:
        return rag_engine.answer(user_query)
    except Exception as exc:
        return {
            "blocked": False,
            "reason": str(exc),
            "answer": f"⚠️ A backend error occurred: {exc}",
            "citation_url": None,
        }


# ── Hero header ────────────────────────────────────────────────────────────────
def render_hero() -> None:
    st.markdown(
        f"""
        <div class="hero-header">
            <p class="hero-title">📈 Groww Mutual Fund FAQ</p>
            <p class="hero-subtitle">
                Official support for Groww AMC schemes. All facts, no financial advice.
            </p>
            <div class="scope-pill">🔍 Real-time access to {len(SCOPE_FUNDS)} mutual fund schemes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Chat UI ────────────────────────────────────────────────────────────────────
def render_chat_ui() -> None:
    # ── Session defaults ──────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "example_clicked" not in st.session_state:
        st.session_state.example_clicked = None

    # ── Example prompts (Stable - always visible) ──────────────────────────
    st.markdown('<p class="section-label">💡 Quick Start — try one of these</p>', unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLE_QUERIES))
    for i, example in enumerate(EXAMPLE_QUERIES):
        if cols[i].button(example, key=f"example_{i}"):
            st.session_state.example_clicked = example
            st.rerun()

    # ── Autoscroll Helper ──────────────────────────────────────────────────
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        window.parent.document.querySelectorAll('.main').forEach(el => {
            el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
        });
        </script>
        """,
        height=0,
    )

    # ── Consume prefill from example button ───────────────────────────────
    user_input: str | None = None
    if st.session_state.example_clicked:
        user_input = st.session_state.example_clicked
        st.session_state.example_clicked = None

    # ── Replay chat history ───────────────────────────────────────────────
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("blocked"):
                st.markdown(
                    f'<div class="refusal-box">🚫 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(msg["content"])
            
            # Show citation and recency in a row if possible
            if not msg.get("blocked") and msg["role"] == "assistant":
                if msg.get("citation_url") or msg.get("last_updated"):
                    st.markdown('<div class="assistant-footer">', unsafe_allow_html=True)
                    if msg.get("citation_url"):
                        st.markdown(
                            f'<a class="citation-link" href="{msg["citation_url"]}" target="_blank">'
                            f'🔗 Source</a>',
                            unsafe_allow_html=True,
                        )
                    if msg.get("last_updated"):
                        st.markdown(f'<p class="data-recency">🗓️ Data as of: {msg["last_updated"]}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Show message timestamp at very bottom
            if msg.get("timestamp"):
                st.markdown(f'<span class="message-timestamp">Sent at {msg["timestamp"]}</span>', unsafe_allow_html=True)

    # ── Chat input ────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask about any Groww Mutual Fund scheme…"):
        user_input = prompt

    # ── Process query ─────────────────────────────────────────────────────
    if user_input:
        from datetime import datetime
        curr_time = datetime.now().strftime("%H:%M")
        
        # Show user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
            st.markdown(f'<span class="message-timestamp">Sent at {curr_time}</span>', unsafe_allow_html=True)
            
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input, 
            "blocked": False,
            "timestamp": curr_time
        })

        # Generate and stream assistant response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Retrieving facts…"):
                response = handle_query(user_input)
            
            resp_time = datetime.now().strftime("%H:%M")

            if response.get("blocked"):
                st.markdown(
                    f'<div class="refusal-box">🚫 {response["answer"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(response["answer"])

            # Footer for assistant message
            if not response.get("blocked"):
                if response.get("citation_url") or response.get("last_updated"):
                    st.markdown('<div class="assistant-footer">', unsafe_allow_html=True)
                    if response.get("citation_url"):
                        st.markdown(
                            f'<a class="citation-link" href="{response["citation_url"]}" target="_blank">'
                            f'🔗 Source</a>',
                            unsafe_allow_html=True,
                        )
                    if response.get("last_updated"):
                        st.markdown(f'<p class="data-recency">🗓️ Data as of: {response["last_updated"]}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f'<span class="message-timestamp">Sent at {resp_time}</span>', unsafe_allow_html=True)

        # Persist to session
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "citation_url": response.get("citation_url"),
            "blocked": response.get("blocked", False),
            "last_updated": response.get("last_updated"),
            "timestamp": resp_time
        })


# ── Clear chat button ──────────────────────────────────────────────────────────
def render_clear_button() -> None:
    if st.session_state.get("messages"):
        col1, col2, col3 = st.columns([7, 1.5, 1.5])
        with col3:
            if st.button("🗑 Clear chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<p class="hero-title" style="font-size:1.5rem; color:#44475b; text-align:left;">🛠 Admin</p>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Ensure scheduler is started and get instance
        from src.shared import ensure_scheduler_started
        scheduler = ensure_scheduler_started()
        from src.scheduler import SCHEDULER_JOB_ID
        
        st.subheader("System Status")
        # APScheduler uses .running (bool)
        if hasattr(scheduler, "running") and scheduler.running:
            st.markdown('<div style="display:flex; align-items:center;"><span class="status-dot"></span><span style="color:#00d09c; font-weight:600;">Active</span></div>', unsafe_allow_html=True)
            job = scheduler.get_job(SCHEDULER_JOB_ID)
            if job:
                next_run = job.next_run_time
                if next_run:
                    st.caption(f"Next update: {next_run.strftime('%d %b, %H:%M')}")
        else:
            st.markdown('<div style="display:flex; align-items:center;"><span class="status-dot off"></span><span style="color:#ff4d4d; font-weight:600;">Inactive</span></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Manual Controls")
        
        if st.button("🚀 Run Data Pipeline", use_container_width=True):
            with st.status("Running scraper + ingestor...", expanded=True) as status:
                try:
                    from src.scheduler import run_pipeline_once
                    st.write("Fetching latest data from Groww...")
                    run_pipeline_once()
                    st.write("Ingestion complete! Refreshing...")
                    status.update(label="Pipeline successfully completed!", state="complete", expanded=False)
                    st.toast("Data successfully updated!", icon="✅")
                    # No longer need to rerun, but might help refresh cached artifacts
                    # st.rerun()
                except Exception as e:
                    status.update(label=f"Pipeline failed: {e}", state="error")
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.write("Built with ❤️ for Groww Mutual Fund Investors")


# ── Main entry point ───────────────────────────────────────────────────────────
def main() -> None:
    # We still ensure the scheduler is started in the background
    ensure_scheduler_started()
    
    render_sidebar()
    render_hero()
    render_clear_button()
    st.markdown("---")
    render_chat_ui()


if __name__ == "__main__":
    main()
