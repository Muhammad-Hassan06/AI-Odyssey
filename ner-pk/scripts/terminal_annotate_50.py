"""
Interactive Terminal Annotation Tool for 50 Human-Gold Sentences.
Loads candidate sentences from review queue, displays predictions with the new v4 model,
allows human reviewer to approve/modify, and saves verified GOLD records.
"""

import os
import sys
import json
from pathlib import Path

# Enforce UTF-8
sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor
from src.constants import ENTITY_TYPES
from src.dataset import spans_to_bio

def run_interactive_annotation(num_sentences=50):
    queue_path = PROJECT_ROOT / "annotation" / "review_queue_label_studio.json"
    output_gold_path = PROJECT_ROOT / "data" / "gold_human_50.jsonl"
    output_gold_path.parent.mkdir(parents=True, exist_ok=True)

    if not queue_path.exists():
        print(f"Error: {queue_path} not found!")
        return

    with open(queue_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    total_tasks = len(tasks)
    target_count = min(num_sentences, total_tasks)
    print("=" * 70)
    print(f"  HUMAN-GOLD TERMINAL ANNOTATION TOOL (Target: {target_count} Sentences)")
    print("  Model: Active v4 Checkpoint + Conservative Hybrid Engine")
    print("=" * 70)
    print("Controls:")
    print("  [Enter]    -> Approve entities as displayed (Mark as GOLD)")
    print("  'e' + Ent  -> Clear all entities (Mark sentence as Negative / 0 entities)")
    print("  'q' + Ent  -> Save and quit early")
    print("=" * 70 + "\n")

    predictor = UnifiedNERPredictor(model_dir=str(PROJECT_ROOT / "models" / "final"), mode="hybrid")

    gold_records = []
    
    # Check if some already completed
    already_done_texts = set()
    if output_gold_path.exists():
        with open(output_gold_path, "r", encoding="utf-8") as gf:
            for line in gf:
                if line.strip():
                    rec = json.loads(line)
                    gold_records.append(rec)
                    already_done_texts.add(rec["text"])
        print(f"Found {len(gold_records)} previously saved GOLD sentences. Resuming...\n")

    count = len(gold_records)
    for idx, task in enumerate(tasks):
        if count >= target_count:
            break

        data = task.get("data", {})
        text = data.get("text", "").strip()
        doc_id = data.get("doc_id", f"gold_sent_{count+1:04d}")

        if not text or text in already_done_texts:
            continue

        # Predict with latest v4 hybrid engine
        pred_entities = predictor.predict_single(text)

        print("-" * 70)
        print(f"Sentence [{count + 1} / {target_count}]:")
        print(f'"{text}"')
        print(f"\nProposed Entities ({len(pred_entities)}):")
        if not pred_entities:
            print("  (None / 0 entities detected)")
        else:
            for e_idx, ent in enumerate(pred_entities, start=1):
                print(f"  {e_idx}. [{ent['label']:<22}] \"{ent['text']}\" (offsets: {ent['start']}-{ent['end']})")

        print("-" * 70)
        try:
            user_choice = input("Approve? [Press Enter to Approve, 'e' for None, 'q' to Quit]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting session...")
            break

        if user_choice == "q":
            print("Saving and quitting session...")
            break
        elif user_choice == "e":
            final_entities = []
            print("✔ Recorded as 0 entities.")
        else:
            final_entities = pred_entities
            print("✔ Approved as GOLD.")

        tokens, bio = spans_to_bio(text, final_entities)
        record = {
            "sentence_id": f"human_gold_{count+1:04d}",
            "doc_id": doc_id,
            "text": text,
            "entities": final_entities,
            "tokens": tokens,
            "bio_tags": bio,
            "tier": "GOLD",
            "annotated_by": "human_reviewer",
            "synthetic": False
        }

        gold_records.append(record)
        already_done_texts.add(text)
        count += 1

        # Incremental save
        with open(output_gold_path, "w", encoding="utf-8") as gf:
            for rec in gold_records:
                gf.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("\n" + "=" * 70)
    print(f"COMPLETED! Saved {len(gold_records)} Human-Gold verified sentences to:")
    print(f"  {output_gold_path}")
    print("=" * 70)

if __name__ == "__main__":
    num = 50
    if len(sys.argv) > 1:
        try:
            num = int(sys.argv[1])
        except ValueError:
            pass
    run_interactive_annotation(num_sentences=num)
