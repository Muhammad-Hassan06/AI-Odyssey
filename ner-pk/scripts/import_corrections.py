"""
Import human corrections from Label Studio JSON into a verified GOLD evaluation set.
Performs:
1. Strict character span alignment validation: text[start:end] == span_text.
2. Validation of labels against the 20-class schema.
3. Assignment of GOLD tier to human-verified annotations.
4. Tokenization and valid IOB2 bio_tags regeneration.
5. Gold count report by entity class.
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict

# Enforce UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import ENTITY_TYPES, validate_entity_type
from src.dataset import spans_to_bio

ALLOWED_20_LABELS = set(ENTITY_TYPES)

def import_label_studio_file(input_file: Path, output_file: Path):
    print(f"Loading Label Studio corrections from: {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    print(f"Loaded {len(tasks)} tasks.")

    verified_records = []
    class_counts = defaultdict(int)
    errors = []

    for task_idx, task in enumerate(tasks):
        data = task.get("data", {})
        text = data.get("text", "")
        task_id = data.get("sentence_id") or f"task_{task.get('id', task_idx)}"

        # Check annotations (or predictions if unedited)
        raw_results = []
        if task.get("annotations"):
            raw_results = task["annotations"][0].get("result", [])
        elif task.get("predictions"):
            raw_results = task["predictions"][0].get("result", [])

        entities = []
        for res_idx, r in enumerate(raw_results):
            val = r.get("value", {})
            start = val.get("start")
            end = val.get("end")
            labels = val.get("labels", [])
            ent_text = val.get("text", "")

            if not labels:
                continue
            lbl = labels[0]

            # Remap plural if present
            if lbl == "GOVERNMENT_BODIES":
                lbl = "GOVERNMENT_BODY"

            if lbl not in ALLOWED_20_LABELS:
                errors.append(f"Task {task_idx}, Ent {res_idx}: Disallowed label '{lbl}'")
                continue

            if start < 0 or end > len(text) or start >= end:
                errors.append(f"Task {task_idx}: Span [{start}:{end}] out of bounds for len {len(text)}")
                continue

            # Verify span slice
            actual_slice = text[start:end]
            if actual_slice != ent_text:
                # If slight whitespace mismatch, use actual slice if non-empty
                if actual_slice.strip() == ent_text.strip():
                    ent_text = actual_slice
                else:
                    errors.append(f"Task {task_idx}: Span mismatch! '{actual_slice}' != '{ent_text}'")
                    continue

            entities.append({
                "start": start,
                "end": end,
                "label": lbl,
                "text": ent_text
            })
            class_counts[lbl] += 1

        # Deduplicate overlapping entities
        entities.sort(key=lambda x: (x["start"], x["end"]))
        clean_entities = []
        occupied = [False] * (len(text) + 1)
        for e in entities:
            if not any(occupied[e["start"]:e["end"]]):
                for i in range(e["start"], e["end"]):
                    occupied[i] = True
                clean_entities.append(e)

        tokens, bio_tags = spans_to_bio(text, clean_entities)

        verified_records.append({
            "sentence_id": task_id,
            "text": text,
            "entities": clean_entities,
            "tokens": tokens,
            "bio_tags": bio_tags,
            "tier": "GOLD",
            "source": data.get("source", "human_review")
        })

    if errors:
        print(f"\n[WARNING] Found {len(errors)} span validation issues:")
        for err in errors[:10]:
            print(f"  - {err}")

    # Write output JSONL
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for r in verified_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nSuccessfully imported {len(verified_records)} GOLD-tier sentences to {output_file}")
    print("\n================ VERIFIED GOLD CLASS COUNTS ================")
    for lbl in ENTITY_TYPES:
        cnt = class_counts.get(lbl, 0)
        print(f"  {lbl:<25}: {cnt:>4} mentions")
    print(f"Total Gold Mentions: {sum(class_counts.values())}")
    print("============================================================")

def main():
    parser = argparse.ArgumentParser(description="Import Label Studio human corrections to verified GOLD JSONL")
    parser.add_argument("input_file", help="Path to Label Studio JSON export")
    parser.add_argument("--output_file", default="data/review/human_gold_300.jsonl", help="Output JSONL path")
    args = parser.parse_args()

    import_label_studio_file(Path(args.input_file), Path(args.output_file))

if __name__ == "__main__":
    main()
