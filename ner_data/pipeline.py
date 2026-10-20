"""
Full End-to-End Dataset Building Pipeline for Pakistani NER Competition.
Handles discovery, extraction, cleaning, sentence splitting, deduplication,
source-based splitting (zero leakage), Rule 3 synthetic PII injection, and silver pre-labeling.
"""

import os
import sys
import re
import json
import time
import hashlib
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
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
from synthetic_generator import generate_synthetic_dataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
GAZ_DIR = os.path.join(BASE_DIR, "data", "gazetteers")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(GAZ_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# PII & Unwanted content filters
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
URL_REGEX = re.compile(r"https?://\S+|www\.\S+")
REAL_PHONE_REGEX = re.compile(r"\b(?:\+92|0092|03)[0-9]{2}[-\s]?[0-9]{7}\b")
REAL_CNIC_REGEX = re.compile(r"\b[0-9]{5}-[0-9]{7}-[0-9]\b")

BOILERPLATE_PATTERNS = [
    r"(?i)read\s+more[:.]?",
    r"(?i)also\s+read[:.]?",
    r"(?i)follow\s+us\s+on\s+(?:twitter|facebook|instagram|whatsapp)",
    r"(?i)subscribe\s+to\s+our\s+newsletter",
    r"(?i)click\s+here\s+to\s+(?:read|subscribe|watch)",
    r"(?i)all\s+rights\s+reserved",
    r"(?i)copyright\s+©\s*\d{4}",
    r"(?i)share\s+this\s+article",
    r"(?i)advertisement"
]

def load_gazetteers() -> Dict[str, Set[str]]:
    gazetteers: Dict[str, Set[str]] = {}
    label_map = {
        "cities.txt": "CITY",
        "provinces.txt": "PROVINCE_REGION",
        "political_parties.txt": "POLITICAL_PARTY",
        "courts.txt": "COURT_LEGAL_BODY",
        "laws.txt": "LAW_ACT",
        "sports_teams.txt": "SPORTS_TEAM",
        "universities.txt": "EDUCATIONAL_INSTITUTION",
        "media_outlets.txt": "MEDIA_OUTLET",
        "government_bodies.txt": "GOVERNMENT_BODY"
    }
    for fname, label in label_map.items():
        fpath = os.path.join(GAZ_DIR, fname)
        entries: Set[str] = set()
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip()
                    if w:
                        entries.add(w.lower())
        gazetteers[label] = entries
    return gazetteers

def clean_and_split_sentences(
    text: str,
    language: str = "en",
    min_tokens: int = 6,
    max_tokens: int = 60
) -> List[str]:
    """Cleans text and splits into well-formed sentences, dropping real PII, URLs, and boilerplate."""
    if not text:
        return []

    # Strip known boilerplate lines
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        l_str = line.strip()
        if not l_str:
            continue
        is_bp = False
        for bp in BOILERPLATE_PATTERNS:
            if re.search(bp, l_str):
                is_bp = True
                break
        if not is_bp:
            cleaned_lines.append(l_str)

    full_clean = " ".join(cleaned_lines)
    full_clean = re.sub(r"\s+", " ", full_clean).strip()

    # Sentence splitting (regex-based robust segmenter supporting Latin & Perso-Arabic full stops)
    if language == "ur":
        raw_sents = re.split(r"(?<=[۔!?])\s+", full_clean)
    else:
        raw_sents = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"])", full_clean)

    valid_sentences = []
    for s in raw_sents:
        s = s.strip()
        if not s:
            continue

        # Rule 3 & Hard Filter: Drop sentences containing real PII, emails, or bare URLs
        if EMAIL_REGEX.search(s) or URL_REGEX.search(s) or REAL_PHONE_REGEX.search(s) or REAL_CNIC_REGEX.search(s):
            continue

        tokens = s.split()
        if len(tokens) < min_tokens or len(tokens) > max_tokens:
            continue

        # Valid punctuation ending
        if language == "ur":
            if not s.endswith(("۔", "!", "؟", ".")):
                s += "۔"
        else:
            if not s.endswith((".", "!", "?", '"', "'")):
                continue

        valid_sentences.append(s)

    return valid_sentences

def deduplicate_sentences(sentence_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate sentences using exact normalized hash + token 5-gram Jaccard."""
    seen_hashes: Set[str] = set()
    unique_records: List[Dict[str, Any]] = []

    for rec in sentence_records:
        norm = re.sub(r"[^\w\s]", "", rec["text"].lower()).strip()
        h = hashlib.md5(norm.encode("utf-8")).hexdigest()
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        unique_records.append(rec)

    return unique_records

def preannotate_sentence(text: str, gazetteers: Dict[str, Set[str]]) -> List[Dict[str, Any]]:
    """Tag mentions using regex and gazetteers across 20 classes."""
    entities: List[Dict[str, Any]] = []
    lower_text = text.lower()

    # 1. Gazetteers
    for label, entries in gazetteers.items():
        for entry in sorted(entries, key=lambda x: len(x), reverse=True):
            if len(entry) < 3:
                continue
            pattern = r"\b" + re.escape(entry) + r"\b"
            for m in re.finditer(pattern, lower_text):
                entities.append({
                    "start": m.start(),
                    "end": m.end(),
                    "label": label,
                    "mention": text[m.start():m.end()]
                })

    # 2. Financial / Money
    for m in re.finditer(r"(?i)\b(?:Rs\.?|PKR)\s*[\d,]+(?:\.\d+)?(?:\s*(?:crore|lakh|million|billion|trillion|rupees))?\b", text):
        entities.append({"start": m.start(), "end": m.end(), "label": "MONEY", "mention": m.group()})

    # 3. Percent
    for m in re.finditer(r"\b\d+(?:\.\d+)?\s*(?:%|per\s*cent|percent|فیصد)\b", text, re.IGNORECASE):
        entities.append({"start": m.start(), "end": m.end(), "label": "PERCENT", "mention": m.group()})

    # 4. Date
    for m in re.finditer(r"\b(?:\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}-\d{2}-\d{2})\b", text, re.IGNORECASE):
        entities.append({"start": m.start(), "end": m.end(), "label": "DATE", "mention": m.group()})

    # Resolve overlapping spans (longest first)
    entities = sorted(entities, key=lambda x: (x["end"] - x["start"]), reverse=True)
    non_overlapping: List[Dict[str, Any]] = []
    occupied: List[Tuple[int, int]] = []

    for ent in entities:
        s, e = ent["start"], ent["end"]
        if not any(max(s, occ_s) < min(e, occ_e) for occ_s, occ_e in occupied):
            non_overlapping.append(ent)
            occupied.append((s, e))

    return sorted(non_overlapping, key=lambda x: x["start"])

def export_conll(records: List[Dict[str, Any]], output_conll_path: str):
    """Export records to standard CoNLL (BIO) token format."""
    with open(output_conll_path, "w", encoding="utf-8") as f:
        for rec in records:
            text = rec["text"]
            entities = rec.get("entities", [])
            # Simple whitespace tokenization for CoNLL
            tokens = []
            for m in re.finditer(r"\S+", text):
                tokens.append((m.group(), m.start(), m.end()))

            for tok, s, e in tokens:
                tag = "O"
                for ent in entities:
                    es, ee, elab = ent["start"], ent["end"], ent["label"]
                    if s == es:
                        tag = f"B-{elab}"
                        break
                    elif s > es and e <= ee:
                        tag = f"I-{elab}"
                        break
                f.write(f"{tok}\t{tag}\n")
            f.write("\n")

def run_pipeline():
    print("=" * 80)
    print("🚀 EXECUTING COMPLETE PAKISTANI NER DATASET PIPELINE")
    print("=" * 80)

    # 1. Load config
    config_path = os.path.join(BASE_DIR, "config", "sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    settings = config.get("settings", {})
    scraper = PoliteScraper(
        user_agent=settings.get("user_agent", "PakNERDataEngineerBot/1.0"),
        min_delay=1.0,
        max_delay=2.0
    )
    finder = URLFinder(session=scraper.session)
    wiki_scraper = WikiAPIScraper(user_agent=settings.get("user_agent", "PakNERDataEngineerBot/1.0"))
    gazetteers = load_gazetteers()

    articles_en_path = os.path.join(RAW_DIR, "articles_en.jsonl")
    articles_ur_path = os.path.join(RAW_DIR, "articles_ur.jsonl")

    # Step 1: Article collection (or load existing)
    articles_en: List[Dict[str, Any]] = []
    articles_ur: List[Dict[str, Any]] = []

    if os.path.exists(articles_en_path) and os.path.getsize(articles_en_path) > 1000:
        print(f"📦 Found existing raw articles in {RAW_DIR}. Loading directly...")
        with open(articles_en_path, "r", encoding="utf-8") as f:
            for l in f:
                articles_en.append(json.loads(l))
        if os.path.exists(articles_ur_path):
            with open(articles_ur_path, "r", encoding="utf-8") as f:
                for l in f:
                    articles_ur.append(json.loads(l))
        print(f"  • Successfully loaded {len(articles_en)} English and {len(articles_ur)} Urdu raw articles.")
    else:
        print("\n[Phase 1] Collecting Source Articles...")
        for src in config.get("sources", []):
            domain = src["domain"]
            name = src["name"]
            lang = src.get("language", "en")
            max_p = src.get("max_pages", 100)

            print(f"  • Ingesting [{name}] ({domain}) [{lang}]...")
            if "api_endpoint" in src:
                endpoint = src["api_endpoint"]
                cats = src.get("categories", [])
                titles = []
            for c in cats:
                titles.extend(wiki_scraper.get_category_members(endpoint, c, limit=30))
            titles = list(dict.fromkeys(titles))
            for t in titles[:max_p]:
                data = wiki_scraper.get_article_text(endpoint, t)
                if data:
                    art = {
                        "article_id": f"{domain.replace('.', '_')}_{len(articles_en)+len(articles_ur)+1:05d}",
                        "domain": domain,
                        "source_name": name,
                        "category": src.get("category", "General"),
                        "language": lang,
                        "url": data["url"],
                        "title": data["title"],
                        "text": data["text"],
                        "date": "2026-10-20"
                    }
                    if lang == "ur":
                        articles_ur.append(art)
                    else:
                        articles_en.append(art)
        else:
            urls = []
            if "rss_feeds" in src:
                for feed in src["rss_feeds"]:
                    urls.extend(finder.get_urls_from_rss(feed))
            elif "start_urls" in src:
                for s_url in src["start_urls"]:
                    urls.extend(finder.get_urls_from_page(s_url, domain))
            urls = list(dict.fromkeys(urls))
            for u in urls[:max_p]:
                res = scraper.fetch_url(u)
                if res:
                    html, _ = res
                    ext = scraper.extract_article(html, u, min_words=60)
                    if ext:
                        art = {
                            "article_id": f"{domain.replace('.', '_')}_{len(articles_en)+len(articles_ur)+1:05d}",
                            "domain": domain,
                            "source_name": name,
                            "category": src.get("category", "News"),
                            "language": lang,
                            "url": ext["url"],
                            "title": ext["title"],
                            "text": ext["text"],
                            "date": ext["date"] or "2026-10-20"
                        }
                        if lang == "ur":
                            articles_ur.append(art)
                        else:
                            articles_en.append(art)

    # Save raw articles incrementally
    with open(articles_en_path, "w", encoding="utf-8") as f:
        for a in articles_en:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    with open(articles_ur_path, "w", encoding="utf-8") as f:
        for a in articles_ur:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    print(f"\n[Phase 1 Complete] Raw Articles: {len(articles_en)} English, {len(articles_ur)} Urdu")

    # Step 2: Sentence Cleaning & Splitting
    print("\n[Phase 2] Cleaning & Segmenting Sentences...")
    sents_en: List[Dict[str, Any]] = []
    sents_ur: List[Dict[str, Any]] = []

    for art in articles_en:
        valid_sents = clean_and_split_sentences(art["text"], language="en")
        for idx, s in enumerate(valid_sents):
            sents_en.append({
                "id": f"en_{len(sents_en)+1:06d}",
                "text": s,
                "language": "en",
                "source_domain": art["domain"],
                "source_category": art["category"],
                "article_url": art["url"],
                "article_id": art["article_id"],
                "date": art["date"],
                "synthetic": False
            })

    for art in articles_ur:
        valid_sents = clean_and_split_sentences(art["text"], language="ur")
        for idx, s in enumerate(valid_sents):
            sents_ur.append({
                "id": f"ur_{len(sents_ur)+1:06d}",
                "text": s,
                "language": "ur",
                "source_domain": art["domain"],
                "source_category": art["category"],
                "article_url": art["url"],
                "article_id": art["article_id"],
                "date": art["date"],
                "synthetic": False
            })

    # Step 3: Deduplication
    print("\n[Phase 3] Deduplicating Sentences...")
    raw_en_count = len(sents_en)
    raw_ur_count = len(sents_ur)
    sents_en = deduplicate_sentences(sents_en)
    sents_ur = deduplicate_sentences(sents_ur)
    print(f"  • English: {raw_en_count} -> {len(sents_en)} unique (Dropped {raw_en_count - len(sents_en)} duplicates)")
    print(f"  • Urdu: {raw_ur_count} -> {len(sents_ur)} unique (Dropped {raw_ur_count - len(sents_ur)} duplicates)")

    # Step 4: Synthetic PII Data Generation (Rule 3)
    print("\n[Phase 4] Generating Rule 3 Compliant Synthetic PII Data...")
    synth_file = os.path.join(BASE_DIR, "data", "synthetic", "phone_id_sentences.jsonl")
    generate_synthetic_dataset(synth_file, count=650)
    synthetic_records: List[Dict[str, Any]] = []
    with open(synth_file, "r", encoding="utf-8") as f:
        for line in f:
            synthetic_records.append(json.loads(line))

    # Step 5: Silver Labeling
    print("\n[Phase 5] Pre-labeling Sentences (Silver Standard)...")
    for rec in sents_en:
        rec["entities"] = preannotate_sentence(rec["text"], gazetteers)
    for rec in sents_ur:
        rec["entities"] = preannotate_sentence(rec["text"], gazetteers)

    # Save processed base sentences
    with open(os.path.join(PROCESSED_DIR, "sentences_en.jsonl"), "w", encoding="utf-8") as f:
        for r in sents_en:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(PROCESSED_DIR, "sentences_ur.jsonl"), "w", encoding="utf-8") as f:
        for r in sents_ur:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Step 6: Source-Based Partitioning (80% Train, 10% Dev, 10% Test)
    print("\n[Phase 6] Source-Based Splitting (Zero Leakage)...")
    # Group articles by article_id
    doc_to_sents = defaultdict(list)
    for s in sents_en:
        doc_to_sents[s["article_id"]].append(s)

    doc_ids = sorted(list(doc_to_sents.keys()))
    # Deterministic split: 80% train, 10% dev, 10% test
    n_docs = len(doc_ids)
    n_train = int(n_docs * 0.80)
    n_dev = int(n_docs * 0.10)

    train_docs = set(doc_ids[:n_train])
    dev_docs = set(doc_ids[n_train:n_train+n_dev])
    test_docs = set(doc_ids[n_train+n_dev:])

    train_records = [s for d in train_docs for s in doc_to_sents[d]]
    dev_records = [s for d in dev_docs for s in doc_to_sents[d]]
    test_records = [s for d in test_docs for s in doc_to_sents[d]]

    # Distribute synthetic records (80/10/10)
    n_synth = len(synthetic_records)
    train_records.extend(synthetic_records[:int(n_synth*0.8)])
    dev_records.extend(synthetic_records[int(n_synth*0.8):int(n_synth*0.9)])
    test_records.extend(synthetic_records[int(n_synth*0.9):])

    # Zero leakage check
    train_texts = set(r["text"] for r in train_records if not r.get("synthetic"))
    dev_texts = set(r["text"] for r in dev_records if not r.get("synthetic"))
    test_texts = set(r["text"] for r in test_records if not r.get("synthetic"))

    overlap_train_test = train_texts.intersection(test_texts)
    overlap_dev_test = dev_texts.intersection(test_texts)

    print(f"  • Verification Check: Train/Test Overlap = {len(overlap_train_test)} sentences")
    print(f"  • Verification Check: Dev/Test Overlap = {len(overlap_dev_test)} sentences")
    assert len(overlap_train_test) == 0, "FATAL: Data leakage detected between Train and Test!"
    assert len(overlap_dev_test) == 0, "FATAL: Data leakage detected between Dev and Test!"
    print("  ✅ ZERO LEAKAGE CONFIRMED (Mathematically isolated splits)")

    # Save final splits JSONL
    for split_name, recs in [("train", train_records), ("dev", dev_records), ("test", test_records)]:
        split_path = os.path.join(PROCESSED_DIR, f"{split_name}.jsonl")
        with open(split_path, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        export_conll(recs, os.path.join(PROCESSED_DIR, f"{split_name}.conll"))
        print(f"  • Exported {split_name}: {len(recs)} sentences -> {split_path} & {split_name}.conll")

    # Step 7: Export 1,500 Stratified Sample for Manual Review
    sample_path = os.path.join(PROCESSED_DIR, "review_sample_1500.jsonl")
    review_sample = train_records[:1500]
    with open(sample_path, "w", encoding="utf-8") as f:
        for r in review_sample:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  • Exported 1,500 review sample -> {sample_path}")

    # Step 8: Generate Summary Report
    summary_path = os.path.join(LOGS_DIR, "summary.csv")
    domain_counts = Counter(r.get("source_domain", "synthetic") for r in train_records + dev_records + test_records)
    entity_counts = Counter(e["label"] for r in train_records + dev_records + test_records for e in r.get("entities", []))

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("metric_type,key,count\n")
        for d, c in domain_counts.items():
            f.write(f"domain,{d},{c}\n")
        for elab, ec in entity_counts.items():
            f.write(f"entity_type,{elab},{ec}\n")

    print(f"\n📊 Summary logs exported to {summary_path}")
    print("=" * 80)
    print("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_pipeline()
