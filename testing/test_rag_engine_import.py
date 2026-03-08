#!/usr/bin/env python3
"""
Test that rag_engine.py can be imported and format_answer works correctly.
"""

import sys
sys.path.insert(0, '.')

try:
    from src.rag_engine import format_answer
    print("✅ Successfully imported format_answer from src.rag_engine")
    
    # Test the function
    test_input = "The NAV is ₹1,545.14 (https://groww.in/mutual-funds/amc/groww-mutual-funds)"
    result = format_answer(test_input)
    expected = "The NAV is ₹1,545.14"
    
    if result == expected:
        print("✅ format_answer works correctly")
        print(f"   Input:  {test_input}")
        print(f"   Output: {result}")
    else:
        print("❌ format_answer output doesn't match expected")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
