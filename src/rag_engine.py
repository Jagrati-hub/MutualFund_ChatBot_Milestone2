from __future__ import annotations

# RAG Engine – Smart & Swift Gemini-Powered Retrieval
# =====================================================
# Groww Mutual Fund FAQ Assistant
#
# Key upgrades:
# - Verified Categories: Equity, Commodities, Debt, Hybrid.
# - Citation logic: Always return a citation_url for the UI.
# - PII & Advice Guardrails strictly enforced.

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Paths & constants ──────────────────────────────────────────────────────────
SYSTEM_PROMPT_PATH = Path("system_prompt.md")
CHROMA_DIR         = Path("chroma")
CHROMA_COLLECTION  = "groww_mf_faq"
GROWW_AMC_LINK     = "https://groww.in/mutual-funds/amc/groww-mutual-fund"

def _get_api_key(key_name: str) -> str:
    """Helper to get keys from st.secrets (Cloud) or os.environ (Local)."""
    try:
        import streamlit as st
        if key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    return os.environ.get(key_name, "")

_GEMINI_KEY: str = _get_api_key("GEMINI_API_KEY") or _get_api_key("GOOGLE_API_KEY")
_GROQ_KEY: str   = _get_api_key("GROQ_API_KEY")
_OPENAI_KEY: str = _get_api_key("OPENAI_API_KEY")

# ── Config dataclass ───────────────────────────────────────────────────────────
@dataclass
class RAGConfig:
    system_prompt_path: Path = field(default=SYSTEM_PROMPT_PATH)
    chroma_dir:         Path = field(default=CHROMA_DIR)
    collection_name:    str  = field(default=CHROMA_COLLECTION)
    k_fetch:            int  = field(default=15)
    k_final:            int  = field(default=6)
    mmr_lambda:         float = field(default=0.7)
    rewrite_query:      bool  = field(default=False)


# ── System prompt helpers ──────────────────────────────────────────────────────
def load_system_prompt(path: Path = SYSTEM_PROMPT_PATH) -> str:
    if not path.exists():
        return "Factual Assistant for Groww Mutual Fund schemes. No advice."
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_default_refusal(path: Path = SYSTEM_PROMPT_PATH) -> str:
    fallback = f"I am a facts-only assistant and cannot provide investment advice. Please refer to official documents: [Groww Official AMC]({GROWW_AMC_LINK})"
    if not path.exists():
        return fallback
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'DEFAULT REFUSAL\s*"(.*?)"', content)
    # The default refusal in prompt might have [Link](url), we try to extract text inside quotes
    try:
        if match:
             return match.group(0).split('"')[1]
    except: pass
    return fallback


# ── Guardrails ─────────────────────────────────────────────────────────────────
def validate_query(
    query: str,
    system_prompt_path: Path = SYSTEM_PROMPT_PATH,
) -> Tuple[bool, Optional[str]]:
    q = query.lower()
    
    suffix = " If you'd like to know more about Groww Mutual Funds or have any questions about them, I'd be happy to help."
    personal_refusal = "I am a facts-only assistant and cannot provide personal advice." + suffix
    financial_refusal = "I am a facts-only assistant and cannot provide financial advice." + suffix
    general_refusal = "I am a facts-only assistant." + suffix

    # 1. PII / Non-MF Personal Queries
    pii_keywords = ["pan", "phone", "email", "account", "aadhar", "aadhaar", "ssn", "password", "otp", "my name", "who am i"]
    if any(kw in q for kw in pii_keywords):
        return False, personal_refusal
    
    # 2. Mutual Fund Advice
    advice_keywords = [
        "should i buy", "should i sell", "best fund", "recommend",
        "predict", "forecast", "where to invest", "good investment",
        "top fund", "which fund", "will it rise", "will it fall",
        "suggest a fund", "help me choose"
    ]
    if any(kw in q for kw in advice_keywords):
        return False, financial_refusal
    
    # 3. Non-MF General Categories (Out of scope)
    # Check if the query is unrelated to finance/mutual funds
    mf_keywords = ["fund", "groww", "sip", "nav", "portfolio", "investment", "amc", "equity", "debt", "hybrid", "commodity", "gold", "silver", "tax", "elss"]
    if not any(kw in q for kw in mf_keywords):
        # We only block truly random stuff like "What is 2+2" or "Who is the PM"
        # but allow simple greetings like "Hi" (usually doesn't contain mf_keywords)
        # However, following the instruction strictly:
        if len(q.split()) > 2: # Ignore short chat like "Hello" or "Hi there"
             return False, general_refusal

    return True, None


# ── Google Gemini helpers ──────────────────────────────────────────────────────
def _get_gemini_llm(temperature: float = 0) -> Any:
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=temperature,
        google_api_key=_GEMINI_KEY,
    )


def _get_google_embeddings() -> Any:
    if _GEMINI_KEY:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=_GEMINI_KEY,
            )
        except Exception as exc:
            logger.warning("Google embeddings unavailable (%s); falling back to HuggingFace.", exc)
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


# ── Query rewriting ────────────────────────────────────────────────────────────
def rewrite_query(raw_query: str) -> str:
    if not _GEMINI_KEY:
        return raw_query
    try:
        llm = _get_gemini_llm(temperature=0)
        rewrite_instruction = (
            "You are a query-rewriting assistant for a mutual fund FAQ retrieval system. "
            "Rewrite the following user question into a precise, self-contained question "
            "that maximises retrieval from a vector store about Groww Mutual Fund schemes. "
            "Output ONLY the rewritten question, nothing else.\n\n"
            f"Original question: {raw_query}"
        )
        result = llm.invoke(rewrite_instruction)
        rewritten = result.content.strip() if hasattr(result, "content") else str(result).strip()
        return rewritten or raw_query
    except Exception as exc:
        logger.warning("Query rewriting failed (%s); using original.", exc)
        return raw_query


# ── Retriever with MMR ─────────────────────────────────────────────────────────
def get_retriever(config: RAGConfig) -> Any:
    from langchain_community.vectorstores import Chroma
    embeddings = _get_google_embeddings()
    vectorstore = Chroma(
        collection_name=config.collection_name,
        embedding_function=embeddings,
        persist_directory=str(config.chroma_dir),
    )
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": config.k_final,
            "fetch_k": config.k_fetch,
            "lambda_mult": config.mmr_lambda,
        },
    )


# ── RAG chain ──────────────────────────────────────────────────────────────────
def build_rag_chain(config: RAGConfig) -> Any:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    system_prompt = load_system_prompt(config.system_prompt_path)
    
    llms = []
    if _GEMINI_KEY:
        try: llms.append(_get_gemini_llm())
        except: pass
    if os.environ.get("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
            llms.append(ChatGroq(model_name="llama-3.1-8b-instant", temperature=0))
        except: pass
    
    if not llms:
        raise RuntimeError("No LLM available. Please check GEMINI_API_KEY or GROQ_API_KEY.")

    final_llm = llms[0]
    if len(llms) > 1:
        final_llm = final_llm.with_fallbacks(llms[1:])

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{system_prompt}\n\nRETIREVED CONTEXT:\n{{context}}"),
        ("human", "{question}"),
    ])
    return prompt | final_llm | StrOutputParser()


# ── Formatting helpers ─────────────────────────────────────────────────────────
def format_answer(answer_text: str) -> str:
    # No filler phrases
    fillers = [r"Based on the provided context,?\s*", r"I have identified,?\s*", r"According to the context,?\s*"]
    for filler in fillers:
        answer_text = re.sub(filler, "", answer_text, flags=re.IGNORECASE)
    return answer_text.strip()


# ── Public API ─────────────────────────────────────────────────────────────────
def answer(query: str, config: Optional[RAGConfig] = None) -> Dict[str, Any]:
    if config is None: config = RAGConfig()

    is_allowed, reason = validate_query(query, config.system_prompt_path)
    if not is_allowed:
        return {"blocked": True, "answer": reason or get_default_refusal(), "citation_url": GROWW_AMC_LINK}

    retrieval_query = rewrite_query(query) if config.rewrite_query else query
    
    try:
        retriever = get_retriever(config)
        docs = retriever.invoke(retrieval_query)
    except Exception as exc:
        return {"blocked": False, "answer": f"⚠️ Retrieval error: {exc}", "citation_url": None}

    # Best citation
    citation_url = docs[0].metadata.get("source_url") if docs else GROWW_AMC_LINK
    
    context = "\n\n".join([f"[SOURCE: {d.metadata.get('source_url', 'N/A')}]\n{d.page_content}" for d in docs])

    try:
        chain = build_rag_chain(config)
        raw_ans = chain.invoke({"context": context, "question": query})
        
        return {
            "blocked": False,
            "answer": format_answer(raw_ans),
            "citation_url": citation_url or GROWW_AMC_LINK
        }
    except Exception as exc:
        return {"blocked": False, "answer": f"⚠️ Error: {exc}", "citation_url": GROWW_AMC_LINK}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(answer("What is SIP?"))
