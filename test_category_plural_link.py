#!/usr/bin/env python3
"""
Test to verify that ALL category-wise queries use the plural link.
"""

from src.rag_engine import _should_use_plural_link

def test_category_wise_queries_use_plural_link():
    """Test that all category-wise queries use plural link."""
    
    category_queries = [
        # Category listing queries
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
        
        # Specific category queries
        "list all equity funds",
        "show me all debt funds",
        "what are the hybrid funds?",
        "which commodities funds does Groww offer?",
        "list all liquid funds",
        "show equity funds",
        "all debt funds",
        "hybrid funds list",
        "commodities funds",
        
        # Category-attribute queries
        "show NAV of equity funds",
        "what is the expense ratio of debt funds?",
        "display the exit load for hybrid funds",
        "commodities funds NAV",
        "equity fund expense ratio",
        "NAV of all debt funds",
        "expense ratio for hybrid funds",
        "exit load in commodities",
        
        # Distribution/breakdown queries
        "distribution of funds",
        "breakdown by category",
        "composition of funds",
        "allocation by category",
        "how are funds organized?",
        "what categories of funds?",
        "fund categories",
        "types of funds",
    ]
    
    print("Testing category-wise queries for plural link:")
    print("=" * 70)
    
    all_passed = True
    for query in category_queries:
        use_plural = _should_use_plural_link(query)
        status = "✅" if use_plural else "❌"
        
        if not use_plural:
            all_passed = False
            print(f"{status} FAILED: '{query}'")
        else:
            print(f"{status} '{query}'")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL CATEGORY-WISE QUERIES USE PLURAL LINK")
        return True
    else:
        print("\n❌ SOME CATEGORY-WISE QUERIES DO NOT USE PLURAL LINK")
        return False

def test_single_fund_queries_use_singular_link():
    """Test that single fund queries use singular link."""
    
    single_fund_queries = [
        "What is the expense ratio of the Groww Nifty Total Market Index Fund?",
        "Tell me about Groww Liquid Fund",
        "Show me the exit load of Groww Aggressive Hybrid Fund",
        "What is the NAV of Groww Gold ETF FoF?",
        "Is the Groww Liquid Fund suitable for short-term parking?",
    ]
    
    print("\nTesting single fund queries for singular link:")
    print("=" * 70)
    
    all_passed = True
    for query in single_fund_queries:
        use_plural = _should_use_plural_link(query)
        status = "✅" if not use_plural else "❌"
        
        if use_plural:
            all_passed = False
            print(f"{status} FAILED: '{query[:60]}...'")
        else:
            print(f"{status} '{query[:60]}...'")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL SINGLE FUND QUERIES USE SINGULAR LINK")
        return True
    else:
        print("\n❌ SOME SINGLE FUND QUERIES USE PLURAL LINK")
        return False

def test_multi_fund_queries_use_plural_link():
    """Test that multi-fund queries use plural link."""
    
    multi_fund_queries = [
        "Compare Groww Gold ETF FoF and Groww Silver ETF FoF",
        "Show me Groww Liquid Fund and Groww Overnight Fund",
        "What are the differences between Groww Large Cap Fund and Groww Small Cap Fund?",
        "Show me Groww Gold ETF FoF or Groww Silver ETF FoF",
        "What is the NAV of Groww Liquid Fund or Groww Overnight Fund?",
    ]
    
    print("\nTesting multi-fund queries for plural link:")
    print("=" * 70)
    
    all_passed = True
    for query in multi_fund_queries:
        use_plural = _should_use_plural_link(query)
        status = "✅" if use_plural else "❌"
        
        if not use_plural:
            all_passed = False
            print(f"{status} FAILED: '{query[:60]}...'")
        else:
            print(f"{status} '{query[:60]}...'")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL MULTI-FUND QUERIES USE PLURAL LINK")
        return True
    else:
        print("\n❌ SOME MULTI-FUND QUERIES DO NOT USE PLURAL LINK")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST: CATEGORY-WISE QUERIES ALWAYS USE PLURAL LINK")
    print("=" * 70)
    
    result1 = test_category_wise_queries_use_plural_link()
    result2 = test_single_fund_queries_use_singular_link()
    result3 = test_multi_fund_queries_use_plural_link()
    
    print("\n" + "=" * 70)
    if result1 and result2 and result3:
        print("✅ ALL TESTS PASSED - LINK LOGIC IS CORRECT")
    else:
        print("❌ SOME TESTS FAILED - LINK LOGIC NEEDS FIXING")
    print("=" * 70 + "\n")
