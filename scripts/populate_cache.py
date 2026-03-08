#!/usr/bin/env python3
"""
Cache Population Script for Fund Attributes

This script pre-populates the cache with fund attribute data to avoid
hitting API quota limits during user queries.

Usage:
    python scripts/populate_cache.py [--attributes nav,expense_ratio,exit_load]
"""

import argparse
import logging
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_engine import _query_fund_attribute, RAGConfig
from src.shared import SCOPE_FUNDS_BY_CATEGORY

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def populate_cache(attributes: list[str], delay: float = 1.0):
    """
    Populate cache for all funds and specified attributes.
    
    Args:
        attributes: List of attribute names to cache
        delay: Delay in seconds between API calls to avoid rate limiting
    """
    config = RAGConfig()
    
    # Get all funds
    all_funds = []
    for category, funds in SCOPE_FUNDS_BY_CATEGORY.items():
        all_funds.extend(funds)
    
    total = len(all_funds) * len(attributes)
    completed = 0
    errors = 0
    cached = 0
    
    logger.info(f"Starting cache population for {len(all_funds)} funds and {len(attributes)} attributes")
    logger.info(f"Total queries: {total}")
    
    for fund in all_funds:
        for attr in attributes:
            completed += 1
            logger.info(f"[{completed}/{total}] Querying {attr} for {fund}")
            
            try:
                result = _query_fund_attribute(fund, attr, config)
                
                if "⚠️ API quota exceeded" in result:
                    logger.warning(f"API quota exceeded. Stopping cache population.")
                    logger.info(f"Completed: {completed}/{total}, Cached: {cached}, Errors: {errors}")
                    return
                elif "Not available" in result:
                    logger.info(f"  → Not available")
                else:
                    logger.info(f"  → Cached: {result[:50]}...")
                    cached += 1
                
                # Delay to avoid rate limiting
                if delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error querying {attr} for {fund}: {e}")
                errors += 1
    
    logger.info(f"Cache population complete!")
    logger.info(f"Completed: {completed}/{total}, Cached: {cached}, Errors: {errors}")


def main():
    parser = argparse.ArgumentParser(description="Populate cache for fund attributes")
    parser.add_argument(
        "--attributes",
        type=str,
        default="nav,expense_ratio,exit_load",
        help="Comma-separated list of attributes to cache (default: nav,expense_ratio,exit_load)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between API calls (default: 1.0)"
    )
    
    args = parser.parse_args()
    attributes = [attr.strip() for attr in args.attributes.split(",")]
    
    logger.info(f"Attributes to cache: {', '.join(attributes)}")
    logger.info(f"Delay between calls: {args.delay}s")
    
    populate_cache(attributes, args.delay)


if __name__ == "__main__":
    main()
