"""
Main Crawler - Orchestrates Firecrawl crawling of Home Affairs website
"""

import os
import sys
import logging
from typing import List, Dict, Any
import json

# Add src to path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crawler.firecrawl_client import firecrawl_client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HomeAffairsCrawler:
    """Main crawler for Home Affairs website"""

    BASE_URL = "https://www.homeaffairs.gov.au/"
    CRAWL_STATE_FILE = "data/cache/crawl_state.json"
    PROCESSED_URLS_FILE = "data/cache/processed_urls.txt"

    def __init__(self):
        self.client = firecrawl_client
        self.limit = int(os.getenv("CRAWL_LIMIT", "10000"))
        self.depth = int(os.getenv("CRAWL_DEPTH", "3"))

        logger.info(
            f"HomeAffairsCrawler initialized (limit: {self.limit}, depth: {self.depth})"
        )

    def load_processed_urls(self):
        """Load set of already processed URLs"""
        try:
            if os.path.exists(self.PROCESSED_URLS_FILE):
                with open(self.PROCESSED_URLS_FILE, "r") as f:
                    urls = set(line.strip() for line in f if line.strip())
                logger.info(f"Loaded {len(urls)} processed URLs")
                return urls
        except Exception as e:
            logger.error(f"Error loading processed URLs: {e}")
            return set()

    def save_processed_urls(self, urls):
        """Save set of processed URLs"""
        try:
            os.makedirs(os.path.dirname(self.PROCESSED_URLS_FILE), exist_ok=True)
            with open(self.PROCESSED_URLS_FILE, "w") as f:
                for url in urls:
                    f.write(f"{url}\n")
            logger.info(f"Saved {len(urls)} processed URLs")
        except Exception as e:
            logger.error(f"Error saving processed URLs: {e}")

    def crawl_home_affairs(self, full_crawl=True):
        """Crawl Home Affairs website

        Args:
            full_crawl: If True, crawl entire site. If False, only crawl new pages.

        Returns:
            Dict with crawl results
        """
        try:
            processed_urls = self.load_processed_urls()

            logger.info(
                f"Starting {'full' if full_crawl else 'incremental'} crawl of {self.BASE_URL}"
            )

            if full_crawl:
                result = self.client.crawl_site(
                    url=self.BASE_URL,
                    limit=self.limit,
                    depth=self.depth,
                    only_main_content=True,
                )

                if result.get("success"):
                    job_id = result.get("id")
                    if not job_id:
                        logger.error("Crawl failed: No job ID returned")
                        return {
                            "success": False,
                            "error": "No job ID returned from crawl",
                        }
                    logger.info(f"Crawl started (job ID: {job_id})")

                    crawl_status = self._wait_for_completion(job_id)

                    if crawl_status.get("status") == "completed":
                        data = crawl_status.get("data", [])
                        urls = self._get_scraped_urls(data)

                        self.save_processed_urls(urls)

                        logger.info(
                            f"Crawl completed! Total documents: {crawl_status.get('total')}"
                        )

                        return {
                            "success": True,
                            "job_id": job_id,
                            "total_documents": crawl_status.get("total"),
                            "urls": urls,
                            "data": data,
                        }
                else:
                    error = result.get("error", "Unknown error")
                    logger.error(f"Crawl failed: {error}")
                    return {
                        "success": False,
                        "error": error,
                    }
            else:
                logger.info("Incremental crawl not yet implemented")
                return {
                    "success": False,
                    "message": "Incremental crawl not yet implemented",
                }

        except Exception as e:
            logger.error(f"Error crawling Home Affairs: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _wait_for_completion(
        self, job_id: str, poll_interval: int = 30
    ) -> Dict[str, Any]:
        """Wait for crawl job to complete"""
        try:
            logger.info(f"Waiting for crawl job {job_id} to complete...")

            while True:
                status = self.client.get_crawl_status(job_id)

                if status.get("status") in ["completed", "failed"]:
                    return status

                total = status.get("total", 0)
                progress = status.get("progress", 0)

                if total > 0:
                    progress_pct = (progress / total) * 100
                    logger.info(
                        f"Crawl progress: {progress_pct:.1f}% ({progress}/{total} documents)"
                    )

                import time

                time.sleep(poll_interval)

        except Exception as e:
            logger.error(f"Error waiting for crawl completion: {e}")
            return {"status": "error", "error": str(e)}

    def _get_scraped_urls(self, data: List) -> List[str]:
        """Extract URLs from crawled data"""
        urls = []
        for doc in data:
            metadata = doc.get("metadata", {})
            url = metadata.get("sourceURL", "")
            if url and url not in urls:
                urls.append(url)
        return urls


# Global instance
crawler = HomeAffairsCrawler()


def crawl_site():
    """Convenience function to crawl website"""
    return crawler.crawl_home_affairs(full_crawl=True)


if __name__ == "__main__":
    import sys

    sys.exit(0 if not crawler.crawl_home_affairs() else 1)
