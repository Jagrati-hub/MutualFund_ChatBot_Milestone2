"""
Groww Mutual Fund FAQ Assistant
Streamlit Cloud Entry Point
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

# Add phase directories to Python path FIRST
# Insert in reverse order so phase-3-retrieval is checked first
_root = Path(__file__).parent
sys.path.insert(0, str(_root / "phases/phase-4-orchestration"))
sys.path.insert(0, str(_root / "phases/phase-1-collection"))
sys.path.insert(0, str(_root / "phases/phase-2-processing"))
sys.path.insert(0, str(_root / "phases/phase-3-retrieval"))

import streamlit as st

# Set page config FIRST
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

# Now import our modules
try:
    from src import rag_engine
    from src.shared import SCOPE_FUNDS_BY_CATEGORY, SCOPE_FUNDS
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    st.stop()

# Scheduler is optional - only initialize if available
try:
    from src.shared import ensure_scheduler_started
except ImportError:
    def ensure_scheduler_started():
        """Fallback if scheduler is not available."""
        pass

# ── constants ──────────────────────────────────────────────────────────────────
EXAMPLE_QUERIES: list[str] = [
    "What is the investment objective of the Groww ELSS Tax Saver Fund?",
    "What is the expense ratio of the Groww Nifty Total Market Index Fund?",
    "Is the Groww Liquid Fund suitable for short-term parking of funds?",
]

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
    """Entry point for all incoming user queries."""
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
            "answer": f"A backend error occurred: {exc}",
            "citation_url": None,
        }


# ── Hero header ────────────────────────────────────────────────────────────────
def render_hero() -> None:
    st.markdown(
        f"""
        <div class="hero-header">
            <p class="hero-title">Groww Mutual Fund FAQ</p>
            <p class="hero-subtitle">
                Official support for Groww AMC schemes. All facts, no financial advice.
            </p>
            <div class="scope-pill">Real-time access to {len(SCOPE_FUNDS)} mutual fund schemes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Chat UI ────────────────────────────────────────────────────────────────────
def render_chat_ui() -> None:
    # Session defaults
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "example_clicked" not in st.session_state:
        st.session_state.example_clicked = None

    # Example prompts
    st.markdown('<p class="section-label">Quick Start - try one of these</p>', unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLE_QUERIES))
    for i, example in enumerate(EXAMPLE_QUERIES):
        if cols[i].button(example, key=f"example_{i}"):
            st.session_state.example_clicked = example
            st.rerun()

    # Autoscroll Helper
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

    # Consume prefill from example button
    user_input: str | None = None
    if st.session_state.example_clicked:
        user_input = st.session_state.example_clicked
        st.session_state.example_clicked = None

    # Replay chat history
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("blocked"):
                st.markdown(
                    f'<div class="refusal-box">{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(msg["content"])
            
            # Show citation and recency
            if not msg.get("blocked") and msg["role"] == "assistant":
                if msg.get("citation_url") or msg.get("last_updated"):
                    st.markdown('<div class="assistant-footer">', unsafe_allow_html=True)
                    if msg.get("citation_url"):
                        st.markdown(
                            f'<a class="citation-link" href="{msg["citation_url"]}" target="_blank">'
                            f'Source</a>',
                            unsafe_allow_html=True,
                        )
                    if msg.get("last_updated"):
                        st.markdown(f'<p class="data-recency">Data as of: {msg["last_updated"]}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Show message timestamp
            if msg.get("timestamp"):
                st.markdown(f'<span class="message-timestamp">Sent at {msg["timestamp"]}</span>', unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Ask about any Groww Mutual Fund scheme..."):
        user_input = prompt

    # Process query
    if user_input:
        curr_time = datetime.now().strftime("%H:%M")
        
        # Show user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
            st.markdown(f'<span class="message-timestamp">Sent at {curr_time}</span>', unsafe_allow_html=True)
            
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input, 
            "blocked": False,
            "timestamp": curr_time
        })

        # Generate assistant response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Retrieving facts..."):
                response = handle_query(user_input)
            
            resp_time = datetime.now().strftime("%H:%M")

            if response.get("blocked"):
                st.markdown(
                    f'<div class="refusal-box">{response["answer"]}</div>',
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
                            f'Source</a>',
                            unsafe_allow_html=True,
                        )
                    if response.get("last_updated"):
                        st.markdown(f'<p class="data-recency">Data as of: {response["last_updated"]}</p>', unsafe_allow_html=True)
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
            if st.button("Clear chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()


# ── Main entry point ───────────────────────────────────────────────────────────
def main() -> None:
    # Initialize scheduler
    with st.spinner("Initializing Groww MF Assistant..."):
        ensure_scheduler_started()
    
    # Render the chat interface
    render_hero()
    render_clear_button()
    st.markdown("---")
    render_chat_ui()


if __name__ == "__main__":
    if 'app_initialized' not in st.session_state:
        with st.spinner("Loading Groww MF Assistant... Please wait..."):
            import time
            time.sleep(0.5)
            st.session_state.app_initialized = True
    
    main()
