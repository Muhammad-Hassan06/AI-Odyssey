"""
Corpus cleaning, Unicode normalization, Urdu sentence tokenization,
PII scrubbing, and near-duplicate filtering for Pakistani text.
"""

import os
import re
import json
import unicodedata
import hashlib
from typing import List, Dict, Set

# Regex patterns for sentence splitting
# Handles English periods and Urdu full stop (۔) and question marks (؟)
URDU_FULL_STOP = "\u06D4"
URDU_QUESTION_MARK = "\u061F"

ABBREVIATIONS = {
    "mr", "mrs", "dr", "prof", "justice", "retd", "vs", "e.g", "i.e", "pvt", "ltd",
    "co", "corp", "inc", "rs", "no", "sec", "art", "vol", "pp", "jan", "feb", "mar",
    "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec"
}

# Regex to scrub any real PII numbers if present in scraped text
REAL_PHONE_PATTERN = re.compile(r"(\+92|0092|03\d{2})[- ]?\d{7}\b")
REAL_CNIC_PATTERN = re.compile(r"\b\d{5}[- ]?\d{7}[- ]?\d\b")

def normalize_unicode(text: str) -> str:
    """Normalize text into NFKC representation and standardize whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    # Replace non-breaking spaces and zero-width spaces
    text = text.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")
    # Normalize multiple whitespace
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def scrub_pii(text: str) -> str:
    """Scrub any real contact details (phone numbers or CNIC) found in public text."""
    text = REAL_PHONE_PATTERN.sub("[REDACTED_CONTACT]", text)
    text = REAL_CNIC_PATTERN.sub("[REDACTED_ID]", text)
    return text

def split_into_sentences(text: str, language: str = "en") -> List[str]:
    """
    Split text into sentences cleanly, honoring both English and Urdu sentence boundaries.
    Prevents erroneous splits on common abbreviations (e.g., 'Rs.', 'Dr.').
    """
    text = normalize_unicode(text)
    if not text:
        return []

    # Temporary mask for abbreviations
    tokens = text.split(" ")
    masked_tokens = []
    for t in tokens:
        clean_t = t.lower().rstrip(".:")
        if clean_t in ABBREVIATIONS and "." in t:
            masked_tokens.append(t.replace(".", "@DOT@"))
        else:
            masked_tokens.append(t)
    
    masked_text = " ".join(masked_tokens)

    # Split on sentence terminals
    pattern = rf"(?<=[.!?{URDU_FULL_STOP}{URDU_QUESTION_MARK}])\s+"
    raw_sentences = re.split(pattern, masked_text)

    clean_sentences = []
    for s in raw_sentences:
        s = s.replace("@DOT@", ".").strip()
        # Drop sentences with fewer than 5 or more than 80 words
        word_count = len(s.split())
        if 5 <= word_count <= 80:
            clean_sentences.append(s)

    return clean_sentences

def compute_ngrams(tokens: List[str], n: int = 5) -> Set[str]:
    """Compute n-grams for near-duplicate Jaccard similarity checking."""
    if len(tokens) < n:
        return {" ".join(tokens)}
    return {" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}

def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Calculate Jaccard similarity between two n-gram sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0

def clean_and_process_documents(raw_dir: str, interim_path: str) -> Dict[str, int]:
    """
    Read all raw documents, normalize, split sentences, scrub PII,
    deduplicate with exact hash and near-duplicate MinHash/n-grams,
    and save clean sentences with document-level provenance.
    """
    os.makedirs(os.path.dirname(interim_path), exist_ok=True)
    
    exact_hashes = set()
    ngram_cache: List[Set[str]] = []
    
    total_docs = 0
    total_raw_sentences = 0
    accepted_sentences = 0
    
    with open(interim_path, "w", encoding="utf-8") as out_f:
        if not os.path.exists(raw_dir):
            return {"docs": 0, "accepted_sentences": 0}

        for fname in sorted(os.listdir(raw_dir)):
            if not fname.endswith(".json"):
                continue

            fpath = os.path.join(raw_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                try:
                    doc = json.load(f)
                except Exception:
                    continue

            total_docs += 1
            doc_id = doc.get("id", fname.replace(".json", ""))
            source = doc.get("source", "Unknown")
            domain = doc.get("domain", "General")
            language = doc.get("language", "en")
            raw_text = doc.get("text", "")

            # Scrub PII
            safe_text = scrub_pii(raw_text)
            sentences = split_into_sentences(safe_text, language=language)

            for idx, s in enumerate(sentences):
                total_raw_sentences += 1
                # Exact deduplication via SHA-256
                s_hash = hashlib.sha256(s.lower().encode("utf-8")).hexdigest()
                if s_hash in exact_hashes:
                    continue

                # Near-duplicate check via 5-gram overlap (Jaccard > 0.85)
                words = s.lower().split()
                s_ngrams = compute_ngrams(words, n=5)
                is_near_duplicate = False
                for existing_ngrams in ngram_cache[-150:]: # Compare against recent window for efficiency
                    if jaccard_similarity(s_ngrams, existing_ngrams) > 0.85:
                        is_near_duplicate = True
                        break

                if is_near_duplicate:
                    continue

                exact_hashes.add(s_hash)
                ngram_cache.append(s_ngrams)
                accepted_sentences += 1

                record = {
                    "sentence_id": f"{doc_id}_s{idx:03d}",
                    "doc_id": doc_id,
                    "source": source,
                    "domain": domain,
                    "language": language,
                    "text": s
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "docs_processed": total_docs,
        "raw_sentences": total_raw_sentences,
        "accepted_sentences": accepted_sentences
    }

if __name__ == "__main__":
    import yaml
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    raw_dir = os.path.join(os.path.dirname(__file__), "..", cfg["paths"]["raw_data_dir"])
    interim_file = os.path.join(os.path.dirname(__file__), "..", cfg["paths"]["interim_data_dir"], "clean_corpus.jsonl")

    stats = clean_and_process_documents(raw_dir, interim_file)
    print(f"Cleaning complete: {stats}")
