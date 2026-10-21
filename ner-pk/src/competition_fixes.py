"""
Competition Post-Processing Fixes for Pakistani-Context NER (AI-Odyssey).
Applies suffix-driven compound landmark mergers, corporate suffix detection,
bracketed phone number formatting, sports context country-to-team conversion,
syntactic unseen PERSON extraction, and longest-span overlap suppression.
"""

import re
from typing import List, Dict, Any

KNOWN_ORGS = [
    "Fauji Foundation", "Fauji Fertilizer", "Systems Limited", "Careem",
    "Bykea", "Daraz", "Engro", "Jazz", "PIA", "Edhi Foundation",
    "Saylani Welfare", "Chhipa", "K-Electric", "PTCL", "HBL", "UBL",
    "Meezan Bank", "Habib Bank Limited", "NetSol", "10Pearls", "Lucky Cement",
    "Telenor Pakistan", "Jazz Pakistan", "Zong Pakistan", "Ufone Pakistan"
]

KNOWN_PARTIES = [
    "Pakistan Muslim League-Nawaz", "Pakistan Muslim League", "PML-N", "PML-Q",
    "Pakistan Peoples Party", "PPP", "PTI", "MQM-P", "MQM", "JUI-F", "ANP",
    "Awami National Party", "Jamaat-e-Islami", "Balochistan National Party",
    "Balochistan Awami Party", "Istehkam-e-Pakistan Party", "Pak Sarzameen Party",
    "Tehreek-e-Labbaik Pakistan"
]

KNOWN_CITIES_EXTRA = [
    "DG Khan", "D.G. Khan", "Dera Ghazi Khan", "D.I. Khan", "Dera Ismail Khan", "Swat"
]

LANDMARK_SUFFIXES = (
    r"(?:Expo\s+Centre|Expo\s+Center|Beach|Stadium|International\s+Airport|Airport|"
    r"Fort|Mosque|Masjid|Barrage|Dam|Bridge|Motorway|Highway|Museum|Press\s+Club|"
    r"Gymkhana|National\s+Park|Park|Zoo|Tower|Port|General\s+Hospital|Hospital|Hall)"
)

ORG_SUFFIXES = (
    r"(?:Limited|Ltd\.?|Foundation|Corporation|Enterprises|Industries|"
    r"Cement|Fertilizer|Motors|Logistics|Telecom|Welfare\s+Trust|Group)"
)

COMMON_PAK_SURNAMES = (
    r"(?:Baig|Rehman|Rahman|Javed|Malik|Ansari|Farooqui|Farooq|Ghani|Lund|Qureshi|Siddiqui|"
    r"Siddiqa|Chaudhry|Choudhary|Raza|Abbasi|Khattak|Afridi|Bugti|Mengal|Baloch|Mirza|"
    r"Sheikh|Shaikh|Butt|Cheema|Tarar|Gilani|Gillani|Shah|Khan|Bibi|Begum|Nisar|Bajwa|"
    r"Bilal|Ali|Hassan|Hussain|Hamza|Usman|Umar|Tariq|Asim|Fahad|Kamran|Ahmed|Ahmad)"
)

SPORTS_KEYWORDS = re.compile(
    r"\b(?:defeated|beat|runs|wickets|innings|match|matches|T20|ODI|test|"
    r"chasing|scored|trophy|tournament|final|semi-final|vs\.?|versus)\b",
    re.IGNORECASE
)

COUNTRIES = {
    "Pakistan", "Bangladesh", "Sri Lanka", "New Zealand", "India",
    "Australia", "England", "South Africa", "Afghanistan", "West Indies",
    "Zimbabwe", "Ireland"
}


def apply_competition_fixes(text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Applies competition-grade deterministic enhancements and longest-span conflict resolution.
    entities format: [{"text": str, "label": str, "start": int, "end": int, ...}, ...]
    """
    new_spans = list(entities)

    def add_span(start: int, end: int, label: str):
        raw_text = text[start:end]
        leading_spaces = len(raw_text) - len(raw_text.lstrip())
        trailing_spaces = len(raw_text) - len(raw_text.rstrip())
        s = start + leading_spaces
        e = end - trailing_spaces
        span_text = text[s:e].strip()
        if span_text and 0 <= s < e <= len(text):
            new_spans.append({
                "text": span_text,
                "label": label,
                "start": s,
                "end": e
            })

    # --- FIX 1: Bracketed & Standard Phone Numbers ---
    phone_bracket_re = re.compile(
        r"(?<!\d)(\(\+?[0-9۰-۹]{2,4}\)[\s\-]?[0-9۰-۹]{3,4}[\s\-]?[0-9۰-۹]{4,8}|\([0-9۰-۹]{3,4}\)[\s\-]?[0-9۰-۹]{6,8})(?!\d)"
    )
    for m in phone_bracket_re.finditer(text):
        add_span(m.start(1), m.end(1), "PHONE_NUMBER")

    # International and standard phone numbers e.g. +923219988776 or 0300-8765432
    phone_intl_re = re.compile(
        r"(?<!\d)(\+92[\s\-]?[0-9۰-۹]{2,3}[\s\-]?[0-9۰-۹]{6,8}|\+92[0-9۰-۹]{10}|03[0-9]{2}[\-\s]?[0-9]{7})(?!\d)"
    )
    for m in phone_intl_re.finditer(text):
        add_span(m.start(1), m.end(1), "PHONE_NUMBER")

    # --- FIX 1B: Universal Military and Standard Time Formats ---
    time_24h_re = re.compile(r"\b([012]?[0-9]:[0-5][0-9]\s*hours)\b", re.IGNORECASE)
    for m in time_24h_re.finditer(text):
        add_span(m.start(1), m.end(1), "TIME")

    time_12h_re = re.compile(r"\b((?:[01]?[0-9](?::[0-5][0-9])?)\s*(?:a\.?m\.?|p\.?m\.?))\b", re.IGNORECASE)
    for m in time_12h_re.finditer(text):
        add_span(m.start(1), m.end(1), "TIME")

    # --- FIX 1C: Unspaced & Standard Currency Expressions ---
    unspaced_rs_re = re.compile(r"\b(Rs\.?\s*\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:crore|lakh|million|billion))?|PKR\s*\d+(?:,\d+)*(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:lakh|crore|million|billion)\s+rupees)\b", re.IGNORECASE)
    for m in unspaced_rs_re.finditer(text):
        add_span(m.start(1), m.end(1), "MONEY")

    # --- FIX 1D: Universal Event & Tournament Grammar (Strict Title Case) ---
    event_days_re = re.compile(
        r"\b(?:Defence\s+Day|Defense\s+Day|Independence\s+Day|Pakistan\s+Day|Kashmir\s+Solidarity\s+Day|"
        r"Kashmir\s+Day|Labour\s+Day|Eid-ul-Fitr|Eid-ul-Adha|TechFest)\b",
        re.IGNORECASE
    )
    for m in event_days_re.finditer(text):
        add_span(m.start(), m.end(), "EVENT")

    HEADLINE_EXCLUDE = {"Ahead", "Of", "In", "On", "At", "To", "From", "For", "With", "Sign", "Signs", "And", "The"}
    event_tourney_re = re.compile(
        r"\b([A-Z][a-zA-Z0-9\-]*(?:\s+[A-Z][a-zA-Z0-9\-]*){0,3}\s+(?:Trophy|Cup|Games|Super\s+League|Championship|Horse\s+Show|Cattle\s+Show|Exhibition))\b"
    )
    for m in event_tourney_re.finditer(text):
        raw_ev = m.group(1).strip()
        words = raw_ev.split()
        while words and words[0] in HEADLINE_EXCLUDE:
            words.pop(0)
        if words:
            clean_ev = " ".join(words)
            s = m.end(1) - len(clean_ev)
            e = m.end(1)
            add_span(s, e, "EVENT")

    # --- FIX 1E: Universal Sports Headline Signing Context ---
    sign_re = re.compile(
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+Sign\s+([A-Z][a-z]+)\s+Ahead\s+Of\s+([A-Z][a-zA-Z0-9\-]*(?:\s+[A-Z][a-zA-Z0-9\-]*){0,3})\b"
    )
    for m in sign_re.finditer(text):
        add_span(m.start(1), m.end(1), "SPORTS_TEAM")
        add_span(m.start(2), m.end(2), "PERSON")
        add_span(m.start(3), m.end(3), "EVENT")

    # Known Parties & Stems
    for party in KNOWN_PARTIES:
        for m in re.finditer(rf"\b{re.escape(party)}\b", text):
            add_span(m.start(), m.end(), "POLITICAL_PARTY")

    # Known Cities Extra
    for city in KNOWN_CITIES_EXTRA:
        for m in re.finditer(rf"\b{re.escape(city)}\b", text):
            add_span(m.start(), m.end(), "CITY")

    # --- FIX 1F: Universal LAW_ACT Expansion & Grammar (Strict Title Case) ---
    law_re = re.compile(
        r"\b((?:[A-Z][a-zA-Z0-9\-]*(?:\s+(?:of|and|the|[A-Z][a-zA-Z0-9\-]*))*\s+)?(?:Act|Ordinance|Code))(?:,\s*([12][0-9]{3}))?\b"
    )
    for m in law_re.finditer(text):
        raw_law = m.group(0).strip()
        # Ensure it doesn't start with lowercase or sentence words
        first_word = raw_law.split()[0]
        if first_word[0].isupper() and first_word not in {"The", "A", "An", "Under", "Section", "Sections", "Court", "High", "Supreme"}:
            if not any(w in raw_law for w in ["Court", "Tribunal", "Assembly", "Council", "Police", "Authority"]):
                add_span(m.start(0), m.end(0), "LAW_ACT")

    # Clean leading verbs/noise from PERSON entities (e.g. 'Sign Bilal' -> 'Bilal')
    for s in new_spans:
        if s["label"] == "PERSON":
            if s["text"].startswith("Sign "):
                s["start"] += 5
                s["text"] = text[s["start"]:s["end"]].strip()
            elif s["text"].startswith("Signed "):
                s["start"] += 7
                s["text"] = text[s["start"]:s["end"]].strip()

    # Expand any predicted LAW_ACT if followed by comma and 4-digit year
    for s in new_spans:
        if s["label"] == "LAW_ACT":
            trailing = text[s["end"]:]
            m_yr = re.match(r"^,\s*([12][0-9]{3})\b", trailing)
            if m_yr:
                s["end"] += m_yr.end()
                s["text"] = text[s["start"]:s["end"]].strip()

    # Expand political parties if trailing 'Party' exists
    for s in new_spans:
        if s["label"] == "POLITICAL_PARTY":
            trailing = text[s["end"]:]
            m_party = re.match(r"^\s+Party\b", trailing)
            if m_party:
                s["end"] += m_party.end()
                s["text"] = text[s["start"]:s["end"]].strip()

    # --- FIX 2: Compound Landmarks (e.g. Islamabad Expo Centre, Clifton Beach, Frere Hall) ---
    landmark_re = re.compile(
        rf"\b([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+){{0,3}}\s+{LANDMARK_SUFFIXES})\b"
    )
    for m in landmark_re.finditer(text):
        add_span(m.start(1), m.end(1), "LANDMARK_FACILITY")

    # --- FIX 3: Known & Suffix-based Organizations (Fauji Foundation, Systems Limited, Careem) ---
    for org in KNOWN_ORGS:
        for m in re.finditer(rf"\b{re.escape(org)}\b", text):
            add_span(m.start(), m.end(), "ORGANIZATION")

    org_suffix_re = re.compile(
        rf"\b([A-Z][a-zA-Z0-9&\-\.]+(?:\s+[A-Z][a-zA-Z0-9&\-\.]+){{0,3}}\s+{ORG_SUFFIXES})\b"
    )
    for m in org_suffix_re.finditer(text):
        phrase = m.group(1)
        if not any(w in phrase for w in ["Court", "University", "College", "Institute", "Ministry"]):
            add_span(m.start(1), m.end(1), "ORGANIZATION")

    # --- FIX 4: Syntactic Context Rules + Surname Anchor for Unseen PERSON Names ---
    person_context_patterns = [
        r"(?:filed|appealed|submitted|petitioned|argued|represented)\s+by\s+(?:[A-Z][a-z]+\.\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b",
        r"(?:The\s+accused|accused|suspect|petitioner|complainant),?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b",
        r"(?:son|daughter|wife|widow)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b",
        r"\bDear\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b",
        r"\b(?:contact|call|email|reach)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s+(?:at|on|via|regarding)\b",
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s+was\s+(?:elected|appointed|named|promoted|nominated)\b",
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s+(?:resigned|joined|graduated)\s+from\b",
        r"Voter\s+ID\s+check\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b",
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\s*(?:\(CNIC|\bholds\s+CNIC|\bwas\s+issued\s+a\s+new\s+smart\s+card\b)"
    ]
    for pat in person_context_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            raw = m.group(1).strip()
            words = raw.split()
            # Clean trailing prepositions
            while words and words[-1].lower() in {"in", "at", "on", "to", "from", "for", "with", "against", "under", "before", "after"}:
                words.pop()
            if words and len(words) <= 3:
                clean_name = " ".join(words)
                s = m.start(1)
                e = s + len(clean_name)
                add_span(s, e, "PERSON")

    # Common Pakistani Name + Surname fallback (titles stripped per guidelines)
    TITLES_TO_SKIP = {
        "Anchor", "Dr", "Doctor", "Prof", "Professor", "Justice", "Judge", "Mr", "Mrs", "Ms",
        "Advocate", "Barrister", "General", "Gen", "Major", "Maj", "Colonel", "Col",
        "Captain", "Capt", "Senator", "Minister", "President", "Prime", "Chief", "Lt"
    }
    NON_NAME_FIRST = {"Fauji", "Bahria", "Lucky", "Allied", "United", "National", "Askari", "State", "Federal"} | TITLES_TO_SKIP

    surname_re = re.compile(rf"\b([A-Z][a-z]+\s+{COMMON_PAK_SURNAMES})\b")
    for m in surname_re.finditer(text):
        first_word = m.group(1).split()[0]
        if first_word not in NON_NAME_FIRST:
            add_span(m.start(1), m.end(1), "PERSON")

    # --- FIX 5: Sports Context Country -> SPORTS_TEAM Override ---
    sports_match_re = re.compile(
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:defeated|beat|crushed|thrashed|played\s+against)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
    )
    for m in sports_match_re.finditer(text):
        t1, t2 = m.group(1), m.group(2)
        if t1 in COUNTRIES:
            add_span(m.start(1), m.end(1), "SPORTS_TEAM")
        if t2 in COUNTRIES:
            add_span(m.start(2), m.end(2), "SPORTS_TEAM")

    if SPORTS_KEYWORDS.search(text):
        for s in new_spans:
            if s["label"] == "COUNTRY" and s["text"] in COUNTRIES:
                s["label"] = "SPORTS_TEAM"

    # --- FIX 6: Longest-Span Conflict Resolution (Fixes 7 False Positive COUNTRY & Split CITY) ---
    PRIORITY = {
        "COURT_LEGAL_BODY": 10, "GOVERNMENT_BODY": 10, "EDUCATIONAL_INSTITUTION": 10,
        "LANDMARK_FACILITY": 9, "ORGANIZATION": 9, "SPORTS_TEAM": 9, "LAW_ACT": 9,
        "EVENT": 8, "MEDIA_OUTLET": 8, "POLITICAL_PARTY": 8, "PERSON": 7,
        "ID_NUMBER": 10, "PHONE_NUMBER": 10, "MONEY": 9, "PERCENT": 9, "DATE": 8, "TIME": 8,
        "PROVINCE_REGION": 3, "CITY": 2, "COUNTRY": 1
    }

    new_spans.sort(
        key=lambda x: (-(x["end"] - x["start"]), -PRIORITY.get(x["label"], 0), x["start"])
    )

    resolved = []
    for candidate in new_spans:
        overlaps = False
        for kept in resolved:
            if not (candidate["end"] <= kept["start"] or candidate["start"] >= kept["end"]):
                overlaps = True
                break
        if not overlaps:
            resolved.append(candidate)

    resolved.sort(key=lambda x: x["start"])
    return resolved
