#!/usr/bin/env python3
"""
Test script to verify web link removal in format_answer function.
"""

import sys
import re
sys.path.insert(0, '.')

# Test the format_answer function directly
def format_answer(answer_text: str) -> str:
    """
    Format the answer by removing filler phrases, inline source mentions, and web links.
    """
    # Remove filler phrases
    fillers = [
        r"Based on the provided context,?\s*", 
        r"I have identified,?\s*", 
        r"According to the context,?\s*"
    ]
    for filler in fillers:
        answer_text = re.sub(filler, "", answer_text, flags=re.IGNORECASE)
    
    # Remove inline source mentions - these appear as plain text in the answer
    # Pattern 1: "Source: [Official Groww Mu..." or "Source: [Off..." or "Source: [Official..."
    answer_text = re.sub(r'Source:\s*\[Official[^\]]*\]\.{0,3}', '', answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r'Source:\s*\[Off[^\]]*\]\.{0,3}', '', answer_text, flags=re.IGNORECASE)
    
    # Pattern 2: Just "Source: [Official Groww Mu..." without closing bracket
    answer_text = re.sub(r'Source:\s*\[Official[^\n]*', '', answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r'Source:\s*\[Off[^\n]*', '', answer_text, flags=re.IGNORECASE)
    
    # Pattern 3: Any remaining "Source: ..." lines
    answer_text = re.sub(r'\n\s*Source:\s*[^\n]+', '', answer_text, flags=re.IGNORECASE)
    answer_text = re.sub(r'^Source:\s*[^\n]+\n?', '', answer_text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove markdown links like [text](url) - replace with just the text
    # Do this BEFORE removing plain URLs to avoid issues
    answer_text = re.sub(r'\[([^\]]+)\]\(([^\)]*)\)', r'\1', answer_text)
    
    # Remove web links - MOST AGGRESSIVE APPROACH
    # Remove URLs with various formats: (https://...), https://..., (www...), www...
    answer_text = re.sub(r'\s*\(https?://[^\)]*\)', '', answer_text)
    answer_text = re.sub(r'\s*\(www\.[^\)]*\)', '', answer_text)
    answer_text = re.sub(r'\s*https?://[^\s\)]+', '', answer_text)
    answer_text = re.sub(r'\s*www\.[^\s\)]+', '', answer_text)
    
    # Remove any remaining URLs that might be in other formats
    answer_text = re.sub(r'\(https?://[^\)]*\)', '', answer_text)
    answer_text = re.sub(r'\(www\.[^\)]*\)', '', answer_text)
    
    # Remove empty brackets and parentheses
    answer_text = re.sub(r'\[\s*\]\s*', '', answer_text)
    answer_text = re.sub(r'\(\s*\)\s*', '', answer_text)
    
    # Remove trailing dots, spaces, and commas after link removal
    answer_text = re.sub(r'\s*[\.,]\s*$', '', answer_text, flags=re.MULTILINE)
    answer_text = re.sub(r'[\.,]\s*$', '', answer_text, flags=re.MULTILINE)
    
    # Clean up multiple newlines and extra spaces
    answer_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer_text)  # Max 2 newlines
    answer_text = re.sub(r'\n\s+', '\n', answer_text)  # Remove leading spaces on lines
    answer_text = re.sub(r'\s+\n', '\n', answer_text)  # Remove trailing spaces before newlines
    
    # Remove extra spaces within lines
    answer_text = re.sub(r'  +', ' ', answer_text)
    
    # Final cleanup: remove any remaining trailing spaces and punctuation
    answer_text = re.sub(r'\s+$', '', answer_text, flags=re.MULTILINE)
    
    return answer_text.strip()


# Test cases
print("=" * 80)
print("TEST: Web Link Removal in format_answer()")
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
    
    ("Groww Liquid Fund: ₹1,100.50 (https://groww.in/...)\nGroww Gilt Fund: ₹1,200.75 (https://groww.in/...)",
     "Groww Liquid Fund: ₹1,100.50\nGroww Gilt Fund: ₹1,200.75"),
]

all_passed = True
for i, (input_text, expected) in enumerate(test_cases, 1):
    result = format_answer(input_text)
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\nTest {i}: {status}")
    print(f"  Input:    {repr(input_text)}")
    print(f"  Expected: {repr(expected)}")
    print(f"  Got:      {repr(result)}")
    if not passed:
        print(f"  Diff: Expected length {len(expected)}, got {len(result)}")

print("\n" + "=" * 80)
print(f"Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
print("=" * 80)
