"""
Firecrawl Client - Firecrawl API wrapper
"""

import os
import logging
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirecrawlClient:
    """Firecrawl API wrapper for web crawling"""

    def __init__(self, api_key=None):
        """Initialize Firecrawl client"""
        if api_key is None:
            api_key = os.getenv("FIRECRAWL_API_KEY")

        if not api_key:
            raise ValueError("Firecrawl API key not provided")

        self.api_key = api_key
        self.client = FirecrawlApp(api_key=api_key)

        logger.info("Firecrawl client initialized")

    def scrape_url(self, url, formats=None, only_main_content=True, timeout=30000):
        """Scrape a single URL"""
        try:
            if formats is None:
                formats = ["markdown"]

            logger.info(f"Scraping URL: {url}")

            result = self.client.scrape_url(
                url=url,
                params={
                    "formats": formats,
                    "onlyMainContent": only_main_content,
                    "timeout": timeout,
                },
            )

            if result.get("success"):
                logger.info(f"Successfully scraped: {url}")
                return {
                    "success": True,
                    "markdown": result.get("markdown", ""),
                    "html": result.get("html", ""),
                    "metadata": result.get("metadata", {}),
                    "url": url,
                }
            else:
                logger.error(f"Failed to scrape: {url}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "url": url,
                }

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }

    def crawl_site(self, url, limit=100, depth=3, formats=None, only_main_content=True):
        """Crawl entire website"""
        try:
            if formats is None:
                formats = ["markdown"]

            logger.info(f"Starting crawl: {url} (limit: {limit}, depth: {depth})")

            result = self.client.crawl_url(
                url=url,
                params={
                    "limit": limit,
                    "depth": depth,
                    "formats": formats,
                    "onlyMainContent": only_main_content,
                    "excludePaths": ["/blog", "/news", "/events"],
                },
            )

            if result.get("success"):
                logger.info(f"Crawl started successfully")
                return {
                    "success": True,
                    "id": result.get("id"),
                    "url": url,
                    "limit": limit,
                    "depth": depth,
                }
            else:
                logger.error("Failed to start crawl")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "url": url,
                }

        except Exception as e:
            logger.error(f"Error starting crawl: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }

    def get_crawl_status(self, job_id):
        """Check status of a crawl job"""
        try:
            logger.info(f"Checking crawl status for job: {job_id}")

            result = self.client.check_crawl_status(job_id=job_id)

            status = result.get("status", "unknown")
            data = result.get("data", [])
            total = result.get("total", 0)

            logger.info(f"Crawl status: {status}, Progress: {total}")

            return {
                "success": True,
                "status": status,
                "total": total,
                "data": data,
                "progress": total / result.get("total", 1)
                if result.get("total") > 0
                else 0,
            }

        except Exception as e:
            logger.error(f"Error checking crawl status: {e}")
            return {
                "success": False,
                "status": "error",
                "error": str(e),
            }

    def cancel_crawl(self, job_id):
        """Cancel a crawl job"""
        logger.warning(f"Crawl cancellation not supported in current Firecrawl API")
        return False


# Global instance
firecrawl_client = FirecrawlClient()
