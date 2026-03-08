# FINAL REQUIREMENTS - Groww Mutual Fund FAQ Assistant

## 1. SOURCE LINK LOGIC (Singular/Plural)
- **Singular query** (specific fund): Show ONE "Source" button linking to that fund's official page
- **Plural/Category query** (multiple funds): Show ONE "Source" button linking to Groww AMC overview page
- Implementation: Already exists in `_should_use_plural_link()` function - PRESERVE

## 2. FUND QUERY WITH ALIAS RESOLUTION
- Accept short names: "liquid", "gold etf", "elss", "silver etf", "small cap", etc.
- Resolve to full Groww AMC fund names automatically
- If complete name not mentioned, use alias mapping
- Implementation: Use `FUND_NAME_ALIASES` mapping - PRESERVE and ENHANCE

## 3. SCOPE: GROWW MUTUAL FUNDS ONLY
- Only show Groww AMC mutual fund details
- If user asks about a fund that Groww has, show Groww's version
- Reject queries outside Groww AMC scope
- Implementation: Scope check in `answer()` function - PRESERVE

## 4. CATEGORY-WISE QUERY LOGIC
- Support queries like: "equity funds", "debt category", "hybrid schemes", "commodities"
- Return all funds in that category with their details
- Implementation: `_handle_category_query()` function - PRESERVE

## 5. "AS OF" DATE ON EVERY ANSWER
- Append "as of DD-MM-YYYY" to every answer
- Format: "The expense ratio is 0.06% as of 08-03-2026"
- Implementation: Already added to all answer paths - PRESERVE

## 6. SCHEDULER: ONLY 33 GROWW AMC PAGES (32 SCHEMES + 1 OVERVIEW)
- Scraper should ONLY collect data for 32 Groww AMC mutual fund schemes
- PLUS 1 Groww AMC official overview page
- Total: 33 page links
- ONLY scrape from Groww AMC official pages
- No other fund data or external sources
- Implementation: Update `scraper.py` to filter by Groww AMC schemes - ENHANCE

## EXISTING LOGIC TO PRESERVE
1. Web link removal from answers
2. NAV retrieval with multiple query variations
3. Response time optimization (3 workers, 15s timeout)
4. Plural link logic for citations
5. Category-attribute query handling
6. Cache management for fund attributes
7. Gemini API key rotation
8. Groq fallback LLM

## IMPLEMENTATION APPROACH
- NO overriding existing functions
- ADD new logic alongside existing code
- ENHANCE existing functions with new features
- PRESERVE all working functionality
