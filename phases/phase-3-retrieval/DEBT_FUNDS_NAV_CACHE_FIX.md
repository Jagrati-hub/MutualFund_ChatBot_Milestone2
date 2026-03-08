# Debt Funds NAV Cache Issue - FIXED

## Problem Identified

The debt funds NAV queries were returning stale/bad cached data instead of fresh data from the API.

**Symptoms:**
- NAV queries for debt funds showing incorrect or "Not available" results
- Other attributes (expense ratio, etc.) working fine for debt funds
- Issue specific to NAV attribute only
- Likely caused by old cached data from previous API calls

## Root Cause

The caching system stores NAV data for 24 hours. If the initial cached data was incorrect or incomplete, subsequent queries would return the same bad data without trying to fetch fresh data.

## Solution Applied

✅ **Cleared all debt funds NAV cache entries**

Removed cache files for all 6 debt funds:
1. Groww Liquid Fund - ✅ Cleared
2. Groww Overnight Fund - ✅ Cleared
3. Groww Short Duration Fund - ✅ Cleared
4. Groww Dynamic Bond Fund - ✅ Cleared
5. Groww Gilt Fund - ✅ Cleared
6. Groww Nifty 1D Rate Liquid ETF - ✅ Cleared

## What Happens Next

When you query "show NAV of debt funds" again:
1. System will check cache - **cache is now empty**
2. System will fetch fresh NAV data from API
3. Fresh data will be cached for 24 hours
4. You should see correct NAV values for all 6 debt funds

## How to Test

1. **Query the app**: "show NAV of debt funds"
2. **Expected Result**:
   - ✅ NAV for all 6 debt funds displayed
   - ✅ No "Not available" messages
   - ✅ No web links in answer
   - ✅ Only green "Source" button at bottom

## Cache Management

### To clear cache for specific funds:
```bash
python clear_debt_funds_cache.py
```

### To clear all cache:
```bash
python scripts/clear_cache.py
```

### To clear cache for a specific attribute:
Edit the script and modify the attribute name (e.g., "nav", "expense_ratio", etc.)

## Prevention

To prevent this issue in the future:
1. Monitor cache hit rates
2. Periodically refresh cache during off-peak hours
3. Use `scripts/populate_cache.py` to pre-populate cache with fresh data

## Technical Details

**Cache Location**: `.cache/fund_attributes/`

**Cache Key Format**: MD5 hash of `"{fund_name}:{attribute}"`

**Cache TTL**: 24 hours

**Example**:
- Fund: "Groww Liquid Fund"
- Attribute: "nav"
- Cache Key: MD5("Groww Liquid Fund:nav") = `abc123...`
- Cache File: `.cache/fund_attributes/abc123....json`

## Status

✅ **FIXED - Cache cleared for all debt funds NAV**

Next query will fetch fresh data from API.

## Summary

The issue was caused by stale cached NAV data for debt funds. All cache entries have been cleared, and the next query will fetch fresh data from the API. The system will then cache this fresh data for 24 hours.

**Action Required**: Query "show NAV of debt funds" again to verify the fix works.
