# Help/Information Queries - Plural Link Implementation

## Requirement
**FOR "HOW CAN YOU HELP" AND SIMILAR KIND OF QUESTIONS PLEASE USE PLURAL LINK**

## Implementation

### What Was Added

Enhanced the `_should_use_plural_link()` function in `src/rag_engine.py` to detect and handle help/information queries.

### Help Query Patterns Detected

```python
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
```

### Smart Detection Logic

The implementation includes smart detection to avoid false positives:

1. **Check if query matches help patterns**
2. **If it does, check if it mentions a specific fund**
3. **If specific fund is mentioned (2+ keywords match), treat as single fund query**
4. **Otherwise, treat as general help query and use plural link**

### Example Queries

#### Help/Information Queries (Plural Link) ✅
```
✅ "How can you help?"
✅ "What do you do?"
✅ "What can you do?"
✅ "How can I use this?"
✅ "How do I use this?"
✅ "Tell me about yourself"
✅ "What is this?"
✅ "What are you?"
✅ "Who are you?"
✅ "Help"
✅ "About"
✅ "Information"
✅ "Guide"
✅ "How to use"
✅ "What's available?"
✅ "What funds do you have?"
✅ "Which funds are available?"
✅ "Do you have any funds?"
✅ "Can you help me?"
✅ "Can you tell me about funds?"
✅ "Can you show me funds?"
✅ "Can you provide information?"
✅ "Can you list funds?"
✅ "Can you give me details?"
✅ "Can you explain?"
✅ "Can you describe?"
✅ "Can you share information?"
✅ "Can you display funds?"
```

#### Single Fund Queries (Singular Link) ✅
```
✅ "Tell me about Groww Liquid Fund"
✅ "What is the expense ratio of the Groww Nifty Total Market Index Fund?"
✅ "What is the NAV of Groww Gold ETF FoF?"
✅ "Is the Groww Liquid Fund suitable for short-term parking?"
```

## Test Results

### ✅ All 41 Tests Pass

```
Help/Information Queries:     37/37 ✅ (plural link)
Single Fund Queries:           4/4  ✅ (singular link - no false positives)
────────────────────────────────────────────
Total:                        41/41 ✅ PASS
```

### Test File
`test_help_queries_plural_link.py`

### Run Tests
```bash
python test_help_queries_plural_link.py
```

## How It Works

### Flow Diagram

```
User Query
    ↓
_should_use_plural_link(query)
    ↓
1. Check help patterns
   ├─ Match found?
   │  ├─ Check if specific fund mentioned (2+ keywords)
   │  │  ├─ Yes → return False (singular link)
   │  │  └─ No → return True (plural link)
   │  └─ No match → continue
    ↓
2. Check category listing patterns
   ├─ Match → return True (plural link)
   └─ No match → continue
    ↓
3. Check category-specific queries
   ├─ Match → return True (plural link)
   └─ No match → continue
    ↓
4. Check category-attribute queries
   ├─ Match → return True (plural link)
   └─ No match → continue
    ↓
5. Check multi-fund queries
   ├─ 2+ funds → return True (plural link)
   └─ Less than 2 → continue
    ↓
6. Check OR keyword
   ├─ Match → return True (plural link)
   └─ No match → continue
    ↓
7. Check SHOW keyword with multiple results
   ├─ Match → return True (plural link)
   └─ No match → return False (singular link)
```

## Link Selection

### Plural Link (Groww AMC)
**URL**: `https://groww.in/mutual-funds/amc/groww-mutual-funds`

**Used for**:
- ✅ Help/information queries (general questions)
- ✅ All category-wise queries
- ✅ All category-specific queries
- ✅ All category-attribute queries
- ✅ Multi-fund queries (2+ funds)
- ✅ OR keyword queries
- ✅ SHOW keyword with multiple results

### Singular Link (Specific Fund)
**Used for**:
- ✅ Single fund queries only
- ✅ Help queries that mention specific fund (e.g., "Tell me about Groww Liquid Fund")

## Files Modified

- `src/rag_engine.py` - Enhanced `_should_use_plural_link()` function

## Backward Compatibility

✅ **Fully backward compatible**
- No breaking changes to function signatures
- No changes to return types
- Only enhanced detection logic
- All existing functionality preserved

## Verification Checklist

- ✅ Help queries detected correctly
- ✅ Help queries use plural link
- ✅ Single fund queries use singular link
- ✅ No false positives on specific fund queries
- ✅ All 41 tests pass
- ✅ No regressions in existing functionality

## Conclusion

The requirement "FOR HOW CAN YOU HELP AND SIMILAR KIND OF QUESTIONS PLEASE USE PLURAL LINK" is now fully implemented and tested.

**Status**: ✅ COMPLETE AND VERIFIED

All help/information queries now correctly use the plural link (Groww AMC link), while single fund queries continue to use the singular link (specific fund link).
