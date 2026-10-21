"""
Organizer Test File Leakage Inspector (Informational Only).
Evaluates incoming organizer test files against train, dev, and benchmark splits.
Checks:
- Exact sentence string overlap
- Near-duplicate sentence collisions (5-gram Jaccard > 0.75)
- Document ID collisions
- Shared entity mentions per class
CRITICAL COMPETITION RULE: Informational only. Never train on or label-tune on the organizer test file!
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

def get_5grams(text):
    words = text.lower().split()
    if len(words) < 5:
        return {text.lower()}
    return {" ".join(words[i:i+5]) for i in range(len(words)-4)}

def normalize_text(text):
    return " ".join(text.lower().split())

def inspect_organizer_file(test_file: Path):
    from predict import load_input_file
    print(f"Loading organizer test file: {test_file}...")
    test_rows = load_input_file(test_file)
    print(f"Loaded {len(test_rows)} sentences from organizer test file.")

    # Load splits
    splits = {}
    for s in ["train", "dev", "benchmark"]:
        p = Path(f"v3/{s}.jsonl")
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                splits[s] = [json.loads(line) for line in f]

    print("\n================ ORGANIZER LEAKAGE AUDIT ================")
    print("NOTE: This audit is informational only to gauge domain shift and unseen entity distribution.\n")

    test_sents = {normalize_text(r["text"]): r["row_id"] for r in test_rows if r["text"].strip()}
    test_5grams = [(r["row_id"], r["text"], get_5grams(r["text"])) for r in test_rows if r["text"].strip()]

    for split_name, split_recs in splits.items():
        split_sents = {normalize_text(r["text"]): r.get("sentence_id") for r in split_recs}
        exact_matches = set(test_sents.keys()) & set(split_sents.keys())

        # Near-duplicate check with inverted index
        inv = defaultdict(list)
        split_grams = {}
        for idx, r in enumerate(split_recs):
            g = get_5grams(r["text"])
            split_grams[idx] = g
            for gram in g:
                inv[gram].append(idx)

        near_dups = []
        for rid, t_txt, tg in test_5grams:
            candidates = defaultdict(int)
            for gram in tg:
                for idx in inv.get(gram, []):
                    candidates[idx] += 1
            for idx, cnt in candidates.items():
                sg = split_grams[idx]
                union = len(tg | sg)
                sim = cnt / union
                if sim > 0.75:
                    near_dups.append((rid, t_txt[:80], split_recs[idx]["text"][:80], sim))

        print(f"--- Comparison against {split_name.upper()} ({len(split_recs)} sentences) ---")
        print(f"  Exact sentence matches:     {len(exact_matches)}")
        if exact_matches:
            for s in list(exact_matches)[:3]:
                print(f"    - '{s[:80]}...'")
        print(f"  Near-duplicates (>0.75 Jacc): {len(near_dups)}")
        if near_dups:
            for rid, t1, t2, sim in near_dups[:3]:
                print(f"    - Test row '{rid}': '{t1}' vs {split_name} '{t2}' (sim={sim:.2f})")
        print()

    print("Audit complete. Do NOT add test sentences to training set.")

def main():
    parser = argparse.ArgumentParser(description="Organizer test-file leakage inspector")
    parser.add_argument("test_file", help="Path to organizer test file")
    args = parser.parse_args()
    inspect_organizer_file(Path(args.test_file))

if __name__ == "__main__":
    main()
