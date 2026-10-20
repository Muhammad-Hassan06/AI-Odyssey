"""
High-Yield Scale Collector for Pakistani-Context NER Corpus.
Collects 20,000+ English sentences and 5,000+ Urdu sentences across polite Pakistani news feeds and Wikipedia APIs.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Set
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from scrapers.base_scraper import PoliteScraper
from scrapers.rss_sitemap_finder import URLFinder
from scrapers.wiki_api_scraper import WikiAPIScraper

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Expanded high-yield Wikipedia categories covering all 20 classes
EN_WIKI_CATEGORIES = [
    "Category:Cities and towns in Pakistan",
    "Category:Provinces and territories of Pakistan",
    "Category:Districts of Pakistan",
    "Category:Politics of Pakistan",
    "Category:Political parties in Pakistan",
    "Category:Judiciary of Pakistan",
    "Category:Supreme Court of Pakistan",
    "Category:Universities and colleges in Pakistan",
    "Category:Pakistani media",
    "Category:Newspapers published in Pakistan",
    "Category:Television stations in Pakistan",
    "Category:Cricket in Pakistan",
    "Category:Pakistan Super League",
    "Category:Pakistani legislation",
    "Category:Constitution of Pakistan",
    "Category:Events in Pakistan",
    "Category:Economy of Pakistan",
    "Category:Companies of Pakistan",
    "Category:Banks of Pakistan",
    "Category:Government agencies of Pakistan",
    "Category:Federal ministries of Pakistan",
    "Category:Law enforcement in Pakistan",
    "Category:Landmarks in Pakistan",
    "Category:Airports in Pakistan",
    "Category:Archaeological sites in Pakistan"
]

UR_WIKI_CATEGORIES = [
    "زمرہ:پاکستان",
    "زمرہ:پاکستانی سیاست",
    "زمرہ:پاکستان کے شہر",
    "زمرہ:پاکستان کی معیشت",
    "زمرہ:پاکستان میں کھیل",
    "زمرہ:پاکستانی شخصیات",
    "زمرہ:پاکستان کی جامعات",
    "زمرہ:عدالت عظمیٰ پاکستان",
    "زمرہ:پاکستان کے اضلاع",
    "زمرہ:پاکستان کے صوبے",
    "زمرہ:پاکستانی اخبارات",
    "زمرہ:پاکستانی کرکٹ",
    "زمرہ:پاکستان کی تاریخ",
    "زمرہ:پاکستان کے قومی نشانات",
    "زمرہ:حکومت پاکستان"
]

RSS_SOURCES = [
    {
        "domain": "thenews.com.pk",
        "name": "The News International",
        "category": "News/National",
        "language": "en",
        "feeds": [
            "https://www.thenews.com.pk/rss/1/1",
            "https://www.thenews.com.pk/rss/1/2",
            "https://www.thenews.com.pk/rss/1/4",
            "https://www.thenews.com.pk/rss/1/5",
            "https://www.thenews.com.pk/rss/1/6"
        ],
        "max": 200
    },
    {
        "domain": "brecorder.com",
        "name": "Business Recorder",
        "category": "Business/Finance",
        "language": "en",
        "feeds": [
            "https://www.brecorder.com/feeds/latest-news",
            "https://www.brecorder.com/feeds/pakistan",
            "https://www.brecorder.com/feeds/markets"
        ],
        "max": 150
    },
    {
        "domain": "app.com.pk",
        "name": "Associated Press of Pakistan",
        "category": "News/StateWire",
        "language": "en",
        "feeds": [
            "https://www.app.com.pk/national/feed/",
            "https://www.app.com.pk/business/feed/",
            "https://www.app.com.pk/sports/feed/",
            "https://www.app.com.pk/features/feed/"
        ],
        "max": 150
    },
    {
        "domain": "geo.tv",
        "name": "Geo News",
        "category": "News/Broadcast",
        "language": "en",
        "feeds": [
            "https://www.geo.tv/rss/1/1",
            "https://www.geo.tv/rss/1/2"
        ],
        "max": 150
    },
    {
        "domain": "arynews.tv",
        "name": "ARY News",
        "category": "News/Broadcast",
        "language": "en",
        "feeds": [
            "https://arynews.tv/feed/",
            "https://arynews.tv/category/pakistan/feed/",
            "https://arynews.tv/category/business/feed/",
            "https://arynews.tv/category/sports/feed/"
        ],
        "max": 150
    },
    {
        "domain": "express.pk",
        "name": "Express News Urdu",
        "category": "News/Urdu",
        "language": "ur",
        "feeds": [
            "https://www.express.pk/feed/",
            "https://www.express.pk/pakistan/feed/",
            "https://www.express.pk/business/feed/"
        ],
        "max": 150
    },
    {
        "domain": "bbc.com",
        "name": "BBC Urdu",
        "category": "News/Urdu",
        "language": "ur",
        "feeds": [
            "https://feeds.bbci.co.uk/urdu/rss.xml"
        ],
        "max": 100
    }
]

def run_scale_collection():
    print("=" * 80)
    print("🚀 LAUNCHING HIGH-YIELD DATASET SCALE COLLECTOR")
    print("   Targets: 20,000+ Clean English Sentences | 5,000+ Clean Urdu Sentences")
    print("=" * 80)

    scraper = PoliteScraper(
        user_agent="PakNERDataEngineerBot/1.0 (+https://github.com/Muhammad-Hassan06/AI-Odyssey; academic-nlp-research)",
        min_delay=1.0,
        max_delay=2.0
    )
    finder = URLFinder(session=scraper.session)
    wiki = WikiAPIScraper(user_agent="PakNERDataEngineerBot/1.0 (academic-nlp-research)")

    en_articles: List[Dict[str, Any]] = []
    ur_articles: List[Dict[str, Any]] = []

    # 1. Load existing smoke test articles first (incremental progress preservation)
    smoke_file = os.path.join(RAW_DIR, "smoke_test_articles.jsonl")
    seen_urls: Set[str] = set()
    if os.path.exists(smoke_file):
        with open(smoke_file, "r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                seen_urls.add(rec["url"])
                if rec["language"] == "ur":
                    ur_articles.append(rec)
                else:
                    en_articles.append(rec)
        print(f"📦 Loaded {len(en_articles)} existing EN and {len(ur_articles)} existing UR articles from smoke test.")

    # 2. Wikipedia English Category Crawl (High Volume, Zero Blocks, 25 Categories)
    print("\n📚 [Step 1] Ingesting English Wikipedia Pakistan Knowledge Base...")
    en_endpoint = "https://en.wikipedia.org/w/api.php"
    for cat in EN_WIKI_CATEGORIES:
        titles = wiki.get_category_members(en_endpoint, cat, limit=35)
        print(f"  • {cat}: Discovered {len(titles)} titles")
        for t in titles:
            data = wiki.get_article_text(en_endpoint, t)
            if data and data["url"] not in seen_urls:
                seen_urls.add(data["url"])
                art = {
                    "article_id": f"en_wiki_{len(en_articles)+1:05d}",
                    "domain": "en.wikipedia.org",
                    "source_name": "English Wikipedia",
                    "category": cat.replace("Category:", ""),
                    "language": "en",
                    "url": data["url"],
                    "title": data["title"],
                    "text": data["text"],
                    "word_count": data["word_count"],
                    "date": "2026-10-20"
                }
                en_articles.append(art)
        print(f"    Total English Articles so far: {len(en_articles)}")

    # 3. Wikipedia Urdu Category Crawl (Bonus Corpus, 15 Categories)
    print("\n📚 [Step 2] Ingesting Urdu Wikipedia Knowledge Base...")
    ur_endpoint = "https://ur.wikipedia.org/w/api.php"
    for cat in UR_WIKI_CATEGORIES:
        titles = wiki.get_category_members(ur_endpoint, cat, limit=30)
        print(f"  • {cat}: Discovered {len(titles)} Urdu titles")
        for t in titles:
            data = wiki.get_article_text(ur_endpoint, t)
            if data and data["url"] not in seen_urls:
                seen_urls.add(data["url"])
                art = {
                    "article_id": f"ur_wiki_{len(ur_articles)+1:05d}",
                    "domain": "ur.wikipedia.org",
                    "source_name": "Urdu Wikipedia",
                    "category": cat.replace("زمرہ:", ""),
                    "language": "ur",
                    "url": data["url"],
                    "title": data["title"],
                    "text": data["text"],
                    "word_count": data["word_count"],
                    "date": "2026-10-20"
                }
                ur_articles.append(art)
        print(f"    Total Urdu Articles so far: {len(ur_articles)}")

    # 4. News RSS Feeds
    print("\n📰 [Step 3] Ingesting Pakistani News Outlets via RSS...")
    for src in RSS_SOURCES:
        domain = src["domain"]
        name = src["name"]
        lang = src["language"]
        max_p = src["max"]
        print(f"  • Crawling {name} ({domain}) [{lang}]...")

        feed_urls: List[str] = []
        for feed in src["feeds"]:
            feed_urls.extend(finder.get_urls_from_rss(feed))
        feed_urls = list(dict.fromkeys(feed_urls))
        print(f"    Discovered {len(feed_urls)} feed links from {domain}")

        count = 0
        for u in feed_urls[:max_p]:
            if u in seen_urls:
                continue
            if domain in scraper.blocked_domains:
                print(f"    ⚠️ {domain} blocked. Skipping.")
                break

            html, status = scraper.fetch_url(u)
            if status in (403, 429):
                print(f"    ⚠️ {domain} returned HTTP {status}. Skipping.")
                break

            if html:
                ext = scraper.extract_article(html, u, min_words=60)
                if ext:
                    seen_urls.add(u)
                    art = {
                        "article_id": f"{domain.replace('.', '_')}_{len(en_articles)+len(ur_articles)+1:05d}",
                        "domain": domain,
                        "source_name": name,
                        "category": src["category"],
                        "language": lang,
                        "url": ext["url"],
                        "title": ext["title"],
                        "text": ext["text"],
                        "word_count": ext["word_count"],
                        "date": ext["date"] or "2026-10-20"
                    }
                    if lang == "ur":
                        ur_articles.append(art)
                    else:
                        en_articles.append(art)
                    count += 1

        print(f"    Extracted {count} articles from {domain}")

    # Save final raw sets
    raw_en_file = os.path.join(RAW_DIR, "articles_en.jsonl")
    raw_ur_file = os.path.join(RAW_DIR, "articles_ur.jsonl")

    with open(raw_en_file, "w", encoding="utf-8") as f:
        for a in en_articles:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    with open(raw_ur_file, "w", encoding="utf-8") as f:
        for a in ur_articles:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    total_en_words = sum(a["word_count"] for a in en_articles)
    total_ur_words = sum(a["word_count"] for a in ur_articles)

    print("\n" + "=" * 80)
    print("📊 RAW COLLECTION COMPLETE")
    print("=" * 80)
    print(f"• English Articles: {len(en_articles)} | Total Words: {total_en_words:,} (Saved -> {raw_en_file})")
    print(f"• Urdu Articles:    {len(ur_articles)} | Total Words: {total_ur_words:,} (Saved -> {raw_ur_file})")
    print("=" * 80)

if __name__ == "__main__":
    run_scale_collection()
