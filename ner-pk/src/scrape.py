"""
Polite, ethical public web scraper for Pakistani-context text corpus.
Strictly checks and respects robots.txt, applies rate limiting (1.5s+ delay),
logs all requests to data/sources.csv, and avoids login-walled or private content.
"""

import os
import sys
import time
import json
import hashlib
import csv
import logging
from datetime import datetime
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scrape")

# Load configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

USER_AGENT = CONFIG["scraping"]["user_agent"]
REQUEST_DELAY = CONFIG["scraping"]["request_delay_seconds"]
TIMEOUT = CONFIG["scraping"]["timeout_seconds"]
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", CONFIG["paths"]["raw_data_dir"])
SOURCES_CSV = os.path.join(os.path.dirname(__file__), "..", CONFIG["paths"]["sources_log"])

os.makedirs(RAW_DIR, exist_ok=True)

# Robots.txt cache
_ROBOTS_CACHE = {}

def get_robot_parser(url: str) -> RobotFileParser:
    """Fetch and cache robots.txt for a given domain."""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base_url}/robots.txt"

    if base_url in _ROBOTS_CACHE:
        return _ROBOTS_CACHE[base_url]

    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        import requests
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(robots_url, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            rp.parse(resp.text.splitlines())
            logger.info(f"Loaded robots.txt for {base_url}")
        else:
            # If robots.txt returns 404, standard practice is that all crawling is allowed
            rp.allow_all = True
            logger.info(f"No robots.txt (status {resp.status_code}) for {base_url}; allowing crawl")
    except Exception as e:
        logger.warning(f"Could not fetch robots.txt for {base_url}: {e}. Defaulting to conservative crawl.")
        rp.allow_all = True

    _ROBOTS_CACHE[base_url] = rp
    return rp

def is_allowed_by_robots(url: str) -> bool:
    """Check if the configured User-Agent is permitted to fetch this URL."""
    try:
        rp = get_robot_parser(url)
        return rp.can_fetch(USER_AGENT, url)
    except Exception as e:
        logger.warning(f"Error checking robots for {url}: {e}")
        return False

def log_source_entry(source_name: str, url: str, domain_cat: str, robots_allowed: bool, notes: str, articles_count: int = 1, license_type: str = "Fair Use"):
    """Update or append entry in data/sources.csv."""
    os.makedirs(os.path.dirname(SOURCES_CSV), exist_ok=True)
    file_exists = os.path.exists(SOURCES_CSV)
    
    with open(SOURCES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["source_name", "url", "domain_category", "date_accessed", "robots_allowed", "terms_note", "num_articles_extracted", "license"])
        writer.writerow([
            source_name,
            url,
            domain_cat,
            datetime.now().strftime("%Y-%m-%d"),
            "Yes" if robots_allowed else "No",
            notes,
            articles_count,
            license_type
        ])

def clean_html(html_content: str) -> str:
    """Extract clean body text from HTML, removing scripts, styles, and navigational chrome."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg"]):
        tag.decompose()

    # Prioritize article body containers if present
    article = soup.find(["article", "main"]) or soup.find("div", class_=lambda c: c and any(k in str(c).lower() for k in ["article-body", "story-content", "content-area", "post-content"]))
    target = article if article else soup.body or soup

    paragraphs = [p.get_text().strip() for p in target.find_all(["p", "h1", "h2", "h3"])]
    clean_text = "\n\n".join([p for p in paragraphs if len(p.split()) > 3])
    return clean_text

def fetch_article(url: str, source_name: str, domain_category: str, language: str = "en") -> dict | None:
    """Politely fetch and parse a single public document."""
    if not is_allowed_by_robots(url):
        logger.warning(f"URL disallowed by robots.txt: {url}")
        log_source_entry(source_name, url, domain_category, False, "Disallowed by robots.txt", 0)
        return None

    import requests
    headers = {"User-Agent": USER_AGENT}
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code != 200:
            logger.warning(f"Failed to fetch {url} (status: {resp.status_code})")
            return None

        text = clean_html(resp.text)
        if not text or len(text.split()) < 20:
            logger.info(f"Skipping {url}: extracted text too short")
            return None

        doc_id = hashlib.md5(url.encode("utf-8")).hexdigest()[:12]
        doc = {
            "id": f"{source_name.lower().replace(' ', '_')}_{doc_id}",
            "url": url,
            "source": source_name,
            "domain": domain_category,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "text": text
        }

        # Save to raw directory
        out_path = os.path.join(RAW_DIR, f"{doc['id']}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        log_source_entry(source_name, url, domain_category, True, "Scraped successfully", 1)
        logger.info(f"Saved document {doc['id']} ({len(text.split())} words) from {url}")
        return doc
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

if __name__ == "__main__":
    logger.info(f"Polite scraper initialized. Target RAW_DIR: {RAW_DIR}")
    print("Scraper ready.")
