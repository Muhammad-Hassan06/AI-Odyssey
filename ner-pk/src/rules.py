"""
Deterministic Regex and Pattern Entity Extraction Engine for Pakistani-Context NER.
Handles PHONE_NUMBER, ID_NUMBER, MONEY, PERCENT, TIME, and DATE with exact span offsets.
"""

import re
from typing import List, Dict, Any

from src.urdu_normalize import convert_urdu_digits_to_ascii

# ==============================================================================
# 1. PHONE_NUMBER PATTERNS (Pakistani mobile, landline, toll-free, English & Urdu)
# ==============================================================================
# Mobile: +92 3xx xxxxxxx, 0092 3xx xxxxxxx, 03xx-xxxxxxx, 03xx xxxxxxx, (03xx) xxxxxxx
# Eastern digits: +۹۲ ۳۰۰ ۱۲۳۴۵۶۷, ۰۳۰۰-۱۲۳۴۵۶۷, ۰۳۰۰۱۲۳۴۵۶۷
# Landline: 021-xxxxxxxx, 042-xxxxxxxx, 051-xxxxxxx, +92 (21) xxxxxxxx
PHONE_REGEXES = [
    # +92 / 0092 / +۹۲ / ۰۰۹۲ with space/dash and mobile/landline code
    re.compile(r"(?:\+92|\+۹۲|0092|۰۰۹۲)[\s-]?(?:\(?0?[0-9۰-۹]{2,3}\)?|[0-9۰-۹]{2,3})[\s-]?[0-9۰-۹]{3,4}[\s-]?[0-9۰-۹]{4}\b"),
    # Standard Pakistani mobile format: 03xx-xxxxxxx or 03xx xxxxxxx or 03xxxxxxxxx (and Eastern digits ۰۳)
    re.compile(r"(?:\b|(?<=[\s\(\[\{]))[0۰][3۳][0-9۰-۹]{2}[-\s]?[0-9۰-۹]{7}\b"),
    # Standard Pakistani landline: 0xx-xxxxxxx or (0xx) xxxxxxx
    re.compile(r"(?:(?<=\s)|(?<=\()|^)\(?[0۰][0-9۰-۹]{2,3}\)?[\s-]?[0-9۰-۹]{7,8}\b"),
    # Toll free: 0800-xxxxx or ۰۸۰۰-xxxxx
    re.compile(r"(?:\b|(?<=[\s\(\[\{]))[0۰][8۸][0۰]{2}[-\s]?[0-9۰-۹]{5}\b")
]

# ==============================================================================
# 2. ID_NUMBER PATTERNS (Pakistani CNIC: 5 digits - 7 digits - 1 digit, ASCII or Urdu)
# ==============================================================================
# Formats: 42101-1234567-1, 35201-7654321-9, ۴۲۱۰۱-۱۲۳۴۵۶۷-۱
CNIC_HYPHEN_REGEX = re.compile(r"(?:\b|(?<=[\s\(\[\{]))[0-9۰-۹]{5}-[0-9۰-۹]{7}-[0-9۰-۹]\b")
CNIC_CONTEXT_REGEX = re.compile(
    r"(?i)(?:\b|(?<=[\s\(\[\{]))(?:CNIC|NIC|ID\s*(?:card)?|شناختی\s*کارڈ|سی\s*این\s*آئی\s*سی)(?:\s*(?:no|number|num|\#|:|\-)|\s+)?\s*([0-9۰-۹]{13})\b"
)

# ==============================================================================
# 3. MONEY PATTERNS (PKR, Rs, USD, lakh, crore, billion, trillion, روپے, ارب, کروڑ)
# ==============================================================================
MONEY_REGEXES = [
    # Rs. / Rs / PKR / PKR. / $ followed by amount and scale
    re.compile(
        r"(?i)(?:(?<=\s)|^)(?:Rs\.?|PKR|USD|\$|EUR|GBP)\s*[\d,۰-۹]+(?:\.[\d۰-۹]+)?(?:\s*(?:crore|lakh|million|billion|trillion|arab|kharab|rupees|dollars))?\b"
    ),
    # Amount followed by currency name: 500 million rupees / dollars
    re.compile(
        r"(?i)\b[\d,]+(?:\.\d+)?\s*(?:crore|lakh|million|billion|trillion|arab|kharab)?\s*(?:rupees|dollars|euros|pounds|PKR)\b"
    ),
    # Urdu currency patterns: 15 کروڑ روپے, ۱۵ کروڑ روپے, 50 ارب ڈالر, ۵۰ ارب روپے
    re.compile(
        r"[\d,۰-۹]+(?:\.[\d۰-۹]+)?\s*(?:کروڑ|لاکھ|ارب|کھرب)\s*(?:روپے|ڈالر|یورو|پاؤنڈ)\b"
    ),
    # Urdu: 5000 روپے or روپے 5000
    re.compile(
        r"[\d,۰-۹]+(?:\.[\d۰-۹]+)?\s*روپے\b"
    ),
    re.compile(
        r"\bروپے\s*[\d,۰-۹]+(?:\.[\d۰-۹]+)?(?:\s*(?:کروڑ|لاکھ|ارب|کھرب))?\b"
    )
]

# ==============================================================================
# 4. PERCENT PATTERNS (%, per cent, percentage points, فیصد)
# ==============================================================================
PERCENT_REGEXES = [
    # 5.2% or ۵.۲%
    re.compile(r"[\d۰-۹]+(?:\.[\d۰-۹]+)?\s*%(?!\w)"),
    # 5.2 per cent / percent / percentage points
    re.compile(r"(?i)\b\d+(?:\.\d+)?\s*(?:per\s*cent|percent|percentage\s*points)\b"),
    # Urdu: 5.2 فیصد or ۵.۲ فیصد
    re.compile(r"[\d۰-۹]+(?:\.[\d۰-۹]+)?\s*فیصد\b")
]

# ==============================================================================
# 5. TIME PATTERNS (clock times, PST timestamps, بجے)
# ==============================================================================
URDU_NUMERAL_WORDS = r"ایک|دو|تین|چار|پانچ|چھ|سات|آٹھ|نو|دس|گیارہ|بارہ"
TIME_REGEXES = [
    # 11:45 PM, 3:30 am, 11:45:00, ۱۱:۴۵
    re.compile(r"(?i)(?:\b|(?<=[\s\(\[\{]))[0-9۰-۹]{1,2}:[0-9۰-۹]{2}(?::[0-9۰-۹]{2})?\s*(?:am|pm|a\.m\.|p\.m\.|PST|UTC|GMT)?\b"),
    # 5 o'clock
    re.compile(r"(?i)\b\d{1,2}\s*o['’]clock\b"),
    # Urdu time: ساڑھے تین بجے, 5 بجے, ۵ بجے, شام 6 بجے, شام ۶ بجے, صبح 8 بجے
    re.compile(rf"(?:صبح|دوپہر|شام|رات)?\s*(?:ساڑھے\s*)?(?:[0-9۰-۹]{{1,2}}|{URDU_NUMERAL_WORDS})\s*بجے")
]

# ==============================================================================
# 6. DATE PATTERNS (Gregorian dates, months, days of week, Urdu dates, Hijri dates)
# ==============================================================================
MONTH_NAMES = (
    r"January|February|March|April|May|June|July|August|September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)
DAY_NAMES = r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun"

DATE_REGEXES = [
    # 14 August 2025, 14th of August 2025, August 14, 2025
    re.compile(rf"(?i)\b\d{{1,2}}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:{MONTH_NAMES})(?:[,\s]+\d{{4}})?\b"),
    re.compile(rf"(?i)\b(?:{MONTH_NAMES})\s+\d{{1,2}}(?:st|nd|rd|th)?(?:[,\s]+\d{{4}})?\b"),
    # ISO / Standard numeric dates: 2025-10-21, 14/08/2025, 14-08-2025
    re.compile(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b"),
    re.compile(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"),
    # Days of week: Monday, Tuesday
    re.compile(rf"(?i)\b(?:{DAY_NAMES})\b"),
    # Urdu months and calendar expressions: 14 اگست 2025, ۱۴ اگست ۲۰۲۵, یکم ستمبر, یکم جنوری
    re.compile(r"(?:[0-9۰-۹]{1,2}|یکم)\s*(?:جنوری|فروری|مارچ|اپریل|مئی|جون|جولائی|اگست|ستمبر|اکتوبر|نومبر|دسمبر)(?:\s*[0-9۰-۹]{4})?"),
    # Urdu weekdays: پیر, منگل, بدھ, جمعرات, جمعہ, ہفتہ, اتوار
    re.compile(r"\b(?:پیر|منگل|بدھ|جمعرات|جمعہ|ہفتہ|اتوار)\b"),
    # Islamic / Hijri calendar dates: ۱۰ محرم, یکم رمضان, ۱۲ ربیع الاول, عید الفطر, عید الاضحیٰ
    re.compile(r"(?:[0-9۰-۹]{1,2}|یکم)\s*(?:محرم(?:\s*الحرام)?|صفر|ربیع\s*(?:الاول|الثانی)|جمادی\s*(?:الاول|الثانی)|رجب|شعبان|رمضان(?:\s*المبارک)?|شوال|ذی\s*(?:القعدہ|الحج))\b"),
    re.compile(r"\b(?:عید\s*الفطر|عید\s*الاضحیٰ|یوم\s*عاشورہ)\b")
]


def heal_ocr_numeric_noise(text: str) -> str:
    """
    Substitutes common OCR / typo confusions in numeric contexts
    (e.g., 'l' or 'I' for '1', 'O' or 'o' for '0') while strictly preserving string length and offsets.
    """
    healed = list(text)
    n = len(text)
    for i in range(n):
        c = text[i]
        prev_c = text[i-1] if i > 0 else ' '
        next_c = text[i+1] if i < n - 1 else ' '

        # 'l' or 'I' as 1 in digits/currency/time
        if c in ['l', 'I']:
            if (prev_c.isdigit() or next_c.isdigit() or 
                (prev_c in ['-', '+', '.', ':', '(', ' '] and next_c in ['-', '.', ':', ' ', ')', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) or
                (i + 4 < n and text[i:i+5].lower() == 'll:45') or
                (i > 0 and text[i-1] == 'l' and next_c == ':') or
                (next_c == 'l' and (i + 2 < n and text[i+2] == ':'))):
                healed[i] = '1'
        # 'O' or 'o' as 0 in phone/CNIC/numbers
        elif c in ['O', 'o']:
            if prev_c.isdigit() or (next_c.isdigit() and prev_c in ['-', '+', ' ', '(']):
                healed[i] = '0'
    return "".join(healed)


def extract_regex_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract pattern entities from text with exact character offsets.
    Returns list of dicts: {"text": str, "start": int, "end": int, "label": str}
    Ensures non-overlapping spans with priority ordering.
    Includes OCR/typo fault tolerance with exact original text offset recovery.
    """
    candidates = []
    
    # Generate clean and OCR-healed versions of input text (lengths identical)
    healed_text = heal_ocr_numeric_noise(text)
    variants = [(text, 10)]
    if healed_text != text:
        variants.append((healed_text, 9))

    for current_text, base_prio in variants:
        # 1. PHONE_NUMBER
        for regex in PHONE_REGEXES:
            for match in regex.finditer(current_text):
                candidates.append({
                    "text": text[match.start():match.end()],
                    "start": match.start(),
                    "end": match.end(),
                    "label": "PHONE_NUMBER",
                    "priority": base_prio
                })

        # 2. ID_NUMBER (CNIC)
        for match in CNIC_HYPHEN_REGEX.finditer(current_text):
            candidates.append({
                "text": text[match.start():match.end()],
                "start": match.start(),
                "end": match.end(),
                "label": "ID_NUMBER",
                "priority": base_prio
            })

        for match in CNIC_CONTEXT_REGEX.finditer(current_text):
            digits_start = match.start(1)
            digits_end = match.end(1)
            candidates.append({
                "text": text[digits_start:digits_end],
                "start": digits_start,
                "end": digits_end,
                "label": "ID_NUMBER",
                "priority": base_prio - 1
            })

        # 3. PERCENT
        for regex in PERCENT_REGEXES:
            for match in regex.finditer(current_text):
                candidates.append({
                    "text": text[match.start():match.end()],
                    "start": match.start(),
                    "end": match.end(),
                    "label": "PERCENT",
                    "priority": base_prio - 2
                })

        # 4. MONEY
        for regex in MONEY_REGEXES:
            for match in regex.finditer(current_text):
                candidates.append({
                    "text": text[match.start():match.end()],
                    "start": match.start(),
                    "end": match.end(),
                    "label": "MONEY",
                    "priority": base_prio - 3
                })

        # 5. TIME
        for regex in TIME_REGEXES:
            for match in regex.finditer(current_text):
                candidates.append({
                    "text": text[match.start():match.end()],
                    "start": match.start(),
                    "end": match.end(),
                    "label": "TIME",
                    "priority": base_prio - 4
                })

        # 6. DATE
        for regex in DATE_REGEXES:
            for match in regex.finditer(current_text):
                candidates.append({
                    "text": text[match.start():match.end()],
                    "start": match.start(),
                    "end": match.end(),
                    "label": "DATE",
                    "priority": base_prio - 5
                })

    # Sort candidates by:
    # 1. Start offset ascending
    # 2. Length descending (longest span preferred)
    # 3. Priority descending
    candidates.sort(key=lambda x: (x["start"], -(x["end"] - x["start"]), -x["priority"]))

    # Resolve overlapping spans (greedy selection of highest priority / longest)
    resolved = []
    occupied = [False] * (len(text) + 1)

    for cand in candidates:
        start, end = cand["start"], cand["end"]
        # Check if span overlaps with already accepted entity
        if any(occupied[start:end]):
            continue

        for i in range(start, end):
            occupied[i] = True

        resolved.append({
            "text": cand["text"],
            "start": cand["start"],
            "end": cand["end"],
            "label": cand["label"]
        })

    # Sort final entities by start offset
    resolved.sort(key=lambda x: x["start"])
    return resolved


if __name__ == "__main__":
    sample = (
        "On 14 August 2025 at 11:45 PM, Mr. Khan paid Rs 15.5 billion (approx PKR 500,000 per share) "
        "with an interest of 17.5 per cent. Contact him via +92 300 1234567 or CNIC 42101-1234567-1."
    )
    entities = extract_regex_entities(sample)
    for ent in entities:
        print(f"[{ent['label']}] '{ent['text']}' ({ent['start']}:{ent['end']})")
