#!/usr/bin/env python
"""
Initial Crawl Script - Trigger first full crawl of Home Affairs website
"""

import os
import sys
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from crawler.crawler import crawler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run initial crawl of Home Affairs website"""

    print("=" * 60)
    print("Initial Crawl - Home Affairs Website")
    print("=" * 60)

    # Check for Firecrawl API key
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("\n❌ Error: FIRECRAWL_API_KEY not found in .env file")
        print("\nPlease add your Firecrawl API key to the .env file:")
        print("FIRECRAWL_API_KEY=your_api_key_here\n")
        return 1

    # Ask user for crawl type
    print("\nSelect crawl type:")
    print("1. Full crawl (all pages)")
    print("2. Test crawl (10 pages)")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "2":
        # Test crawl with limit
        print("\nStarting test crawl (10 pages)...")
        result = crawler.client.crawl_site(
            url=crawler.BASE_URL, limit=10, depth=2, only_main_content=True
        )

        if result.get("success"):
            job_id = result.get("id")
            print(f"✅ Crawl started (Job ID: {job_id})")
            print("Use the update_db.py script to check status and process results.")
        else:
            print(f"❌ Crawl failed: {result.get('error', 'Unknown error')}")
            return 1

    elif choice == "1":
        # Full crawl
        print("\nStarting full crawl (this may take a while)...")
        result = crawler.client.crawl_site(
            url=crawler.BASE_URL, limit=10000, depth=3, only_main_content=True
        )

        if result.get("success"):
            job_id = result.get("id")
            print(f"✅ Crawl started (Job ID: {job_id})")
            print("Use the update_db.py script to check status and process results.")
        else:
            print(f"❌ Crawl failed: {result.get('error', 'Unknown error')}")
            return 1
    else:
        print("\n❌ Invalid choice")
        return 1

    print("\n" + "=" * 60)
    print("Crawl initiated successfully!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
