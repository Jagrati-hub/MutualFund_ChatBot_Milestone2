#!/usr/bin/env python3
"""
Test to diagnose the debt funds issue.
"""

import sys
sys.path.insert(0, '.')

from src.shared import SCOPE_FUNDS_BY_CATEGORY

# Check debt funds
debt_funds = SCOPE_FUNDS_BY_CATEGORY.get("🏦 Debt", [])

print("=" * 80)
print("DEBT FUNDS ANALYSIS")
print("=" * 80)
print(f"\nTotal debt funds: {len(debt_funds)}")
print("\nDebt funds list:")
for i, fund in enumerate(debt_funds, 1):
    print(f"  {i}. {fund}")

# Check for potential issues
print("\n" + "=" * 80)
print("POTENTIAL ISSUES TO CHECK")
print("=" * 80)

# Check for special characters or encoding issues
print("\nChecking for special characters:")
for fund in debt_funds:
    if any(ord(c) > 127 for c in fund):
        print(f"  ⚠️ {fund} - Contains non-ASCII characters")
    else:
        print(f"  ✅ {fund} - ASCII only")

# Check for duplicate names
print("\nChecking for duplicates:")
if len(debt_funds) == len(set(debt_funds)):
    print(f"  ✅ No duplicates found")
else:
    print(f"  ❌ Duplicates found!")
    from collections import Counter
    counts = Counter(debt_funds)
    for fund, count in counts.items():
        if count > 1:
            print(f"     {fund} appears {count} times")

# Check fund name patterns
print("\nFund name patterns:")
for fund in debt_funds:
    parts = fund.split()
    print(f"  {fund}")
    print(f"    - Length: {len(fund)} chars")
    print(f"    - Words: {len(parts)}")
    print(f"    - Starts with 'Groww': {fund.startswith('Groww')}")

print("\n" + "=" * 80)
