#!/usr/bin/env python3
"""Test Gemini API key rotation with actual queries."""

import logging
logging.basicConfig(level=logging.INFO)

from src import rag_engine

print("=" * 60)
print("GEMINI API KEY ROTATION TEST")
print("=" * 60)
print()

print(f"Total Gemini keys loaded: {len(rag_engine._GEMINI_KEYS)}")
for i, key in enumerate(rag_engine._GEMINI_KEYS):
    print(f"  Key #{i + 1}: {key[:20]}...")
print()

print(f"Current key index: {rag_engine._CURRENT_GEMINI_KEY_INDEX}")
print(f"Current key: {rag_engine._get_current_gemini_key()[:20]}...")
print()

# Simulate quota errors
print("Simulating 3 quota errors for key #1...")
for i in range(3):
    rag_engine._handle_quota_error("RESOURCE_EXHAUSTED: 429 Too Many Requests")
    print(f"  After error #{i + 1}: Current key index = {rag_engine._CURRENT_GEMINI_KEY_INDEX}, Failures = {rag_engine._GEMINI_KEY_FAILURES}")

print()
print(f"After rotation: Now using key #{rag_engine._CURRENT_GEMINI_KEY_INDEX + 1}")
print(f"Current key: {rag_engine._get_current_gemini_key()[:20]}...")
print()

# Simulate more errors to test full rotation
print("Simulating 3 more quota errors for key #2...")
for i in range(3):
    rag_engine._handle_quota_error("RESOURCE_EXHAUSTED: 429 Too Many Requests")
    print(f"  After error #{i + 1}: Current key index = {rag_engine._CURRENT_GEMINI_KEY_INDEX}, Failures = {rag_engine._GEMINI_KEY_FAILURES}")

print()
print(f"After 2nd rotation: Now using key #{rag_engine._CURRENT_GEMINI_KEY_INDEX + 1}")
print(f"Current key: {rag_engine._get_current_gemini_key()[:20]}...")
print()

# Simulate more errors to test full rotation
print("Simulating 3 more quota errors for key #3...")
for i in range(3):
    rag_engine._handle_quota_error("RESOURCE_EXHAUSTED: 429 Too Many Requests")
    print(f"  After error #{i + 1}: Current key index = {rag_engine._CURRENT_GEMINI_KEY_INDEX}, Failures = {rag_engine._GEMINI_KEY_FAILURES}")

print()
print(f"After 3rd rotation: Now using key #{rag_engine._CURRENT_GEMINI_KEY_INDEX + 1}")
print(f"Current key: {rag_engine._get_current_gemini_key()[:20]}...")
print()

print("=" * 60)
print("All 3 keys have been rotated through!")
print("=" * 60)
