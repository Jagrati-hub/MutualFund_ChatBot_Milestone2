"""
Bug Condition Exploration Test - Category Query Pattern Matching Inconsistency

**Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4**

This test is designed to FAIL on unfixed code to prove the bug exists.
The bug: Incomplete pattern matching in _handle_category_query() causes certain
category query variations to fall through to RAG, resulting in non-deterministic results.

EXPECTED OUTCOME: This test SHOULD FAIL on unfixed code.
- Failure confirms that pattern matching is incomplete
- Counterexamples will show which query variations are not being intercepted
- After the fix, this test will pass and validate the correction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "phases" / "phase-3-retrieval"))

import pytest
from hypothesis import given, strategies as st, settings, Phase
from src.rag_engine import _handle_category_query, answer, validate_query
from src.shared import SCOPE_FUNDS_BY_CATEGORY


# ── Property 1: Fault Condition - Category Query Pattern Matching Inconsistency ──

@given(
    query_template=st.sampled_from([
        "segregate by category",
        "categorize funds",
    ])
)
@settings(
    max_examples=1,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_category_query_variations_are_intercepted(query_template):
    """
    **Property 1: Fault Condition** - Category Query Pattern Matching Inconsistency
    
    **Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4**
    
    CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
    
    Tests that various category query phrasings are intercepted by _handle_category_query()
    and return deterministic results from SCOPE_FUNDS_BY_CATEGORY.
    """
    result = _handle_category_query(query_template)
    
    assert result is not None, (
        f"Query '{query_template}' was NOT intercepted by _handle_category_query(). "
        f"COUNTEREXAMPLE FOUND: Pattern matching is incomplete."
    )
    
    answer_text = result["answer"]
    
    # Verify all 4 categories are present
    assert "📈 Equity" in answer_text or "Equity" in answer_text
    assert "🏦 Debt" in answer_text or "Debt" in answer_text
    assert "⚖️ Hybrid" in answer_text or "Hybrid" in answer_text
    assert "🪙 Commodities" in answer_text or "Commodities" in answer_text


@given(
    query_template=st.sampled_from([
        "segregate by category",
        "categorize funds",
    ])
)
@settings(
    max_examples=1,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_repeated_queries_return_identical_results(query_template):
    """
    **Property 1: Fault Condition** - Non-deterministic Results from RAG Fallthrough
    
    **Validates: Requirements 1.2, 2.2**
    
    CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
    
    Tests that the same category query returns identical results on repeated calls.
    """
    result1 = _handle_category_query(query_template)
    result2 = _handle_category_query(query_template)
    
    assert result1 is not None
    assert result2 is not None
    assert result1["answer"] == result2["answer"], (
        f"Query '{query_template}' returned different results on repeated calls. "
        f"COUNTEREXAMPLE: Non-deterministic behavior detected."
    )


# ── Property 2: Preservation - Non-Category Query Behavior ──

@given(
    fund_name=st.sampled_from([
        "Groww Nifty Total Market Index Fund",
        "Groww Small Cap Fund",
    ]),
    query_type=st.sampled_from([
        "What is the NAV of {}?",
        "Tell me about {}?",
    ])
)
@settings(
    max_examples=1,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_fund_specific_queries_use_rag_retrieval(fund_name, query_type):
    """
    **Property 2: Preservation** - Fund-Specific Queries Use RAG Retrieval
    
    **Validates: Requirements 3.1, 3.2**
    
    Tests that queries about specific funds are NOT intercepted by _handle_category_query()
    and instead fall through to RAG retrieval from the vector store.
    """
    query = query_type.format(fund_name)
    
    result = _handle_category_query(query)
    
    assert result is None, (
        f"Fund-specific query '{query}' was incorrectly intercepted by _handle_category_query(). "
        f"REGRESSION DETECTED: Non-category queries are being intercepted."
    )
    
    full_result = answer(query)
    
    assert full_result is not None
    assert not full_result.get("blocked", False)
    
    answer_text = full_result.get("answer", "")
    assert "category-wise segregation" not in answer_text.lower()
    assert len(answer_text) > 0


@given(
    pii_query=st.sampled_from([
        "What is my PAN number?",
        "Can you tell me my email address?",
    ])
)
@settings(
    max_examples=1,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_pii_guardrails_continue_to_work(pii_query):
    """
    **Property 2: Preservation** - PII Guardrails Continue to Work
    
    **Validates: Requirement 3.3**
    
    Tests that PII-related queries are blocked by validate_query() guardrails.
    """
    is_allowed, reason = validate_query(pii_query)
    
    assert not is_allowed
    assert reason is not None
    
    result = answer(pii_query)
    assert result.get("blocked", False)


@given(
    advice_query=st.sampled_from([
        "Should I buy Groww Small Cap Fund?",
        "Which is the best fund for me?",
    ])
)
@settings(
    max_examples=1,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_advice_guardrails_continue_to_work(advice_query):
    """
    **Property 2: Preservation** - Advice Guardrails Continue to Work
    
    **Validates: Requirement 3.3**
    
    Tests that advice-seeking queries are blocked by validate_query() guardrails.
    """
    is_allowed, reason = validate_query(advice_query)
    
    assert not is_allowed
    assert reason is not None
    
    result = answer(advice_query)
    assert result.get("blocked", False)


@given(
    query=st.sampled_from([
        "What is SIP in Groww mutual funds?",
        "Tell me about NAV in mutual funds",
    ])
)
@settings(
    max_examples=1,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_response_formatting_continues_to_work(query):
    """
    **Property 2: Preservation** - Response Formatting Continues to Work
    
    **Validates: Requirement 3.4**
    
    Tests that response formatting (removing filler phrases) continues to work correctly.
    """
    result = answer(query)
    
    assert not result.get("blocked", False)
    
    answer_text = result.get("answer", "")
    
    filler_phrases = [
        "based on the provided context",
        "i have identified",
        "according to the context",
    ]
    
    for filler in filler_phrases:
        assert filler not in answer_text.lower()
    
    assert len(answer_text) > 0
    assert answer_text == answer_text.strip()


@given(
    query=st.sampled_from([
        "What is the NAV of Groww Small Cap Fund?",
        "Tell me about Groww ELSS Tax Saver Fund",
    ])
)
@settings(
    max_examples=1,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_non_category_queries_not_intercepted(query):
    """
    **Property 2: Preservation** - Non-Category Queries Are Not Intercepted
    
    **Validates: Requirements 3.1, 3.2**
    
    Tests that non-category queries are NOT intercepted by _handle_category_query()
    and fall through to RAG retrieval.
    """
    result = _handle_category_query(query)
    
    assert result is None, (
        f"Non-category query '{query}' was incorrectly intercepted by _handle_category_query(). "
        f"REGRESSION: The fix is too broad and is intercepting non-category queries."
    )
    
    full_result = answer(query)
    
    assert full_result is not None
    assert not full_result.get("blocked", False)
    
    answer_text = full_result.get("answer", "")
    
    category_indicators = [
        "category-wise segregation",
        "📈 Equity (21)",
        "🏦 Debt (6)",
        "⚖️ Hybrid (3)",
        "🪙 Commodities (2)",
    ]
    
    for indicator in category_indicators:
        assert indicator not in answer_text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
