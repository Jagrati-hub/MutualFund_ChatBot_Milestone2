# Implementation Checklist - NO OVERRIDES

## Status of Each Requirement

### ✅ 1. SOURCE LINK LOGIC (Singular/Plural)
- **Status**: ALREADY IMPLEMENTED
- **Function**: `_should_use_plural_link()` (line 577)
- **Logic**: Determines if plural link should be used based on query context
- **Action**: PRESERVE - Do not modify

### ✅ 2. FUND QUERY WITH ALIAS RESOLUTION
- **Status**: PARTIALLY IMPLEMENTED
- **Function**: `resolve_fund_name()` (line 128) - NEWLY ADDED
- **Mapping**: `FUND_NAME_ALIASES` (line 70) - NEWLY ADDED
- **Action**: PRESERVE - Already added without overriding

### ✅ 3. SCOPE: GROWW MUTUAL FUNDS ONLY
- **Status**: PARTIALLY IMPLEMENTED
- **Function**: `validate_query()` (line 217) - Existing guardrail
- **Enhancement**: Added scope check in `answer()` function
- **Action**: PRESERVE - Scope check added without overriding existing validation

### ✅ 4. CATEGORY-WISE QUERY LOGIC
- **Status**: ALREADY IMPLEMENTED
- **Function**: `_handle_category_query()` (line 760)
- **Function**: `_handle_category_attribute_query()` (line 1047)
- **Action**: PRESERVE - Do not modify

### ✅ 5. "AS OF" DATE ON EVERY ANSWER
- **Status**: IMPLEMENTED
- **Added to**: 
  - `answer()` function - appends date to formatted answer
  - `_handle_category_attribute_query()` - appends date to category-attribute results
  - `_handle_category_query()` - appends date to category listing results
- **Format**: "as of DD-MM-YYYY"
- **Action**: PRESERVE - Already added to all answer paths

### 6. ✅ SCHEDULER: ONLY 33 GROWW AMC PAGES (32 SCHEMES + 1 OVERVIEW)
- **Status**: ALREADY CONFIGURED
- **File**: `phases/phase-0-foundation/config/sources.json`
- **Count**: 32 Groww AMC mutual fund schemes + 1 Groww AMC overview page = 33 total
- **Scraper**: `phases/phase-1-collection/src/scraper.py`
- **Action**: VERIFY - Config is correct, scraper loads from config

## EXISTING LOGIC PRESERVED
1. ✅ Web link removal from answers - `format_answer()` function
2. ✅ NAV retrieval with multiple query variations - `_query_fund_attribute()` function
3. ✅ Response time optimization - 3 workers, 15s timeout in `_handle_category_attribute_query()`
4. ✅ Plural link logic for citations - `_should_use_plural_link()` function
5. ✅ Category-attribute query handling - `_handle_category_attribute_query()` function
6. ✅ Cache management for fund attributes - `_get_cached_attribute()`, `_cache_attribute()`
7. ✅ Gemini API key rotation - `_switch_gemini_key()`, `_get_current_gemini_key()`
8. ✅ Groq fallback LLM - `_get_available_llms()` function

## VERIFICATION NEEDED
- [ ] Test fund alias resolution: "liquid", "gold etf", "elss", "silver etf"
- [ ] Test category queries: "equity funds", "debt category", "hybrid", "commodities"
- [ ] Test date appending: All answers should show "as of DD-MM-YYYY"
- [ ] Test singular/plural link logic
- [ ] Test scope enforcement: Non-Groww queries should be rejected
- [ ] Verify scraper only collects 32 Groww AMC schemes

## SUMMARY
All requirements are either already implemented or have been added WITHOUT overriding existing logic.
The system is designed to preserve all working functionality while enhancing with new features.
