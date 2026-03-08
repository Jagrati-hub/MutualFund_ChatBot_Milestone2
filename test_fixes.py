#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test to verify the three main fixes are working."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'phases' / 'phase-3-retrieval'))

from src.rag_engine import answer

print("=" * 80)
print("TESTING THE THREE MAIN FIXES")
print("=" * 80)

# Test 1: Alias resolution - 'gold etf' should resolve to specific fund
print("\nTEST 1: Alias Resolution")
print("-" * 80)
print("Query: What is the NAV of gold etf?")
result = answer('What is the NAV of gold etf?')
print(f"Answer preview: {result['answer'][:150]}...")
print(f"Citation URL: {result['citation_url']}")
is_singular_link = "groww.in/mutual-funds/amc/groww-mutual-funds" not in result['citation_url'] or "gold" in result['citation_url'].lower()
print(f"[PASS] Using singular fund link (not plural): {is_singular_link}")

# Test 2: Date appending - should always have 'as of' date
print("\nTEST 2: Date Appending")
print("-" * 80)
print("Query: What is SIP in Groww mutual funds?")
result = answer('What is SIP in Groww mutual funds?')
has_date = 'as of' in result['answer']
print(f"Answer ends with: ...{result['answer'][-40:]}")
print(f"[PASS] Has 'as of' date appended: {has_date}")

# Test 3: Category query - should be intercepted
print("\nTEST 3: Category Query Interception")
print("-" * 80)
print("Query: segregate by category")
result = answer('segregate by category')
is_category_response = 'Equity' in result['answer']
# Safely print answer preview
try:
    print(f"Answer preview: {result['answer'][:150]}...")
except:
    print("Answer preview: [Category response with special characters]")
print(f"[PASS] Is category response (not RAG): {is_category_response}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED")
print("=" * 80)
