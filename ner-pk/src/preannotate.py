"""
Hybrid Pre-Annotation Engine for Pakistani-Context NER.
Combines deterministic regex rules, curated domain gazetteers, and context heuristics.
Enforces strict span boundary validation, priority conflict resolution, and the exact 20-class schema.
"""

import os
import sys
import re
import json
from typing import List, Dict, Any, Tuple

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES, validate_entity_type
from src.rules import extract_regex_entities

GAZETTEER_DIR = os.path.join(os.path.dirname(__file__), "gazetteers")

# Mapping gazetteer filename to Entity Type
GAZETTEER_MAP = {
    "provinces.json": "PROVINCE_REGION",
    "cities.json": "CITY",
    "political_parties.json": "POLITICAL_PARTY",
    "courts.json": "COURT_LEGAL_BODY",
    "government_bodies.json": "GOVERNMENT_BODY",
    "educational_institutions.json": "EDUCATIONAL_INSTITUTION",
    "media_outlets.json": "MEDIA_OUTLET",
    "sports_teams.json": "SPORTS_TEAM",
    "laws.json": "LAW_ACT",
    "landmarks.json": "LANDMARK_FACILITY"
}

# Country gazetteer
COUNTRIES = [
    "Pakistan", "China", "Saudi Arabia", "United States", "United Kingdom", "UK", "USA",
    "United Arab Emirates", "UAE", "India", "Afghanistan", "Iran", "Turkey", "Russia",
    "Qatar", "Kuwait", "Oman", "Bahrain", "Japan", "Germany", "France", "Canada",
    "پاکستان", "چین", "سعودی عرب", "افغانستان", "ایران", "ترکیہ"
]

# Additional curated Organizations
ORGANIZATIONS = [
    "Pakistan International Airlines", "PIA", "Pakistan Cricket Board", "PCB",
    "Oil and Gas Development Company Limited", "OGDCL", "Pakistan State Oil", "PSO",
    "Edhi Foundation", "Chhipa Welfare Association", "Saylani Welfare Trust",
    "Pakistan Railways", "Sui Northern Gas Pipelines Limited", "SNGPL",
    "Sui Southern Gas Company", "SSGC", "National Bank of Pakistan", "NBP",
    "Habib Bank Limited", "HBL", "United Bank Limited", "UBL", "MCB Bank", "Allied Bank",
    "Karachi Chamber of Commerce & Industry", "KCCI", "Supreme Court Bar Association", "SCBA",
    "Lahore Chamber of Commerce and Industry", "LCCI", "Pakistan Olympic Association"
]

# Prominent Pakistani Persons (names only; titles are strictly stripped per guidelines)
PROMINENT_PERSONS = [
    "Muhammad Ali Jinnah", "Quaid-e-Azam", "Fatima Jinnah", "Allama Iqbal", "Liaquat Ali Khan",
    "Zulfikar Ali Bhutto", "Benazir Bhutto", "Nawaz Sharif", "Shehbaz Sharif", "Maryam Nawaz",
    "Imran Khan", "Asif Ali Zardari", "Bilawal Bhutto Zardari", "Bilawal Bhutto",
    "Qazi Faez Isa", "Gulzar Ahmed", "Asif Saeed Khosa", "Saqib Nisar",
    "Abdul Qadeer Khan", "Abdus Salam", "Arshad Nadeem", "Babar Azam", "Shaheen Shah Afridi",
    "Mohammad Rizwan", "Wasim Akram", "Waqar Younis", "Jahangir Khan", "Jansher Khan",
    "قائد اعظم", "محمد علی جناح", "علامہ اقبال", "عمران خان", "نواز شریف", "شہباز شریف", "بلاول بھٹو زرداری"
]

# Prominent Events
KNOWN_EVENTS = [
    "Pakistan Super League", "PSL", "Independence Day", "Pakistan Day", "Defense Day",
    "Defence Day", "Youm-e-Takbir", "Kashmir Solidarity Day", "Eid-ul-Fitr", "Eid-ul-Adha",
    "Federal Budget", "Budget 2025-26", "Budget 2024-25", "General Elections 2024",
    "General Elections 2018", "SCO Summit", "COP29", "COP28", "2022 Pakistan floods"
]

def load_gazetteers() -> List[Tuple[re.Pattern, str, int]]:
    """Compile gazetteer terms into regex patterns with word boundaries and specificity priorities."""
    compiled_patterns = []

    for filename, label in GAZETTEER_MAP.items():
        fpath = os.path.join(GAZETTEER_DIR, filename)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            terms = json.load(f)

        # Sort terms by length descending to match longest phrases first
        terms.sort(key=lambda t: len(t), reverse=True)
        for term in terms:
            term_clean = term.strip()
            if not term_clean:
                continue
            # Handle English vs Urdu boundary
            if any(ord(c) > 127 for c in term_clean):
                pat = re.compile(re.escape(term_clean))
            else:
                pat = re.compile(rf"\b{re.escape(term_clean)}\b", re.IGNORECASE)

            # Assign priority based on specificity
            priority = 8 if label in ["COURT_LEGAL_BODY", "LAW_ACT", "SPORTS_TEAM", "EDUCATIONAL_INSTITUTION", "POLITICAL_PARTY"] else 6
            compiled_patterns.append((pat, label, priority))

    # Add Countries
    for country in sorted(COUNTRIES, key=lambda c: len(c), reverse=True):
        if any(ord(c) > 127 for c in country):
            pat = re.compile(re.escape(country))
        else:
            pat = re.compile(rf"\b{re.escape(country)}\b", re.IGNORECASE)
        compiled_patterns.append((pat, "COUNTRY", 7))

    # Add Organizations
    for org in sorted(ORGANIZATIONS, key=lambda o: len(o), reverse=True):
        pat = re.compile(rf"\b{re.escape(org)}\b", re.IGNORECASE)
        compiled_patterns.append((pat, "ORGANIZATION", 7))

    # Add Persons
    for person in sorted(PROMINENT_PERSONS, key=lambda p: len(p), reverse=True):
        if any(ord(c) > 127 for c in person):
            pat = re.compile(re.escape(person))
        else:
            pat = re.compile(rf"\b{re.escape(person)}\b", re.IGNORECASE)
        compiled_patterns.append((pat, "PERSON", 8))

    # Add Events
    for ev in sorted(KNOWN_EVENTS, key=lambda e: len(e), reverse=True):
        pat = re.compile(rf"\b{re.escape(ev)}\b", re.IGNORECASE)
        compiled_patterns.append((pat, "EVENT", 7))

    return compiled_patterns

_COMPILED_GAZETTEERS = None

def get_compiled_gazetteers():
    global _COMPILED_GAZETTEERS
    if _COMPILED_GAZETTEERS is None:
        _COMPILED_GAZETTEERS = load_gazetteers()
    return _COMPILED_GAZETTEERS

def preannotate_sentence(text: str) -> List[Dict[str, Any]]:
    """
    Produce non-overlapping, high-confidence entity annotations for a sentence.
    Applies regex rules first, then gazetteer matchers, then resolves conflicts.
    """
    candidates = []

    # 1. Regex rule entities (PHONE, ID, MONEY, PERCENT, TIME, DATE)
    regex_ents = extract_regex_entities(text)
    for ent in regex_ents:
        candidates.append({
            "text": ent["text"],
            "start": ent["start"],
            "end": ent["end"],
            "label": ent["label"],
            "priority": 10
        })

    # 2. Gazetteer entities
    gazetteers = get_compiled_gazetteers()
    for pat, label, priority in gazetteers:
        for match in pat.finditer(text):
            candidates.append({
                "text": text[match.start():match.end()],
                "start": match.start(),
                "end": match.end(),
                "label": label,
                "priority": priority
            })

    # Sort candidates by:
    # 1. Start offset ascending
    # 2. Length descending (longest span preferred per flat NER guideline)
    # 3. Priority descending
    candidates.sort(key=lambda x: (x["start"], -(x["end"] - x["start"]), -x["priority"]))

    # Resolve overlapping spans (greedy selection)
    resolved = []
    occupied = [False] * (len(text) + 1)

    for cand in candidates:
        start, end = cand["start"], cand["end"]
        label = cand["label"]

        # Validate that label is one of the exact 20
        if not validate_entity_type(label):
            continue

        # Strict character alignment check
        if text[start:end] != cand["text"]:
            continue

        # Check overlap
        if any(occupied[start:end]):
            continue

        for i in range(start, end):
            occupied[i] = True

        resolved.append({
            "text": cand["text"],
            "start": start,
            "end": end,
            "label": label
        })

    # Sort resolved entities chronologically by start offset
    resolved.sort(key=lambda x: x["start"])
    return resolved

def process_interim_corpus(interim_path: str, output_path: str, min_entities: int = 1) -> Dict[str, Any]:
    """Annotate cleaned corpus sentences and filter for sentences with at least min_entities mentions."""
    total_sentences = 0
    annotated_count = 0
    label_counts = {ent: 0 for ent in ENTITY_TYPES}

    with open(interim_path, "r", encoding="utf-8") as in_f, open(output_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            total_sentences += 1
            data = json.loads(line)
            text = data["text"]
            entities = preannotate_sentence(text)

            if len(entities) >= min_entities:
                annotated_count += 1
                data["entities"] = entities
                out_f.write(json.dumps(data, ensure_ascii=False) + "\n")

                for e in entities:
                    label_counts[e["label"]] += 1

    return {
        "total_corpus_sentences": total_sentences,
        "annotated_sentences": annotated_count,
        "label_counts": label_counts
    }

if __name__ == "__main__":
    interim_file = os.path.join(os.path.dirname(__file__), "..", "data", "interim", "clean_corpus.jsonl")
    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "silver_annotated.jsonl")

    stats = process_interim_corpus(interim_file, out_file)
    print("Pre-annotation statistics:")
    print(f"Annotated sentences: {stats['annotated_sentences']} / {stats['total_corpus_sentences']}")
    print("Mentions per class:")
    for k, v in stats["label_counts"].items():
        print(f"  {k:25s}: {v}")
