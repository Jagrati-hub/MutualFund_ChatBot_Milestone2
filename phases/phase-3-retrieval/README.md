# Phase 3: Retrieval & Guarded Generation

## Purpose
Core RAG engine that retrieves relevant documents and generates factual answers with guardrails.

## Files in This Phase

### Core Modules
- `src/rag_engine.py` - Main RAG engine with guardrails
- `src/shared.py` - Shared utilities and constants

### Features
- **Guardrails**: PII detection, advice blocking
- **Web Link Removal**: Automatic removal of inline URLs
- **NAV Retrieval**: Multiple query variations for better data retrieval
- **Response Optimization**: 3-4x faster response times

### Test Files
- `test_*.py` - Tests for RAG functionality
- `test_format_answer_only.py` - Web link removal tests
- `test_rag_engine_import.py` - Import tests

### Documentation
- Feature-specific guides and implementation notes

## Key Responsibilities
1. Validate queries (PII, advice detection)
2. Retrieve relevant chunks from ChromaDB
3. Call LLM with system prompt + context
4. Remove web links from answers
5. Extract and format citations
6. Return final answer with source URL

## Latest Enhancements
✅ Web link removal - All inline URLs removed from answers
✅ NAV retrieval - Multiple query variations ensure success
✅ Response time - 3-4x faster (8-12s for category queries)

## Status
✅ Complete - All features implemented and tested
