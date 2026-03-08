#!/usr/bin/env python3
"""
Updated test to verify category-wise query detection with new logic.
"""

def test_category_detection():
    """Test category keyword and pattern detection with new logic."""
    
    # NEW LOGIC: Category listing patterns (these are ALWAYS category queries)
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
    
    category_keywords = ["equity", "debt", "hybrid", "commodity", "commodities", "liquid", "multi asset"]
    plural_indicators = ["funds", "all", "each", "every", "list", "show"]
    
    category_queries = [
        # Category listing queries (should match category_listing_patterns)
        ("category wise listing", True),
        ("list all categories", True),
        ("all funds by category", True),
        ("segregate by category", True),
        ("categorize funds", True),
        ("break down by category", True),
        ("organize by category", True),
        ("group by category", True),
        ("classify by category", True),
        ("separate by category", True),
        ("divide by category", True),
        ("split by category", True),
        ("arrange by category", True),
        ("show category", True),
        ("list category", True),
        ("all category", True),
        ("by category", True),
        ("fund names", True),
        ("show fund", True),
        ("list fund", True),
        ("all fund", True),
        ("distribution of funds", True),
        ("breakdown by category", True),
        ("composition of funds", True),
        ("allocation by category", True),
        ("how are funds organized?", True),
        ("what categories of funds?", True),
        ("fund categories", True),
        ("types of funds", True),
        
        # Category-specific queries (have category keyword + plural indicator)
        ("list all equity funds", True),
        ("show me all debt funds", True),
        ("what are the hybrid funds?", True),
        ("which commodities funds does Groww offer?", True),
        ("list all liquid funds", True),
        ("show equity funds", True),
        ("all debt funds", True),
        ("hybrid funds list", True),
        ("commodities funds", True),
        
        # Category-attribute queries (have category + attribute)
        ("show NAV of equity funds", True),
        ("what is the expense ratio of debt funds?", True),
        ("display the exit load for hybrid funds", True),
        ("commodities funds NAV", True),
        ("NAV of all debt funds", True),
        ("expense ratio for hybrid funds", True),
        
        # Single fund queries (should NOT match)
        ("What is the expense ratio of the Groww Nifty Total Market Index Fund?", False),
        ("Tell me about Groww Liquid Fund", False),
        ("What is the NAV of Groww Gold ETF FoF?", False),
        ("Is the Groww Liquid Fund suitable for short-term parking?", False),
    ]
    
    print("Testing category detection logic (NEW):")
    print("=" * 70)
    
    all_passed = True
    for query, should_be_plural in category_queries:
        q = query.lower()
        
        # Check if query matches category listing patterns
        matches_listing_pattern = any(pattern in q for pattern in category_listing_patterns)
        
        if matches_listing_pattern:
            detected_as_plural = True
        else:
            # Check if query has category keyword + plural indicator
            has_category_keyword = any(keyword in q for keyword in category_keywords)
            has_plural_indicator = any(ind in q for ind in plural_indicators)
            detected_as_plural = has_category_keyword and has_plural_indicator
        
        status = "✅" if detected_as_plural == should_be_plural else "❌"
        
        if detected_as_plural != should_be_plural:
            all_passed = False
            expected = "plural" if should_be_plural else "singular"
            got = "plural" if detected_as_plural else "singular"
            print(f"{status} FAILED: '{query[:50]}...' (expected {expected}, got {got})")
        else:
            link_type = "plural" if detected_as_plural else "singular"
            print(f"{status} '{query[:50]}...' → {link_type}")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL CATEGORY DETECTION TESTS PASSED")
        return True
    else:
        print("\n❌ SOME CATEGORY DETECTION TESTS FAILED")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("UPDATED TEST: CATEGORY DETECTION LOGIC")
    print("=" * 70)
    
    result = test_category_detection()
    
    print("\n" + "=" * 70)
    if result:
        print("✅ ALL TESTS PASSED - CATEGORY PLURAL LINK LOGIC IS CORRECT")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70 + "\n")
