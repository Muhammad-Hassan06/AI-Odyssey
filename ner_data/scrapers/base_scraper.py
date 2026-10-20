import os
import sys
import time
import random
import logging
from urllib.parse import urlparse, urljoin
import urllib.robotparser
from typing import Optional, Dict, Any, Tuple
import requests
from bs4 import BeautifulSoup

try:
    import trafilatura
except ImportError:
    trafilatura = None

# Configure logging
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

robots_logger = logging.getLogger("robots")
robots_logger.setLevel(logging.INFO)
rf_handler = logging.FileHandler(os.path.join(LOGS_DIR, "robots_decisions.log"), encoding="utf-8")
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
robots_logger.addHandler(rf_handler)

error_logger = logging.getLogger("scraper_errors")
error_logger.setLevel(logging.WARNING)
ef_handler = logging.FileHandler(os.path.join(LOGS_DIR, "scraping_errors.log"), encoding="utf-8")
ef_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
error_logger.addHandler(ef_handler)


class PoliteScraper:
    """
    Polite Web Scraper enforcing:
    - robots.txt compliance
    - Domain rate limiting with jitter (>= 2.0s per domain)
    - Exponential backoff retries (max 3)
    - Graceful skipping on 403/429/blocks
    - Trafilatura primary text extraction with BeautifulSoup fallback
    """

    def __init__(
        self,
        user_agent: str = "PakNERDataEngineerBot/1.0 (+https://github.com/Muhammad-Hassan06/AI-Odyssey; academic-nlp-research)",
        min_delay: float = 2.0,
        max_delay: float = 3.5,
        timeout: int = 15,
        max_retries: int = 3
    ):
        self.user_agent = user_agent
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.max_retries = max_retries

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ur;q=0.8",
        })

        self._robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_request_time: Dict[str, float] = {}
        self.blocked_domains: Set[str] = set()

    def get_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower()

    def is_allowed_by_robots(self, url: str) -> bool:
        domain = self.get_domain(url)
        if not domain:
            return False

        if domain in self.blocked_domains:
            return False

        if domain not in self._robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"https://{domain}/robots.txt"
            rp.set_url(robots_url)
            try:
                resp = self.session.get(robots_url, timeout=10)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                    robots_logger.info(f"Loaded robots.txt successfully for {domain}")
                elif resp.status_code in (401, 403, 429):
                    robots_logger.warning(f"Robots.txt forbidden (HTTP {resp.status_code}) for {domain} -> Disallowing and blocking domain")
                    self.blocked_domains.add(domain)
                    return False
                else:
                    rp.allow_all = True
                    robots_logger.info(f"No restrictive robots.txt (HTTP {resp.status_code}) for {domain} -> Defaulting to Allow")
            except Exception as e:
                rp.allow_all = True
                robots_logger.warning(f"Failed to fetch robots.txt for {domain}: {e} -> Defaulting to Allow")
            self._robots_cache[domain] = rp

        allowed = self._robots_cache[domain].can_fetch(self.user_agent, url)
        if not allowed:
            robots_logger.info(f"DISALLOWED by robots.txt: {url}")
        return allowed

    def _wait_for_domain(self, domain: str):
        now = time.time()
        last_time = self._last_request_time.get(domain, 0)
        delay = random.uniform(self.min_delay, self.max_delay)
        elapsed = now - last_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request_time[domain] = time.time()

    def fetch_url(self, url: str) -> Tuple[Optional[str], int]:
        """Fetch URL content with rate limiting and exponential backoff retries. Returns (html_or_none, status_code)."""
        domain = self.get_domain(url)
        if domain in self.blocked_domains:
            return None, 429

        if not self.is_allowed_by_robots(url):
            return None, 403

        self._wait_for_domain(domain)

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.text, 200
                elif resp.status_code in (403, 429):
                    error_logger.warning(f"Blocked (HTTP {resp.status_code}) on {url}. Marking {domain} as blocked.")
                    self.blocked_domains.add(domain)
                    return None, resp.status_code
                elif resp.status_code in (404, 410):
                    return None, resp.status_code
                else:
                    error_logger.warning(f"HTTP {resp.status_code} on attempt {attempt} for {url}")
            except requests.RequestException as e:
                error_logger.warning(f"Network error on attempt {attempt} for {url}: {e}")

            if attempt < self.max_retries:
                backoff_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(backoff_time)

        return None, 500

    def extract_article(self, html: str, url: str, min_words: int = 80) -> Optional[Dict[str, Any]]:
        """Extract main text, title, and date using trafilatura with BeautifulSoup fallback."""
        if not html:
            return None

        text = None
        title = ""
        date = ""

        # 1. Primary extractor: Trafilatura
        if trafilatura:
            try:
                extracted = trafilatura.extract(
                    html,
                    url=url,
                    include_comments=False,
                    include_tables=False,
                    no_fallback=False
                )
                if extracted:
                    text = extracted
                    meta = trafilatura.extract_metadata(html, default_url=url)
                    if meta:
                        title = meta.title or ""
                        date = meta.date or ""
            except Exception as e:
                error_logger.warning(f"Trafilatura error on {url}: {e}")

        # 2. Fallback: BeautifulSoup
        if not text:
            try:
                soup = BeautifulSoup(html, "html.parser")
                # Remove scripts, styles, nav, footers
                for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                    tag.decompose()

                if not title:
                    title_tag = soup.find("title") or soup.find("h1")
                    if title_tag:
                        title = title_tag.get_text().strip()

                # Collect paragraph text
                paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
                text = "\n\n".join(paragraphs)
            except Exception as e:
                error_logger.warning(f"BS4 extraction error on {url}: {e}")
                return None

        if not text:
            return None

        # Clean text
        words = text.split()
        if len(words) < min_words:
            return None

        return {
            "url": url,
            "domain": self.get_domain(url),
            "title": title,
            "text": text,
            "date": date,
            "word_count": len(words)
        }
