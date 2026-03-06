# 📈 Groww Mutual Fund FAQ Assistant

A specialized RAG-based (Retrieval-Augmented Generation) chatbot designed to provide factual information about **32 Groww Mutual Fund schemes**. Built with LangChain, ChromaDB, and Google Gemini.

---

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.9 or higher
- Git
- Google Gemini API Key (or Groq/OpenAI key for fallback)

### 2. Local Installation
```bash
# Clone the repository
git clone https://github.com/Jagrati-hub/MutualFund_ChatBot_Milestone2.git
cd MutualFund_ChatBot_Milestone2

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for scraping)
playwright install chromium
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Running the App
```bash
streamlit run app.py
```

---

## 🔍 Scope: Groww AMC & Schemes

The assistant supports exactly **32 funds** across 4 categories:

### 1. 📈 Equity (20 Funds)
- Groww Large Cap Fund, Multicap, Small Cap, Value Fund, ELSS Tax Saver.
- Index Funds: Nifty Total Market, Smallcap 250, Non-Cyclical Consumer, Next 50, Midcap 150.
- ETFs & FoFs: EV & New Age Automotive, India Defence, 200 ETF, 500 Momentum 50, India Railways, BSE Power, India Internet, PSE ETF, Capital Markets.

### 2. 🏦 Debt (6 Funds)
- Groww Liquid Fund, Overnight Fund, Short Duration, Dynamic Bond, Gilt Fund.
- Groww Nifty 1D Rate Liquid ETF.

### 3. ⚖️ Hybrid (4 Funds)
- Groww Aggressive Hybrid Fund, Multi Asset Allocation, Arbitrage Fund.
- Groww Multi Asset Omni FoF.

### 4. 🪙 Commodities (2 Funds)
- Groww Gold ETF FoF.
- Groww Silver ETF FoF.

---

## 🛡️ Key Features & Guardrails

- **Multi-Page Architecture**: 
  - **Home**: Clean, user-facing chatbot interface for mutual fund queries.
  - **Admin Panel**: Dedicated `/admin` page for scheduler management and pipeline control.
- **Protected Admin Access**: The Admin Panel is secured with a login gate.
  - **URL**: Navigate to `Admin` in the sidebar.
  - **Credentials**: Username: `admin` | Password: `admin`
- **Stable UI**: Always-visible sample questions and smooth autoscrolling.
- **Strict Citation**: Every factual answer includes a direct hyperlink and a "Source" citation line.
- **Tiered Refusals**:
  - **Personal Advice**: Blocks PAN, Aadhaar, account numbers, etc.
  - **Financial Advice**: Refuses "Should I buy/sell?" or return comparisons.
  - **Out-of-Scope**: Polite refusal for non-finance queries with a helpful redirection.
- **Fail-Safe Retrieval**: Primary LLM: Gemini 1.5 Flash with automatic fallback to Groq (Llama 3.1) if quota limit (429) hit.

---

## ⚠️ Known Limits

1. **Facts Only**: The bot cannot compute or compare fund performance (e.g., "Which fund gave better returns?"). It will redirect you to the official factsheet.
2. **Groww AMC Only**: Information is limited to Groww Mutual Fund schemes. It does not possess data on other AMCs (HDFC, SBI, etc.).
3. **No Advice**: The bot is strictly a document-retrieval tool and cannot provide personalized investment recommendations.
4. **Data Recency**: Information is as current as the last scraper run (viewable on the Admin Page).

---

## 🌐 Deployment
This project is configured for **Streamlit Cloud**:
- `packages.txt` for Playwright Linux dependencies.
- `streamlit/secrets` support in `rag_engine.py` for secure API key management.
