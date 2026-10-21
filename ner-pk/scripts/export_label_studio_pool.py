"""
Export 300 English sentences from un-split pool documents into Label Studio JSON.
Prioritizes rare classes: GOVERNMENT_BODY, ORGANIZATION, POLITICAL_PARTY, PERSON, EVENT, DATE.
Pre-fills labels using models/final checkpoint and marks each prediction UNVERIFIED.
"""

import os
import sys
import json
import random
from pathlib import Path
from collections import defaultdict

# Enforce UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor

RARE_CLASSES = ["GOVERNMENT_BODY", "ORGANIZATION", "POLITICAL_PARTY", "PERSON", "EVENT", "DATE"]

def normalize_text(text):
    return " ".join(text.lower().split())

def is_english(text):
    # Check ASCII / Latin ratio
    if not text or len(text.strip()) < 15:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    return (ascii_chars / len(text)) > 0.85

def main():
    print("Loading active split sentences to ensure ZERO split overlap...")
    active_texts = set()
    for split in ["train", "dev", "benchmark"]:
        p = Path(f"v3/{split}.jsonl")
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    r = json.loads(line)
                    active_texts.add(normalize_text(r["text"]))

    print(f"Collected {len(active_texts)} active split sentences.")

    # Load candidate sentences from clean_corpus.jsonl and data/raw/
    candidates = []
    seen_cand_texts = set()

    corpus_path = Path("data/interim/clean_corpus.jsonl")
    if corpus_path.exists():
        with open(corpus_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                r = json.loads(line)
                txt = r.get("text", "").strip()
                norm = normalize_text(txt)
                if norm not in active_texts and norm not in seen_cand_texts and is_english(txt):
                    candidates.append({"id": f"corpus_{idx}", "text": txt, "source": r.get("source", "corpus")})
                    seen_cand_texts.add(norm)

    # Also load from data/raw if needed
    raw_dir = Path("data/raw")
    if raw_dir.exists():
        for fpath in raw_dir.glob("wikipedia_*.json"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                    text = doc.get("text", "")
                    for idx, para in enumerate(text.split("\n\n")):
                        para = para.strip()
                        if 40 <= len(para) <= 300 and is_english(para):
                            norm = normalize_text(para)
                            if norm not in active_texts and norm not in seen_cand_texts:
                                candidates.append({"id": f"{fpath.stem}_p{idx}", "text": para, "source": fpath.stem})
                                seen_cand_texts.add(norm)
            except Exception:
                continue

    print(f"Discovered {len(candidates)} unallocated, non-split English candidate sentences.")

    # Initialize predictor with real fine-tuned checkpoint
    print("Initializing Unified Predictor with models/final...")
    predictor = UnifiedNERPredictor(model_dir="models/final", mode="hybrid")

    scored_candidates = []
    print(f"Scoring candidates to prioritize rare classes {RARE_CLASSES}...")
    for idx, cand in enumerate(candidates):
        txt = cand["text"]
        preds = predictor.predict_single(txt)
        cand["entities"] = preds

        # Score based on rare classes
        score = 0
        counts = defaultdict(int)
        for e in preds:
            counts[e["label"]] += 1
            if e["label"] in RARE_CLASSES:
                score += 3
            else:
                score += 1

        cand["score"] = score
        cand["class_counts"] = dict(counts)
        scored_candidates.append(cand)

    # Sort candidates by score descending
    scored_candidates.sort(key=lambda x: -x["score"])
    selected_300 = scored_candidates[:300]
    print(f"Selected 300 sentences maximizing rare class diversity.")

    # Convert to Label Studio JSON format
    label_studio_tasks = []
    for idx, item in enumerate(selected_300):
        task_id = item["id"]
        text = item["text"]
        entities = item["entities"]

        ls_predictions = []
        for ent in entities:
            ls_predictions.append({
                "from_name": "label",
                "to_name": "text",
                "type": "labels",
                "value": {
                    "start": ent["start"],
                    "end": ent["end"],
                    "text": ent["text"],
                    "labels": [ent["label"]]
                }
            })

        task = {
            "id": idx + 1,
            "data": {
                "text": text,
                "sentence_id": task_id,
                "source": item.get("source", "unallocated_pool")
            },
            "predictions": [
                {
                    "model_version": "models/final (xlm-roberta-base)",
                    "result": ls_predictions
                }
            ],
            "meta": {
                "verification_status": "UNVERIFIED",
                "note": "Pre-filled by fine-tuned model for human review. Spans must be validated by 2 annotators for GOLD tier."
            }
        }
        label_studio_tasks.append(task)

    out_dir = Path("data/review")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "label_studio_300_unverified.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(label_studio_tasks, f, ensure_ascii=False, indent=2)

    # Summary statistics
    rare_counts = defaultdict(int)
    for s in selected_300:
        for lbl, cnt in s["class_counts"].items():
            rare_counts[lbl] += cnt

    print(f"\nSaved Label Studio export to: {out_file}")
    print("Class distribution across 300 exported sentences:")
    for lbl in RARE_CLASSES:
        print(f"  {lbl:<25}: {rare_counts[lbl]} mentions")

if __name__ == "__main__":
    main()
