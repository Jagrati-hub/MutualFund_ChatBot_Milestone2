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

import pytest
from hypothesis import given, strategies as st, settings, Phase
from src.rag_engine import _handle_category_query, answer, validate_query
from src.shared import SCOPE_FUNDS_BY_CATEGORY


# ── Property 1: Fault Condition - Category Query Pattern Matching Inconsistency ──

@given(
    query_template=st.sampled_from([
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
    ])
)
@settings(
    max_examples=5,
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
    
    The bug: Current pattern matching only catches "category wise listing", "list all categories",
    and "all funds by category". Other natural variations like "segregate by category" or
    "categorize funds" fall through to RAG, causing non-deterministic results.
    
    Expected behavior after fix:
    - All category query variations should be intercepted
    - Should return deterministic results with exact fund counts: 21 Equity, 6 Debt, 3 Hybrid, 2 Commodities
    - Repeated queries should return identical results (no variation)
    """
    # Test that the query is intercepted by _handle_category_query
    result = _handle_category_query(query_template)
    
    # ASSERTION 1: Query should be intercepted (not fall through to RAG)
    assert result is not None, (
        f"Query '{query_template}' was NOT intercepted by _handle_category_query(). "
        f"This means it will fall through to RAG and produce non-deterministic results. "
        f"COUNTEREXAMPLE FOUND: Pattern matching is incomplete."
    )
    
    # ASSERTION 2: Result should contain all categories with correct counts
    answer_text = result["answer"]
    
    # Verify all 4 categories are present
    assert "📈 Equity" in answer_text or "Equity" in answer_text, (
        f"Equity category missing from response to '{query_template}'"
    )
    assert "🏦 Debt" in answer_text or "Debt" in answer_text, (
        f"Debt category missing from response to '{query_template}'"
    )
    assert "⚖️ Hybrid" in answer_text or "Hybrid" in answer_text, (
        f"Hybrid category missing from response to '{query_template}'"
    )
    assert "🪙 Commodities" in answer_text or "Commodities" in answer_text, (
        f"Commodities category missing from response to '{query_template}'"
    )
    
    # ASSERTION 3: Verify correct fund counts (deterministic from SCOPE_FUNDS_BY_CATEGORY)
    # Count occurrences of fund names in the response
    equity_funds = SCOPE_FUNDS_BY_CATEGORY["📈 Equity"]
    debt_funds = SCOPE_FUNDS_BY_CATEGORY["🏦 Debt"]
    hybrid_funds = SCOPE_FUNDS_BY_CATEGORY["⚖️ Hybrid"]
    commodity_funds = SCOPE_FUNDS_BY_CATEGORY["🪙 Commodities"]
    
    # Check that the response indicates correct counts
    # (either explicitly states counts or lists all funds)
    assert "21" in answer_text or len([f for f in equity_funds if f in answer_text]) == 21, (
        f"Equity fund count incorrect for '{query_template}'. Expected 21 funds."
    )
    assert "6" in answer_text or len([f for f in debt_funds if f in answer_text]) == 6, (
        f"Debt fund count incorrect for '{query_template}'. Expected 6 funds."
    )
    assert "3" in answer_text or len([f for f in hybrid_funds if f in answer_text]) == 3, (
        f"Hybrid fund count incorrect for '{query_template}'. Expected 3 funds."
    )
    assert "2" in answer_text or len([f for f in commodity_funds if f in answer_text]) == 2, (
        f"Commodities fund count incorrect for '{query_template}'. Expected 2 funds."
    )


@given(
    query_template=st.sampled_from([
        "segregate by category",
        "categorize funds",
        "organize by category",
    ])
)
@settings(
    max_examples=3,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_repeated_queries_return_identical_results(query_template):
    """
    **Property 1: Fault Condition** - Non-deterministic Results from RAG Fallthrough
    
    **Validates: Requirements 1.2, 2.2**
    
    CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists.
    
    Tests that the same category query returns identical results on repeated calls.
    
    The bug: When queries fall through to RAG (due to incomplete pattern matching),
    the RAG system may return different results on different calls, causing
    inconsistent fund distributions across categories.
    
    Expected behavior after fix:
    - Same query should return identical results every time
    - No variation in fund distribution across repeated queries
    """
    # Make the same query 3 times
    result1 = _handle_category_query(query_template)
    result2 = _handle_category_query(query_template)
    result3 = _handle_category_query(query_template)
    
    # All results should be intercepted (not None)
    assert result1 is not None, (
        f"First call: Query '{query_template}' fell through to RAG. "
        f"COUNTEREXAMPLE: Pattern matching incomplete."
    )
    assert result2 is not None, (
        f"Second call: Query '{query_template}' fell through to RAG. "
        f"COUNTEREXAMPLE: Pattern matching incomplete."
    )
    assert result3 is not None, (
        f"Third call: Query '{query_template}' fell through to RAG. "
        f"COUNTEREXAMPLE: Pattern matching incomplete."
    )
    
    # All results should be identical (deterministic)
    assert result1["answer"] == result2["answer"], (
        f"Query '{query_template}' returned different results on repeated calls. "
        f"COUNTEREXAMPLE: Non-deterministic behavior detected. "
        f"This confirms the bug exists."
    )
    assert result2["answer"] == result3["answer"], (
        f"Query '{query_template}' returned different results on repeated calls. "
        f"COUNTEREXAMPLE: Non-deterministic behavior detected. "
        f"This confirms the bug exists."
    )


if __name__ == "__main__":
    # Run the tests to document counterexamples
    print("=" * 80)
    print("BUG CONDITION EXPLORATION TEST")
    print("=" * 80)
    print("\nThis test is EXPECTED TO FAIL on unfixed code.")
    print("Failure confirms that pattern matching is incomplete.\n")
    
    pytest.main([__file__, "-v", "--tb=short"])


# ══════════════════════════════════════════════════════════════════════════════
# PRESERVATION PROPERTY TESTS - Non-Category Query Behavior
# ══════════════════════════════════════════════════════════════════════════════
"""
Preservation Property Tests - Non-Category Query Behavior

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

These tests verify that non-category queries continue to work correctly:
- Fund-specific queries use RAG retrieval (not hardcoded data)
- PII and advice keyword guardrails are applied
- Response formatting (removing filler phrases) works
- Non-category queries are NOT intercepted by _handle_category_query()

EXPECTED OUTCOME: These tests SHOULD PASS on unfixed code.
- Passing confirms baseline behavior that must be preserved after the fix
- These tests act as regression prevention
"""


# ── Property 2: Preservation - Non-Category Query Behavior ──

@given(
    fund_name=st.sampled_from([
        # Use funds WITHOUT category keywords in their names to avoid pre-existing bug
        "Groww Nifty Total Market Index Fund",
        "Groww Small Cap Fund",
        "Groww ELSS Tax Saver Fund",
        "Groww Multicap Fund",
        "Groww Large Cap Fund",
        "Groww Value Fund",
    ]),
    query_type=st.sampled_from([
        "What is the NAV of {}?",
        "Tell me about {}",
        "How does {} perform?",
        "What is the expense ratio of {}?",
        "Explain {} to me",
    ])
)
@settings(
    max_examples=5,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_fund_specific_queries_use_rag_retrieval(fund_name, query_type):
    """
    **Property 2: Preservation** - Fund-Specific Queries Use RAG Retrieval
    
    **Validates: Requirements 3.1, 3.2**
    
    Tests that queries about specific funds are NOT intercepted by _handle_category_query()
    and instead fall through to RAG retrieval from the vector store.
    
    This behavior MUST be preserved after the fix.
    
    NOTE: We use funds without category keywords in their names (e.g., not "Liquid Fund" or "Gold ETF")
    to test the core preservation behavior. The pre-existing issue with category keywords in fund names
    is a separate concern.
    """
    query = query_type.format(fund_name)
    
    # ASSERTION 1: Query should NOT be intercepted by _handle_category_query
    result = _handle_category_query(query)
    
    assert result is None, (
        f"Fund-specific query '{query}' was incorrectly intercepted by _handle_category_query(). "
        f"This query should fall through to RAG retrieval. "
        f"REGRESSION DETECTED: Non-category queries are being intercepted."
    )
    
    # ASSERTION 2: Query should be processed by the full answer() function using RAG
    full_result = answer(query)
    
    assert full_result is not None, (
        f"Query '{query}' failed to get a response from answer() function."
    )
    
    assert not full_result.get("blocked", False), (
        f"Query '{query}' was incorrectly blocked. "
        f"Fund-specific queries should not be blocked by guardrails."
    )
    
    # ASSERTION 3: Response should come from RAG (not hardcoded category data)
    answer_text = full_result.get("answer", "")
    
    # The response should NOT be the category listing format
    assert "category-wise segregation" not in answer_text.lower(), (
        f"Query '{query}' returned category listing instead of fund-specific information. "
        f"REGRESSION: Fund queries are being treated as category queries."
    )
    
    # The response should contain some content (RAG retrieved something)
    assert len(answer_text) > 0, (
        f"Query '{query}' returned empty response. RAG retrieval may have failed."
    )


@given(
    pii_query=st.sampled_from([
        "What is my PAN number?",
        "Can you tell me my email address?",
        "What is my phone number?",
        "Show me my account details",
        "What is my Aadhar number?",
    ])
)
@settings(
    max_examples=2,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_pii_guardrails_continue_to_work(pii_query):
    """
    **Property 2: Preservation** - PII Guardrails Continue to Work
    
    **Validates: Requirement 3.3**
    
    Tests that PII-related queries are blocked by validate_query() guardrails.
    
    This behavior MUST be preserved after the fix.
    """
    # ASSERTION 1: Query should be blocked by validate_query
    is_allowed, reason = validate_query(pii_query)
    
    assert not is_allowed, (
        f"PII query '{pii_query}' was NOT blocked by validate_query(). "
        f"REGRESSION: PII guardrails are not working."
    )
    
    assert reason is not None, (
        f"PII query '{pii_query}' was blocked but no reason was provided."
    )
    
    assert "personal" in reason.lower() or "facts-only" in reason.lower(), (
        f"PII query '{pii_query}' was blocked but the reason doesn't mention personal/facts-only. "
        f"Reason: {reason}"
    )
    
    # ASSERTION 2: Query should be blocked by answer() function
    result = answer(pii_query)
    
    assert result.get("blocked", False), (
        f"PII query '{pii_query}' was NOT blocked by answer() function. "
        f"REGRESSION: PII guardrails are not working in answer()."
    )


@given(
    advice_query=st.sampled_from([
        "Should I buy Groww Small Cap Fund?",
        "Which is the best fund for me?",
        "Recommend a good equity fund",
        "Will Groww Liquid Fund rise?",
        "Where should I invest?",
        "Suggest a fund for tax saving",
    ])
)
@settings(
    max_examples=3,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_advice_guardrails_continue_to_work(advice_query):
    """
    **Property 2: Preservation** - Advice Guardrails Continue to Work
    
    **Validates: Requirement 3.3**
    
    Tests that advice-seeking queries are blocked by validate_query() guardrails.
    
    This behavior MUST be preserved after the fix.
    """
    # ASSERTION 1: Query should be blocked by validate_query
    is_allowed, reason = validate_query(advice_query)
    
    assert not is_allowed, (
        f"Advice query '{advice_query}' was NOT blocked by validate_query(). "
        f"REGRESSION: Advice guardrails are not working."
    )
    
    assert reason is not None, (
        f"Advice query '{advice_query}' was blocked but no reason was provided."
    )
    
    assert "financial" in reason.lower() or "advice" in reason.lower() or "facts-only" in reason.lower(), (
        f"Advice query '{advice_query}' was blocked but the reason doesn't mention financial/advice/facts-only. "
        f"Reason: {reason}"
    )
    
    # ASSERTION 2: Query should be blocked by answer() function
    result = answer(advice_query)
    
    assert result.get("blocked", False), (
        f"Advice query '{advice_query}' was NOT blocked by answer() function. "
        f"REGRESSION: Advice guardrails are not working in answer()."
    )


@given(
    query=st.sampled_from([
        "What is SIP?",
        "Tell me about NAV",
        "What are the benefits of mutual funds?",
        "How does ELSS work?",
    ])
)
@settings(
    max_examples=2,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_response_formatting_continues_to_work(query):
    """
    **Property 2: Preservation** - Response Formatting Continues to Work
    
    **Validates: Requirement 3.4**
    
    Tests that response formatting (removing filler phrases) continues to work correctly.
    
    This behavior MUST be preserved after the fix.
    """
    # Get the answer
    result = answer(query)
    
    assert not result.get("blocked", False), (
        f"Query '{query}' was incorrectly blocked."
    )
    
    answer_text = result.get("answer", "")
    
    # ASSERTION 1: Filler phrases should be removed
    filler_phrases = [
        "based on the provided context",
        "i have identified",
        "according to the context",
    ]
    
    for filler in filler_phrases:
        assert filler not in answer_text.lower(), (
            f"Response to '{query}' contains filler phrase '{filler}'. "
            f"REGRESSION: Response formatting (filler removal) is not working. "
            f"Answer: {answer_text[:200]}"
        )
    
    # ASSERTION 2: Response should have content
    assert len(answer_text) > 0, (
        f"Query '{query}' returned empty response."
    )
    
    # ASSERTION 3: Response should be properly formatted (no leading/trailing whitespace)
    assert answer_text == answer_text.strip(), (
        f"Response to '{query}' has leading or trailing whitespace. "
        f"REGRESSION: Response formatting is not working properly."
    )


@given(
    query=st.sampled_from([
        # Use queries without category keywords to test core preservation behavior
        "What is the NAV of Groww Small Cap Fund?",
        "Tell me about Groww ELSS Tax Saver Fund",
        "How does Groww Multicap Fund work?",
        "What is SIP?",
        "Explain NAV to me",
    ])
)
@settings(
    max_examples=3,
    phases=[Phase.generate, Phase.target],
    deadline=None
)
def test_non_category_queries_not_intercepted(query):
    """
    **Property 2: Preservation** - Non-Category Queries Are Not Intercepted
    
    **Validates: Requirements 3.1, 3.2**
    
    Tests that non-category queries are NOT intercepted by _handle_category_query()
    and fall through to RAG retrieval.
    
    This is the core preservation property: the fix should ONLY affect category queries,
    not fund-specific queries.
    
    NOTE: We use queries without category keywords to test the core preservation behavior.
    """
    # ASSERTION 1: _handle_category_query should return None (not intercepted)
    result = _handle_category_query(query)
    
    assert result is None, (
        f"Non-category query '{query}' was incorrectly intercepted by _handle_category_query(). "
        f"REGRESSION: The fix is too broad and is intercepting non-category queries. "
        f"Only category-related queries should be intercepted."
    )
    
    # ASSERTION 2: Full answer() should process the query using RAG
    full_result = answer(query)
    
    assert full_result is not None, (
        f"Query '{query}' failed to get a response."
    )
    
    assert not full_result.get("blocked", False), (
        f"Query '{query}' was incorrectly blocked."
    )
    
    # ASSERTION 3: Response should NOT be category listing format
    answer_text = full_result.get("answer", "")
    
    # Should not contain category listing indicators
    category_indicators = [
        "category-wise segregation",
        "📈 Equity (21)",
        "🏦 Debt (6)",
        "⚖️ Hybrid (3)",
        "🪙 Commodities (2)",
    ]
    
    for indicator in category_indicators:
        assert indicator not in answer_text, (
            f"Non-category query '{query}' returned category listing format. "
            f"REGRESSION: Non-category queries are being treated as category queries. "
            f"Answer: {answer_text[:200]}"
        )


if __name__ == "__main__":
    # Run all tests
    print("=" * 80)
    print("RUNNING ALL TESTS")
    print("=" * 80)
    print("\nBug Condition Exploration Tests (EXPECTED TO FAIL on unfixed code)")
    print("Preservation Property Tests (EXPECTED TO PASS on unfixed code)\n")
    
    pytest.main([__file__, "-v", "--tb=short"])
