#!/usr/bin/env python3
"""
Cache Clearing Script

This script clears the fund attribute cache.

Usage:
    python scripts/clear_cache.py [--older-than-hours 24]
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CACHE_DIR = Path(".cache/fund_attributes")


def clear_cache(older_than_hours: int = None):
    """
    Clear cache files.
    
    Args:
        older_than_hours: Only clear files older than this many hours.
                         If None, clear all files.
    """
    if not CACHE_DIR.exists():
        logger.info("Cache directory does not exist. Nothing to clear.")
        return
    
    cache_files = list(CACHE_DIR.glob("*.json"))
    
    if not cache_files:
        logger.info("Cache is already empty.")
        return
    
    deleted = 0
    kept = 0
    
    for cache_file in cache_files:
        try:
            if older_than_hours is not None:
                # Check file age
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                
                cached_time = datetime.fromisoformat(cache_data["timestamp"])
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                if age_hours < older_than_hours:
                    kept += 1
                    continue
            
            # Delete the file
            cache_file.unlink()
            deleted += 1
            
        except Exception as e:
            logger.error(f"Error processing {cache_file}: {e}")
    
    logger.info(f"Cache clearing complete!")
    logger.info(f"Deleted: {deleted} files, Kept: {kept} files")


def main():
    parser = argparse.ArgumentParser(description="Clear fund attribute cache")
    parser.add_argument(
        "--older-than-hours",
        type=int,
        default=None,
        help="Only clear cache files older than this many hours (default: clear all)"
    )
    
    args = parser.parse_args()
    
    if args.older_than_hours:
        logger.info(f"Clearing cache files older than {args.older_than_hours} hours")
    else:
        logger.info("Clearing all cache files")
    
    clear_cache(args.older_than_hours)


if __name__ == "__main__":
    main()
