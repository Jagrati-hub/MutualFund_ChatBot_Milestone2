#!/usr/bin/env python3
"""
Test script to verify web link removal and NAV retrieval fixes.
"""

import sys
sys.path.insert(0, '.')

from src.rag_engine import format_answer, _query_fund_attribute, RAGConfig

# Test 1: Web link removal
print("=" * 80)
print("TEST 1: Web Link Removal")
print("=" * 80)

test_cases = [
    ("The NAV is ₹1,545.14 (https://groww.in/mutual-funds/amc/groww-mutual-funds)", 
     "The NAV is ₹1,545.14"),
    
    ("Groww Gilt Fund: ₹1,234.56 (https://groww.in/...)", 
     "Groww Gilt Fund: ₹1,234.56"),
    
    ("NAV: ₹1,000 (www.groww.in/funds)", 
     "NAV: ₹1,000"),
    
    ("The fund has https://groww.in/details in its description", 
     "The fund has in its description"),
    
    ("Visit www.groww.in for more info", 
     "Visit for more info"),
]

all_passed = True
for i, (input_text, expected) in enumerate(test_cases, 1):
    result = format_answer(input_text)
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\nTest 1.{i}: {status}")
    print(f"  Input:    {input_text}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")

print("\n" + "=" * 80)
print(f"Web Link Removal: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
print("=" * 80)

# Test 2: NAV retrieval with multiple query variations
print("\n" + "=" * 80)
print("TEST 2: NAV Retrieval (Multiple Query Variations)")
print("=" * 80)

config = RAGConfig()

# Test with a few funds
test_funds = [
    "Groww Liquid Fund",
    "Groww Gilt Fund",
    "Groww Gold ETF FoF",
]

print("\nTesting NAV retrieval for funds:")
for fund in test_funds:
    try:
        nav = _query_fund_attribute(fund, "nav", config)
        status = "✅" if nav and "Not available" not in nav else "⚠️"
        print(f"{status} {fund}: {nav}")
    except Exception as e:
        print(f"❌ {fund}: Error - {e}")

print("\n" + "=" * 80)
print("Tests completed!")
print("=" * 80)
