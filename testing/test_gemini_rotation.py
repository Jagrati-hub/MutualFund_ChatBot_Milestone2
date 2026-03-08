#!/usr/bin/env python3
"""Test Gemini API key rotation."""

import logging
logging.basicConfig(level=logging.INFO)

from src.rag_engine import (
    _GEMINI_KEYS,
    _CURRENT_GEMINI_KEY_INDEX,
    _GEMINI_KEY_FAILURES,
    _get_current_gemini_key,
    _switch_gemini_key,
    _handle_quota_error
)

print("=" * 60)
print("GEMINI API KEY ROTATION TEST")
print("=" * 60)
print()

print(f"Total Gemini keys loaded: {len(_GEMINI_KEYS)}")
print(f"Current key index: {_CURRENT_GEMINI_KEY_INDEX}")
print(f"Current key: {_get_current_gemini_key()[:20]}...")
print()

print("Simulating quota errors...")
print()

# Simulate 3 quota errors for key #1
for i in range(3):
    print(f"Quota error #{i + 1} for key #1")
    _handle_quota_error("RESOURCE_EXHAUSTED: 429 Too Many Requests")
    print(f"  Current key index: {_CURRENT_GEMINI_KEY_INDEX}")
    print(f"  Failures: {_GEMINI_KEY_FAILURES}")
    print()

print("=" * 60)
print("Key rotation should have occurred!")
print(f"Now using key #{_CURRENT_GEMINI_KEY_INDEX + 1}")
print("=" * 60)
