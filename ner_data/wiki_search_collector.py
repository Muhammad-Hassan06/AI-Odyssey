"""
Dedicated Wikipedia Search Ingestion Script for Pakistani-Context NER Corpus.
Collects hundreds of in-depth articles across English and Urdu using MediaWiki Search API.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from scrapers.wiki_api_scraper import WikiAPIScraper

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

EN_QUERIES = [
    "Politics of Pakistan", "Government of Pakistan", "Supreme Court of Pakistan", "Constitution of Pakistan",
    "Pakistan Penal Code", "High Court Pakistan", "State Bank of Pakistan", "Federal Board of Revenue",
    "Pakistan Stock Exchange", "Pakistan Super League", "Pakistan national cricket team", "Cities in Pakistan",
    "Districts of Pakistan", "Provinces of Pakistan", "Universities in Pakistan", "LUMS Pakistan",
    "NUST Pakistan", "Higher Education Commission Pakistan", "Pakistan Railways", "Pakistan International Airlines",
    "Edhi Foundation", "Elections in Pakistan", "National Assembly of Pakistan", "Senate of Pakistan",
    "Media of Pakistan", "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Quetta", "Multan", "Faisalabad"
]

UR_QUERIES = [
    "پاکستان کی سیاست", "حکومت پاکستان", "عدالت عظمیٰ پاکستان", "آئین پاکستان", "پاکستان کی معیشت",
    "اسٹیٹ بینک آف پاکستان", "پاکستان کے شہر", "پاکستان کے اضلاع", "پاکستان کی جامعات", "پاکستان کرکٹ ٹیم",
    "پاکستان سپر لیگ", "کراچی", "لاہور", "اسلام آباد", "پشاور", "کوئٹہ", "سندھ", "پنجاب، پاکستان",
    "خیبر پختونخوا", "بلوچستان", "روزنامہ جنگ", "روزنامہ ایکسپریس", "پاکستان تحریک انصاف", "مسلم لیگ ن", "پیپلز پارٹی"
]

def run_wiki_search_collection():
    print("=" * 80)
    print("🔍 EXPANDED WIKIPEDIA SEARCH CRAWLER (English & Urdu)")
    print("=" * 80)

    wiki = WikiAPIScraper(user_agent="PakNERDataEngineerBot/1.0 (academic-nlp-research)")
    en_endpoint = "https://en.wikipedia.org/w/api.php"
    ur_endpoint = "https://ur.wikipedia.org/w/api.php"

    en_file = os.path.join(RAW_DIR, "wiki_search_en.jsonl")
    ur_file = os.path.join(RAW_DIR, "wiki_search_ur.jsonl")

    seen_titles_en: Set[str] = set()
    seen_titles_ur: Set[str] = set()

    en_articles: List[Dict[str, Any]] = []
    ur_articles: List[Dict[str, Any]] = []

    print("\n[EN Search] Querying 33 English Topics...")
    for q in EN_QUERIES:
        titles = wiki.search_articles(en_endpoint, q, limit=15)
        for t in titles:
            if t in seen_titles_en:
                continue
            seen_titles_en.add(t)
            data = wiki.get_article_text(en_endpoint, t)
            if data and data["word_count"] >= 60:
                art = {
                    "article_id": f"wiki_en_{len(en_articles)+1:05d}",
                    "domain": "en.wikipedia.org",
                    "source_name": "English Wikipedia",
                    "category": "Knowledge",
                    "language": "en",
                    "url": data["url"],
                    "title": data["title"],
                    "text": data["text"],
                    "word_count": data["word_count"],
                    "date": "2026-10-20"
                }
                en_articles.append(art)
        print(f"  • Q: '{q}' -> Total EN Articles: {len(en_articles)}")

    with open(en_file, "w", encoding="utf-8") as f:
        for a in en_articles:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    print(f"✅ Saved {len(en_articles)} English Wikipedia articles -> {en_file}")

    print("\n[UR Search] Querying 25 Urdu Topics...")
    for q in UR_QUERIES:
        titles = wiki.search_articles(ur_endpoint, q, limit=15)
        for t in titles:
            if t in seen_titles_ur:
                continue
            seen_titles_ur.add(t)
            data = wiki.get_article_text(ur_endpoint, t)
            if data and data["word_count"] >= 60:
                art = {
                    "article_id": f"wiki_ur_{len(ur_articles)+1:05d}",
                    "domain": "ur.wikipedia.org",
                    "source_name": "Urdu Wikipedia",
                    "category": "Knowledge/Urdu",
                    "language": "ur",
                    "url": data["url"],
                    "title": data["title"],
                    "text": data["text"],
                    "word_count": data["word_count"],
                    "date": "2026-10-20"
                }
                ur_articles.append(art)
        print(f"  • Q: '{q}' -> Total UR Articles: {len(ur_articles)}")

    with open(ur_file, "w", encoding="utf-8") as f:
        for a in ur_articles:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    print(f"✅ Saved {len(ur_articles)} Urdu Wikipedia articles -> {ur_file}")

if __name__ == "__main__":
    run_wiki_search_collection()
