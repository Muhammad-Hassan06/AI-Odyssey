"""
50-Article Smoke Test across priority domains.
Verifies polite crawling, robots.txt, rate limits, trafilatura extraction, and sentence yield.
"""

import os
import sys
import json
import time
from typing import Dict, List, Any
import yaml

# Add current dir to sys.path
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

def run_smoke_test(target_articles_per_domain: int = 50):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    settings = config.get("settings", {})
    scraper = PoliteScraper(
        user_agent=settings.get("user_agent", "PakNERDataEngineerBot/1.0"),
        min_delay=1.0,  # Fast polite delay for initial verification
        max_delay=2.0
    )
    finder = URLFinder(session=scraper.session)
    wiki_scraper = WikiAPIScraper(user_agent=settings.get("user_agent", "PakNERDataEngineerBot/1.0"))

    raw_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    smoke_raw_file = os.path.join(raw_dir, "smoke_test_articles.jsonl")

    # Pick top diverse domains for smoke test
    priority_domains = [
        "dawn.com",
        "tribune.com.pk",
        "thenews.com.pk",
        "brecorder.com",
        "pakistantoday.com.pk",
        "app.com.pk",
        "en.wikipedia.org",
        "ur.wikipedia.org"
    ]

    selected_sources = [s for s in config.get("sources", []) if s.get("domain") in priority_domains]

    domain_stats: Dict[str, Dict[str, Any]] = {}
    collected_articles: List[Dict[str, Any]] = []

    print(f"\n🚀 STARTING SMOKE TEST (Target: {target_articles_per_domain} articles per domain)")
    print("=" * 80)

    for src in selected_sources:
        domain = src["domain"]
        name = src["name"]
        lang = src.get("language", "en")
        print(f"\n🔍 Testing [{name}] ({domain}) - Lang: {lang}")

        domain_stats[domain] = {
            "name": name,
            "category": src.get("category", "General"),
            "language": lang,
            "urls_discovered": 0,
            "articles_extracted": 0,
            "total_words": 0,
            "avg_words": 0,
            "status": "Running"
        }

        # 1. Wikipedia API sources
        if "api_endpoint" in src:
            endpoint = src["api_endpoint"]
            cats = src.get("categories", [])
            titles = []
            for c in cats:
                members = wiki_scraper.get_category_members(endpoint, c, limit=25)
                titles.extend(members)
                if len(titles) >= target_articles_per_domain * 2:
                    break
            titles = list(dict.fromkeys(titles))
            domain_stats[domain]["urls_discovered"] = len(titles)
            print(f"  • Discovered {len(titles)} candidate topics from categories")

            count = 0
            for t in titles[:target_articles_per_domain]:
                data = wiki_scraper.get_article_text(endpoint, t)
                if data:
                    article_record = {
                        "article_id": f"{domain.replace('.', '_')}_{count+1:04d}",
                        "domain": domain,
                        "source_name": name,
                        "category": src.get("category", "Knowledge"),
                        "language": lang,
                        "url": data["url"],
                        "title": data["title"],
                        "text": data["text"],
                        "word_count": data["word_count"],
                        "date": "2026-10-20"
                    }
                    collected_articles.append(article_record)
                    count += 1
                    domain_stats[domain]["total_words"] += data["word_count"]
                    if count >= target_articles_per_domain:
                        break

            domain_stats[domain]["articles_extracted"] = count
            domain_stats[domain]["status"] = "Success" if count > 0 else "No Articles"

        # 2. RSS and Web News Sources
        else:
            urls: List[str] = []
            if "rss_feeds" in src:
                for feed in src["rss_feeds"]:
                    found = finder.get_urls_from_rss(feed)
                    urls.extend(found)
                    if len(urls) >= target_articles_per_domain * 2:
                        break
            elif "start_urls" in src:
                for s_url in src["start_urls"]:
                    found = finder.get_urls_from_page(s_url, domain)
                    urls.extend(found)

            urls = list(dict.fromkeys(urls))
            domain_stats[domain]["urls_discovered"] = len(urls)
            print(f"  • Discovered {len(urls)} candidate URLs from feeds/sitemaps")

            count = 0
            for u in urls[:target_articles_per_domain]:
                if domain in scraper.blocked_domains:
                    print(f"  ⚠️ Domain {domain} blocked. Skipping immediately to next domain.")
                    domain_stats[domain]["status"] = "Blocked (403/429)"
                    break

                html, status = scraper.fetch_url(u)
                if status in (403, 429):
                    print(f"  ⚠️ Domain {domain} returned HTTP {status}. Skipping immediately to next domain.")
                    domain_stats[domain]["status"] = f"Blocked ({status})"
                    break

                if html:
                    extracted = scraper.extract_article(html, u, min_words=settings.get("min_article_words", 80))
                    if extracted:
                        article_record = {
                            "article_id": f"{domain.replace('.', '_')}_{count+1:04d}",
                            "domain": domain,
                            "source_name": name,
                            "category": src.get("category", "News"),
                            "language": lang,
                            "url": extracted["url"],
                            "title": extracted["title"],
                            "text": extracted["text"],
                            "word_count": extracted["word_count"],
                            "date": extracted["date"] or "2026-10-20"
                        }
                        collected_articles.append(article_record)
                        count += 1
                        domain_stats[domain]["total_words"] += extracted["word_count"]
                        if count >= target_articles_per_domain:
                            break

            domain_stats[domain]["articles_extracted"] = count
            if domain_stats[domain]["status"] == "Running":
                domain_stats[domain]["status"] = "Success" if count > 0 else "Empty/Filtered"

        extracted_count = domain_stats[domain]["articles_extracted"]
        total_w = domain_stats[domain]["total_words"]
        avg_w = (total_w // extracted_count) if extracted_count > 0 else 0
        domain_stats[domain]["avg_words"] = avg_w
        print(f"  ✅ Extracted {extracted_count} articles (Avg {avg_w} words/article) from {domain}")

    # Save collected articles incrementally
    with open(smoke_raw_file, "w", encoding="utf-8") as f:
        for a in collected_articles:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    print("\n" + "=" * 80)
    print("📊 SMOKE TEST SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Domain':<22} | {'Category':<15} | {'Lang':<5} | {'URLs':<6} | {'Articles':<9} | {'Avg Words':<10} | {'Status'}")
    print("-" * 80)
    for d, st in domain_stats.items():
        print(f"{d:<22} | {st['category']:<15} | {st['language']:<5} | {st['urls_discovered']:<6} | {st['articles_extracted']:<9} | {st['avg_words']:<10} | {st['status']}")
    print("=" * 80)
    print(f"Total smoke test articles saved: {len(collected_articles)} -> {smoke_raw_file}\n")
    return domain_stats, collected_articles

if __name__ == "__main__":
    run_smoke_test(50)
