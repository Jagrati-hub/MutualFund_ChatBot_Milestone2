#!/usr/bin/env python3
"""
Test to verify OR and SHOW keyword logic for plural links.
"""

from src.rag_engine import _should_use_plural_link

def test_or_keyword():
    """Test that OR keyword triggers plural link."""
    test_cases = [
        ("Show me Groww Gold ETF FoF or Groww Silver ETF FoF", True),
        ("What is the NAV of Groww Liquid Fund or Groww Overnight Fund?", True),
        ("Compare Groww Large Cap Fund or Groww Small Cap Fund", True),
    ]
    
    print("Testing OR keyword logic:")
    for query, expected_plural in test_cases:
        use_plural = _should_use_plural_link(query)
        status = "✓" if use_plural == expected_plural else "✗"
        link_type = "plural" if use_plural else "singular"
        expected_type = "plural" if expected_plural else "singular"
        print(f"  {status} '{query[:60]}...' → {link_type} link (expected {expected_type})")
        assert use_plural == expected_plural, f"Expected {expected_plural}, got {use_plural}"

def test_show_keyword():
    """Test that SHOW keyword with multiple results triggers plural link."""
    test_cases = [
        # SHOW with multiple results should use plural link
        ("Show me all equity funds", True),  # num_results > 1
        ("Show Groww Gold ETF FoF and Groww Silver ETF FoF", True),  # 2 explicit funds
    ]
    
    print("\nTesting SHOW keyword logic:")
    for query, expected_plural in test_cases:
        # For SHOW with multiple results, we need to pass num_results > 1
        if "all" in query.lower():
            use_plural = _should_use_plural_link(query, num_results=21)  # Multiple results
        else:
            use_plural = _should_use_plural_link(query)
        
        status = "✓" if use_plural == expected_plural else "✗"
        link_type = "plural" if use_plural else "singular"
        expected_type = "plural" if expected_plural else "singular"
        print(f"  {status} '{query[:60]}...' → {link_type} link (expected {expected_type})")
        assert use_plural == expected_plural, f"Expected {expected_plural}, got {use_plural}"

if __name__ == "__main__":
    test_or_keyword()
    test_show_keyword()
    print("\n✅ All OR/SHOW tests passed!")
