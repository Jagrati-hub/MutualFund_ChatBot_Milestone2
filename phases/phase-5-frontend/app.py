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
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://groww.in",
        "Report a bug": "https://groww.in/support",
        "About": "Groww Mutual Fund FAQ Assistant"
    }
)

import sys
from pathlib import Path

# Add phase directories to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "phase-4-orchestration"))
sys.path.insert(0, str(Path(__file__).parent.parent / "phase-3-retrieval"))

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

# Modern Dark Theme
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0f172a;
}

.block-container {
    padding: 2rem 1rem !important;
    max-width: 1100px;
}

/* Header */
.hero-header {
    background: #1e293b;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    border: 1px solid #334155;
}

.hero-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0 0 0.5rem 0;
}

.hero-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    margin: 0;
}

.scope-pill {
    display: inline-block;
    background: #334155;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
    color: #cbd5e1;
    margin-top: 1rem;
    font-weight: 500;
}

/* Section Labels */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8;
    margin-bottom: 0.8rem;
}

/* Example Buttons */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    color: #e2e8f0 !important;
    font-size: 0.85rem;
    padding: 0.9rem 1rem;
    width: 100%;
    text-align: left;
    transition: all 0.2s;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    font-weight: 500;
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: #3b82f6;
    background: #334155;
    box-shadow: 0 4px 12px rgba(59,130,246,0.2);
    transform: translateY(-1px);
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    margin-bottom: 1rem !important;
    padding: 1rem !important;
    border: 1px solid #334155 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
}

[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: #1e293b !important;
    margin-left: 8% !important;
}

[data-testid="stChatMessage"][data-testid*="assistant"],
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #334155 !important;
    margin-right: 8% !important;
}

[data-testid="stChatMessage"] p {
    color: #e2e8f0 !important;
    line-height: 1.6;
    margin: 0;
}

/* Citation & Date */
.assistant-footer {
    display: flex;
    gap: 0.8rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #475569;
    align-items: center;
}

.citation-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #3b82f6;
    color: white !important;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.85rem !important;
    text-decoration: none !important;
    transition: all 0.2s;
    font-weight: 600;
}

.citation-link:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

.data-recency {
    font-size: 0.75rem;
    color: #94a3b8 !important;
    font-weight: 500;
    font-style: italic;
}

.message-timestamp {
    font-size: 0.7rem;
    color: #64748b !important;
    margin-top: 0.5rem;
    text-align: right;
}

/* Sidebar - Hidden */
[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

/* Chat Input */
[data-testid="stChatInput"] {
    border: 2px solid #334155 !important;
    border-radius: 12px !important;
    background: #1e293b !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    padding: 0.6rem 1rem !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}

[data-testid="stChatInput"] textarea {
    font-size: 0.95rem !important;
    color: #e2e8f0 !important;
    background: transparent !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
}

/* Status Dot */
.status-dot {
    height: 8px;
    width: 8px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}

.status-dot.off {
    background: #ef4444;
}

/* Refusal Box */
.refusal-box {
    background: #7f1d1d;
    border-left: 3px solid #ef4444;
    border-radius: 8px;
    padding: 1rem;
    color: #fca5a5 !important;
}

/* Loading */
.stSpinner > div {
    border-color: #3b82f6 !important;
}

[data-testid="stStatusWidget"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

#MainMenu, footer, header {visibility: hidden;}
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


# ── Main entry point ───────────────────────────────────────────────────────────
def main() -> None:
    # Show loading spinner while initializing
    with st.spinner("🚀 Initializing Groww MF Assistant..."):
        # Ensure scheduler is started in the background
        ensure_scheduler_started()
    
    # Render the chat interface
    render_hero()
    render_clear_button()
    st.markdown("---")
    render_chat_ui()




if __name__ == "__main__":
    # Show initial loading message
    if 'app_initialized' not in st.session_state:
        with st.spinner("Loading Groww MF Assistant... Please wait..."):
            import time
            time.sleep(0.5)  # Brief pause to show spinner
            st.session_state.app_initialized = True
    
    main()

