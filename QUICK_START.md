# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
cd phases/phase-0-foundation
pip install -r requirements.txt
playwright install chromium
```

### 2. Add API Keys
Create `phases/phase-0-foundation/.env`:
```env
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY_1=your_gemini_key
```

Get keys:
- Groq: https://console.groq.com
- Gemini: https://makersuite.google.com/app/apikey

### 3. Setup Data
```bash
# Scrape data
cd phases/phase-1-collection
python -m src.scraper

# Ingest to database
cd ../phase-2-processing
python -m src.ingest
```

### 4. Run App
```bash
cd ../phase-5-frontend
streamlit run app.py
```

**Open**: http://localhost:8501

---

## 📱 Usage

### Regular Users
- Ask questions about Groww mutual funds
- Use fund aliases (e.g., "ELSS", "liquid fund")
- Compare multiple funds

### Administrators
- Access: http://localhost:8501/admin
- Run manual data updates
- View system status

---

## 🔧 Troubleshooting

### Embedding Error
```bash
fix_embedding_error.bat
```

### Quota Error
Wait 1 minute or add more API keys

---

## 📚 Full Documentation
See `PROJECT_DOCUMENTATION.md`
