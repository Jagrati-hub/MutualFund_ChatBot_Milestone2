# Groww Mutual Fund FAQ Assistant - Complete Documentation

## Project Overview

A production-ready AI-powered chatbot that provides factual information about 32 Groww AMC mutual fund schemes. Built with Streamlit, LangChain, and Groq LLM.

**Version:** 2.0  
**Last Updated:** March 2024

---

## Features

### Core Capabilities
- ✅ **32 Groww AMC Funds**: Complete coverage across Equity, Debt, Hybrid, and Commodities
- ✅ **Intelligent Q&A**: Powered by Groq Llama 3.1 8B Instant with RAG
- ✅ **Fund Alias Recognition**: Understands short names (e.g., "ELSS", "liquid fund")
- ✅ **Multi-Fund Queries**: Compare multiple funds in single question
- ✅ **Factual Comparisons**: "Which fund has highest NAV?" etc.
- ✅ **Dark Theme UI**: Modern, professional dark interface
- ✅ **Automated Data Updates**: Daily scraping at 10 AM IST
- ✅ **Admin Dashboard**: Separate admin page at `/admin`

### Technical Features
- **Optimized Scraping**: JSON-based storage (90% smaller than HTML)
- **Smart Retrieval**: ChromaDB with MMR search
- **Multi-Model Support**: Groq (primary), OpenAI, Gemini (fallbacks)
- **Guardrails**: Blocks personal advice, allows factual queries
- **Caching**: 24-hour cache for repeated queries

---

## Architecture

### Tech Stack
- **Frontend**: Streamlit 1.x
- **LLM**: Groq Llama 3.1 8B Instant
- **Vector DB**: ChromaDB
- **Embeddings**: Google Gemini Embeddings
- **Scraper**: Playwright + BeautifulSoup4
- **Scheduler**: APScheduler

### Project Structure
```
MutualFund_ChatBot_Milestone2-1/
├── phases/
│   ├── phase-0-foundation/          # Config & system prompt
│   │   ├── .env                     # API keys
│   │   ├── system_prompt.md         # LLM instructions
│   │   └── config/sources.json      # Fund URLs
│   │
│   ├── phase-1-collection/          # Web scraping
│   │   └── src/scraper.py           # Optimized scraper
│   │
│   ├── phase-2-processing/          # Data ingestion
│   │   ├── src/ingest.py            # ChromaDB ingestion
│   │   ├── chroma/                  # Vector database
│   │   └── data/raw/                # Scraped data
│   │
│   ├── phase-3-retrieval/           # RAG engine
│   │   └── src/rag_engine.py        # Query processing
│   │
│   ├── phase-4-orchestration/       # Scheduling
│   │   └── src/scheduler.py         # Daily automation
│   │
│   └── phase-5-frontend/            # UI
│       ├── app.py                   # Main chat interface
│       ├── pages/admin.py           # Admin dashboard
│       └── .streamlit/config.toml   # Theme config
│
├── fix_embedding_error.bat          # Database reset script
└── [Documentation files]
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Windows/Linux/macOS
- API Keys: Groq (required), Gemini/OpenAI (optional)

### Step 1: Install Dependencies
```bash
cd phases/phase-0-foundation
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Configure API Keys
Create `phases/phase-0-foundation/.env`:
```env
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY_1=your_gemini_key_1
GEMINI_API_KEY_2=your_gemini_key_2
GEMINI_API_KEY_3=your_gemini_key_3
OPENAI_API_KEY=your_openai_key (optional)
```

### Step 3: Initial Data Setup
```bash
# Run scraper
cd phases/phase-1-collection
python -m src.scraper

# Run ingestor
cd ../phase-2-processing
python -m src.ingest
```

### Step 4: Launch App
```bash
cd ../phase-5-frontend
streamlit run app.py
```

**Access:**
- Main App: `http://localhost:8501`
- Admin Dashboard: `http://localhost:8501/admin`

---

## Usage Guide

### For Regular Users

#### Asking Questions
```
✅ "What is the NAV of Liquid Fund?"
✅ "What is the expense ratio of ELSS?"
✅ "Which fund has the highest NAV?"
✅ "Compare NAV of Liquid Fund and Gold Fund"
✅ "Tell me about Groww Multicap Fund"
```

#### Blocked Questions
```
❌ "Should I buy this fund?"
❌ "Which fund should I invest in?"
❌ "Will this fund give good returns?"
```

### For Administrators

#### Access Admin Dashboard
Navigate to: `http://localhost:8501/admin`

#### Features
- **System Status**: View scheduler status and next run time
- **Run Pipeline**: Manually trigger scraping + ingestion
- **Fund Categories**: View all 32 funds by category
- **Metrics**: Total fund count

---

## Data Pipeline

### Automated Daily Updates

**Schedule**: Every day at 10:00 AM IST

**Process:**
1. **Scraper** fetches latest data from Groww
2. **Ingestor** processes and stores in ChromaDB
3. **RAG Engine** uses updated data for queries

### Manual Updates

**Option 1: Admin Dashboard**
1. Go to `/admin`
2. Click "🚀 Run Pipeline Now"

**Option 2: Command Line**
```bash
cd phases/phase-1-collection
python -m src.scraper

cd ../phase-2-processing
python -m src.ingest
```

---

## Configuration

### System Prompt
Edit: `phases/phase-0-foundation/system_prompt.md`

Key sections:
- **ROLE**: Define assistant behavior
- **FUND ALIAS RECOGNITION**: Add/modify fund aliases
- **REFUSAL PROTOCOLS**: Customize blocked queries
- **RESPONSE CONSTRAINTS**: Format guidelines

### Fund Sources
Edit: `phases/phase-0-foundation/config/sources.json`

Add new funds:
```json
{
  "name": "Fund Name",
  "category": "Equity",
  "url": "https://groww.in/mutual-funds/...",
  "enabled": true,
  "type": "fund_page"
}
```

### UI Theme
Edit: `phases/phase-5-frontend/.streamlit/config.toml`

Current theme: Dark mode with blue accents

---

## Troubleshooting

### Embedding Dimension Mismatch
**Error**: `Collection expecting embedding with dimension of 384, got 3072`

**Fix:**
```bash
# Run the fix script
fix_embedding_error.bat

# Or manually:
cd phases/phase-2-processing
python clear_chroma.py
python -m src.ingest
```

### Scheduler Not Running
**Check logs** for:
```
Scheduled daily job at 10:00 AM IST
Next scheduled run: 2024-03-09 10:00:00 IST
```

**Fix:**
1. Restart app
2. Check `/admin` for scheduler status
3. Verify timezone settings in `scheduler.py`

### Quota Errors (429)
**Groq quota exceeded**

**Solutions:**
1. Wait for quota reset (usually 1 minute)
2. Add OpenAI API key as fallback
3. Use multiple Gemini keys for rotation

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| **Response Time** | 2-4 seconds |
| **Scrape Time** | ~3 seconds per fund |
| **Storage per Fund** | 5-10 KB (JSON) |
| **Total Storage** | ~320 KB for 32 funds |
| **Ingestion Time** | ~1 minute |
| **Concurrent Users** | 10+ supported |

---

## API Keys & Costs

### Groq (Primary LLM)
- **Model**: Llama 3.1 8B Instant
- **Free Tier**: 30 requests/minute
- **Cost**: Free
- **Get Key**: https://console.groq.com

### Google Gemini (Embeddings)
- **Model**: gemini-embedding-001
- **Free Tier**: 1,500 requests/day
- **Cost**: Free
- **Get Key**: https://makersuite.google.com/app/apikey

### OpenAI (Fallback)
- **Model**: GPT-3.5 Turbo
- **Cost**: $0.0015 per 1K tokens
- **Get Key**: https://platform.openai.com/api-keys

---

## Security & Best Practices

### API Key Management
- ✅ Store in `.env` file (never commit)
- ✅ Use separate keys for dev/prod
- ✅ Rotate keys regularly

### Admin Access
- ✅ Admin dashboard at `/admin` (no auth by default)
- ⚠️ Add authentication for production
- ⚠️ Restrict admin page access via firewall

### Data Privacy
- ✅ No user data stored
- ✅ No PII collected
- ✅ Queries not logged

---

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets (API keys)
4. Deploy

### Docker (Coming Soon)
```dockerfile
# Dockerfile will be provided
```

### Production Checklist
- [ ] Add authentication to admin page
- [ ] Set up monitoring/logging
- [ ] Configure rate limiting
- [ ] Set up backup for ChromaDB
- [ ] Add error tracking (Sentry)

---

## Maintenance

### Daily Tasks
- ✅ Automated scraping at 10 AM IST
- ✅ Automated ingestion after scraping

### Weekly Tasks
- Check admin dashboard for errors
- Review query logs (if enabled)
- Monitor API quota usage

### Monthly Tasks
- Update fund list if new funds added
- Review and update system prompt
- Check for library updates

---

## Support & Contact

**Issues**: Create GitHub issue  
**Documentation**: See `/docs` folder  
**Updates**: Check `CHANGELOG.md`

---

## License

Proprietary - Groww Mutual Fund Assistant

---

## Changelog

### Version 2.0 (March 2024)
- ✅ Dark theme UI
- ✅ Separate admin dashboard
- ✅ Optimized scraping (90% smaller files)
- ✅ Groq LLM integration
- ✅ Multi-fund query support
- ✅ Factual comparison queries
- ✅ Improved guardrails
- ✅ Better date formatting

### Version 1.0 (February 2024)
- Initial release
- 32 Groww AMC funds
- Basic RAG implementation
- Gemini 2.0 Flash integration

---

**Built with ❤️ for Groww Mutual Fund Investors**
