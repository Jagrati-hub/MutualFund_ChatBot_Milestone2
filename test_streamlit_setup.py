#!/usr/bin/env python
"""Test script to verify Streamlit setup and imports."""

import sys
from pathlib import Path

# Add phase directories to Python path
sys.path.insert(0, str(Path("phases/phase-4-orchestration")))
sys.path.insert(0, str(Path("phases/phase-3-retrieval")))

print("=" * 60)
print("Testing Groww MF FAQ Assistant Setup")
print("=" * 60)

# Test 1: Import Streamlit
print("\n[1/5] Testing Streamlit import...")
try:
    import streamlit as st
    print("✓ Streamlit imported successfully")
except Exception as e:
    print(f"✗ Streamlit import failed: {e}")
    sys.exit(1)

# Test 2: Import RAG Engine
print("\n[2/5] Testing RAG Engine import...")
try:
    from src import rag_engine
    print("✓ RAG Engine imported successfully")
except Exception as e:
    print(f"✗ RAG Engine import failed: {e}")
    sys.exit(1)

# Test 3: Import Shared module
print("\n[3/5] Testing Shared module import...")
try:
    from src.shared import SCOPE_FUNDS, SCOPE_FUNDS_BY_CATEGORY
    print(f"✓ Shared module imported successfully")
    print(f"  - Total funds: {len(SCOPE_FUNDS)}")
    print(f"  - Categories: {list(SCOPE_FUNDS_BY_CATEGORY.keys())}")
except Exception as e:
    print(f"✗ Shared module import failed: {e}")
    sys.exit(1)

# Test 4: Test RAG Engine functions
print("\n[4/5] Testing RAG Engine functions...")
try:
    # Test validate_query
    is_allowed, reason = rag_engine.validate_query("What is the NAV of Groww Liquid Fund?")
    print(f"✓ validate_query works: allowed={is_allowed}")
    
    # Test get_default_refusal
    refusal = rag_engine.get_default_refusal()
    print(f"✓ get_default_refusal works: {len(refusal)} chars")
except Exception as e:
    print(f"✗ RAG Engine functions failed: {e}")
    sys.exit(1)

# Test 5: Check environment
print("\n[5/5] Testing environment configuration...")
try:
    import os
    from dotenv import load_dotenv
    
    env_path = Path("phases/phase-0-foundation/.env")
    load_dotenv(env_path)
    
    gemini_key_1 = os.getenv("GEMINI_API_KEY_1")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if gemini_key_1:
        print(f"✓ GEMINI_API_KEY_1 configured: {gemini_key_1[:10]}...")
    else:
        print("✗ GEMINI_API_KEY_1 not found")
        
    if groq_key:
        print(f"✓ GROQ_API_KEY configured: {groq_key[:10]}...")
    else:
        print("✗ GROQ_API_KEY not found")
except Exception as e:
    print(f"✗ Environment check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed! Setup is ready.")
print("=" * 60)
print("\nYou can now run:")
print("  streamlit run phases/phase-5-frontend/app.py")
