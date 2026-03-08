"""
Clear Chroma database to fix embedding dimension mismatch.
Run this before re-ingesting data.
"""
import shutil
from pathlib import Path

chroma_dir = Path(__file__).parent / "chroma"

if chroma_dir.exists():
    print(f"Deleting {chroma_dir}...")
    shutil.rmtree(chroma_dir, ignore_errors=True)
    print("✓ Chroma database cleared!")
else:
    print("Chroma directory doesn't exist.")

print("\nNow run the ingestion pipeline to rebuild the database.")
