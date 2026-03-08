#!/usr/bin/env python3
"""Test plural link logic for multiple fund queries."""

import logging
logging.basicConfig(level=logging.INFO)

from src.rag_engine import _count_explicit_funds_in_query, _should_use_plural_link

test_cases = [
    ("show nav of groww liquid fund", False, "Single fund - should use singular link"),
    ("show nav of groww liquid fund and groww gold etf", True, "Two funds - should use plural link"),
    ("silver etf or gold etf", True, "OR keyword - should use plural link"),
    ("show silver etf and gold etf", True, "Two funds with SHOW - should use plural link"),
    ("show all equity funds", True, "Category query - should use plural link"),
    ("what is the nav of groww overnight fund", False, "Single fund - should use singular link"),
]

print("=" * 70)
print("PLURAL LINK LOGIC TEST")
print("=" * 70)
print()

for query, expected_plural, description in test_cases:
    explicit_count = _count_explicit_funds_in_query(query)
    use_plural = _should_use_plural_link(query, 2 if explicit_count >= 2 else 1)
    
    status = "✓" if use_plural == expected_plural else "✗"
    print(f"{status} {description}")
    print(f"  Query: '{query}'")
    print(f"  Explicit funds: {explicit_count}")
    print(f"  Use plural link: {use_plural} (expected: {expected_plural})")
    print()

print("=" * 70)
