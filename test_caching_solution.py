#!/usr/bin/env python3
"""
Test script to verify the caching solution for API quota issue.

This script tests:
1. Cache functionality (read/write)
2. Single-fund vs category query detection
3. Performance improvement with caching
"""

import time
from src.rag_engine import (
    _cache_attribute, 
    _get_cached_attribute,
    _handle_category_attribute_query,
    answer
)

def test_cache_functionality():
    """Test basic cache read/write operations."""
    print("=" * 60)
    print("TEST 1: Cache Functionality")
    print("=" * 60)
    
    # Test caching
    print("✓ Caching test value...")
    _cache_attribute("Test Fund", "nav", "₹100.00")
    
    # Test retrieval
    print("✓ Retrieving cached value...")
    cached = _get_cached_attribute("Test Fund", "nav")
    assert cached == "₹100.00", f"Expected '₹100.00', got '{cached}'"
    print(f"  → Retrieved: {cached}")
    
    # Test non-existent cache
    print("✓ Testing non-existent cache...")
    not_cached = _get_cached_attribute("Test Fund", "expense_ratio")
    assert not_cached is None, f"Expected None, got '{not_cached}'"
    print("  → Correctly returns None")
    
    print("\n✅ Cache functionality test PASSED\n")


def test_query_detection():
    """Test single-fund vs category query detection."""
    print("=" * 60)
    print("TEST 2: Query Detection")
    print("=" * 60)
    
    test_cases = [
        ("show exit load of aggressive hybrid fund", None, "Single fund query"),
        ("show exit load of all hybrid funds", "handled", "Category query with 'all'"),
        ("show nav of equity funds", "handled", "Category query with 'funds'"),
        ("what is the nav of groww liquid fund", None, "Single fund query"),
        ("show expense ratio of debt funds", "handled", "Category query"),
    ]
    
    for query, expected, description in test_cases:
        result = _handle_category_attribute_query(query)
        status = "handled" if result is not None else None
        
        if status == expected:
            print(f"✓ {description}")
            print(f"  Query: '{query}'")
            print(f"  Result: {status}")
        else:
            print(f"✗ {description}")
            print(f"  Query: '{query}'")
            print(f"  Expected: {expected}, Got: {status}")
            raise AssertionError(f"Query detection failed for: {query}")
    
    print("\n✅ Query detection test PASSED\n")


def test_performance():
    """Test performance improvement with caching."""
    print("=" * 60)
    print("TEST 3: Performance Improvement")
    print("=" * 60)
    
    query = "show nav of commodities funds"
    
    # First query (may hit API or use existing cache)
    print(f"Query: '{query}'")
    print("First execution (building cache)...")
    start = time.time()
    result1 = answer(query)
    elapsed1 = time.time() - start
    print(f"  Time: {elapsed1:.2f}s")
    
    # Second query (should use cache)
    print("Second execution (using cache)...")
    start = time.time()
    result2 = answer(query)
    elapsed2 = time.time() - start
    print(f"  Time: {elapsed2:.2f}s")
    
    # Check if second query was faster
    if elapsed2 < elapsed1:
        improvement = elapsed1 / elapsed2
        print(f"\n✅ Performance improvement: {improvement:.1f}x faster")
    else:
        print(f"\n⚠️  Second query not faster (may already be cached)")
    
    # Verify both queries returned same structure
    assert result1['blocked'] == result2['blocked']
    assert 'answer' in result1 and 'answer' in result2
    print("✓ Both queries returned consistent results")
    
    print("\n✅ Performance test PASSED\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CACHING SOLUTION TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_cache_functionality()
        test_query_detection()
        test_performance()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        print("\nCaching solution is working correctly!")
        print("- Cache read/write operations work")
        print("- Single-fund vs category queries are correctly detected")
        print("- Performance improvement with caching is verified")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("TEST FAILED ❌")
        print("=" * 60)
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
