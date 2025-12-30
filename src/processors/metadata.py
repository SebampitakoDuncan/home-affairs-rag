"""
Metadata Extractor - Extract metadata from documents
"""

import os
import hashlib
import logging
from typing import Dict, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract metadata from documents"""

    def __init__(self):
        pass

    def extract_url(self, html: str, default_url: str = "") -> str:
        """Extract canonical URL from HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Try canonical link
            canonical = soup.find("link", rel="canonical")
            if canonical and canonical.get("href"):
                return canonical["href"]

            # Try og:url
            og_url = soup.find("meta", property="og:url")
            if og_url and og_url.get("content"):
                return og_url["content"]

            return default_url

        except Exception as e:
            logger.error(f"Error extracting URL: {e}")
            return default_url

    def extract_title(self, html: str) -> str:
        """Extract page title from HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Try title tag
            title = soup.find("title")
            if title and title.get_text():
                return title.get_text(strip=True).strip()

            # Try h1
            h1 = soup.find("h1")
            if h1 and h1.get_text():
                return h1.get_text(strip=True).strip()

            return "Untitled"

        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return "Untitled"

    def extract_date(self, html: str, url: str = "") -> str:
        """Extract last modified date"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Try last-modified meta
            last_mod = soup.find("meta", attrs={"http-equiv": "last-modified"})
            if last_mod and last_mod.get("content"):
                return last_mod["content"]

            # Try article:modified_time
            article_date = soup.find("meta", property="article:modified_time")
            if article_date and article_date.get("content"):
                return article_date["content"]

            # Try og:updated_time
            og_date = soup.find("meta", property="og:updated_time")
            if og_date and og_date.get("content"):
                return og_date["content"]

            return ""

        except Exception as e:
            logger.error(f"Error extracting date: {e}")
            return ""

    def extract_section(self, url: str) -> str:
        """Extract section/category from URL"""
        try:
            # Parse URL path
            from urllib.parse import urlparse

            parsed = urlparse(url)
            path = parsed.path

            # Extract section from path
            parts = [p for p in path.split("/") if p]
            if parts:
                return parts[0]

            return "home"

        except Exception as e:
            logger.error(f"Error extracting section: {e}")
            return "home"

    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            # Simple heuristic detection
            if not text or len(text) < 10:
                return "unknown"

            # Check for common English patterns
            english_indicators = ["the", "and", "is", "in", "to", "of", "for", "with"]
            english_count = sum(
                1
                for indicator in english_indicators
                if indicator.lower() in text.lower()
            )

            if english_count >= 3:
                return "en"

            return "unknown"

        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "unknown"

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA256 hash of content"""
        try:
            hash_obj = hashlib.sha256(content.encode())
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error generating content hash: {e}")
            return ""

    def extract_all_metadata(self, html: str, url: str = "") -> Dict[str, str]:
        """Extract all metadata from HTML"""
        return {
            "url": url or self.extract_url(html, url),
            "title": self.extract_title(html),
            "date": self.extract_date(html, url),
            "section": self.extract_section(url),
            "language": self.detect_language(html),
            "content_hash": self.generate_content_hash(html),
        }


# Global instance
metadata_extractor = MetadataExtractor()
