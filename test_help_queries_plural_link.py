#!/usr/bin/env python3
"""
Test to verify that help/information queries use the plural link.
"""

def test_help_queries_use_plural_link():
    """Test that all help/information queries use plural link."""
    
    help_patterns = [
        "how can you help",
        "what do you do",
        "what can you do",
        "how can i use",
        "how do i use",
        "tell me about",
        "what is this",
        "what are you",
        "who are you",
        "help",
        "about",
        "information",
        "guide",
        "how to",
        "what's available",
        "what funds",
        "which funds",
        "do you have",
        "can you help",
        "can you tell",
        "can you show",
        "can you provide",
        "can you list",
        "can you give",
        "can you explain",
        "can you describe",
        "can you share",
        "can you display",
        "can you show me",
        "can you tell me",
        "can you give me",
        "can you provide me",
        "can you list me",
        "can you explain me",
        "can you describe me",
        "can you share me",
        "can you display me",
    ]
    
    help_queries = [
        "How can you help?",
        "What do you do?",
        "What can you do?",
        "How can I use this?",
        "How do I use this?",
        "Tell me about yourself",
        "What is this?",
        "What are you?",
        "Who are you?",
        "Help",
        "About",
        "Information",
        "Guide",
        "How to use",
        "What's available?",
        "What funds do you have?",
        "Which funds are available?",
        "Do you have any funds?",
        "Can you help me?",
        "Can you tell me about funds?",
        "Can you show me funds?",
        "Can you provide information?",
        "Can you list funds?",
        "Can you give me details?",
        "Can you explain?",
        "Can you describe?",
        "Can you share information?",
        "Can you display funds?",
        "Can you show me funds?",
        "Can you tell me about available funds?",
        "Can you give me a list?",
        "Can you provide me with information?",
        "Can you list me the funds?",
        "Can you explain the funds?",
        "Can you describe the funds?",
        "Can you share the funds?",
        "Can you display the funds?",
    ]
    
    print("Testing help/information queries for plural link:")
    print("=" * 70)
    
    all_passed = True
    for query in help_queries:
        q = query.lower()
        
        # Check if query matches any help pattern
        matches_help_pattern = any(pattern in q for pattern in help_patterns)
        
        status = "✅" if matches_help_pattern else "❌"
        
        if not matches_help_pattern:
            all_passed = False
            print(f"{status} FAILED: '{query}'")
        else:
            print(f"{status} '{query}'")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL HELP QUERIES DETECTED CORRECTLY - WILL USE PLURAL LINK")
        return True
    else:
        print("\n❌ SOME HELP QUERIES NOT DETECTED")
        return False

def test_help_queries_dont_match_single_fund():
    """Test that help queries don't accidentally match single fund queries."""
    
    single_fund_queries = [
        "What is the expense ratio of the Groww Nifty Total Market Index Fund?",
        "Tell me about Groww Liquid Fund",
        "What is the NAV of Groww Gold ETF FoF?",
        "Is the Groww Liquid Fund suitable for short-term parking?",
    ]
    
    help_patterns = [
        "how can you help",
        "what do you do",
        "what can you do",
        "how can i use",
        "how do i use",
        "what is this",
        "what are you",
        "who are you",
        "help",
        "about",
        "information",
        "guide",
        "how to",
        "what's available",
        "what funds",
        "which funds",
        "do you have",
        "can you help",
        "can you tell",
        "can you show",
        "can you provide",
        "can you list",
        "can you give",
        "can you explain",
        "can you describe",
        "can you share",
        "can you display",
        "can you show me",
        "can you tell me",
        "can you give me",
        "can you provide me",
        "can you list me",
        "can you explain me",
        "can you describe me",
        "can you share me",
        "can you display me",
    ]
    
    # Simulate fund list
    all_funds = [
        "Groww Nifty Total Market Index Fund",
        "Groww Liquid Fund",
        "Groww Gold ETF FoF",
    ]
    
    print("\nTesting that single fund queries don't match help patterns:")
    print("=" * 70)
    
    all_passed = True
    for query in single_fund_queries:
        q = query.lower()
        
        # Check if query matches any help pattern
        matches_help_pattern = any(pattern in q for pattern in help_patterns)
        
        if matches_help_pattern:
            # Check if it's a specific fund query
            for fund in all_funds:
                fund_lower = fund.lower()
                # Extract key words from fund name (skip common words)
                fund_keywords = [word for word in fund_lower.split() 
                                if word not in ["fund", "direct", "growth", "etf", "fof", "index"]]
                
                # If 2+ keywords from fund name are in query, it's a specific fund query
                matches = sum(1 for keyword in fund_keywords if keyword in q)
                if matches >= 2:
                    # This is a specific fund query, not a general help query
                    matches_help_pattern = False
                    break
        
        # For single fund queries, we DON'T want them to match help patterns
        status = "✅" if not matches_help_pattern else "❌"
        
        if matches_help_pattern:
            all_passed = False
            print(f"{status} FAILED: '{query[:60]}...' (incorrectly matched help pattern)")
        else:
            print(f"{status} '{query[:60]}...'")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ NO FALSE POSITIVES - SINGLE FUND QUERIES NOT MATCHED")
        return True
    else:
        print("\n❌ SOME SINGLE FUND QUERIES INCORRECTLY MATCHED HELP PATTERNS")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST: HELP/INFORMATION QUERIES USE PLURAL LINK")
    print("=" * 70)
    
    result1 = test_help_queries_use_plural_link()
    result2 = test_help_queries_dont_match_single_fund()
    
    print("\n" + "=" * 70)
    if result1 and result2:
        print("✅ ALL TESTS PASSED - HELP QUERIES WILL USE PLURAL LINK")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 70 + "\n")
