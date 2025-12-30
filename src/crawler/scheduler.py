"""
Scheduler - Weekly cron job for crawling (Sunday 2 AM)
"""

import os
import sys
import logging
import schedule
import time

# Add src to path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crawler.crawler import crawler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CrawlScheduler:
    """Scheduler for weekly Home Affairs website crawling"""

    def __init__(self):
        self.crawler = crawler
        self.schedule = os.getenv("CRAWL_SCHEDULE", "0 2 * * 0")  # Sunday at 2 AM
        logger.info(f"Scheduler initialized (schedule: {self.schedule})")

    def run_scheduled_crawl(self):
        """Run the scheduled crawl"""
        logger.info("Starting scheduled crawl...")

        try:
            result = self.crawler.crawl_home_affairs(full_crawl=True)

            if result.get("success"):
                logger.info(
                    f"✅ Scheduled crawl completed: {result.get('total_documents', 0)} documents processed"
                )
            else:
                logger.error(
                    f"❌ Scheduled crawl failed: {result.get('error', 'Unknown')}"
                )
        except Exception as e:
            logger.error(f"Error in scheduled crawl: {e}")

    def start_scheduler(self):
        """Start the scheduler daemon"""
        logger.info("Starting crawl scheduler...")

        try:
            schedule.every().sunday.at("02:00").do(self.run_scheduled_crawl)

            logger.info("Scheduler started successfully. Waiting for Sunday 2 AM...")

            while True:
                schedule.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
            raise

    def run_single_crawl(self):
        """Run a single crawl immediately (for testing)"""
        logger.info("Running single crawl now...")
        return self.crawler.crawl_home_affairs(full_crawl=True)


# Global instance
scheduler = CrawlScheduler()


if __name__ == "__main__":
    import sys

    scheduler.run_single_crawl()
