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
import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv

load_dotenv()

from src.shared import SCOPE_FUNDS_BY_CATEGORY

logger = logging.getLogger(__name__)

# ── Cache directory for attribute queries ──────────────────────────────────────
CACHE_DIR = Path(".cache/fund_attributes")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ── Paths & constants ──────────────────────────────────────────────────────────
SYSTEM_PROMPT_PATH = Path("system_prompt.md")
CHROMA_DIR         = Path("chroma")
CHROMA_COLLECTION  = "groww_mf_faq"
GROWW_AMC_LINK     = "https://groww.in/mutual-funds/amc/groww-mutual-funds"

# ── Category and Attribute Mappings ────────────────────────────────────────────
# Maps category keywords to internal category keys used in SCOPE_FUNDS_BY_CATEGORY
CATEGORY_MAPPING = {
    "equity": "📈 Equity",
    "debt": "🏦 Debt",
    "liquid": "🏦 Debt",
    "hybrid": "⚖️ Hybrid",
    "multi asset": "⚖️ Hybrid",
    "commodity": "🪙 Commodities",
    "commodities": "🪙 Commodities",
    "gold": "🪙 Commodities",
    "silver": "🪙 Commodities",
}

# Maps attribute names to their synonyms and variations
ATTRIBUTE_MAPPING = {
    "nav": ["nav", "net asset value", "current nav", "latest nav"],
    "expense_ratio": ["expense ratio", "expense", "cost", "fee", "charges"],
    "exit_load": ["exit load", "exit fee", "redemption charge", "withdrawal fee"],
    "returns": ["returns", "return", "performance", "gain", "growth"],
    "aum": ["aum", "assets under management", "fund size", "corpus"],
    "minimum_investment": ["minimum investment", "minimum amount", "min investment", "minimum sip"],
    "fund_manager": ["fund manager", "manager", "who manages", "managed by"],
}

def _get_api_key(key_name: str) -> str:
    """Helper to get keys from st.secrets (Cloud) or os.environ (Local)."""
    try:
        import streamlit as st
        if key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    return os.environ.get(key_name, "")

# Load all Gemini API keys
_GEMINI_KEYS: list[str] = []
for i in range(1, 10):  # Check for up to 9 keys
    key = _get_api_key(f"GEMINI_API_KEY_{i}") or _get_api_key(f"GOOGLE_API_KEY_{i}")
    if key:
        _GEMINI_KEYS.append(key)

# Fallback to single key if numbered keys not found
if not _GEMINI_KEYS:
    single_key = _get_api_key("GEMINI_API_KEY") or _get_api_key("GOOGLE_API_KEY")
    if single_key:
        _GEMINI_KEYS.append(single_key)

_GROQ_KEY: str   = _get_api_key("GROQ_API_KEY")
_OPENAI_KEY: str = _get_api_key("OPENAI_API_KEY")

# Track which Gemini key is currently active
_CURRENT_GEMINI_KEY_INDEX = 0
_GEMINI_KEY_FAILURES = [0] * len(_GEMINI_KEYS)  # Track failures per key
_MAX_FAILURES_BEFORE_SWITCH = 3

logger.info(f"Loaded {len(_GEMINI_KEYS)} Gemini API key(s)")

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
    mf_keywords = [
        "fund", "groww", "sip", "nav", "portfolio", "investment", "amc", 
        "equity", "debt", "hybrid", "commodity", "gold", "silver", "tax", "elss",
        "help", "can you", "what can", "do for me", "purpose", "who are you"
    ]
    if not any(kw in q for kw in mf_keywords):
        # We only block truly random stuff like "What is 2+2" or "Who is the PM"
        if len(q.split()) > 2: 
             return False, general_refusal

    return True, None


# ── Google Gemini helpers ──────────────────────────────────────────────────────
def _get_gemini_llm(temperature: float = 0) -> Any:
    from langchain_google_genai import ChatGoogleGenerativeAI
    current_key = _get_current_gemini_key()
    if not current_key:
        raise ValueError("No Gemini API key available")
    return ChatGoogleGenerativeAI(
        model="models/gemini-1.5-pro",  # Using Pro for higher quota
        temperature=temperature,
        google_api_key=current_key,
    )


def _get_google_embeddings() -> Any:
    """Get embeddings with fallback support."""
    current_key = _get_current_gemini_key()
    if current_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=current_key,
            )
        except Exception as exc:
            logger.warning("Google embeddings unavailable (%s); falling back to HuggingFace.", exc)
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


def _get_available_llms() -> list[Any]:
    """
    Get all available LLMs in priority order.
    Returns list of LLM instances that can be used with fallback.
    """
    llms = []
    
    # 1. Try all Gemini keys first (primary)
    for i, key in enumerate(_GEMINI_KEYS):
        # Only add Gemini keys that haven't been exhausted
        if _GEMINI_KEY_FAILURES[i] < _MAX_FAILURES_BEFORE_SWITCH:
            try:
                llms.append(_get_gemini_llm())
                logger.info(f"Using Gemini key #{i + 1} as LLM")
                break  # Use first available Gemini key
            except Exception as e:
                logger.warning(f"Gemini key #{i + 1} LLM unavailable: {e}")
    
    # 2. Try Groq (fallback 1)
    if _GROQ_KEY:
        try:
            from langchain_groq import ChatGroq
            llms.append(ChatGroq(model_name="llama-3.1-8b-instant", temperature=0))
            logger.info("Added Groq as fallback LLM")
        except Exception as e:
            logger.warning(f"Groq LLM unavailable: {e}")
    
    # 3. Try OpenAI (fallback 2)
    if _OPENAI_KEY:
        try:
            from langchain_openai import ChatOpenAI
            llms.append(ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=_OPENAI_KEY))
            logger.info("Added OpenAI as fallback LLM")
        except Exception as e:
            logger.warning(f"OpenAI LLM unavailable: {e}")
    
    # 4. Add remaining Gemini keys as last resort
    for i, key in enumerate(_GEMINI_KEYS):
        if _GEMINI_KEY_FAILURES[i] >= _MAX_FAILURES_BEFORE_SWITCH:
            try:
                # Temporarily switch to this key for fallback
                old_index = _CURRENT_GEMINI_KEY_INDEX
                globals()['_CURRENT_GEMINI_KEY_INDEX'] = i
                llms.append(_get_gemini_llm())
                globals()['_CURRENT_GEMINI_KEY_INDEX'] = old_index
                logger.info(f"Added Gemini key #{i + 1} as fallback LLM")
            except Exception as e:
                logger.warning(f"Gemini key #{i + 1} LLM unavailable: {e}")
    
    return llms


def _get_current_gemini_key() -> str:
    """Get the currently active Gemini API key."""
    global _CURRENT_GEMINI_KEY_INDEX
    if _GEMINI_KEYS:
        return _GEMINI_KEYS[_CURRENT_GEMINI_KEY_INDEX]
    return ""


def _switch_gemini_key() -> bool:
    """
    Switch to the next available Gemini API key.
    Returns True if switched successfully, False if no more keys available.
    """
    global _CURRENT_GEMINI_KEY_INDEX
    
    if len(_GEMINI_KEYS) <= 1:
        return False  # No other keys to switch to
    
    old_index = _CURRENT_GEMINI_KEY_INDEX
    _CURRENT_GEMINI_KEY_INDEX = (_CURRENT_GEMINI_KEY_INDEX + 1) % len(_GEMINI_KEYS)
    
    logger.info(f"Switching Gemini API key from #{old_index + 1} to #{_CURRENT_GEMINI_KEY_INDEX + 1}")
    return True


def _handle_quota_error(error_msg: str) -> None:
    """
    Handle quota errors by switching to next Gemini key or alternative model.
    """
    global _CURRENT_GEMINI_KEY_INDEX, _GEMINI_KEY_FAILURES
    
    if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "quota" in error_msg.lower():
        # Track failure for current Gemini key
        _GEMINI_KEY_FAILURES[_CURRENT_GEMINI_KEY_INDEX] += 1
        current_failures = _GEMINI_KEY_FAILURES[_CURRENT_GEMINI_KEY_INDEX]
        
        logger.warning(f"Quota error for Gemini key #{_CURRENT_GEMINI_KEY_INDEX + 1}. Failure count: {current_failures}")
        
        if current_failures >= _MAX_FAILURES_BEFORE_SWITCH:
            # Try to switch to next Gemini key
            if _switch_gemini_key():
                logger.info(f"Now using Gemini key #{_CURRENT_GEMINI_KEY_INDEX + 1}")
                # Check if all keys are exhausted
                all_exhausted = all(f >= _MAX_FAILURES_BEFORE_SWITCH for f in _GEMINI_KEY_FAILURES)
                if all_exhausted:
                    logger.warning("All Gemini API keys exhausted. Will use Groq/OpenAI fallback.")
            else:
                logger.warning("No more Gemini keys available. Will use Groq/OpenAI fallback.")


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
    
    llms = _get_available_llms()
    
    if not llms:
        raise RuntimeError("No LLM available. Please check GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY.")

    final_llm = llms[0]
    if len(llms) > 1:
        final_llm = final_llm.with_fallbacks(llms[1:])
        logger.info(f"Configured LLM with {len(llms)-1} fallback(s)")

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{system_prompt}\n\nRETIREVED CONTEXT:\n{{context}}"),
        ("human", "{question}"),
    ])
    return prompt | final_llm | StrOutputParser()


# ── Formatting helpers ─────────────────────────────────────────────────────────
def format_answer(answer_text: str) -> str:
    """
    Format the answer by removing filler phrases, inline source mentions, and web links.
    """
    # Remove filler phrases
    fillers = [
        r"Based on the provided context,?\s*",
        r"I have identified,?\s*",
        r"According to the context,?\s*"
    ]
    for filler in fillers:
        answer_text = re.sub(filler, "", answer_text, flags=re.IGNORECASE)

    # Remove inline source mentions - these appear as plain text in the answer
    # Pattern 1: "Source: [Official Groww Mu..." or "Source: [Off..." or "Source: [Official..."
    answer_text = re.sub(r'Source:\s*\[Official[^\]]*\]\.{0,3}', '', answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r'Source:\s*\[Off[^\]]*\]\.{0,3}', '', answer_text, flags=re.IGNORECASE)

    # Pattern 2: Just "Source: [Official Groww Mu..." without closing bracket
    answer_text = re.sub(r'Source:\s*\[Official[^\n]*', '', answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r'Source:\s*\[Off[^\n]*', '', answer_text, flags=re.IGNORECASE)

    # Pattern 3: Any remaining "Source: ..." lines
    answer_text = re.sub(r'\n\s*Source:\s*[^\n]+', '', answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r'^Source:\s*[^\n]+\n?', '', answer_text, flags=re.IGNORECASE | re.MULTILINE)

    # Remove markdown links like [text](url) - replace with just the text
    # Do this BEFORE removing plain URLs to avoid issues
    answer_text = re.sub(r'\[([^\]]+)\]\(([^\)]*)\)', r'\1', answer_text)

    # Remove web links - MOST AGGRESSIVE APPROACH
    # Remove URLs with various formats: (https://...), https://..., (www...), www...
    answer_text = re.sub(r'\s*\(https?://[^\)]*\)', '', answer_text)
    answer_text = re.sub(r'\s*\(www\.[^\)]*\)', '', answer_text)
    answer_text = re.sub(r'\s*https?://[^\s\)]+', '', answer_text)
    answer_text = re.sub(r'\s*www\.[^\s\)]+', '', answer_text)

    # Remove any remaining URLs that might be in other formats
    answer_text = re.sub(r'\(https?://[^\)]*\)', '', answer_text)
    answer_text = re.sub(r'\(www\.[^\)]*\)', '', answer_text)

    # Remove empty brackets and parentheses
    answer_text = re.sub(r'\[\s*\]\s*', '', answer_text)
    answer_text = re.sub(r'\(\s*\)\s*', '', answer_text)

    # Remove trailing dots, spaces, and commas after link removal
    answer_text = re.sub(r'\s*[\.,]\s*$', '', answer_text, flags=re.MULTILINE)
    answer_text = re.sub(r'[\.,]\s*$', '', answer_text, flags=re.MULTILINE)

    # Clean up multiple newlines and extra spaces
    answer_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer_text)  # Max 2 newlines
    answer_text = re.sub(r'\n\s+', '\n', answer_text)  # Remove leading spaces on lines
    answer_text = re.sub(r'\s+\n', '\n', answer_text)  # Remove trailing spaces before newlines

    # Remove extra spaces within lines
    answer_text = re.sub(r'  +', ' ', answer_text)

    # Final cleanup: remove any remaining trailing spaces and punctuation
    answer_text = re.sub(r'\s+$', '', answer_text, flags=re.MULTILINE)

    return answer_text.strip()



def _count_explicit_funds_in_query(query: str) -> int:
    """
    Count how many explicit fund names are mentioned in the query.
    Returns the count of funds explicitly named.
    
    Uses strict matching to avoid false positives on generic fund name parts.
    """
    q = query.lower()
    all_funds = [fund for funds in SCOPE_FUNDS_BY_CATEGORY.values() for fund in funds]
    
    matched_funds = set()
    
    # Generic patterns that should NOT trigger multi-fund matching
    # These are common fund name suffixes that appear in many funds
    generic_patterns = [
        "index fund", "etf fof", "total market", "nifty", "fund",
        "hybrid fund", "bond fund", "liquid fund", "asset allocation"
    ]
    
    for fund in all_funds:
        fund_lower = fund.lower()
        
        # Exact match (highest priority) - most reliable
        if fund_lower in q:
            matched_funds.add(fund)
            continue
        
        # Try matching key parts, but be more selective
        parts = fund_lower.split()
        
        # Check last 2 words (e.g., "liquid fund", "gold etf", "silver etf")
        # BUT: Skip if it's a generic pattern that appears in many funds
        if len(parts) >= 2:
            key_part = " ".join(parts[-2:])
            if key_part not in generic_patterns and key_part in q:
                matched_funds.add(fund)
                continue
        
        # Check last 3 words (e.g., "nifty total market")
        # BUT: Skip if it's a generic pattern that appears in many funds
        if len(parts) >= 3:
            key_part = " ".join(parts[-3:])
            if key_part not in generic_patterns and key_part in q:
                matched_funds.add(fund)
                continue
        
        # Check for specific fund identifiers (only for unique keywords)
        # Only match if the keyword is unique to this fund or appears with "groww"
        unique_keywords = ["gold", "silver", "arbitrage"]  # Unique fund identifiers
        for keyword in unique_keywords:
            if keyword in fund_lower and keyword in q:
                matched_funds.add(fund)
                break
    
    return len(matched_funds)


def _should_use_plural_link(query: str, num_results: int = 1) -> bool:
    """
    Determine if plural link should be used based on query context.
    
    Returns True if:
    - Query asks for multiple funds explicitly (2+ fund names mentioned)
    - Query uses "OR" keyword with in-scope funds
    - Query is a category query (multiple funds by category)
    - Query is a category-attribute query (e.g., "NAV of equity funds")
    - Query is a help/information query (e.g., "How can you help?", "What do you do?")
    
    Returns False if:
    - Single fund is explicitly asked for
    """
    q = query.lower()
    
    # CRITICAL: Check for help/information queries FIRST
    # These ALWAYS use plural link (general information about all funds)
    # BUT: Exclude queries that mention specific fund names
    help_patterns = [
        "how can you help",
        "what do you do",
        "what can you do",
        "how can i use",
        "how do i use",
        "what is this",
        "what are you",
        "who are you",
        "help",
        "about",
        "information",
        "guide",
        "how to",
        "what's available",
        "what funds",
        "which funds",
        "do you have",
        "can you help",
        "can you tell",
        "can you show",
        "can you provide",
        "can you list",
        "can you give",
        "can you explain",
        "can you describe",
        "can you share",
        "can you display",
        "can you show me",
        "can you tell me",
        "can you give me",
        "can you provide me",
        "can you list me",
        "can you explain me",
        "can you describe me",
        "can you share me",
        "can you display me",
    ]
    
    # Check if query matches help patterns
    matches_help_pattern = any(pattern in q for pattern in help_patterns)
    
    if matches_help_pattern:
        # BUT: Check if it's a specific fund query (e.g., "Tell me about Groww Liquid Fund")
        # If it mentions a specific fund, it's NOT a general help query
        all_funds = [fund for funds in SCOPE_FUNDS_BY_CATEGORY.values() for fund in funds]
        for fund in all_funds:
            fund_lower = fund.lower()
            # Extract key words from fund name (skip common words)
            fund_keywords = [word for word in fund_lower.split() 
                            if word not in ["fund", "direct", "growth", "etf", "fof", "index"]]
            
            # If 2+ keywords from fund name are in query, it's a specific fund query
            matches = sum(1 for keyword in fund_keywords if keyword in q)
            if matches >= 2:
                # This is a specific fund query, not a general help query
                matches_help_pattern = False
                break
    
    if matches_help_pattern:
        logger.info("Help/information query detected, using plural link")
        return True
    
    # CRITICAL: Check for category-wise queries
    # These ALWAYS use plural link
    
    # Category listing patterns (these are ALWAYS category queries)
    category_listing_patterns = [
        "category wise listing",
        "list all categories",
        "all funds by category",
        "segregate by category",
        "categorize funds",
        "break down by category",
        "organize by category",
        "group by category",
        "classify by category",
        "separate by category",
        "divide by category",
        "split by category",
        "arrange by category",
        "distribution",
        "breakdown",
        "composition",
        "allocation",
        "how are funds",
        "what categories",
        "fund categories",
        "types of funds",
        "category wise",
        "categorywise",
        "show category",
        "list category",
        "all category",
        "by category",
        "fund names",
        "show fund",
        "list fund",
        "all fund",
    ]
    
    if any(pattern in q for pattern in category_listing_patterns):
        logger.info("Category listing query detected, using plural link")
        return True
    
    # Category-specific queries (e.g., "list all equity funds", "show debt funds")
    # These have category keywords AND plural/list indicators
    category_keywords = ["equity", "debt", "hybrid", "commodity", "commodities", "liquid", "multi asset"]
    plural_indicators = ["funds", "all", "each", "every", "list", "show"]
    
    # Check if query has category keyword
    has_category_keyword = any(keyword in q for keyword in category_keywords)
    
    if has_category_keyword:
        # Check if it's a specific fund query (e.g., "Groww Aggressive Hybrid Fund")
        # by looking for "groww" + fund name pattern
        all_funds = [fund for funds in SCOPE_FUNDS_BY_CATEGORY.values() for fund in funds]
        for fund in all_funds:
            fund_lower = fund.lower()
            # Extract key words from fund name (skip common words)
            fund_keywords = [word for word in fund_lower.split() 
                            if word not in ["fund", "direct", "growth", "etf", "fof", "index"]]
            
            # If 2+ keywords from fund name are in query, it's a specific fund query
            matches = sum(1 for keyword in fund_keywords if keyword in q)
            if matches >= 2:
                # This is a specific fund query, not a category query
                break
        else:
            # No specific fund matched, check for plural indicators
            has_plural_indicator = any(ind in q for ind in plural_indicators)
            if has_plural_indicator:
                logger.info("Category-specific query with plural indicator detected, using plural link")
                return True
    
    # Check if query is a category-attribute query (e.g., "NAV of equity funds")
    category = _extract_category(query)
    attribute = _extract_attribute(query)
    if category and attribute:
        logger.info(f"Category-attribute query detected ({category}, {attribute}), using plural link")
        return True
    
    # Check if multiple funds are explicitly mentioned
    explicit_fund_count = _count_explicit_funds_in_query(query)
    if explicit_fund_count >= 2:
        logger.info(f"Multiple funds explicitly mentioned ({explicit_fund_count}), using plural link")
        return True
    
    # Check for "OR" keyword with fund names
    if " or " in q:
        # If "OR" is used, likely asking for multiple funds
        logger.info("Query contains 'OR', using plural link")
        return True
    
    # Check for multiple results with "SHOW" keyword
    if "show" in q and num_results > 1:
        logger.info(f"Query contains 'SHOW' with {num_results} results, using plural link")
        return True
    
    # Single fund query
    return False


# ── Specialized Category Handlers ─────────────────────────────────────────────
def _handle_category_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Checks if the query is asking for a listing or count of categories.
    Bypasses RAG to ensure 100% consistency for these scope-level questions.
    """
    q = query.lower()
    
    # Map synonyms to internal category keys
    mapping = {
        "equity": "📈 Equity",
        "debt": "🏦 Debt",
        "liquid": "🏦 Debt",
        "hybrid": "⚖️ Hybrid",
        "multi asset": "⚖️ Hybrid",
        "commodity": "🪙 Commodities",
        "commodities": "🪙 Commodities",
        "gold": "🪙 Commodities",
        "silver": "🪙 Commodities",
    }
    
    # 1. Check for "Category wise listing" or "All categories"
    # IMPORTANT: Don't match queries that have attribute keywords (nav, expense ratio, etc.)
    # Those should be handled by _handle_category_attribute_query()
    
    # First check if query contains attribute keywords
    attribute_keywords = ["nav", "expense ratio", "expense", "exit load", "returns", "aum", 
                         "minimum investment", "fund manager", "performance", "cost", "fee"]
    has_attribute = any(attr in q for attr in attribute_keywords)
    
    # If query has attribute keywords, don't treat it as category listing
    if has_attribute:
        return None
    
    category_listing_patterns = [
        "category wise listing",
        "list all categories",
        "all funds by category",
        "segregate by category",
        "categorize funds",
        "break down by category",
        "organize by category",
        "group by category",
        "classify by category",
        "separate by category",
        "divide by category",
        "split by category",
        "arrange by category",
        "distribution",
        "breakdown",
        "composition",
        "allocation",
        "how are funds",
        "what categories",
        "fund categories",
        "types of funds",
        "category wise",
        "categorywise",
        "show category",
        "list category",
        "all category",
        "by category",
        "fund names",
        "show fund",
        "list fund",
        "all fund",
    ]
    
    if any(x in q for x in category_listing_patterns):
        lines = ["Here is the category-wise segregation of all 32 Groww Mutual Fund schemes:"]
        for cat, funds in SCOPE_FUNDS_BY_CATEGORY.items():
            lines.append(f"\n**{cat} ({len(funds)})**")
            for f in sorted(funds):
                lines.append(f"- {f}")
        return {
            "blocked": False,
            "answer": "\n".join(lines),
            "citation_url": GROWW_AMC_LINK,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    # 2. Check for specific category LIST or COUNT
    # But first, check if a specific fund name is mentioned
    all_funds = [fund for funds in SCOPE_FUNDS_BY_CATEGORY.values() for fund in funds]
    for fund in all_funds:
        fund_lower = fund.lower()
        # Extract key words from fund name (skip common words)
        fund_keywords = [word for word in fund_lower.split() 
                        if word not in ["fund", "direct", "growth", "etf", "fof", "index"]]
        
        # If 2+ keywords from fund name are in query, it's a specific fund query
        matches = sum(1 for keyword in fund_keywords if keyword in q)
        if matches >= 2:
            return None  # Let it go to regular RAG
    
    for key, internal_key in mapping.items():
        if key in q:
            funds = SCOPE_FUNDS_BY_CATEGORY[internal_key]
            # List intent - but only if asking for category listing, not specific fund details
            if any(x in q for x in ["list", "show", "what are", "which funds"]):
                # Additional check: if query contains "details", "about", "information", it's likely a specific fund query
                if any(word in q for word in ["details", "about", "information", "tell me"]):
                    return None  # Let it go to RAG
                    
                ans = f"Here are the {len(funds)} {key.capitalize()} funds offered by Groww AMC:\n\n"
                ans += "\n".join([f"- {f}" for f in sorted(funds)])
                return {
                    "blocked": False,
                    "answer": ans,
                    "citation_url": GROWW_AMC_LINK,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            # Count intent
            if any(x in q for x in ["how many", "count", "number of"]):
                return {
                    "blocked": False,
                    "answer": f"Groww AMC currently offers **{len(funds)}** funds in the {key.capitalize()} category.",
                    "citation_url": GROWW_AMC_LINK,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
    
    return None


# ── Helper functions for category-attribute queries ────────────────────────────
def _extract_category(query: str) -> Optional[str]:
    """
    Extract category name from query using CATEGORY_MAPPING.
    Returns internal category key (e.g., "📈 Equity") or None.
    """
    q = query.lower()
    for keyword, internal_key in CATEGORY_MAPPING.items():
        if keyword in q:
            return internal_key
    return None


def _extract_attribute(query: str) -> Optional[str]:
    """
    Extract attribute name from query using ATTRIBUTE_MAPPING.
    Returns normalized attribute name or None.
    """
    q = query.lower()
    for attr_name, synonyms in ATTRIBUTE_MAPPING.items():
        if any(syn in q for syn in synonyms):
            return attr_name
    return None


def _get_cache_key(fund_name: str, attribute: str) -> str:
    """Generate a cache key for fund-attribute pair."""
    key_str = f"{fund_name}:{attribute}"
    return hashlib.md5(key_str.encode()).hexdigest()


def _get_cached_attribute(fund_name: str, attribute: str) -> Optional[str]:
    """
    Retrieve cached attribute value for a fund.
    Returns None if not cached or cache is older than 24 hours.
    """
    cache_key = _get_cache_key(fund_name, attribute)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        
        # Check if cache is less than 24 hours old
        cached_time = datetime.fromisoformat(cache_data["timestamp"])
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600
        
        if age_hours < 24:
            logger.info(f"Cache hit for {fund_name} - {attribute}")
            return cache_data["value"]
        else:
            logger.info(f"Cache expired for {fund_name} - {attribute}")
            return None
    except Exception as e:
        logger.warning(f"Error reading cache for {fund_name} - {attribute}: {e}")
        return None


def _cache_attribute(fund_name: str, attribute: str, value: str) -> None:
    """Cache an attribute value for a fund."""
    cache_key = _get_cache_key(fund_name, attribute)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    try:
        cache_data = {
            "fund_name": fund_name,
            "attribute": attribute,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
        logger.info(f"Cached {fund_name} - {attribute}")
    except Exception as e:
        logger.warning(f"Error caching {fund_name} - {attribute}: {e}")


def _query_fund_attribute(fund_name: str, attribute: str, config: RAGConfig) -> str:
    """
    Query RAG for a specific fund's attribute value.
    Returns attribute value or "Not available".
    Uses caching to avoid redundant API calls.
    Tries multiple query variations to find the data.
    OPTIMIZED: Only tries first 2 variations for faster response.
    """
    # Check cache first
    cached_value = _get_cached_attribute(fund_name, attribute)
    if cached_value is not None:
        return cached_value
    
    # Construct specific query for the fund's attribute
    attr_display = attribute.replace("_", " ").title()
    
    # Try only first 2 query variations for faster response
    query_variations = [
        f"What is the {attr_display} of {fund_name}?",
        f"{fund_name} {attr_display}",
    ]
    
    try:
        retriever = get_retriever(config)
        chain = build_rag_chain(config)
        
        # Try each query variation
        for fund_query in query_variations:
            try:
                docs = retriever.invoke(fund_query)
                
                if docs and len(docs) > 0:
                    context = "\n\n".join([f"[SOURCE: {d.metadata.get('source_url', 'N/A')}]\n{d.page_content}" for d in docs])
                    raw_ans = chain.invoke({"context": context, "question": fund_query})
                    
                    # Format and extract the answer
                    formatted = format_answer(raw_ans)
                    
                    # Check if we got a meaningful answer (not just "not available" or error messages)
                    if formatted and len(formatted) > 5 and "not available" not in formatted.lower() and "cannot" not in formatted.lower():
                        # Limit length
                        if len(formatted) > 100:
                            result = formatted[:97] + "..."
                        else:
                            result = formatted
                        
                        # Cache the result
                        _cache_attribute(fund_name, attribute, result)
                        return result
            except Exception as e:
                logger.debug(f"Query variation failed for {fund_name}: {str(e)}")
                continue
        
        # If all variations failed, return not available
        result = "Not available"
        _cache_attribute(fund_name, attribute, result)
        return result
        
    except Exception as e:
        error_msg = str(e)
        # Check if it's a quota error
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "quota" in error_msg.lower():
            logger.warning(f"API quota exceeded for {fund_name}, returning placeholder")
            _handle_quota_error(error_msg)  # Track quota errors
            result = "⚠️ API quota exceeded"
            # Don't cache quota errors
            return result
        logger.error(f"Error querying {attribute} for {fund_name}: {e}")
        result = "Not available"
        _cache_attribute(fund_name, attribute, result)
        return result


def _handle_category_attribute_query(query: str, config: Optional[RAGConfig] = None) -> Optional[Dict[str, Any]]:
    """
    Detects and handles category-attribute queries (e.g., "NAV of equity funds").
    
    Args:
        query: User's natural language query
        config: RAG configuration
        
    Returns:
        Dict with keys: blocked, answer, citation_url, last_updated
        None if query is not a category-attribute query
    """
    if config is None:
        config = RAGConfig()
    
    q = query.lower()
    
    # CRITICAL: Check if query uses singular "fund" instead of plural "funds"
    # Singular indicates a specific fund query, not a category query
    # Must check this BEFORE fund name detection to avoid false positives
    
    # First check if "funds" (plural) or category indicators are present
    has_plural_indicators = any(word in q for word in ["funds", "all", "category", "categories", "each", "every"])
    
    # If no plural indicators, check for singular "fund"
    if not has_plural_indicators:
        if " fund " in q or q.endswith(" fund") or q.startswith("fund "):
            return None  # Singular "fund" without plural indicators = specific fund query
    
    # IMPORTANT: Check if a specific fund name is mentioned
    # If yes, this is a single-fund query, not a category query
    all_funds = [fund for funds in SCOPE_FUNDS_BY_CATEGORY.values() for fund in funds]
    for fund in all_funds:
        # Check if the fund name (or significant part of it) is in the query
        fund_lower = fund.lower()
        # Extract key words from fund name (skip common words like "fund", "direct", "growth")
        fund_keywords = [word for word in fund_lower.split() 
                        if word not in ["fund", "direct", "growth", "etf", "fof", "index"]]
        
        # If 2+ keywords from fund name are in query, it's likely a specific fund query
        matches = sum(1 for keyword in fund_keywords if keyword in q)
        if matches >= 2:
            return None  # Let it go to regular RAG
    
    # Extract category and attribute
    category = _extract_category(query)
    attribute = _extract_attribute(query)
    
    # If both are not found, this is not a category-attribute query
    if not category or not attribute:
        return None
    
    # Check if query matches category-attribute patterns
    # Patterns can be:
    # 1. "[attribute] of [category]" - "NAV of equity funds"
    # 2. "[attribute] for [category]" - "returns for hybrid funds"
    # 3. "[attribute] in [category]" - "exit load in commodities"
    # 4. "show [category] [attribute]" - "show hybrid nav"
    # 5. "[category] [attribute]" - "equity nav", "hybrid fund nav"
    
    category_attr_patterns = [
        "of",  # "NAV of equity", "expense ratio of debt"
        "for",  # "returns for hybrid funds"
        "in",  # "exit load in commodities"
    ]
    
    # Check if query has explicit pattern words OR if it's a simple category+attribute query
    has_explicit_pattern = any(pattern in q for pattern in category_attr_patterns)
    
    # Also accept queries like "show hybrid nav" or "equity fund nav" (category + attribute without pattern word)
    # These are valid if we found both category and attribute
    if not has_explicit_pattern:
        # Check if query is simple enough (category + attribute without complex structure)
        # Accept if query has "show", "what", "get", or is just category + attribute
        simple_query_indicators = ["show", "what", "get", "display", "list"]
        is_simple_query = any(ind in q for ind in simple_query_indicators) or len(q.split()) <= 5
        
        if not is_simple_query:
            return None
    
    # Get fund list for the category
    if category not in SCOPE_FUNDS_BY_CATEGORY:
        return {
            "blocked": False,
            "answer": f"I couldn't find the category '{category}'. Valid categories are: Equity, Debt, Hybrid, and Commodities.",
            "citation_url": GROWW_AMC_LINK,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    funds = SCOPE_FUNDS_BY_CATEGORY[category]
    
    # Query each fund's attribute IN PARALLEL for faster response
    results = {}
    attr_display = attribute.replace("_", " ").title()
    
    # Use ThreadPoolExecutor to query all funds concurrently
    # Reduced workers for faster response time (3-5 workers instead of 10)
    max_workers = min(3, len(funds))  # Reduced from 10 to 3 for faster response
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all queries
        future_to_fund = {
            executor.submit(_query_fund_attribute, fund, attribute, config): fund 
            for fund in funds
        }
        
        # Collect results as they complete with timeout
        for future in as_completed(future_to_fund, timeout=15):  # 15 second timeout
            fund = future_to_fund[future]
            try:
                attr_value = future.result(timeout=10)  # 10 second timeout per fund
                results[fund] = attr_value
            except Exception as e:
                logger.error(f"Error querying {fund}: {e}")
                results[fund] = "Not available"
    
    # Format response (sorted by fund name)
    formatted_results = []
    for fund in sorted(results.keys()):
        formatted_results.append(f"- **{fund}**: {results[fund]}")
    
    answer_text = f"Here is the {attr_display} for all {len(funds)} {category} funds:\n\n"
    answer_text += "\n".join(formatted_results)
    
    return {
        "blocked": False,
        "answer": answer_text,
        "citation_url": GROWW_AMC_LINK,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }


# ── Public API ─────────────────────────────────────────────────────────────────
def answer(query: str, config: Optional[RAGConfig] = None) -> Dict[str, Any]:
    if config is None: config = RAGConfig()

    is_allowed, reason = validate_query(query, config.system_prompt_path)
    if not is_allowed:
        return {"blocked": True, "answer": reason or get_default_refusal(), "citation_url": GROWW_AMC_LINK}

    # Intercept category-attribute queries FIRST (e.g., "NAV of equity funds")
    category_attr_result = _handle_category_attribute_query(query, config)
    if category_attr_result:
        return category_attr_result
    
    # Then intercept category-specific queries for 100% consistency
    intercepted = _handle_category_query(query)
    if intercepted:
        return intercepted

    retrieval_query = rewrite_query(query) if config.rewrite_query else query
    
    try:
        retriever = get_retriever(config)
        docs = retriever.invoke(retrieval_query)
    except Exception as exc:
        error_msg = str(exc)
        _handle_quota_error(error_msg)  # Track quota errors
        return {"blocked": False, "answer": f"⚠️ Retrieval error: {exc}", "citation_url": None}

    # Best citation and data recency
    # Determine if we should use plural link based on query context
    use_plural_link = _should_use_plural_link(query, len(docs) if docs else 1)
    
    if use_plural_link:
        citation_url = GROWW_AMC_LINK  # Use plural link
    else:
        citation_url = docs[0].metadata.get("source_url") if docs else GROWW_AMC_LINK
    
    # Try fetching precise timestamp, fallback to run_date
    raw_timestamp = docs[0].metadata.get("fetched_at") or docs[0].metadata.get("run_date") if docs else None
    last_updated = raw_timestamp
    if last_updated and "T" in last_updated:
        # Simple format: 2026-03-07T23:18:44 -> 2026-03-07 23:18
        try:
             last_updated = last_updated.split(".")[0].replace("T", " ")
             if len(last_updated) > 16:
                 last_updated = last_updated[:16]
        except: pass
    
    context = "\n\n".join([f"[SOURCE: {d.metadata.get('source_url', 'N/A')}]\n{d.page_content}" for d in docs])

    try:
        chain = build_rag_chain(config)
        raw_ans = chain.invoke({"context": context, "question": query})
        
        return {
            "blocked": False,
            "answer": format_answer(raw_ans),
            "citation_url": citation_url or GROWW_AMC_LINK,
            "last_updated": last_updated
        }
    except Exception as exc:
        error_msg = str(exc)
        _handle_quota_error(error_msg)  # Track quota errors
        return {"blocked": False, "answer": f"⚠️ Error: {exc}", "citation_url": GROWW_AMC_LINK, "last_updated": None}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(answer("What is SIP?"))
