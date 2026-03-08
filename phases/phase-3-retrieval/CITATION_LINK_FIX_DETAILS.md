# Citation Link Fix - Detailed Technical Documentation

## Problem Statement

When users asked single-fund queries like "What is the expense ratio of the Groww Nifty Total Market Index Fund?", the system was incorrectly using the plural link (Groww AMC link) instead of the singular link (specific fund link).

### Root Cause Analysis

The issue was in the `_count_explicit_funds_in_query()` function in `src/rag_engine.py`.

**Problem**: The function was matching generic fund name parts against multiple funds:
- Query: "What is the expense ratio of the Groww Nifty Total Market Index Fund?"
- The function extracted "nifty total market" (last 3 words)
- This pattern matched MULTIPLE funds:
  - "Groww Nifty Total Market Index Fund" ✓
  - "Groww Nifty 500 Momentum 50 ETF FoF" (contains "nifty") ✓
  - "Groww Nifty Smallcap 250 Index Fund" (contains "nifty") ✓
  - And other Nifty-based funds...
- Result: Function returned count > 1, triggering plural link logic

### Impact

- Single fund queries incorrectly used plural link
- Users saw generic Groww AMC link instead of specific fund link
- Inconsistent user experience

---

## Solution Implementation

### File Modified: `src/rag_engine.py`

**Function**: `_count_explicit_funds_in_query()` (Line 418)

### Changes Made

#### 1. Added Generic Pattern Exclusion List

```python
# Generic patterns that should NOT trigger multi-fund matching
# These are common fund name suffixes that appear in many funds
generic_patterns = [
    "index fund", "etf fof", "total market", "nifty", "fund",
    "hybrid fund", "bond fund", "liquid fund", "asset allocation"
]
```

**Rationale**: These patterns appear in multiple funds and should not be used for fund counting.

#### 2. Updated Matching Logic

**Before**:
```python
# Check last 3 words (e.g., "nifty total market")
if len(parts) >= 3:
    key_part = " ".join(parts[-3:])
    if key_part in q:
        matched_funds.add(fund)
        continue
```

**After**:
```python
# Check last 3 words (e.g., "nifty total market")
# BUT: Skip if it's a generic pattern that appears in many funds
if len(parts) >= 3:
    key_part = " ".join(parts[-3:])
    if key_part not in generic_patterns and key_part in q:
        matched_funds.add(fund)
        continue
```

**Applied to both 2-word and 3-word matching patterns**

### How It Works Now

#### Example 1: Single Fund Query
```
Query: "What is the expense ratio of the Groww Nifty Total Market Index Fund?"

Step 1: Extract fund name parts
  - Fund: "Groww Nifty Total Market Index Fund"
  - Parts: ["groww", "nifty", "total", "market", "index", "fund"]

Step 2: Try exact match
  - Full fund name in query? YES ✓
  - Add to matched_funds

Step 3: Check 2-word patterns
  - "index fund" in generic_patterns? YES → SKIP
  - "market index" in generic_patterns? NO → Check if in query
  - "market index" in query? NO → Don't match

Step 4: Check 3-word patterns
  - "total market index" in generic_patterns? NO → Check if in query
  - "total market index" in query? NO → Don't match

Result: matched_funds = {1 fund}
Link Type: SINGULAR ✓
```

#### Example 2: Multi-Fund Query
```
Query: "Compare Groww Gold ETF FoF and Groww Silver ETF FoF"

Step 1: Check "Groww Gold ETF FoF"
  - Exact match? YES ✓
  - Add to matched_funds

Step 2: Check "Groww Silver ETF FoF"
  - Exact match? YES ✓
  - Add to matched_funds

Result: matched_funds = {2 funds}
Link Type: PLURAL ✓
```

#### Example 3: Generic Pattern Query
```
Query: "What is the NAV of Groww Nifty 500 Momentum 50 ETF FoF?"

Step 1: Extract fund name parts
  - Fund: "Groww Nifty 500 Momentum 50 ETF FoF"
  - Parts: ["groww", "nifty", "500", "momentum", "50", "etf", "fof"]

Step 2: Try exact match
  - Full fund name in query? YES ✓
  - Add to matched_funds

Step 3: Check 2-word patterns
  - "etf fof" in generic_patterns? YES → SKIP
  - "50 etf" in generic_patterns? NO → Check if in query
  - "50 etf" in query? NO → Don't match

Step 4: Check 3-word patterns
  - "50 etf fof" in generic_patterns? NO → Check if in query
  - "50 etf fof" in query? NO → Don't match

Result: matched_funds = {1 fund}
Link Type: SINGULAR ✓
```

---

## Testing

### Test Cases Verified

#### Single-Fund Queries (Should Use Singular Link)
✅ "What is the expense ratio of the Groww Nifty Total Market Index Fund?"
✅ "Tell me about Groww Liquid Fund"
✅ "Show me the exit load of Groww Aggressive Hybrid Fund"

#### Multi-Fund Queries (Should Use Plural Link)
✅ "Compare Groww Gold ETF FoF and Groww Silver ETF FoF"
✅ "Show me Groww Liquid Fund and Groww Overnight Fund"
✅ "What are the differences between Groww Large Cap Fund and Groww Small Cap Fund?"

#### OR Keyword Queries (Should Use Plural Link)
✅ "Show me Groww Gold ETF FoF or Groww Silver ETF FoF"
✅ "What is the NAV of Groww Liquid Fund or Groww Overnight Fund?"

#### SHOW Keyword Queries (Should Use Plural Link)
✅ "Show me all equity funds" (with multiple results)

### Test Files
- `test_citation_link_fix.py` - Comprehensive citation link tests
- `test_or_show_logic.py` - OR/SHOW keyword tests
- `test_comprehensive_final.py` - All features integration test

**All tests pass ✅**

---

## Link Selection Logic

### When to Use Singular Link
1. User explicitly asks for ONE specific fund
2. `_count_explicit_funds_in_query()` returns 1
3. `_should_use_plural_link()` returns False

**Example**: "What is the expense ratio of the Groww Nifty Total Market Index Fund?"
**Link**: Specific fund page on Groww website

### When to Use Plural Link
1. User asks for multiple funds explicitly (2+ fund names)
2. User uses "OR" keyword with fund names
3. User uses "SHOW" keyword with multiple results
4. User asks for category-wise listing
5. User asks for category-attribute query

**Example**: "Compare Groww Gold ETF FoF and Groww Silver ETF FoF"
**Link**: `https://groww.in/mutual-funds/amc/groww-mutual-funds`

---

## Code Flow Diagram

```
User Query
    ↓
_should_use_plural_link(query)
    ↓
_count_explicit_funds_in_query(query)
    ↓
For each fund in SCOPE_FUNDS:
    ├─ Try exact match (highest priority)
    │  └─ If match: add to matched_funds, continue
    ├─ Try 2-word pattern
    │  ├─ Extract last 2 words
    │  ├─ Check if in generic_patterns → SKIP if yes
    │  └─ If match: add to matched_funds, continue
    ├─ Try 3-word pattern
    │  ├─ Extract last 3 words
    │  ├─ Check if in generic_patterns → SKIP if yes
    │  └─ If match: add to matched_funds, continue
    └─ Try unique keywords (gold, silver, arbitrage)
       └─ If match: add to matched_funds, break
    ↓
Return len(matched_funds)
    ↓
If count >= 2: use_plural = True
Else: use_plural = False
    ↓
Select appropriate link
    ├─ If use_plural: https://groww.in/mutual-funds/amc/groww-mutual-funds
    └─ Else: specific fund link from metadata
```

---

## Performance Impact

- **Minimal**: Added one list check per pattern match
- **Negligible**: Generic patterns list is small (9 items)
- **Benefit**: Eliminates false positives, improves accuracy

---

## Backward Compatibility

✅ **Fully backward compatible**
- Exact match logic unchanged
- Unique keyword logic unchanged
- Only added exclusion check for generic patterns
- No breaking changes to function signature or return type

---

## Future Improvements

1. **Dynamic Pattern Learning**: Learn generic patterns from fund names automatically
2. **Fuzzy Matching**: Use fuzzy matching for typos and variations
3. **Context-Aware Matching**: Consider query context for better disambiguation
4. **User Feedback Loop**: Learn from user corrections to improve matching

---

## Conclusion

The citation link fix successfully resolves the issue of single-fund queries using plural links. The solution is:
- ✅ Simple and maintainable
- ✅ Fully tested
- ✅ Backward compatible
- ✅ Performant
- ✅ Ready for production

All tests pass and the system is ready for deployment.
