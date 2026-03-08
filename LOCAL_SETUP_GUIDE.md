# Local Setup Guide - Groww Mutual Fund FAQ Assistant

## Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

## Step 1: Clone/Navigate to Project Directory
```bash
cd /path/to/MutualFund_ChatBot_Milestone2
```

## Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install -r phases/phase-0-foundation/requirements.txt
```

## Step 4: Verify .env Configuration
The `.env` file is already configured with:
- ✅ GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3 (3 valid keys)
- ✅ GROQ_API_KEY (fallback)
- ✅ GITHUB_API_KEY (for scraping)

Location: `phases/phase-0-foundation/.env`

## Step 5: Run the Streamlit App
```bash
streamlit run phases/phase-5-frontend/app.py
```

This will:
- Start the Streamlit server (usually on http://localhost:8501)
- Automatically start the background scheduler
- Load the Chroma vector database
- Initialize the RAG engine with Gemini Flash 2.0

## Step 6: Access the Application
Open your browser and navigate to:
```
http://localhost:8501
```

You should see:
- Hero section: "Groww Mutual Fund FAQ"
- Quick Start section with 3 example queries
- Chat input box at the bottom

## Testing the System

### Test 1: Fund-Specific Query
```
Query: "What is the NAV of Groww Liquid Fund?"
Expected: Specific fund information with source link and date
```

### Test 2: Category Query
```
Query: "segregate by category"
Expected: All 32 funds organized by category (21 Equity, 6 Debt, 3 Hybrid, 2 Commodities)
```

### Test 3: Alias Resolution
```
Query: "What is the expense ratio of gold etf?"
Expected: Information about Groww Gold ETF FoF with date appended
```

### Test 4: Guardrails
```
Query: "Should I buy Groww Small Cap Fund?"
Expected: Blocked - "I am a facts-only assistant and cannot provide financial advice."
```

## Troubleshooting

### Issue: "No module named 'streamlit'"
**Solution:**
```bash
pip install streamlit
```

### Issue: "Chroma database not found"
**Solution:** The database is pre-populated. If missing, run:
```bash
python phases/phase-2-processing/populate_cache.py
```

### Issue: "API Key exhausted" errors
**Solution:** The system automatically cycles through 3 Gemini Flash keys. If all are exhausted, it falls back to Groq.

### Issue: Port 8501 already in use
**Solution:**
```bash
streamlit run phases/phase-5-frontend/app.py --server.port 8502
```

## Project Structure
```
phases/
├── phase-0-foundation/     # Config, .env, system prompts
├── phase-1-collection/     # Web scraper
├── phase-2-processing/     # Data ingestion, Chroma DB
├── phase-3-retrieval/      # RAG engine (Gemini Flash 2.0)
├── phase-4-orchestration/  # Scheduler
└── phase-5-frontend/       # Streamlit app
```

## Key Features
✅ Gemini Flash 2.0 for fast responses
✅ Multi-model fallback (3 Gemini keys + Groq + OpenAI)
✅ 32 Groww AMC mutual funds
✅ Category-wise organization
✅ Fund alias resolution
✅ Date appending to all responses
✅ PII and advice guardrails
✅ Real-time data access

## Next Steps
1. Run the app: `streamlit run phases/phase-5-frontend/app.py`
2. Try the example queries
3. Ask custom questions about Groww funds
4. Check the admin panel for scheduler status

## Support
For issues, check:
- `phases/phase-3-retrieval/src/rag_engine.py` - RAG logic
- `phases/phase-5-frontend/app.py` - UI logic
- `.kiro/specs/mutual-fund-category-consistency/` - Spec documentation
