# Groww Mutual Fund FAQ Assistant

AI-powered chatbot providing factual information about 32 Groww AMC mutual fund schemes.

## ✨ Features

- 🤖 **Intelligent Q&A** - Powered by Groq Llama 3.1 8B
- 📊 **32 Groww Funds** - Complete coverage
- 🎨 **Dark Theme UI** - Modern, professional interface
- 🔄 **Auto Updates** - Daily data refresh at 10 AM IST
- 🛠️ **Admin Dashboard** - Separate admin controls
- ⚡ **Fast Responses** - 2-4 second response time

## 🚀 Quick Start

```bash
# 1. Install
pip install -r phases/phase-0-foundation/requirements.txt
playwright install chromium

# 2. Add API keys to phases/phase-0-foundation/.env
GROQ_API_KEY=your_key

# 3. Setup data
cd phases/phase-1-collection && python -m src.scraper
cd ../phase-2-processing && python -m src.ingest

# 4. Run
cd ../phase-5-frontend && streamlit run app.py
```

**Access:**
- Main App: http://localhost:8501
- Admin: http://localhost:8501/admin

## 📖 Documentation

- **Full Guide**: [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Fixes Applied**: [FINAL_FIXES_COMPLETE.md](FINAL_FIXES_COMPLETE.md)

## 🎯 Example Queries

```
✅ "What is the NAV of Liquid Fund?"
✅ "Which fund has the highest expense ratio?"
✅ "Compare ELSS and Multicap Fund"
✅ "Tell me about Groww Gold ETF"
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Groq Llama 3.1 8B Instant
- **Vector DB**: ChromaDB
- **Embeddings**: Google Gemini
- **Scraper**: Playwright + BeautifulSoup4

## 📊 Performance

- Response Time: 2-4 seconds
- Storage: 320 KB for 32 funds
- Concurrent Users: 10+

## 🔐 API Keys Required

- **Groq** (required): https://console.groq.com
- **Gemini** (optional): https://makersuite.google.com/app/apikey
- **OpenAI** (optional): https://platform.openai.com/api-keys

## 📝 License

Proprietary - Groww Mutual Fund Assistant

---

**Built with ❤️ for Groww Mutual Fund Investors**
