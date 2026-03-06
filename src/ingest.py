from __future__ import annotations

"""
Phase 2 implementation: Ingestion for the Groww Mutual Fund FAQ Assistant.

Responsibilities:
- Read daily scrape outputs from `data/raw/<YYYY-MM-DD>/manifest.json`.
- Load HTML/text and PDF artifacts into LangChain `Document` objects.
- Chunk documents using `RecursiveCharacterTextSplitter`.
- Upsert chunks into a ChromaDB vector store.

Core requirement:
- Every chunk stored in Chroma **must** include `source_url` in its metadata,
  so the RAG engine can emit automated citations.
"""

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

_GEMINI_KEY: str = (
    os.environ.get("GEMINI_API_KEY") or
    os.environ.get("GOOGLE_API_KEY") or
    ""
)

RAW_DATA_ROOT = Path("data") / "raw"
CHROMA_DIR = Path("chroma")
CHROMA_COLLECTION_NAME = "groww_mf_faq"

# Chunking defaults (tunable)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


@dataclass
class IngestionConfig:
    """
    Configuration options for a single ingestion run.
    """

    run_date: date
    raw_root: Path = RAW_DATA_ROOT
    chroma_dir: Path = CHROMA_DIR
    collection_name: str = CHROMA_COLLECTION_NAME


def get_manifest_path(config: IngestionConfig) -> Path:
    """
    Compute the manifest path for the given run date, e.g.:
        data/raw/2026-03-06/manifest.json
    """
    return config.raw_root / config.run_date.isoformat() / "manifest.json"


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Load a scrape manifest describing artifacts produced by the scraper.
    """
    import json

    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _html_to_text(html_path: Path) -> str:
    """Extract readable text from an HTML file."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Normalize whitespace
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def _pdf_to_text(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(str(pdf_path))
    parts = []
    for page in reader.pages:
        part = page.extract_text()
        if part:
            parts.append(part)
    return "\n\n".join(parts)


def build_documents_from_manifest(manifest: Dict[str, Any], project_root: Path) -> List[Document]:
    """
    Convert manifest entries into LangChain `Document` objects.

    - For `content_type == "html"`, load and normalize HTML to text.
    - For `content_type == "pdf"`, use pypdf to extract text.
    - Attach metadata: `source_url`, `content_type`, `run_date`.
    """
    run_date = manifest.get("run_date", "")
    documents: List[Document] = []

    for artifact in manifest.get("artifacts", []):
        path_str = artifact.get("path", "")
        source_url = artifact.get("source_url", "")
        content_type = artifact.get("content_type", "html")

        file_path = project_root / path_str
        if not file_path.exists():
            continue

        try:
            if content_type == "html":
                text = _html_to_text(file_path)
            elif content_type == "pdf":
                text = _pdf_to_text(file_path)
            else:
                continue

            if not text.strip():
                continue

            metadata = {
                "source_url": source_url,
                "content_type": content_type,
                "run_date": run_date,
            }
            documents.append(Document(page_content=text, metadata=metadata))
        except Exception:
            continue

    return documents


def chunk_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Document]:
    """
    Chunk raw documents using `RecursiveCharacterTextSplitter`.

    Preserves `source_url` and other metadata on every resulting chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def get_chroma_vectorstore(config: IngestionConfig, embedding_model: Any = None) -> Chroma:
    """
    Initialize (or connect to) a ChromaDB collection.
    Uses Google gemini-embedding-001 to match the RAG engine.
    """
    if embedding_model is None:
        if _GEMINI_KEY:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                embedding_model = GoogleGenerativeAIEmbeddings(
                    model="models/gemini-embedding-001",
                    google_api_key=_GEMINI_KEY,
                )
            except Exception:
                pass

        if embedding_model is None:
            # Fallback (rarely needed if key is set)
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
            )

    return Chroma(
        collection_name=config.collection_name,
        embedding_function=embedding_model,
        persist_directory=str(config.chroma_dir),
    )


def upsert_chunks_to_chroma(chunks: List[Document], config: IngestionConfig) -> int:
    """
    Replace the Chroma collection with the new chunks (full refresh per run).
    Includes rate-limiting pause to avoid 429 error on Gemini free tier.
    """
    if not chunks:
        return 0

    import chromadb
    import time
    from tqdm import tqdm

    # Delete existing collection to avoid duplicates (full replace)
    client = chromadb.PersistentClient(path=str(config.chroma_dir))
    try:
        client.delete_collection(config.collection_name)
    except Exception:
        pass

    vectorstore = get_chroma_vectorstore(config)
    
    # Process in small batches and wait to avoid hitting free-tier 429 quota (100 RPM)
    # 20 chunks per batch, wait 15 seconds = 80 documents/minute (safely under 100)
    batch_size = 20
    total_written = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vectorstore.add_documents(batch)
        total_written += len(batch)
        
        if i + batch_size < len(chunks):
            time.sleep(15.0)
            
    return total_written


def ingest_daily(run_date: Optional[date] = None, project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Orchestrate ingestion for a given day.

    High-level flow:
    1. Resolve `run_date` (default: today) and construct `IngestionConfig`.
    2. Locate and load the scraper `manifest.json`.
    3. Build LangChain `Document` objects from HTML/PDF artifacts.
    4. Chunk documents with `RecursiveCharacterTextSplitter`.
    5. Upsert chunks into Chroma, ensuring `source_url` in every chunk's metadata.
    """
    if run_date is None:
        run_date = date.today()
    if project_root is None:
        project_root = Path.cwd()

    config = IngestionConfig(run_date=run_date)
    manifest_path = get_manifest_path(config)

    if not manifest_path.exists():
        return {
            "run_date": run_date.isoformat(),
            "chunk_count": 0,
            "collection_name": config.collection_name,
            "chroma_dir": str(config.chroma_dir),
            "error": f"Manifest not found: {manifest_path}",
        }

    manifest = load_manifest(manifest_path)
    documents = build_documents_from_manifest(manifest, project_root)
    chunks = chunk_documents(documents)
    chunk_count = upsert_chunks_to_chroma(chunks, config)

    return {
        "run_date": run_date.isoformat(),
        "chunk_count": chunk_count,
        "collection_name": config.collection_name,
        "chroma_dir": str(config.chroma_dir),
    }


if __name__ == "__main__":
    import json

    summary = ingest_daily()
    print(json.dumps(summary, indent=2))
