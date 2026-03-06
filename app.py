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
}

/* ── App background ── */
.stApp {
    background: linear-gradient(145deg, #0f1117 0%, #1a1d2e 50%, #0d1421 100%);
    min-height: 100vh;
}

/* ── Main container ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 900px;
}

/* ── Header hero area ── */
.hero-header {
    background: linear-gradient(135deg, #00c896 0%, #00a8e8 50%, #7c3aed 100%);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,200,150,0.25);
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -20%;
    width: 60%;
    height: 200%;
    background: rgba(255,255,255,0.05);
    transform: rotate(30deg);
}
.hero-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.3rem 0;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.85);
    margin: 0;
    font-weight: 400;
}

/* ── Scope disclaimer pill ── */
.scope-pill {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 50px;
    padding: 0.3rem 1rem;
    font-size: 0.78rem;
    color: rgba(255,255,255,0.9);
    margin-top: 0.8rem;
    backdrop-filter: blur(8px);
}

/* ── Section labels ── */
.section-label {
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #7c8db5;
    margin-bottom: 0.6rem;
}

/* ── Example question buttons ── */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    color: #c8d1e8;
    font-size: 0.84rem;
    padding: 0.7rem 1rem;
    width: 100%;
    text-align: left;
    transition: all 0.25s ease;
    line-height: 1.4;
    white-space: normal;
    height: auto;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: rgba(0,200,150,0.1);
    border-color: rgba(0,200,150,0.45);
    color: #00e8b3;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,200,150,0.2);
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    margin-bottom: 0.6rem !important;
    padding: 0.8rem 1.2rem !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
}

/* user bubble */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, rgba(0,168,232,0.12), rgba(124,58,237,0.08)) !important;
}

/* assistant bubble */
[data-testid="stChatMessage"][data-testid*="assistant"],
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(255,255,255,0.03) !important;
}

/* ── Citation link ── */
.citation-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(0,200,150,0.1);
    border: 1px solid rgba(0,200,150,0.35);
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    font-size: 0.82rem;
    color: #00e8b3 !important;
    text-decoration: none !important;
    transition: all 0.2s ease;
    margin-top: 0.4rem;
}
.citation-link:hover {
    background: rgba(0,200,150,0.2);
    border-color: rgba(0,200,150,0.6);
}

/* ── Blocked / refusal box ── */
.refusal-box {
    background: rgba(255,100,80,0.08);
    border: 1px solid rgba(255,100,80,0.3);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    color: #ffb3a7;
    font-size: 0.9rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15, 17, 30, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #00c896, #00a8e8);
    border: none;
    border-radius: 10px;
    color: #0a0e1a;
    font-weight: 600;
    padding: 0.6rem 1rem;
    width: 100%;
    transition: opacity 0.2s ease, transform 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(0,200,150,0.35);
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── Dividers ── */
hr {
    border-color: rgba(255,255,255,0.07) !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #00c896 !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Custom CSS ─────────────────────────────────────────────────────────────────


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
            <p class="hero-title">📈 Groww Mutual Fund FAQ Assistant</p>
            <p class="hero-subtitle">
                Facts-only answers about Groww Mutual Fund schemes — no investment advice, ever.
            </p>
            <div class="scope-pill">🔍 Scope: {len(SCOPE_FUNDS)} Groww AMC funds across Equity · Debt · Hybrid · Commodities</div>
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
        with st.chat_message(msg["role"]):
            if msg.get("blocked"):
                st.markdown(
                    f'<div class="refusal-box">🚫 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(msg["content"])
            if msg.get("citation_url"):
                st.markdown(
                    f'<a class="citation-link" href="{msg["citation_url"]}" target="_blank">'
                    f'🔗 Source</a>',
                    unsafe_allow_html=True,
                )

    # ── Chat input ────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask about any Groww Mutual Fund scheme…"):
        user_input = prompt

    # ── Process query ─────────────────────────────────────────────────────
    if user_input:
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input, "blocked": False})

        # Generate and stream assistant response
        with st.chat_message("assistant"):
            with st.spinner("Retrieving facts…"):
                response = handle_query(user_input)

            if response.get("blocked"):
                st.markdown(
                    f'<div class="refusal-box">🚫 {response["answer"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(response["answer"])

            if response.get("citation_url"):
                st.markdown(
                    f'<a class="citation-link" href="{response["citation_url"]}" target="_blank">'
                    f'🔗 Source</a>',
                    unsafe_allow_html=True,
                )

        # Persist to session
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "citation_url": response.get("citation_url"),
            "blocked": response.get("blocked", False),
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
    # We still ensure the scheduler is started in the background
    ensure_scheduler_started()
    
    render_hero()
    st.markdown("---")
    render_chat_ui()


if __name__ == "__main__":
    main()
