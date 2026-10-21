"""
Post-Processing and Span Normalization Layer for Pakistani-Context NER.
Cleans systematic boundary errors, merges adjacent same-label fragments,
strips trailing punctuation/possessives, and enforces hybrid priority resolution.
"""

import re
from typing import List, Dict, Any

PUNCTUATION_TO_STRIP = ",.;:!?\"'()[]{}۔،"


FALSE_POSITIVE_WORDS = {
    "MEDIA_OUTLET": {"dawn", "daw", "nation", "the nation", "star", "sun", "today", "express", "رات"},
    "GOVERNMENT_BODY": {"nab"},
    "ORGANIZATION": {"jazz", "united", "express"}
}

def is_unwanted_false_positive(text: str, ent: Dict[str, Any]) -> bool:
    lbl = ent["label"]
    start, end = ent["start"], ent["end"]
    span = text[start:end].strip()
    span_lower = span.lower()

    # 1. Single-letter alphabetic fragment (e.g. "n", "s") is an orphan subword, never an entity!
    if len(span) <= 1 and span.isalpha():
        return True

    # 2. Subword fragment that cuts inside an alphanumeric word boundary
    if start > 0 and text[start - 1].isalnum() and text[start].isalnum():
        return True
    if end < len(text) and text[end - 1].isalnum() and text[end].isalnum():
        return True

        # 2.5 PERCENT must contain % or percent or فیصد
    if lbl == "PERCENT":
        if not ("%" in span or "percent" in span_lower or "per cent" in span_lower or "فیصد" in span):
            return True

    if lbl in FALSE_POSITIVE_WORDS:
        if span_lower in FALSE_POSITIVE_WORDS[lbl]:
            # Proper nouns must be Title Case or UPPERCASE, not lowercase homonyms
            if span.islower() or span == "رات":
                return True
            if span_lower == "the nation":
                # Guard against "the nation's economy" or "addressed the nation"
                surrounding = text[max(0, start - 15):min(len(text), end + 15)].lower()
                if "'s" in text[end:end+2] or any(w in surrounding for w in ["addressed", "across", "for", "economy", "centre of"]):
                    return True
    return False

def clean_span_boundaries(text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean span boundaries:
    1. Strip leading and trailing whitespace or punctuation from entity spans.
    2. Strip English possessive `'s` or `s'` from person/org names per guidelines.
    3. Update character offsets accordingly.
    """
    cleaned = []
    for ent in entities:
        start = ent["start"]
        end = ent["end"]
        label = ent["label"]
        span_text = text[start:end]

        # 1. Strip trailing possessives ('s or s')
        if span_text.endswith("'s") or span_text.endswith("’s"):
            end -= 2
            span_text = span_text[:-2]
        elif span_text.endswith("s'") or span_text.endswith("s’"):
            end -= 1
            span_text = span_text[:-1]

        # 2. Strip leading whitespace or punctuation
        while start < end and (text[start] in PUNCTUATION_TO_STRIP or text[start].isspace()):
            if label == "PHONE_NUMBER" and text[start] == "(" and ")" in text[start:end]:
                break
            start += 1

        # 3. Strip trailing whitespace or punctuation (except if part of ID or abbreviation)
        while end > start and (text[end - 1] in PUNCTUATION_TO_STRIP or text[end - 1].isspace()):
            # Keep % for PERCENT
            if label == "PERCENT" and text[end - 1] == "%":
                break
            # Keep dot for a.m. and p.m. in TIME
            if label == "TIME" and text[start:end].lower().endswith(("a.m.", "p.m.")):
                break
            end -= 1

        if start >= end:
            continue

        cand_ent = {
            "text": text[start:end],
            "start": start,
            "end": end,
            "label": label
        }
        if not is_unwanted_false_positive(text, cand_ent):
            cleaned.append(cand_ent)

    return cleaned

def merge_adjacent_fragments(text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge adjacent or whitespace-separated spans of identical entity type.
    Example: [Rs 10] [crore] -> [Rs 10 crore]
    """
    if len(entities) <= 1:
        return entities

    entities = sorted(entities, key=lambda x: x["start"])
    merged = [entities[0]]

    for current in entities[1:]:
        prev = merged[-1]
        # Check if same label and separated only by a space or hyphen
        gap = text[prev["end"]:current["start"]]
        if prev["label"] == current["label"] and gap in [" ", "-", ""]:
            # Do not merge statute name (e.g. CrPC, PPC) with statutory section (e.g. Section 144)
            if prev["label"] == "LAW_ACT" and current["text"].startswith(("Section", "Sec.", "Article", "Art.", "دفعہ", "آرٹیکل")):
                merged.append(current)
                continue
            # Merge into prev
            merged[-1] = {
                "text": text[prev["start"]:current["end"]],
                "start": prev["start"],
                "end": current["end"],
                "label": prev["label"]
            }
        else:
            merged.append(current)

    return merged

def hybrid_merge_predictions(
    model_entities: List[Dict[str, Any]],
    rule_entities: List[Dict[str, Any]],
    text_len: int,
    confidence_thresholds: Dict[str, float] = None,
    default_threshold: float = 0.40
) -> List[Dict[str, Any]]:
    """
    Merge neural model predictions with deterministic rules using conservative priority:
    1. Deterministic pattern entities (PHONE_NUMBER, ID_NUMBER, MONEY, PERCENT, TIME, DATE)
       from rules have absolute highest priority (100).
    2. Curated high-precision gazetteer matches have priority (80).
    3. Neural model spans for contextual classes (PERSON, ORGANIZATION, EVENT, LANDMARK_FACILITY)
       are filtered by tuned confidence thresholds, and retained unless conflicting with rules.
    4. Post-inference label filter: remaps GOVERNMENT_BODIES -> GOVERNMENT_BODY, drops invalid.
    """
    if confidence_thresholds is None:
        confidence_thresholds = {
            "PERSON": 0.40,
            "LANDMARK_FACILITY": 0.40,
            "ORGANIZATION": 0.40,
            "GOVERNMENT_BODY": 0.40,
            "DATE": 0.35
        }

    ALLOWED_20_LABELS = {
        "PERSON", "CITY", "PROVINCE_REGION", "COUNTRY", "LANDMARK_FACILITY",
        "GOVERNMENT_BODY", "POLITICAL_PARTY", "ORGANIZATION", "EDUCATIONAL_INSTITUTION",
        "COURT_LEGAL_BODY", "LAW_ACT", "EVENT", "MEDIA_OUTLET", "SPORTS_TEAM",
        "DATE", "TIME", "MONEY", "PERCENT", "PHONE_NUMBER", "ID_NUMBER"
    }

    DETERMINISTIC_RULE_LABELS = {"PHONE_NUMBER", "ID_NUMBER", "MONEY", "PERCENT", "TIME", "DATE"}
    GAZETTEER_LABELS = {
        "COURT_LEGAL_BODY", "GOVERNMENT_BODY", "LAW_ACT", "POLITICAL_PARTY",
        "EDUCATIONAL_INSTITUTION", "MEDIA_OUTLET", "SPORTS_TEAM", "CITY",
        "PROVINCE_REGION", "COUNTRY", "ORGANIZATION", "EVENT", "LANDMARK_FACILITY"
    }

    final_candidates = []
    for r in rule_entities:
        lbl = r["label"]
        if lbl == "GOVERNMENT_BODIES":
            lbl = "GOVERNMENT_BODY"
            r["label"] = lbl
        if lbl not in ALLOWED_20_LABELS:
            continue

        if lbl in DETERMINISTIC_RULE_LABELS:
            priority = 100
        elif lbl in GAZETTEER_LABELS or lbl == "PERSON":
            priority = 85
        else:
            priority = 60
        final_candidates.append({**r, "priority": priority, "source": "rule"})

    for m in model_entities:
        lbl = m["label"]
        if lbl == "GOVERNMENT_BODIES":
            lbl = "GOVERNMENT_BODY"
            m["label"] = lbl
        if lbl not in ALLOWED_20_LABELS:
            continue

        conf = m.get("confidence", 1.0)
        thresh = confidence_thresholds.get(lbl, default_threshold)
        if conf < thresh:
            continue

        # Model predictions on deterministic or closed-set classes get lower priority
        if lbl in DETERMINISTIC_RULE_LABELS:
            priority = 30
        elif lbl in GAZETTEER_LABELS:
            priority = 50
        else:
            priority = 70
        final_candidates.append({**m, "priority": priority, "source": "model"})

    # Sort strictly by priority DESCENDING first, then span length DESCENDING
    final_candidates.sort(key=lambda x: (-x["priority"], -(x["end"] - x["start"]), x["start"]))

    resolved = []
    occupied = [False] * (text_len + 1)

    for cand in final_candidates:
        start, end = cand["start"], cand["end"]
        if start < 0 or end > text_len or start >= end:
            continue
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

    resolved.sort(key=lambda x: x["start"])
    return resolved


def postprocess_entities(text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Complete postprocessing pipeline: clean boundaries -> merge fragments."""
    cleaned = clean_span_boundaries(text, entities)
    merged = merge_adjacent_fragments(text, cleaned)
    return merged
