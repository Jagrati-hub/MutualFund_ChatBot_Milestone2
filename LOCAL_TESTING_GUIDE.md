# Local Testing Guide - Groww Mutual Fund FAQ Assistant

## ✅ App is Running!

The Streamlit app is now running on your local machine.

### Access the App

**Local URL**: http://localhost:8502

Open this URL in your web browser to access the application.

---

## Test Scenarios

### Test 1: Category-Wise Query (Should Show Plural Link)

**Query**: "category wise listing"

**Expected Result**:
- ✅ Shows all 32 funds organized by category
- ✅ Green "Source" button at bottom with Groww AMC link
- ✅ NO inline links in answer text

---

### Test 2: Category-Specific Query (Should Show Plural Link)

**Query**: "list all equity funds"

**Expected Result**:
- ✅ Shows all 21 equity funds
- ✅ Green "Source" button at bottom with Groww AMC link
- ✅ NO inline links in answer text

---

### Test 3: Category-Attribute Query (Should Show Plural Link)

**Query**: "show NAV of commodities funds"

**Expected Result**:
- ✅ Shows NAV for both commodity funds (Gold ETF FoF, Silver ETF FoF)
- ✅ Green "Source" button at bottom with Groww AMC link
- ✅ Fast response (cached results)
- ✅ NO inline links in answer text

---

### Test 4: Single Fund Query (Should Show Singular Link)

**Query**: "What is the expense ratio of the Groww Liquid Fund?"

**Expected Result**:
- ✅ Shows expense ratio for Groww Liquid Fund
- ✅ Green "Source" button at bottom with specific fund link
- ✅ NO inline links in answer text

---

### Test 5: Multi-Fund Query (Should Show Plural Link)

**Query**: "Compare Groww Gold ETF FoF and Groww Silver ETF FoF"

**Expected Result**:
- ✅ Shows comparison of both funds
- ✅ Green "Source" button at bottom with Groww AMC link
- ✅ NO inline links in answer text

---

### Test 6: OR Keyword Query (Should Show Plural Link)

**Query**: "Show me Groww Gold ETF FoF or Groww Silver ETF FoF"

**Expected Result**:
- ✅ Shows both funds
- ✅ Green "Source" button at bottom with Groww AMC link
- ✅ NO inline links in answer text

---

## What to Verify

### Citation Link Display
- ✅ Only ONE green "Source" button at bottom of message
- ✅ NO inline links in answer text
- ✅ NO "Source: [...]" text in answer
- ✅ NO web links (http://, https://, www.*) in answer

### Link Type Selection
- ✅ Category-wise queries → Groww AMC link (plural)
- ✅ Single fund queries → Specific fund link (singular)
- ✅ Multi-fund queries → Groww AMC link (plural)
- ✅ OR keyword queries → Groww AMC link (plural)
- ✅ SHOW keyword queries → Groww AMC link (plural)

### Response Quality
- ✅ Answers are factual and concise
- ✅ No filler phrases ("Based on the provided context", etc.)
- ✅ Consistent results on repeated queries
- ✅ Fast responses (especially for cached queries)

---

## Troubleshooting

### Issue: App not loading
**Solution**: 
- Check if port 8502 is available
- Try refreshing the browser
- Check console for errors

### Issue: API quota exhausted
**Solution**:
- System automatically rotates to next API key
- Check logs for key rotation messages
- Wait for quota to reset (24 hours)

### Issue: Slow responses
**Solution**:
- First query for a fund will be slower (API call)
- Subsequent queries will be faster (cached)
- Cache is stored in `.cache/fund_attributes/`

### Issue: Wrong link type
**Solution**:
- Verify query matches expected pattern
- Check logs for link selection reason
- Run test suite: `python test_category_plural_updated.py`

---

## Admin Controls

### Sidebar Options

1. **System Status**
   - Shows if scheduler is active
   - Shows next scheduled update time

2. **Manual Controls**
   - "Run Data Pipeline" button to manually update data
   - Useful for testing data refresh

---

## Quick Test Commands

### Run All Tests
```bash
python test_category_plural_updated.py
```

### Run Specific Test
```bash
python test_citation_link_fix.py
```

### Clear Cache
```bash
python scripts/clear_cache.py
```

### Pre-populate Cache
```bash
python scripts/populate_cache.py
```

---

## Example Queries to Try

### Category-Wise (Plural Link)
- "category wise listing"
- "list all categories"
- "segregate by category"
- "categorize funds"
- "distribution of funds"
- "breakdown by category"

### Category-Specific (Plural Link)
- "list all equity funds"
- "show me all debt funds"
- "what are the hybrid funds?"
- "commodities funds"

### Category-Attribute (Plural Link)
- "show NAV of equity funds"
- "expense ratio of debt funds"
- "exit load for hybrid funds"

### Single Fund (Singular Link)
- "What is the expense ratio of Groww Liquid Fund?"
- "Tell me about Groww Gold ETF FoF"
- "NAV of Groww Nifty Total Market Index Fund?"

### Multi-Fund (Plural Link)
- "Compare Groww Gold ETF FoF and Groww Silver ETF FoF"
- "Show me Groww Liquid Fund and Groww Overnight Fund"

### OR Keyword (Plural Link)
- "Show me Groww Gold ETF FoF or Groww Silver ETF FoF"
- "What is the NAV of Groww Liquid Fund or Groww Overnight Fund?"

---

## Monitoring

### Check Logs
The console shows:
- API key rotation messages
- Link selection reasons
- Query processing details
- Cache hits/misses

### Monitor Cache
```bash
ls -la .cache/fund_attributes/
```

### Check API Usage
- Monitor Gemini API quota in Google Cloud Console
- System rotates keys automatically when quota exhausted

---

## Next Steps

1. ✅ Open http://localhost:8502 in browser
2. ✅ Try the test queries above
3. ✅ Verify citation links appear correctly
4. ✅ Check that only ONE green "Source" button appears
5. ✅ Verify NO inline links in answer text
6. ✅ Test category-wise queries use plural link
7. ✅ Test single fund queries use singular link

---

## Support

For issues or questions:
1. Check `QUICK_REFERENCE.md` for common issues
2. Review `CATEGORY_PLURAL_LINK_FIX.md` for technical details
3. Run test files to verify functionality
4. Check logs for error messages

---

**Status**: 🟢 APP RUNNING AND READY FOR TESTING

**Local URL**: http://localhost:8502

**Process ID**: 5

**Status**: Running
