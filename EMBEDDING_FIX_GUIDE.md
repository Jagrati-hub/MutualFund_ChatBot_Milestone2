# Quick Fix: Embedding Dimension Mismatch

## Problem
```
⚠️ Retrieval error: Collection expecting embedding with dimension of 384, got 3072
```

This happens because the old Chroma collection was created with a different embedding model.

## Solution

### Step 1: Stop the Streamlit App
Close the running app (Ctrl+C in terminal)

### Step 2: Clear Chroma Database
```bash
cd phases/phase-2-processing
python clear_chroma.py
```

### Step 3: Run Scraper & Ingestor
```bash
# From project root
cd phases/phase-1-collection
python -m src.scraper

cd ../phase-2-processing
python -m src.ingest
```

### Step 4: Restart App
```bash
cd ../phase-5-frontend
streamlit run app.py
```

## What Was Fixed

### 1. Scraper Improvements
- **Before**: Extracted all HTML sections with random class names
- **After**: Extracts only business-relevant text with keyword filtering
- **Keywords**: nav, expense, return, aum, exit load, minimum, investment, objective, risk, fund manager, benchmark, allocation, holdings

### 2. JSON Structure
**Before:**
```json
{
  "fund_name": "...",
  "unknown_class_1": "random text...",
  "unknown_class_2": "more random text..."
}
```

**After:**
```json
{
  "fund_name": "Groww Liquid Fund",
  "url": "https://...",
  "category": "Debt",
  "scraped_at": "2024-03-08T...",
  "content": "NAV: ₹1234.56\nExpense Ratio: 0.25%\n..."
}
```

### 3. Ingestor Simplification
Now only uses the `content` field which contains filtered, relevant text.

## Verification

After restarting, test with:
- "What is the NAV of Liquid Fund?"
- "What is the expense ratio of ELSS?"

Should work without errors! ✅
