"""
Contextual Syntactic Grammar Engine for Pakistani Bilingual NER.
Resolves polysemy, metonymy (e.g. Country vs Sports Team), and extracts
unseen entities based purely on grammatical and syntactic sentence context.
Works in English and Urdu without depending on hardcoded entity dictionaries.
"""

import re
from typing import List, Dict, Any

# Capitalized personal name tokens (strictly title case, 1 to 3 words)
CAP_NAME = r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}"
URDU_WORD = r"[\u0600-\u06FF]+"

NON_PERSON_WORDS = {
    "The", "This", "That", "These", "Those", "After", "Before", "During", "Under",
    "Section", "Article", "High", "Supreme", "Court", "Government", "Govt",
    "Pakistan", "Sindh", "Punjab", "Balochistan", "Khyber", "Bank", "Police",
    "In", "At", "On", "To", "From", "By", "For", "With", "Against"
}


def _clean_person_span(span: str, start_pos: int):
    """Clean candidate person span and adjust offsets, ensuring no trailing prepositions."""
    words = span.strip().split()
    while words and words[-1].lower() in {"in", "at", "on", "to", "from", "for", "with", "against", "under", "before", "after"}:
        words.pop()
    if not words or len(words) > 3:
        return None, None, None
    if any(w in NON_PERSON_WORDS for w in words):
        return None, None, None
    clean_text = " ".join(words)
    return clean_text, start_pos, start_pos + len(clean_text)


def extract_contextual_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract entities by analyzing grammatical context and sentence roles.
    Assigns high priority (12 for sports metonymy, 11 for contextual roles).
    """
    candidates = []

    # =========================================================================
    # 1. METONYMY RESOLUTION: COUNTRY VS SPORTS_TEAM
    # When a country/city name is in cricket, football, or sporting match context
    # =========================================================================
    # 1.1 "X defeated / beat / lost to Y by N runs / wickets / goals / points"
    MATCH_RESULT = re.compile(
        r"(?i:\b([A-Z][a-zA-Z\s]+?)\s+(?:defeated|beat|thrashed|lost to|played against|won against)\s+([A-Z][a-zA-Z\s]+?)\s+by\s+\d+\s+(?:runs|wickets|goals|points|sets)\b)"
    )
    for m in MATCH_RESULT.finditer(text):
        t1, t2 = m.group(1).strip(), m.group(2).strip()
        candidates.append({"text": t1, "start": m.start(1), "end": m.start(1) + len(t1), "label": "SPORTS_TEAM", "priority": 12})
        candidates.append({"text": t2, "start": m.start(2), "end": m.start(2) + len(t2), "label": "SPORTS_TEAM", "priority": 12})

    # 1.2 "match between X and Y" / "clash between X and Y"
    MATCH_BETWEEN = re.compile(
        r"(?i:\b(?:match|clash|final|semi-final|game|series)\s+between\s+)([A-Z][a-zA-Z\s]+?)\s+(?i:and)\s+([A-Z][a-zA-Z\s]+?)(?:[\s,.]|\bat\b|\bin\b)"
    )
    for m in MATCH_BETWEEN.finditer(text):
        t1, t2 = m.group(1).strip(), m.group(2).strip()
        candidates.append({"text": t1, "start": m.start(1), "end": m.start(1) + len(t1), "label": "SPORTS_TEAM", "priority": 12})
        candidates.append({"text": t2, "start": m.start(2), "end": m.start(2) + len(t2), "label": "SPORTS_TEAM", "priority": 12})

    # 1.3 Urdu Match Result: "[Team1] نے [Team2] کو شکست دی"
    URDU_MATCH = re.compile(
        r"([\u0600-\u06FF\s]+?)\s+نے\s+([\u0600-\u06FF\s]+?)\s+کو\s+(?:[0-9۰-۹]+\s*(?:رنز|وکٹوں|گول)\s+سے\s+)?شکست\s+دی"
    )
    for m in URDU_MATCH.finditer(text):
        t1, t2 = m.group(1).strip(), m.group(2).strip()
        if len(t1.split()) <= 4:
            candidates.append({"text": t1, "start": m.start(1), "end": m.start(1) + len(t1), "label": "SPORTS_TEAM", "priority": 12})
        if len(t2.split()) <= 4:
            candidates.append({"text": t2, "start": m.start(2), "end": m.start(2) + len(t2), "label": "SPORTS_TEAM", "priority": 12})

    # =========================================================================
    # 2. UNSEEN PERSON EXTRACTION VIA SYNTACTIC GRAMMAR
    # Identifies people through structural positions (legal, corporate, identity)
    # =========================================================================

    # 2.1 Accused / Family relation: "The accused, [Name], son of [Name]" / "wife of / daughter of"
    ACCUSED_PAT = re.compile(
        rf"(?i:\b(?:The\s+accused|accused|convict)\s*,\s*)({CAP_NAME})(?i:\s*,\s*(?:son|daughter|wife|widow)\s+of\s+)({CAP_NAME})\b"
    )
    for m in ACCUSED_PAT.finditer(text):
        for g_idx in [1, 2]:
            raw_name = m.group(g_idx).strip()
            name, s, e = _clean_person_span(raw_name, m.start(g_idx))
            if name:
                candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    # Urdu Accused: "ملزم [Name] ولد [Name]" / "دختر [Name]" / "زوجہ [Name]"
    URDU_ACCUSED = re.compile(
        r"(?:ملزم|ملزمہ)\s+([\u0600-\u06FF\s]+?)\s+(?:ولد|دختر|زوجہ)\s+([\u0600-\u06FF\s]+?)(?:[\s,۔]|$)"
    )
    for m in URDU_ACCUSED.finditer(text):
        for g_idx in [1, 2]:
            name = m.group(g_idx).strip()
            words = name.split()
            if 1 <= len(words) <= 3:
                candidates.append({"text": name, "start": m.start(g_idx), "end": m.start(g_idx) + len(name), "label": "PERSON", "priority": 11})

    # 2.2 Legal filing: "...petition was filed by [Name]" / "filed by [Name]"
    FILED_BY_PAT = re.compile(
        rf"(?i:(?:\b(?:petition|appeal|plea|complaint|case)\s+(?:was\s+|is\s+|has\s+been\s+)?|\b)(?:filed|moved|lodged|submitted|argued|represented)\s+by\s+)({CAP_NAME})\b"
    )
    for m in FILED_BY_PAT.finditer(text):
        raw_name = m.group(1).strip()
        name, s, e = _clean_person_span(raw_name, m.start(1))
        if name:
            candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    # 2.3 Legal bail / notice: "...granted bail to [Name]" / "...issued notices to [Name]"
    LEGAL_ACTION_PAT = re.compile(
        rf"(?i:\b(?:granted\s+bail\s+to|issued\s+notice\s+to|issued\s+notices\s+to|remanded)\s+)({CAP_NAME})\b"
    )
    for m in LEGAL_ACTION_PAT.finditer(text):
        raw_name = m.group(1).strip()
        name, s, e = _clean_person_span(raw_name, m.start(1))
        if name:
            candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    # 2.4 Communication / Salutation: "Dear [Name]," / "Please contact [Name] at"
    CONTACT_PAT = re.compile(
        rf"(?:(?i:Dear\s+)({CAP_NAME})(?i:\s*,)|(?i:\b(?:contact|reach|call|email)\s+)({CAP_NAME})(?i:\s+(?:at|on|regarding)\b))"
    )
    for m in CONTACT_PAT.finditer(text):
        g_idx = 1 if m.group(1) else 2
        raw_name = m.group(g_idx).strip()
        name, s, e = _clean_person_span(raw_name, m.start(g_idx))
        if name:
            candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    # 2.5 Corporate Appointment / Resignation: "[Name] was elected / appointed president/director..."
    APPOINT_PAT = re.compile(
        rf"\b({CAP_NAME})(?i:\s+was\s+(?:elected|appointed|nominated|selected)\s+(?:as\s+)?(?:president|director|chairman|chief|head|CEO|counsel)\b)"
    )
    for m in APPOINT_PAT.finditer(text):
        raw_name = m.group(1).strip()
        name, s, e = _clean_person_span(raw_name, m.start(1))
        if name:
            candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    RESIGN_PAT = re.compile(
        rf"\b({CAP_NAME})(?i:\s+(?:resigned|stepped\s+down)\s+from\b)"
    )
    for m in RESIGN_PAT.finditer(text):
        raw_name = m.group(1).strip()
        name, s, e = _clean_person_span(raw_name, m.start(1))
        if name:
            candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    # 2.6 Identity records: "[Name] (CNIC ...)" or "[Name] holds CNIC" or "Voter ID check: [Name],"
    ID_CONTEXT_PAT = re.compile(
        rf"(?:(?i:Voter\s+ID\s+check\s*:\s*)({CAP_NAME})(?i:\s*,)|\b({CAP_NAME})(?i:\s*(?:\(CNIC|\bholds\s+CNIC|\bwas\s+issued\s+a\s+new\s+smart\s+card\b)))"
    )
    for m in ID_CONTEXT_PAT.finditer(text):
        g_idx = 1 if m.group(1) else 2
        raw_name = m.group(g_idx).strip()
        name, s, e = _clean_person_span(raw_name, m.start(g_idx))
        if name:
            candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    # 2.7 Sports performance: "[Name] of [Team] took N wickets / scored N runs"
    CRICKET_PERF_PAT = re.compile(
        rf"\b({CAP_NAME})(?i:\s+of\s+[A-Z][a-zA-Z\s]+?\s+took\s+\w+\s+wickets)|\b({CAP_NAME})(?i:\s+scored\s+\d+\s+runs)"
    )
    for m in CRICKET_PERF_PAT.finditer(text):
        g_idx = 1 if m.group(1) else 2
        raw_name = m.group(g_idx).strip()
        name, s, e = _clean_person_span(raw_name, m.start(g_idx))
        if name:
            candidates.append({"text": name, "start": s, "end": e, "label": "PERSON", "priority": 11})

    # =========================================================================
    # 3. CONTEXTUAL ORGANIZATION EXTRACTION
    # "Shares of [ORG] fell / rose" | "[ORG] announced its results / profit"
    # =========================================================================
    ORG_SHARES_PAT = re.compile(
        r"(?i:\b(?:Shares\s+of|Stocks\s+of)\s+)([A-Z][a-zA-Z0-9\s]+?)(?i:\s+(?:fell|rose|surged|dropped|climbed|plunged)\b)"
    )
    for m in ORG_SHARES_PAT.finditer(text):
        org = m.group(1).strip()
        if len(org.split()) <= 4:
            candidates.append({"text": org, "start": m.start(1), "end": m.start(1) + len(org), "label": "ORGANIZATION", "priority": 11})

    return candidates
