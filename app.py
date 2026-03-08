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
    menu_items={
        "Get Help": "https://groww.in",
        "Report a bug": "https://groww.in/support",
        "About": "Groww Mutual Fund FAQ Assistant"
    }
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

# Force Streamlit Cloud redeployment - Updated textbox styling
CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #262c3a !important;
}

/* ── App background (Premium Groww style) ── */
.stApp {
    background: linear-gradient(135deg, #f7f9fc 0%, #f0f5fa 100%);
}

/* ── Main container ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 900px;
}

/* ── Header hero area (Groww Mint Gradient - Premium) ── */
.hero-header {
    background: linear-gradient(135deg, #00d09c 0%, #00b386 50%, #009970 100%);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 20px 50px rgba(0,208,156,0.2);
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
    background: rgba(255,255,255,0.1);
    transform: rotate(25deg);
}
.hero-header::after {
    content: "";
    position: absolute;
    bottom: -30%;
    right: -20%;
    width: 60%;
    height: 150%;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #ffffff !important;
    margin: 0 0 0.8rem 0;
    letter-spacing: -0.03em;
    position: relative;
    z-index: 1;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: rgba(255,255,255,0.95) !important;
    margin: 0;
    font-weight: 400;
    position: relative;
    z-index: 1;
}

/* ── Scope disclaimer pill ── */
.scope-pill {
    display: inline-block;
    background: rgba(255,255,255,0.25);
    border: 1.5px solid rgba(255,255,255,0.4);
    border-radius: 100px;
    padding: 0.6rem 1.5rem;
    font-size: 0.9rem;
    color: #ffffff !important;
    margin-top: 1.5rem;
    backdrop-filter: blur(10px);
    font-weight: 600;
    position: relative;
    z-index: 1;
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

/* ── Section labels ── */
.section-label {
    font-size: 0.8rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #00d09c;
    margin-bottom: 1rem;
    padding-left: 0.4rem;
}

/* ── Example question buttons ── */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: #ffffff;
    border: 2px solid #e5eef5;
    border-radius: 16px;
    color: #262c3a !important;
    font-size: 0.9rem;
    padding: 1rem 1.5rem;
    width: 100%;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    height: auto;
    min-height: 4rem;
    font-weight: 500;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: #f0fffb;
    border-color: #00d09c;
    color: #00d09c !important;
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(0,208,156,0.2);
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 20px !important;
    margin-bottom: 1.5rem !important;
    padding: 1.5rem !important;
    border: none !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06) !important;
}

/* User bubble (Soft Blue) */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #e9efff 0%, #f0f5ff 100%) !important;
    border: 1px solid #d1dae6 !important;
    margin-left: 5% !important;
}

/* Assistant bubble (Soft Mint) */
[data-testid="stChatMessage"][data-testid*="assistant"],
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #e6f9f4 0%, #f0fdf9 100%) !important;
    border: 1px solid #b7e9dc !important;
    margin-right: 5% !important;
}

/* ── Text within bubbles ── */
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
    color: #1a202c !important;
    line-height: 1.7;
}

/* ── Citation & Recency Bar ── */
.assistant-footer {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1.5rem;
    padding-top: 1.2rem;
    border-top: 2px solid rgba(0, 208, 156, 0.2);
    align-items: center;
}

.citation-link {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, #00d09c 0%, #00b386 100%);
    color: #ffffff !important;
    border-radius: 100px;
    padding: 0.6rem 1.5rem;
    font-size: 0.95rem !important;
    text-decoration: none !important;
    transition: all 0.3s ease;
    font-weight: 700;
    box-shadow: 0 6px 16px rgba(0,208,156,0.2);
}
.citation-link:hover {
    background: linear-gradient(135deg, #00b386 0%, #009970 100%);
    box-shadow: 0 8px 24px rgba(0,208,156,0.3);
    transform: translateY(-2px);
}

.data-recency {
    font-size: 0.8rem;
    color: #4a5568 !important;
    font-weight: 700;
    margin: 0;
}

/* ── Message timestamps ── */
.message-timestamp {
    font-size: 0.75rem;
    color: #a0aec0 !important;
    margin-top: 0.8rem;
    display: block;
    text-align: right;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 2px solid #f0f5fa !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #00d09c 0%, #00b386 100%);
    border: none;
    border-radius: 14px;
    color: #ffffff;
    font-weight: 700;
    padding: 0.9rem 1.2rem;
    transition: all 0.3s ease;
    box-shadow: 0 6px 16px rgba(0,208,156,0.15);
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #00b386 0%, #009970 100%);
    box-shadow: 0 8px 24px rgba(0,208,156,0.25);
    transform: translateY(-2px);
}

/* ── Chat input (Centered & Floating feel) ── */
[data-testid="stChatInput"] {
    border: 2px solid #00d09c !important;
    border-radius: 100px !important;
    background: #ffffff !important;
    box-shadow: 0 8px 24px rgba(0,208,156,0.12) !important;
    padding: 0.8rem 1.5rem !important;
    margin: 1.5rem auto !important;
    max-width: 100% !important;
    width: 100% !important;
}

.stChatInput {
    border: 2px solid #00d09c !important;
    border-radius: 100px !important;
}

.stChatInput input {
    border: 2px solid #00d09c !important;
    border-radius: 100px !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #00b386 !important;
    box-shadow: 0 12px 32px rgba(0,208,156,0.25) !important;
    outline: none !important;
}

/* ── Chat input text styling ── */
[data-testid="stChatInput"] textarea {
    font-size: 1rem !important;
    color: #262c3a !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.5rem 0 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #a0aec0 !important;
    font-weight: 400 !important;
}

/* ── Chat input container alignment ── */
.stChatInput {
    margin: 1.5rem 0 !important;
    padding: 0 1rem !important;
}

/* ── Chat input wrapper ── */
[data-testid="stChatInputContainer"] {
    margin: 1.5rem auto !important;
    max-width: 100% !important;
    padding: 0 !important;
}

/* ── Admin Status Dots ── */
.status-dot {
    height: 12px;
    width: 12px;
    background-color: #00d09c;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    box-shadow: 0 0 8px rgba(0,208,156,0.4);
}
.status-dot.off {
    background-color: #ff4d4d;
    box-shadow: 0 0 8px rgba(255,77,77,0.4);
}

/* ── Refusal box ── */
.refusal-box {
    background: linear-gradient(135deg, #ffe6e6 0%, #fff0f0 100%);
    border-left: 4px solid #ff4d4d;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #c53030 !important;
    font-weight: 500;
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
        st.markdown('<p class="hero-title" style="font-size:1.5rem; color:#00d09c; text-align:left;">🛠 Admin</p>', unsafe_allow_html=True)
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
        st.subheader("Quick Actions")
        
        # Admin Dashboard Link
        if st.button("📊 Admin Dashboard", use_container_width=True):
            st.query_params["page"] = "admin"
            st.rerun()
        
        # Run Pipeline Button
        if st.button("🚀 Run Pipeline", use_container_width=True):
            with st.status("Running scraper + ingestor...", expanded=True) as status:
                try:
                    from src.scheduler import run_pipeline_once
                    st.write("Fetching latest data from Groww...")
                    run_pipeline_once()
                    st.write("Ingestion complete! Refreshing...")
                    status.update(label="Pipeline successfully completed!", state="complete", expanded=False)
                    st.toast("Data successfully updated!", icon="✅")
                except Exception as e:
                    status.update(label=f"Pipeline failed: {e}", state="error")
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.write("Built with ❤️ for Groww Mutual Fund Investors")


# ── Main entry point ───────────────────────────────────────────────────────────
def main() -> None:
    # Ensure scheduler is started in the background
    ensure_scheduler_started()
    
    # Render the chat interface
    render_hero()
    render_clear_button()
    st.markdown("---")
    render_chat_ui()




if __name__ == "__main__":
    main()

