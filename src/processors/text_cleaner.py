"""
Text Cleaner - Clean HTML/Markdown for better embedding quality
"""

import re
import logging
from typing import Optional
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextCleaner:
    """Clean HTML and Markdown text for better embedding quality"""

    def __init__(self):
        pass

    def clean_html(self, html: str) -> str:
        """Remove navigation, footer, ads from HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove unwanted elements
            for tag in [
                "nav",
                "footer",
                "aside",
                "header",
                "script",
                "style",
                "noscript",
            ]:
                for element in soup.find_all(tag):
                    element.decompose()

            # Remove elements with common ad/privacy classes
            for class_pattern in [
                "ad",
                "advertisement",
                "banner",
                "sidebar",
                "privacy",
                "cookie",
            ]:
                for element in soup.find_all(
                    class_=lambda c: c
                    and any(p in " ".join(c).lower() for p in class_pattern)
                ):
                    element.decompose()

            # Get text
            text = soup.get_text(separator=" ", strip=True)

            return text

        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html

    def clean_markdown(self, markdown: str) -> str:
        """Clean markdown text"""
        try:
            # Remove markdown syntax
            markdown = re.sub(r"!\[.*?\]\(.*?\)", "", markdown)  # Remove images
            markdown = re.sub(r"\[.*?\]\(.*?\)", "", markdown)  # Remove markdown links
            markdown = re.sub(r"#{1,6}\s*", "", markdown)  # Remove headers
            markdown = re.sub(r"\*{1,2}", "", markdown)  # Remove bold/italic
            markdown = re.sub(r"_{1,2}", "", markdown)  # Remove bold/italic

            return markdown

        except Exception as e:
            logger.error(f"Error cleaning Markdown: {e}")
            return markdown

    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        try:
            # Replace multiple whitespace with single space
            text = re.sub(r"\s+", " ", text)

            # Remove leading/trailing whitespace
            text = text.strip()

            # Remove empty lines
            text = re.sub(r"\n\s*\n", "\n", text)

            return text

        except Exception as e:
            logger.error(f"Error normalizing whitespace: {e}")
            return text

    def remove_urls(self, text: str) -> str:
        """Remove URLs from text (optional)"""
        try:
            # Remove HTTP/HTTPS URLs
            text = re.sub(r"https?://\S+", "", text)

            return text

        except Exception as e:
            logger.error(f"Error removing URLs: {e}")
            return text

    def extract_main_content(self, html: str) -> str:
        """Extract main content from HTML"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Try common main content selectors
            main_content = None

            # Try main tag
            main = soup.find("main")
            if main:
                main_content = main.get_text(separator=" ", strip=True)
            else:
                # Try article tag
                article = soup.find("article")
                if article:
                    main_content = article.get_text(separator=" ", strip=True)
                else:
                    # Try content divs
                    for class_name in ["content", "main-content", "article"]:
                        for element in soup.find_all(
                            class_=lambda c: c and class_name in " ".join(c).lower()
                        ):
                            main_content = element.get_text(separator=" ", strip=True)
                            break

            if main_content:
                return main_content
            else:
                return soup.get_text(separator=" ", strip=True)

        except Exception as e:
            logger.error(f"Error extracting main content: {e}")
            return html


# Global instance
text_cleaner = TextCleaner()
