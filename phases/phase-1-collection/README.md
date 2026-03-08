# Phase 1: Collection (Stealth Scraper)

## Purpose
Web scraping of official Groww pages using stealth Playwright to collect HTML and PDF content.

## Files in This Phase

### Core Module
- `src/scraper.py` - Stealth Playwright scraper with anti-bot heuristics

### Utilities
- `scripts/` - Helper scripts for scraping

### Test Files
- `test_*.py` - Tests related to scraper functionality

## Key Responsibilities
1. Load enabled sources from `config/sources.json`
2. Launch Playwright in stealth mode
3. Capture HTML snapshots
4. Download associated PDFs
5. Generate `manifest.json` with metadata

## Output
- `data/raw/<YYYY-MM-DD>/` - Scraped HTML/PDF files
- `data/raw/<YYYY-MM-DD>/manifest.json` - Metadata describing artifacts

## Status
✅ Complete - Scraper fully functional with stealth mode
