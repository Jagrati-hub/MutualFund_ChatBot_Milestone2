# Project Phases Structure

This directory organizes all project files according to the phase-based architecture defined in `architecture.md`.

## Phase 0: Foundation
**Location**: `phase-0-foundation/`
**Purpose**: Project setup, configuration, and system prompts
**Files**:
- `requirements.txt` - Python dependencies
- `system_prompt.md` - Facts-only system rules
- `config/sources.json` - Groww URLs configuration
- `.env` - Environment variables (API keys)
- `.streamlit/config.toml` - Streamlit theme configuration

## Phase 1: Collection (Stealth Scraper)
**Location**: `phase-1-collection/`
**Purpose**: Web scraping and data collection
**Files**:
- `src/scraper.py` - Stealth Playwright scraper
- `scripts/` - Scraping utilities
- Tests: `test_*.py` files related to scraping

## Phase 2: Processing & Vectorization
**Location**: `phase-2-processing/`
**Purpose**: Data processing and vector store ingestion
**Files**:
- `src/ingest.py` - LangChain ingestion pipeline
- `data/raw/` - Raw scraped data
- `chroma/` - ChromaDB vector store
- Tests: `test_*.py` files related to ingestion

## Phase 3: Retrieval & Guarded Generation
**Location**: `phase-3-retrieval/`
**Purpose**: RAG engine and answer generation
**Files**:
- `src/rag_engine.py` - Core RAG engine
- `src/shared.py` - Shared utilities
- Tests: `test_*.py` files related to RAG
- Documentation: Feature-specific docs

## Phase 4: Orchestration & Scheduling
**Location**: `phase-4-orchestration/`
**Purpose**: Background job scheduling
**Files**:
- `src/scheduler.py` - APScheduler orchestration
- `src/shared.py` - Shared utilities

## Phase 5: Frontend (Streamlit App)
**Location**: `phase-5-frontend/`
**Purpose**: User-facing chat interface and admin dashboard
**Files**:
- `app.py` - Main chat interface
- `pages/admin.py` - Admin dashboard
- `.streamlit/config.toml` - Theme configuration

## Documentation
**Location**: `docs/`
**Purpose**: Project documentation and guides
**Files**:
- `architecture.md` - System architecture
- `README.md` - Project overview
- `SAMPLE_QA_AND_SOURCES.md` - Sample questions and source links
- Feature guides and implementation notes
