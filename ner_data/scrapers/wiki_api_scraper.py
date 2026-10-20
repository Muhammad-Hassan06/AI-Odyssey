import os
import time
import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("wiki_api")

class WikiAPIScraper:
    """Official MediaWiki API scraper for English and Urdu Wikipedia categories."""

    def __init__(self, user_agent: str = "PakNERDataEngineerBot/1.0 (academic-nlp-research)"):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def search_articles(self, endpoint: str, query: str, limit: int = 50) -> List[str]:
        """Search Wikipedia articles matching query keywords."""
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json"
        }
        titles = []
        try:
            resp = self.session.get(endpoint, params=params, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("query", {}).get("search", [])
                for r in results:
                    titles.append(r["title"])
        except Exception as e:
            logger.warning(f"Failed to search {query} on {endpoint}: {e}")
        return titles

    def get_category_members(self, endpoint: str, category_title: str, limit: int = 50) -> List[str]:
        """Fetch article page titles in a given Wikipedia category."""
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmlimit": limit,
            "cmtype": "page",
            "format": "json"
        }
        titles = []
        try:
            resp = self.session.get(endpoint, params=params, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                members = data.get("query", {}).get("categorymembers", [])
                for m in members:
                    titles.append(m["title"])
        except Exception as e:
            logger.warning(f"Failed to query category {category_title} on {endpoint}: {e}")
        return titles

    def get_article_text(self, endpoint: str, title: str) -> Optional[Dict[str, Any]]:
        """Fetch plain-text extract of a Wikipedia article."""
        params = {
            "action": "query",
            "prop": "extracts|info",
            "inprop": "url",
            "explaintext": 1,
            "exsectionformat": "plain",
            "titles": title,
            "format": "json"
        }
        try:
            time.sleep(0.5)  # Respectful API delay
            resp = self.session.get(endpoint, params=params, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    if page_id == "-1":
                        continue
                    extract = page_data.get("extract", "")
                    url = page_data.get("fullurl", f"{endpoint}?curid={page_id}")
                    if extract and len(extract.split()) >= 60:
                        return {
                            "title": title,
                            "url": url,
                            "text": extract,
                            "word_count": len(extract.split())
                        }
        except Exception as e:
            logger.warning(f"Failed to fetch Wikipedia article {title}: {e}")
        return None
