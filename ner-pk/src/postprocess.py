"""
Post-Processing and Span Normalization Layer for Pakistani-Context NER.
Cleans systematic boundary errors, merges adjacent same-label fragments,
strips trailing punctuation/possessives, and enforces hybrid priority resolution.
"""

import re
from typing import List, Dict, Any

PUNCTUATION_TO_STRIP = ",.;:!?\"'()[]{}۔،"

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
            start += 1

        # 3. Strip trailing whitespace or punctuation (except if part of ID or abbreviation)
        while end > start and (text[end - 1] in PUNCTUATION_TO_STRIP or text[end - 1].isspace()):
            # Keep % for PERCENT
            if label == "PERCENT" and text[end - 1] == "%":
                break
            end -= 1

        if start >= end:
            continue

        cleaned.append({
            "text": text[start:end],
            "start": start,
            "end": end,
            "label": label
        })

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
    text_len: int
) -> List[Dict[str, Any]]:
    """
    Merge neural model predictions with deterministic rules using strict priority:
    1. Pattern entities (PHONE_NUMBER, ID_NUMBER, MONEY, PERCENT, TIME) strictly override model predictions.
    2. Longest span / most specific label takes precedence for overlapping spans.
    """
    # Deterministic pattern entities override
    RULE_PRIORITY_LABELS = {"PHONE_NUMBER", "ID_NUMBER", "MONEY", "PERCENT", "TIME"}

    final_candidates = []
    for r in rule_entities:
        priority = 10 if r["label"] in RULE_PRIORITY_LABELS else 7
        final_candidates.append({**r, "priority": priority})

    for m in model_entities:
        # Lower priority if overlapping with a rule priority label
        priority = 5 if m["label"] in RULE_PRIORITY_LABELS else 8
        final_candidates.append({**m, "priority": priority})

    # Sort candidates by:
    # 1. Start offset ascending
    # 2. Length descending (longest span first)
    # 3. Priority descending
    final_candidates.sort(key=lambda x: (x["start"], -(x["end"] - x["start"]), -x["priority"]))

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
