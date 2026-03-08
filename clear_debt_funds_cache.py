#!/usr/bin/env python3
"""
Clear cache specifically for debt funds NAV queries.
"""

import os
import hashlib
from pathlib import Path

CACHE_DIR = Path(".cache/fund_attributes")

# Debt funds
debt_funds = [
    "Groww Liquid Fund",
    "Groww Overnight Fund",
    "Groww Short Duration Fund",
    "Groww Dynamic Bond Fund",
    "Groww Gilt Fund",
    "Groww Nifty 1D Rate Liquid ETF",
]

print("=" * 80)
print("CLEARING DEBT FUNDS NAV CACHE")
print("=" * 80)

cleared_count = 0
for fund in debt_funds:
    # Generate cache key for NAV attribute
    cache_key_str = f"{fund}:nav"
    cache_key = hashlib.md5(cache_key_str.encode()).hexdigest()
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            os.remove(cache_file)
            print(f"✅ Cleared: {fund}")
            cleared_count += 1
        except Exception as e:
            print(f"❌ Error clearing {fund}: {e}")
    else:
        print(f"⚠️  No cache found for: {fund}")

print("\n" + "=" * 80)
print(f"Total cleared: {cleared_count}/{len(debt_funds)}")
print("=" * 80)
print("\nNext query for debt funds NAV will fetch fresh data from API.")
