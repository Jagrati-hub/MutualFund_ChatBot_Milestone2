# Complete Feature Documentation - Groww Mutual Fund FAQ Assistant

## Overview
The Groww Mutual Fund FAQ Assistant is a facts-only chatbot that provides information about 32 Groww AMC mutual fund schemes across 4 categories: Equity, Debt, Hybrid, and Commodities.

## Core Features

### 1. Fund Name Alias Resolution
**Purpose**: Allow users to query funds using short names instead of full names

**Supported Aliases**:
```
Equity Funds:
- "nifty total market" → Groww Nifty Total Market Index Fund
- "multicap" → Groww Multicap Fund
- "small cap" → Groww Small Cap Fund
- "large cap" → Groww Large Cap Fund
- "value" → Groww Value Fund
- "elss" / "tax saver" → Groww ELSS Tax Saver Fund
- "banking" → Groww Banking & Financial Services Fund
- "nifty smallcap 250" → Groww Nifty Smallcap 250 Index Fund
- "nifty non-cyclical" → Groww Nifty Non-Cyclical Consumer Index Fund
- "nifty next 50" → Groww Nifty Next 50 Index Fund
- "nifty midcap 150" → Groww Nifty Midcap 150 Index Fund
- "ev automotive" → Groww Nifty EV & New Age Automotive ETF FoF
- "defence" → Groww Nifty India Defence ETF FoF
- "nifty 200" → Groww Nifty 200 ETF FoF
- "nifty 500 momentum" → Groww Nifty 500 Momentum 50 ETF FoF
- "internet" → Groww Nifty India Internet ETF FoF
- "railways" → Groww Nifty India Railways PSU Index Fund
- "psu" → Groww Nifty PSE ETF FoF
- "power" → Groww BSE Power ETF FoF
- "capital markets" → Groww Nifty Capital Markets ETF FoF
- "arbitrage" → Groww Arbitrage Fund

Debt Funds:
- "liquid" → Groww Liquid Fund
- "overnight" → Groww Overnight Fund
- "short duration" → Groww Short Duration Fund
- "dynamic bond" → Groww Dynamic Bond Fund
- "gilt" → Groww Gilt Fund
- "nifty 1d rate" → Groww Nifty 1D Rate Liquid ETF

Hybrid Funds:
- "aggressive hybrid" → Groww Aggressive Hybrid Fund
- "multi asset allocation" → Groww Multi Asset Allocation Fund
- "multi asset omni" → Groww Multi Asset Omni FoF

Commodities:
- "gold etf" / "gold" → Groww Gold ETF FoF
- "silver etf" / "silver" → Groww Silver ETF FoF
```

**Implementation**: `resolve_fund_name()` function in `rag_engine.py`

### 2. Singular/Plural Link Logic
**Purpose**: Show appropriate source link based on query type

**Rules**:
- **Singular Query** (specific fund): Show ONE "Source" button linking to that fund's official page
- **Plural/Category Query** (multiple funds): Show ONE "Source" button linking to Groww AMC overview page

**Implementation**: `_should_use_plural_link()` function

**Example**:
- Query: "What is NAV of Groww Liquid Fund?" → Link to Groww Liquid Fund page
- Query: "Show NAV of all debt funds" → Link to Groww AMC overview page

### 3. Category-Wise Query Handling
**Purpose**: Support queries about fund categories

**Supported Categories**:
- Equity (21 funds)
- Debt (6 funds)
- Hybrid (3 funds)
- Commodities (2 funds)

**Query Examples**:
- "Show all equity funds"
- "List debt category funds"
- "How many hybrid funds?"
- "What are commodities funds?"

**Implementation**: `_handle_category_query()` function

### 4. Category-Attribute Query Handling
**Purpose**: Support queries like "NAV of equity funds" or "expense ratio of debt funds"

**Supported Attributes**:
- NAV (Net Asset Value)
- Expense Ratio
- Exit Load
- Returns
- AUM (Assets Under Management)
- Minimum Investment
- Fund Manager

**Query Examples**:
- "NAV of equity funds"
- "Expense ratio of debt funds"
- "Exit load for hybrid funds"
- "Fund managers of commodities"

**Implementation**: `_handle_category_attribute_query()` function

### 5. Data Date Display
**Purpose**: Show users when the data was last updated

**Format**: "as of DD-MM-YYYY"

**Applied To**:
- All fund queries
- All category queries
- All category-attribute queries

**Example Answers**:
- "The expense ratio of the Groww Nifty Total Market Index Fund is 0.06% as of 08-03-2026"
- "Here are the 21 Equity funds offered by Groww AMC: ... as of 08-03-2026"

**Implementation**: Date appending in `answer()`, `_handle_category_query()`, and `_handle_category_attribute_query()` functions

### 6. Scope Enforcement
**Purpose**: Keep assistant focused on Groww AMC mutual funds only

**Behavior**:
- Accepts queries about Groww AMC funds
- Rejects queries about other fund companies
- Rejects non-financial queries
- Rejects investment advice requests

**Implementation**: Scope check in `answer()` function

### 7. Web Link Removal
**Purpose**: Clean answers by removing web links

**Behavior**:
- Removes inline URLs
- Removes markdown links
- Removes parenthetical links
- Keeps only the answer text

**Implementation**: `format_answer()` function

### 8. Response Time Optimization
**Purpose**: Provide fast responses for category-attribute queries

**Optimization**:
- 3 parallel workers (reduced from 10)
- 15-second overall timeout
- 10-second per-fund timeout
- Expected response time: 8-12 seconds for category queries

**Implementation**: ThreadPoolExecutor in `_handle_category_attribute_query()` function

### 9. API Key Rotation
**Purpose**: Handle Gemini API quota limits

**Behavior**:
- Supports up to 9 Gemini API keys
- Automatically switches to next key on quota error
- Falls back to Groq API if all Gemini keys exhausted

**Implementation**: `_switch_gemini_key()`, `_get_current_gemini_key()` functions

### 10. Cache Management
**Purpose**: Speed up repeated queries for fund attributes

**Behavior**:
- Caches fund attribute values (NAV, expense ratio, etc.)
- Cache expires after 24 hours
- Automatically refreshes expired cache

**Implementation**: `_get_cached_attribute()`, `_cache_attribute()` functions

## Data Sources

### Configuration
- **File**: `phases/phase-0-foundation/config/sources.json`
- **Contains**: 32 Groww AMC schemes (1 overview + 31 funds)
- **Scope**: ONLY Groww AMC official pages

### Scraper
- **File**: `phases/phase-1-collection/src/scraper.py`
- **Behavior**: Loads sources from config, scrapes only enabled sources
- **Frequency**: Daily (via APScheduler)
- **Data Storage**: `phases/phase-2-processing/data/raw/`

### Vector Store
- **Type**: ChromaDB
- **Location**: `phases/phase-2-processing/chroma/`
- **Collection**: "groww_mf_faq"
- **Embeddings**: Google Gemini Embeddings

## Query Processing Flow

```
User Query
    ↓
[1] Validate Query (guardrails check)
    ↓
[2] Check Scope (Groww-related keywords)
    ↓
[3] Resolve Fund Name Aliases
    ↓
[4] Check for Category-Attribute Query
    ├─ YES → Handle with parallel workers → Append date → Return
    └─ NO → Continue
    ↓
[5] Check for Category Query
    ├─ YES → Handle category listing/count → Append date → Return
    └─ NO → Continue
    ↓
[6] Retrieve from Vector Store
    ↓
[7] Determine Link Type (singular/plural)
    ↓
[8] Build RAG Chain
    ↓
[9] Generate Answer
    ↓
[10] Format Answer (remove links)
    ↓
[11] Append Data Date
    ↓
[12] Return with Citation Link
```

## File Structure

```
phases/
├── phase-0-foundation/
│   ├── config/sources.json (32 Groww AMC schemes)
│   ├── system_prompt.md (guardrails)
│   ├── requirements.txt
│   └── .env (API keys)
├── phase-1-collection/
│   └── src/scraper.py (web scraper)
├── phase-2-processing/
│   ├── src/ingest.py (data ingestion)
│   ├── data/raw/ (scraped data)
│   └── chroma/ (vector store)
├── phase-3-retrieval/
│   └── src/rag_engine.py (RAG logic)
├── phase-4-orchestration/
│   └── src/scheduler.py (APScheduler)
└── phase-5-frontend/
    ├── app.py (main chat interface)
    └── admin.py (admin dashboard)
```

## Testing

### Test Queries
1. **Alias Resolution**: "What is the NAV of liquid fund?"
2. **Category Query**: "Show all equity funds"
3. **Category-Attribute**: "Expense ratio of debt funds"
4. **Singular Link**: "Tell me about Groww Liquid Fund"
5. **Plural Link**: "List all hybrid funds"
6. **Date Display**: Any query should show "as of DD-MM-YYYY"
7. **Scope Enforcement**: "What is Bitcoin?" should be rejected

### Expected Results
- All answers should include "as of DD-MM-YYYY"
- Singular queries should link to fund page
- Plural queries should link to Groww AMC overview
- Alias queries should resolve to full fund names
- Out-of-scope queries should be rejected

## Deployment

### Local Development
```bash
streamlit run phases/phase-5-frontend/app.py
```

### Production (Streamlit Cloud)
- Requires `.streamlit/config.toml` with theme settings
- Requires `packages.txt` for system dependencies
- Requires `.env` file with API keys

## Maintenance

### Adding New Funds
1. Add fund to `phases/phase-0-foundation/config/sources.json`
2. Add alias to `FUND_NAME_ALIASES` in `rag_engine.py`
3. Update `SCOPE_FUNDS_BY_CATEGORY` in `shared.py`
4. Run scraper to collect data

### Updating Aliases
- Edit `FUND_NAME_ALIASES` in `phases/phase-3-retrieval/src/rag_engine.py`
- No restart needed (aliases loaded on each query)

### Clearing Cache
- Run: `python phases/phase-2-processing/clear_debt_funds_cache.py`
- Or delete `.cache/fund_attributes/` directory

## Performance Metrics

- **Single Fund Query**: 2-3 seconds
- **Category Query**: 8-12 seconds
- **Category-Attribute Query**: 8-12 seconds
- **Cache Hit**: <1 second
- **API Calls**: Optimized with key rotation and fallback

## Support

For issues or questions:
1. Check `FINAL_REQUIREMENTS.md` for feature specifications
2. Check `IMPLEMENTATION_CHECKLIST.md` for implementation status
3. Review `PROJECT_SYNC_STATUS.md` for project organization
