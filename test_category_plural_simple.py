#!/usr/bin/env python3
"""
Simple test to verify category-wise query detection logic.
"""

def test_category_detection():
    """Test category keyword and pattern detection."""
    
    category_keywords = ["equity", "debt", "hybrid", "commodity", "commodities", "liquid", "multi asset"]
    category_patterns = [
        "category wise", "categorywise", "by category", "all categories",
        "category listing", "list all", "all funds", "segregate by",
        "categorize", "break down", "organize", "group", "classify",
        "separate", "divide", "split", "arrange", "distribution",
        "breakdown", "composition", "allocation", "types of funds",
        "fund categories", "what categories", "how are funds"
    ]
    
    category_queries = [
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
        "show category",
        "list category",
        "all category",
        "by category",
        "fund names",
        "show fund",
        "list fund",
        "all fund",
        "list all equity funds",
        "show me all debt funds",
        "what are the hybrid funds?",
        "which commodities funds does Groww offer?",
        "list all liquid funds",
        "show equity funds",
        "all debt funds",
        "hybrid funds list",
        "commodities funds",
        "show NAV of equity funds",
        "what is the expense ratio of debt funds?",
        "display the exit load for hybrid funds",
        "commodities funds NAV",
        "equity fund expense ratio",
        "NAV of all debt funds",
        "expense ratio for hybrid funds",
        "exit load in commodities",
        "distribution of funds",
        "breakdown by category",
        "composition of funds",
        "allocation by category",
        "how are funds organized?",
        "what categories of funds?",
        "fund categories",
        "types of funds",
    ]
    
    print("Testing category detection logic:")
    print("=" * 70)
    
    all_passed = True
    for query in category_queries:
        q = query.lower()
        
        # Check if query contains category keywords
        has_category_keyword = any(keyword in q for keyword in category_keywords)
        
        # Check if query contains category patterns
        has_category_pattern = any(pattern in q for pattern in category_patterns)
        
        # If query has category keyword AND (category pattern OR plural indicators)
        should_use_plural = False
        if has_category_keyword:
            plural_indicators = ["funds", "all", "each", "every", "list", "show"]
            has_plural_indicator = any(ind in q for ind in plural_indicators)
            
            if has_category_pattern or has_plural_indicator:
                should_use_plural = True
        
        status = "✅" if should_use_plural else "❌"
        
        if not should_use_plural:
            all_passed = False
            print(f"{status} FAILED: '{query}'")
        else:
            print(f"{status} '{query}'")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL CATEGORY-WISE QUERIES DETECTED CORRECTLY")
        return True
    else:
        print("\n❌ SOME CATEGORY-WISE QUERIES NOT DETECTED")
        return False

def test_single_fund_detection():
    """Test single fund query detection."""
    
    category_keywords = ["equity", "debt", "hybrid", "commodity", "commodities", "liquid", "multi asset"]
    category_patterns = [
        "category wise", "categorywise", "by category", "all categories",
        "category listing", "list all", "all funds", "segregate by",
        "categorize", "break down", "organize", "group", "classify",
        "separate", "divide", "split", "arrange", "distribution",
        "breakdown", "composition", "allocation", "types of funds",
        "fund categories", "what categories", "how are funds"
    ]
    
    single_fund_queries = [
        "What is the expense ratio of the Groww Nifty Total Market Index Fund?",
        "Tell me about Groww Liquid Fund",
        "Show me the exit load of Groww Aggressive Hybrid Fund",
        "What is the NAV of Groww Gold ETF FoF?",
        "Is the Groww Liquid Fund suitable for short-term parking?",
    ]
    
    print("\nTesting single fund query detection:")
    print("=" * 70)
    
    all_passed = True
    for query in single_fund_queries:
        q = query.lower()
        
        # Check if query contains category keywords
        has_category_keyword = any(keyword in q for keyword in category_keywords)
        
        # Check if query contains category patterns
        has_category_pattern = any(pattern in q for pattern in category_patterns)
        
        # If query has category keyword AND (category pattern OR plural indicators)
        should_use_plural = False
        if has_category_keyword:
            plural_indicators = ["funds", "all", "each", "every", "list", "show"]
            has_plural_indicator = any(ind in q for ind in plural_indicators)
            
            if has_category_pattern or has_plural_indicator:
                should_use_plural = True
        
        status = "✅" if not should_use_plural else "❌"
        
        if should_use_plural:
            all_passed = False
            print(f"{status} FAILED: '{query[:60]}...'")
        else:
            print(f"{status} '{query[:60]}...'")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL SINGLE FUND QUERIES DETECTED CORRECTLY")
        return True
    else:
        print("\n❌ SOME SINGLE FUND QUERIES DETECTED AS CATEGORY")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SIMPLE TEST: CATEGORY DETECTION LOGIC")
    print("=" * 70)
    
    result1 = test_category_detection()
    result2 = test_single_fund_detection()
    
    print("\n" + "=" * 70)
    if result1 and result2:
        print("✅ ALL TESTS PASSED - CATEGORY DETECTION LOGIC IS CORRECT")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70 + "\n")
