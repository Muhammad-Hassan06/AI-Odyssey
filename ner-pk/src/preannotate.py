COMMON_SENSITIVE = {
    "Dawn", "The Nation", "Nation", "Jazz", "Express", "United", "Sun", "Star",
    "NAB", "FIA", "ECP", "FBR", "PIA", "PBS", "PEMRA", "LUMS", "NUST", "NADRA",
    "MQM", "PTI", "PML", "PPP", "ANP", "JUI", "OGDCL", "PSO", "SNGPL", "SSGC",
    "NBP", "HBL", "UBL", "MCB", "BOP", "IMF", "ADB", "PECA", "CrPC", "PPC", "SC", "SCP",
    "LHC", "SHC", "PHC", "IHC", "BHC", "FSC", "JCP", "SJC", "ATC", "PCB", "KCCI", "LCCI", "SCBA"
}

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
from src.contextual_grammar import extract_contextual_entities

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
    "Lahore Chamber of Commerce and Industry", "LCCI", "Pakistan Olympic Association",
    "Pakistan Steel Mills", "Pakistan Steel", "Bank of Punjab", "BOP",
    "Engro Corporation", "Engro", "International Monetary Fund", "IMF",
    "World Bank", "Asian Development Bank", "ADB", "State Bank", "Federal Board of Revenue",
    "Jazz", "Ufone", "Telenor", "Zong",
    "ZTBL",
    "Zarai Taraqiati Bank",
    "Bank of Khyber",
    "Habib Metropolitan Bank",
    "Standard Chartered Bank",
    "Dubai Islamic Bank",
    "Al Baraka Bank",
    "JS Bank",
    "Soneri Bank",
    "Askari Bank",
    "Faysal Bank",
    "Meezan Bank",
    "Bank Alfalah",
    "Bank Alfalah Limited",
    "Sindh Bank",
    "Telenor Pakistan",
    "Jazz Pakistan",
    "Zong Pakistan",
    "Ufone Pakistan",
    "Fauji Foundation",
    "Systems Limited",
    "Careem"
]

# Prominent Pakistani Persons (names only; titles are strictly stripped per guidelines)
PROMINENT_PERSONS = [
    "Muhammad Bilal", "Muhammad Ali Jinnah", "Quaid-e-Azam", "Fatima Jinnah", "Allama Iqbal", "Liaquat Ali Khan",
    "Zulfikar Ali Bhutto", "Benazir Bhutto", "Nawaz Sharif", "Shehbaz Sharif", "Maryam Nawaz",
    "Imran Khan", "Asif Ali Zardari", "Bilawal Bhutto Zardari", "Bilawal Bhutto",
    "Qazi Faez Isa", "Gulzar Ahmed", "Asif Saeed Khosa", "Saqib Nisar",
    "Abdul Qadeer Khan", "Abdus Salam", "Arshad Nadeem", "Babar Azam", "Shaheen Shah Afridi",
    "Mohammad Rizwan", "Wasim Akram", "Waqar Younis", "Jahangir Khan", "Jansher Khan",
    "Aamer Farooq", "Salman Akram Raja", "Salman Akram", "Ayesha Khan", "Jinnah Ali",
    "قائد اعظم", "محمد علی جناح", "علامہ اقبال", "عمران خان", "نواز شریف", "شہباز شریف", "بلاول بھٹو زرداری",
    "بلاول بھٹو", "بابر اعظم", "احمد علی", "عامر فاروق", "سلمان اکرم راجہ", "عائشہ خان", "آصف علی زرداری", "مریم نواز", "ذوالفقار علی بھٹو", "لیاقت علی خان", "ایوب خان", "یحییٰ خان", "محمد عامر", "حارث رؤف", "شاداب خان", "فخر زمان", "نسیم شاہ", "محمد رضوان", "شاہین شاہ آفریدی", "شاہین آفریدی"
]

# Prominent Events
KNOWN_EVENTS = [
    "Pakistan Super League 10", "Pakistan Super League 9", "Pakistan Super League", "PSL 10", "PSL 9", "PSL 8", "PSL",
    "Independence Day", "Pakistan Day", "Defense Day",
    "Defence Day", "National Games", "Asia Cup", "Youm-e-Takbir", "Kashmir Solidarity Day", "Eid-ul-Fitr", "Eid-ul-Adha",
    "Federal Budget 2025-26", "Federal Budget 2024-25", "Federal Budget", "Budget 2025-26", "Budget 2024-25",
    "General Elections 2024", "General Elections 2018", "SCO Summit", "COP29", "COP28", "2022 Pakistan floods",
    "پاکستان سپر لیگ 10", "پاکستان سپر لیگ", "پی ایس ایل 10", "پی ایس ایل", "یوم آزادی", "یوم پاکستان", "یوم دفاع", "یوم تکبیر", "وفاقی بجٹ 2025-26", "وفاقی بجٹ"
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
                pat = re.compile(rf"(?<![\u0600-\u06FF]){re.escape(term_clean)}(?![\u0600-\u06FF])")
            else:
                if term_clean in COMMON_SENSITIVE or (len(term_clean) <= 5 and term_clean.isupper()):
                    pat = re.compile(rf"\b{re.escape(term_clean)}\b")
                else:
                    pat = re.compile(rf"\b{re.escape(term_clean)}\b", re.IGNORECASE)

            # Assign priority based on specificity
            priority = 8 if label in ["COURT_LEGAL_BODY", "LAW_ACT", "SPORTS_TEAM", "EDUCATIONAL_INSTITUTION", "POLITICAL_PARTY", "GOVERNMENT_BODY"] else 6
            compiled_patterns.append((pat, label, priority))

    # Provincial and Federal Government Patterns (High priority over nested province/country)
    GOV_PAT = re.compile(
        r"\b(?:(?:Government|Govt\.?)\s+of\s+(?:Sindh|Punjab|Balochistan|Khyber\s+Pakhtunkhwa|KP|KPK|Gilgit[- ]Baltistan|AJK|Azad\s+Kashmir|Pakistan)|(?:Sindh|Punjab|Balochistan|Khyber\s+Pakhtunkhwa|KP|KPK|Gilgit[- ]Baltistan|AJK|Azad\s+Kashmir|Pakistan)\s+(?:government|govt\.?))\b",
        re.IGNORECASE
    )
    compiled_patterns.append((GOV_PAT, "GOVERNMENT_BODY", 9))

    URDU_GOV_PAT = re.compile(
        r"(?<![\u0600-\u06FF])حکومت\s+(?:پاکستان|سندھ|پنجاب|بلوچستان|خیبر\s*پختونخوا|گلگت\s*بلتستان|آزاد\s*کشمیر)(?![\u0600-\u06FF])"
    )
    compiled_patterns.append((URDU_GOV_PAT, "GOVERNMENT_BODY", 9))

    # Add Countries
    for country in sorted(COUNTRIES, key=lambda c: len(c), reverse=True):
        if any(ord(c) > 127 for c in country):
            pat = re.compile(re.escape(country))
        else:
            pat = re.compile(rf"\b{re.escape(country)}\b", re.IGNORECASE)
        compiled_patterns.append((pat, "COUNTRY", 7))

    # Add Organizations
    for org in sorted(ORGANIZATIONS, key=lambda o: len(o), reverse=True):
        if org in COMMON_SENSITIVE or (len(org) <= 5 and org.isupper()):
            pat = re.compile(rf"\b{re.escape(org)}\b")
        else:
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

    # Add Roman Urdu Legal & Government Terms
    ROMAN_URDU_COURTS = ["Adalat-e-Uzma", "Adalat-e-Aalia", "Adalat-e-Insaaf", "Supreme Court"]
    for c in ROMAN_URDU_COURTS:
        pat = re.compile(rf"\b{re.escape(c)}\b", re.IGNORECASE)
        compiled_patterns.append((pat, "COURT_LEGAL_BODY", 8))

    ROMAN_URDU_GOV = [
        "Qaumi Assembly", "Subaee Assembly", "Hukoomat-e-Pakistan", "Hukumat-e-Pakistan",
        "Hukoomat-e-Sindh", "Hukumat-e-Sindh", "Hukoomat-e-Punjab", "Hukumat-e-Punjab",
        "Hukoomat-e-Balochistan", "Hukumat-e-Balochistan", "Hukoomat-e-KP", "Hukumat-e-KP",
        "Hukoomat-e-KPK", "Hukumat-e-KPK",
        "Wazarat-e-Khazana", "Wazarat-e-Dakhla", "Wazarat-e-Kharija", "NAB",
        "National Accountability Bureau", "Pak Fauj", "Pakistan Armed Forces", "Pakistan Army"
    ]
    for g in ROMAN_URDU_GOV:
        pat = re.compile(rf"\b{re.escape(g)}\b", re.IGNORECASE)
        compiled_patterns.append((pat, "GOVERNMENT_BODY", 8))

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
    Features OCR/typo word healing for robust boundary alignment.
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

    # 1.2 Contextual Syntactic Grammar entities (Sports match vs Country, legal filings, accused, etc.)
    context_ents = extract_contextual_entities(text)
    candidates.extend(context_ents)

    # 1.5 Honorific-based Person Extraction (Dr., Justice, Mr., Advocate, Maulana etc.)
    # Titles/honorifics are strictly stripped per guidelines; the extracted entity is the person's name!
    PREFIX_TITLES_EN = (
        r'(?:Chief\s+Justice|Justice|Judge|'
        r'Lt\.?\s*Gen\.?|Lieutenant\s+General|Gen\.?|General|Maj\.?\s*Gen\.?|Major\s+General|Brig\.?|Brigadier|Col\.?|Colonel|Maj\.?|Major|Capt\.?|Captain|'
        r'Prof\.?\s*Dr\.?|Prof\.?|Professor|Dr\.?|Doctor|'
        r'Barrister|Advocate|Senator|'
        r'Chairman|Chairperson|President|Prime\s+Minister|Chief\s+Minister|Minister|Governor|Director\s+General|DG|Director|CEO|Inspector\s+General|IG|'
        r'Anchor|'
        r'Mohtarma|Sahibzada|Makhdoom|Pir|Sardar|Chaudhry|Chaudhary|Mr\.?|Ms\.?|Mrs\.?|Maulana|Mufti)'
        r'(?:\s*\((?:Retd\.?|retd\.?|R)\))?'
    )
    HONORIFIC_EN_PATTERN = re.compile(
        rf'\b{PREFIX_TITLES_EN}\s+([A-Z][a-zA-Z\-]*(?:\s+[A-Z][a-zA-Z\-]*){{0,3}})\b'
    )
    for m in HONORIFIC_EN_PATTERN.finditer(text):
        raw_name = m.group(1).strip()
        name_text = re.sub(r"\s+(?:Sahib|Sahiba)$", "", raw_name).strip()
        end_pos = m.start(1) + len(name_text)
        candidates.append({
            "text": name_text,
            "start": m.start(1),
            "end": end_pos,
            "label": "PERSON",
            "priority": 12
        })

    URDU_PREFIXES = (
        r'(?:جسٹس\s*(?:\([رR]\))?|چیف\s*جسٹس\s*(?:\([رR]\))?|'
        r'ڈاکٹر|پروفیسر|علامہ|مولانا|مفتی|سینیٹر|بیرسٹر|ایڈووکیٹ|'
        r'سردار|مخدوم|پیر|صاحبزادہ|محترمہ|'
        r'ملزم|مجرم|مقتول|مدعی|مفرور)'
    )
    URDU_HONORIFIC_PAT = re.compile(
        rf'(?<![\u0600-\u06FF]){URDU_PREFIXES}\s+([\u0600-\u06FF]+(?:\s+[\u0600-\u06FF]+){{0,3}})'
    )
    URDU_NON_NAME_TOKENS = {
        'کا', 'کی', 'کے', 'نے', 'کو', 'سے', 'میں', 'پر', 'تک', 'اور', 'یا',
        'عدالت', 'پولیس', 'تھانہ', 'جیل', 'حکومت', 'اسمبلی', 'وزارت', 'دفتر',
        'کمیشن', 'بینک', 'بورڈ', 'کمیٹی', 'پارٹی', 'کوٹہ', 'فیصلہ', 'پیش'
    }
    for m in URDU_HONORIFIC_PAT.finditer(text):
        raw_name = m.group(1).strip()
        raw_name = re.sub(r'\s+(?:صاحب|صاحبہ)$', '', raw_name).strip()
        tokens = raw_name.split()
        valid_tokens = []
        for t in tokens:
            if t in URDU_NON_NAME_TOKENS or any(c.isdigit() or ('۰' <= c <= '۹') for c in t):
                break
            valid_tokens.append(t)
        if valid_tokens:
            final_name = ' '.join(valid_tokens)
            end_pos = m.start(1) + len(final_name)
            candidates.append({
                "text": final_name,
                "start": m.start(1),
                "end": end_pos,
                "label": "PERSON",
                "priority": 12
            })

    
    # 1.6 Common Pakistani Personal Name convention (Muhammad Bilal, Shazia Baig, etc.)
    PAK_FIRST_NAMES = (
        r"Muhammad|Mohammad|Mohd\.?|Syed|Hafiz|Malik|Shazia|Mehwish|Hira|Sana|Komal|"
        r"Maryam|Saad|Junaid|Bilal|Sadia|Danish|Omar|Hamza|Ali|Usman|Zain|Ahmed|Ahmad|"
        r"Fatima|Ayesha|Zahra|Tariq|Asim|Fahad|Kamran|Waqar|Noman|Farhan|Imran|Babar|"
        r"Shaheen|Rizwan|Haris|Naseem|Fakhar|Shadab|Iftikhar|Imad|Sarfaraz|Shoaib|Shahid|"
        r"Misbah|Younis|Inzamam|Wasim|Javed|Saeed|Azhar|Shan|Abdullah|Saim|Tahir|Naveed|"
        r"Kashif|Rashid|Sohail|Adnan|Salman|Rehan|Zeeshan|Arsalan|Ahsan|Umair|Waleed|"
        r"Atif|Shahzad|Shahbaz|Nawaz|Asif|Arshad"
    )
    PAK_SURNAMES = (
        r"Baig|Ansari|Javed|Rehman|Rahman|Ahmed|Ahmad|Farooqui|Farooq|Siddiqui|Ghani|"
        r"Malik|Butt|Shaikh|Sheikh|Khan|Chaudhry|Choudhary|Qureshi|Raza|Shah|Memon|"
        r"Abbasi|Bhatti|Mirza|Niazi|Bajwa|Dar|Lodhi|Gillani|Gilani|Tareen|Tarar|"
        r"Warraich|Zardari|Sharif|Bhutto|Iqbal|Jinnah|Akram|Younis|Afridi|Nadeem|Salam|"
        r"Bilal|Ali|Hassan|Hussain|Hamza|Usman|Umar|Tariq|Asim|Fahad|Kamran|"
        r"Wattoo|Leghari|Mazari|Mengal|Bugti|Marri|Achakzai|Kakar|Durrani|Yousafzai|Shinwari|Khattak"
    )
    PAK_NAME_PATTERN = re.compile(
        rf"\b(?:{PAK_FIRST_NAMES})\s+(?:{PAK_SURNAMES})\b"
    )
    for m in PAK_NAME_PATTERN.finditer(text):
        full_name = m.group(0).strip()
        candidates.append({
            "text": full_name,
            "start": m.start(),
            "end": m.end(),
            "label": "PERSON",
            "priority": 10
        })

    # 1.7 Sports Match Context: teams competing in cricket/football matches are SPORTS_TEAM
    SPORTS_MATCH_PAT = re.compile(
        r"\b([A-Z][a-zA-Z\s]+?)\s+(?:defeated|beat|won against|lost to|played against)\s+([A-Z][a-zA-Z\s]+?)\s+by\s+\d+\s+(?:runs|wickets|goals|points)\b"
    )
    for m in SPORTS_MATCH_PAT.finditer(text):
        team1 = m.group(1).strip()
        team2 = m.group(2).strip()
        candidates.append({
            "text": team1,
            "start": m.start(1),
            "end": m.start(1) + len(team1),
            "label": "SPORTS_TEAM",
            "priority": 11
        })
        candidates.append({
            "text": team2,
            "start": m.start(2),
            "end": m.start(2) + len(team2),
            "label": "SPORTS_TEAM",
            "priority": 11
        })

    # 1.8 Sports player signing / transaction pattern
    SIGN_PAT = re.compile(r"\b(?:Sign|Signs|Signed|Draft|Drafts|Drafted|Appoint|Appoints|Pick|Picks)\s+([A-Z][a-z]+)\b")
    for m in SIGN_PAT.finditer(text):
        player = m.group(1).strip()
        candidates.append({
            "text": player,
            "start": m.start(1),
            "end": m.end(1),
            "label": "PERSON",
            "priority": 9
        })

    # 2. Gazetteer entities with OCR/typo word healing (e.g. Karach1 -> Karachi)
    healed_word_text = re.sub(r'(?<=[a-zA-Z])1(?=[a-zA-Z]|\b)', 'i', text)
    healed_word_text = re.sub(r'(?<=[a-zA-Z])0(?=[a-zA-Z]|\b)', 'o', healed_word_text)
    text_variants = [(text, 8)]
    if healed_word_text != text:
        text_variants.append((healed_word_text, 7))

    gazetteers = get_compiled_gazetteers()
    for cur_txt, prio_adj in text_variants:
        for pat, label, priority in gazetteers:
            for match in pat.finditer(cur_txt):
                candidates.append({
                    "text": text[match.start():match.end()],
                    "start": match.start(),
                    "end": match.end(),
                    "label": label,
                    "priority": min(priority, prio_adj)
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
