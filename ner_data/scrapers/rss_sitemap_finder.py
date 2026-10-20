import re
import logging
from typing import List, Set
from urllib.parse import urlparse, urljoin
import requests
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger("rss_sitemap")

class URLFinder:
    """Discovers article URLs from RSS feeds, sitemaps, and section pages."""

    def __init__(self, session: requests.Session):
        self.session = session

    def get_urls_from_rss(self, feed_url: str) -> List[str]:
        urls: List[str] = []
        try:
            resp = self.session.get(feed_url, timeout=12)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                for entry in feed.entries:
                    link = getattr(entry, "link", None)
                    if link and link.startswith("http"):
                        urls.append(link.split("?")[0])
        except Exception as e:
            logger.warning(f"Error fetching RSS feed {feed_url}: {e}")
        return list(dict.fromkeys(urls))

    def get_urls_from_sitemap(self, sitemap_url: str) -> List[str]:
        urls: List[str] = []
        try:
            resp = self.session.get(sitemap_url, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "xml")
                # Look for <loc> tags
                for loc in soup.find_all("loc"):
                    u = loc.get_text().strip()
                    if u.startswith("http") and not any(u.endswith(ext) for ext in [".jpg", ".png", ".pdf", ".xml"]):
                        urls.append(u.split("?")[0])
        except Exception as e:
            logger.warning(f"Error fetching sitemap {sitemap_url}: {e}")
        return list(dict.fromkeys(urls))

    def get_urls_from_page(self, page_url: str, base_domain: str) -> List[str]:
        """Extract links from a section or press page matching the domain."""
        urls: List[str] = []
        try:
            resp = self.session.get(page_url, timeout=12)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    full_url = urljoin(page_url, href)
                    if base_domain in full_url and not any(full_url.endswith(ext) for ext in [".jpg", ".png", ".pdf", ".css", ".js"]):
                        urls.append(full_url.split("?")[0])
        except Exception as e:
            logger.warning(f"Error crawling page {page_url}: {e}")
        return list(dict.fromkeys(urls))
