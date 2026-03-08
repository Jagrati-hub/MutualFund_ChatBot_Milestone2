#!/usr/bin/env python3
"""
Test to verify the citation link fix for single-fund vs multi-fund queries.
"""

from src.rag_engine import _count_explicit_funds_in_query, _should_use_plural_link

def test_single_fund_queries():
    """Test that single fund queries are correctly identified."""
    test_cases = [
        ("What is the expense ratio of the Groww Nifty Total Market Index Fund?", 1),
        ("Tell me about Groww Liquid Fund", 1),
        ("What is the NAV of Groww Gold ETF FoF?", 1),
        ("Show me the exit load of Groww Aggressive Hybrid Fund", 1),
        ("What is the investment objective of the Groww ELSS Tax Saver Fund?", 1),
    ]
    
    print("Testing single fund queries:")
    for query, expected_count in test_cases:
        count = _count_explicit_funds_in_query(query)
        status = "✓" if count == expected_count else "✗"
        print(f"  {status} '{query[:60]}...' → {count} fund(s) (expected {expected_count})")
        assert count == expected_count, f"Expected {expected_count}, got {count}"

def test_multi_fund_queries():
    """Test that multi-fund queries are correctly identified."""
    test_cases = [
        ("Compare Groww Gold ETF FoF and Groww Silver ETF FoF", 2),
        ("Show me Groww Liquid Fund and Groww Overnight Fund", 2),
        ("What are the differences between Groww Large Cap Fund and Groww Small Cap Fund?", 2),
    ]
    
    print("\nTesting multi-fund queries:")
    for query, expected_count in test_cases:
        count = _count_explicit_funds_in_query(query)
        status = "✓" if count == expected_count else "✗"
        print(f"  {status} '{query[:60]}...' → {count} fund(s) (expected {expected_count})")
        assert count == expected_count, f"Expected {expected_count}, got {count}"

def test_plural_link_logic():
    """Test that plural link logic works correctly."""
    test_cases = [
        ("What is the expense ratio of the Groww Nifty Total Market Index Fund?", False),
        ("Show me Groww Gold ETF FoF and Groww Silver ETF FoF", True),
        ("Tell me about equity funds", False),  # Category query, not explicit fund names
        ("What is the NAV of Groww Liquid Fund?", False),
    ]
    
    print("\nTesting plural link logic:")
    for query, expected_plural in test_cases:
        use_plural = _should_use_plural_link(query)
        status = "✓" if use_plural == expected_plural else "✗"
        link_type = "plural" if use_plural else "singular"
        expected_type = "plural" if expected_plural else "singular"
        print(f"  {status} '{query[:60]}...' → {link_type} link (expected {expected_type})")
        assert use_plural == expected_plural, f"Expected {expected_plural}, got {use_plural}"

if __name__ == "__main__":
    test_single_fund_queries()
    test_multi_fund_queries()
    test_plural_link_logic()
    print("\n✅ All tests passed!")
