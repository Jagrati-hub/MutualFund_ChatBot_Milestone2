# Phase 2: Processing & Vectorization

## Purpose
Process scraped content and ingest it into ChromaDB vector store for semantic search.

## Files in This Phase

### Core Module
- `src/ingest.py` - LangChain ingestion pipeline

### Data Storage
- `data/raw/` - Raw scraped HTML/PDF files
- `chroma/` - Persistent ChromaDB vector store

### Test Files
- `test_*.py` - Tests related to ingestion and vectorization

## Key Responsibilities
1. Load manifest and read artifacts
2. Normalize HTML and extract text
3. Extract text from PDFs
4. Build LangChain Documents with metadata
5. Chunk using RecursiveCharacterTextSplitter
6. Upsert chunks into Chroma

## Output
- ChromaDB collection: `groww_mf_faq`
- Vectorized chunks with metadata (source_url, content_type, run_date)

## Status
✅ Complete - Ingestion pipeline fully functional
