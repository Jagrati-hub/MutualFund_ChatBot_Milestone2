#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test alias resolution."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'phases' / 'phase-3-retrieval'))

from src.rag_engine import resolve_fund_name

# Test alias resolution
queries = [
    "What is the NAV of gold etf?",
    "gold etf",
    "gold",
    "silver etf",
    "liquid fund",
]

for query in queries:
    resolved = resolve_fund_name(query)
    print(f"Query: '{query}'")
    print(f"Resolved: {resolved}")
    print()
