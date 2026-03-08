### Groww Mutual Fund FAQ Assistant – High-Level Architecture

---

### 1. Goal & Overview

**Goal**: A modular, AI-powered FAQ assistant for Groww Mutual Fund schemes that:
- Scrapes official Groww pages (stealth Playwright) on a daily schedule.
- Ingests HTML/PDF content into a Chroma-based vector store.
- Serves a multi-page Streamlit chat interface backed by a guarded RAG engine.
- Strictly follows the facts-only rules from `system_prompt.md`.

Top-level flow:
- **Daily pipeline**: `scheduler.py` → `scraper.py` → `ingest.py` → ChromaDB
- **User interaction**: Streamlit `app.py` (main) + `pages/admin.py` (admin) → `rag_engine.py` → ChromaDB → LLM answer with citation.

---

### 2. Project Structure (Logical View)

- `architecture.md` – This blueprint.
- `requirements.txt` – Python dependencies (Playwright, APScheduler, LangChain, Chroma, Streamlit, etc.).
- `system_prompt.md` – Facts-only system rules for the assistant.
- `.streamlit/config.toml` – Streamlit theme configuration (Groww colors).
- `config/`
  - `sources.json` – List of official Groww URLs (AMC overview + all schemes).
- `data/`
  - `raw/<YYYY-MM-DD>/` – Scraped HTML/PDF and `manifest.json` per run.
- `chroma/` – Persistent ChromaDB data directory.
- `src/`
  - `scraper.py` – Stealth Playwright scraper + manifest generator.
  - `ingest.py` – LangChain ingestion + chunking + Chroma upsert.
  - `scheduler.py` – APScheduler orchestration (24h pipeline).
  - `rag_engine.py` – Retrieval engine, guardrails, and citation handling.
  - `shared.py` – Shared utilities and constants.
- `app.py` – Streamlit main chat frontend + background scheduler bootstrap.
- `pages/admin.py` – Streamlit admin dashboard page.

---

### 3. Phase-Based Architecture

#### Phase 0 – Foundation
- Define directory layout: `config/`, `data/raw/`, `chroma/`.
- Add `requirements.txt` and `system_prompt.md`.
- Configure `config/sources.json` with Groww AMC page and all scheme URLs.

#### Phase 1 – Collection (Stealth Scraper)
- **Module**: `src/scraper.py`
- **Inputs**: `config/sources.json`.
- **Outputs**:
  - HTML snapshots (`*.html`) and PDFs (`*.pdf`) under `data/raw/<YYYY-MM-DD>/`.
  - `manifest.json` describing all artifacts and their `source_url`.
- **Key responsibilities**:
  - Load enabled sources from `config/sources.json`.
  - Launch Playwright in **stealth mode** (anti-bot heuristics).
  - For each URL:
    - Capture HTML snapshot.
    - Discover & download associated PDFs (factsheets, scheme docs).
  - Record metadata per artifact:
    - `path`, `source_url`, `content_type`, `fetched_at`.

#### Phase 2 – Processing & Vectorization
- **Module**: `src/ingest.py`
- **Inputs**: `data/raw/<YYYY-MM-DD>/manifest.json` and artifacts.
- **Outputs**: Chunked documents stored in **ChromaDB** (`chroma/`).
- **Key responsibilities**:
  - Load manifest and read all HTML/PDF artifacts.
  - Normalize HTML / extract text; extract text from PDFs.
  - Build LangChain `Document`s with metadata:
    - **Required**: `source_url`, `content_type`, `run_date`.
  - Chunk using `RecursiveCharacterTextSplitter`.
  - Upsert chunks into Chroma (`groww_mf_faq` collection).

#### Phase 3 – Retrieval & Guarded Generation
- **Module**: `src/rag_engine.py`
- **Inputs**: User query, ChromaDB, `system_prompt.md`.
- **Outputs**: Final answer text + citation URL (or refusal).
- **Key responsibilities**:
  - **Guardrails**:
    - `validate_query(query)` detects:
      - PII requests (PAN, phone, email, account details).
      - Advice-oriented questions ("buy/sell", "best fund", predictions).
    - If blocked, the caller returns the **default refusal** from `system_prompt.md`.
  - **RAG chain**:
    - Load system prompt from `system_prompt.md`.
    - Connect to Chroma (`chroma/`, `groww_mf_faq`).
    - Retrieve top-k chunks for the query.
    - Call LLM with system prompt + retrieved context.
  - **Answer Enhancement**:
    - `format_answer()` removes all web links from answer text for cleaner presentation.
    - `_query_fund_attribute()` uses multiple query variations to ensure NAV and other attributes are retrieved for all funds.
  - **Citation handler**:
    - `extract_citation_url(retrieved_docs)` picks one `source_url` (top document).
    - `format_answer_with_citation(answer_text, citation_url)` enforces:
      - ≤ 3 sentences.
      - Exactly one citation line: `"Source: <url>"`.
  - **Public API**:
    - `answer(query)` returns:
      - `blocked`, `reason`, `answer`, `citation_url`.

#### Phase 4 – Orchestration & Scheduling
- **Module**: `src/scheduler.py`
- **Inputs**: Time (24h interval), `scraper.fetch_daily`, `ingest.ingest_daily`.
- **Outputs**: Daily refreshed `data/raw/` and Chroma content.
- **Key responsibilities**:
  - Maintain a single APScheduler instance.
  - Define `run_pipeline_once()`:
    - `fetch_daily()` → `ingest_daily()`.
  - Define `schedule_daily_job(scheduler)`:
    - Job ID `daily_scrape_and_ingest`.
    - Interval: every 24 hours (exact timing configurable).
  - Define `start_scheduler_once()`:
    - Idempotent start of scheduler and job registration.
    - Safe to call multiple times (e.g., on Streamlit reruns).

#### Phase 5 – Frontend (Streamlit App - Multi-Page)
- **Modules**: `app.py` (main), `pages/admin.py` (admin dashboard)
- **Inputs**: User queries, results from `rag_engine.answer`.
- **Outputs**: Web UI, chat experience, admin controls.
- **Key responsibilities**:
  - **Main Page (`app.py`)**:
    - On app load: `ensure_scheduler_started()` → `start_scheduler_once()` (scheduler only once).
    - Layout:
      - Hero section with Groww theme (mint green #00d09c gradient).
      - 3 example question buttons (prefilled prompts).
      - Chat history with improved styling.
      - Enhanced chat input textbox with mint green border and better alignment.
      - ⚙️ button in top-right corner for admin access.
    - Query handling:
      - `handle_query(user_query)`:
        - Calls `rag_engine.validate_query()` / `answer()`.
        - If blocked, display default refusal from `system_prompt.md`.
        - If allowed, display answer + "Source" link.
        - Web links are automatically removed from answer text.
  - **Admin Page (`pages/admin.py`)**:
    - Dark sidebar with admin controls.
    - System status monitoring (scheduler status, next update time).
    - Pipeline controls (Run Now, Clear Cache).
    - Cache statistics and fund statistics.
    - Activity logs and recent updates.
    - "← Back to Chat" button for navigation.

---

### 4. Data & Metadata Design

- **Scrape manifest** (`data/raw/<date>/manifest.json`):
  - `run_date`: ISO date string.
  - `artifacts`: list of:
    - `path`: relative file path under `data/raw/`.
    - `source_url`: originating Groww URL.
    - `content_type`: `"html"` or `"pdf"`.
    - `fetched_at`: ISO datetime.

- **Vector store metadata (per chunk)**:
  - `source_url` (required for citations).
  - `content_type` (html/pdf).
  - `run_date`.
  - Optional: scheme name, category, risk label, etc.

---

### 5. Key Design Decisions & Constraints

- **Processing Logic & Response Rules**:
  1. **[Internal_DB] Single Fund Query**:
     - *Definition*: User asks about one specific fund from Internal_DB.
     - *Constraint*: Max 3 lines of text.
     - *Linking*: Fund Name itself is the hyperlink to its source URL.
     - *Tone*: Concise and direct.
  2. **[Internal_DB] Multi-Fund Query**:
     - *Definition*: User asks to compare or list multiple funds from Internal_DB.
     - *Constraint*: Comprehensive, detailed answer. No line limits.
     - *Linking*: One hyperlink at the end: Groww Official AMC Link.
     - *Tone*: Analytical and informative.
  3. **[Internal_DB] COUNT/LIST Queries**:
     - *COUNT*: Numerical count only. No names.
     - *LIST*: Bulleted names only. No descriptions/NAV/AUM.
  4. **General Financial Query**:
     - *Definition*: General questions (SIP, Types of funds) with no Internal_DB data.
     - *Constraint*: Comprehensive, detailed answer. No line limits.
     - *Linking*: One hyperlink at the end: Groww Official AMC Link.
     - *Tone*: Educational.

- **STRICT LINK HYGIENE**:
  - **Zero-Link Policy**: No links if unrelated or no data retrieved.
  - **Single-Link Policy**: Exactly one URL per response.
  - **No Double Links**: Never use both "Source: URL" text and a UI button.
  - **Web Link Removal**: All inline web links are automatically removed from answer text.

- **NEGATIVE CONSTRAINTS**:
  - Do NOT start with "Based on the provided context..." or "I have identified...".
  - Do NOT provide descriptions for "list" queries.
  - Do NOT provide a link if no data is retrieved.

- **Stealth scraping**:
  - Use Playwright with stealth configuration to reduce bot detection.
  - Conservative navigation and rate limiting.

- **Facts-only answers**:
  - `system_prompt.md` strictly defines role, scope, and refusal behavior.
  - `validate_query()` blocks advice/PII before any LLM call.

- **Citations**:
  - Single `source_url` per answer, always present.
  - Enables transparent trace-back to Groww's official pages.

- **Idempotent scheduler**:
  - Background scheduler is started once and reused across Streamlit reruns.
  - Daily job runs the end-to-end scrape → ingest pipeline.

- **Performance Optimization**:
  - Reduced parallel workers (10 → 3) for faster response times.
  - Multiple query variations for NAV and attribute retrieval.
  - Overall timeout: 15 seconds, per-fund timeout: 10 seconds.
  - Expected response time: 8-12 seconds for category queries.

---

### 6. Technology Stack (from `requirements.txt`)

- **Scraping**: `playwright`, `playwright-stealth`, `beautifulsoup4`.
- **Scheduling**: `APScheduler`.
- **RAG / Vector Store**:
  - `langchain`, `langchain-community`, `langchain-text-splitters`.
  - `chromadb`, `pypdf`.
- **Frontend**: `streamlit`.
- **Utilities**: `python-dotenv` for configuration/env management.
