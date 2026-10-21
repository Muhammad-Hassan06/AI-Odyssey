"""
Evaluator for Human-Verified GOLD Set.
Evaluates models/final (and Conservative Hybrid) on the human-corrected set once.
Outputs strict seqeval precision, recall, F1, support per class.
Saves report to reports/audit_final/human_gold_evaluation.md.
"""

import sys
import json
import argparse
from pathlib import Path
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score

# Enforce UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor
from src.dataset import spans_to_bio

def evaluate_gold(gold_file: Path, model_dir: str = "models/final"):
    print(f"Loading Human-Verified GOLD set: {gold_file}...")
    with open(gold_file, "r", encoding="utf-8") as f:
        gold_records = [json.loads(line) for line in f]

    print(f"Loaded {len(gold_records)} GOLD sentences.")

    predictor = UnifiedNERPredictor(model_dir=model_dir, mode="hybrid")

    gold_bio = []
    pred_bio = []

    print(f"Predicting with {predictor.mode.upper()} mode on {len(gold_records)} sentences...")
    for idx, r in enumerate(gold_records):
        text = r["text"]
        g_bio = r["bio_tags"]

        pred_ents = predictor.predict_single(text)
        _, p_bio = spans_to_bio(text, pred_ents)

        if len(p_bio) < len(g_bio):
            p_bio.extend(["O"] * (len(g_bio) - len(p_bio)))
        elif len(p_bio) > len(g_bio):
            p_bio = p_bio[:len(g_bio)]

        gold_bio.append(g_bio)
        pred_bio.append(p_bio)

    p = precision_score(gold_bio, pred_bio)
    r = recall_score(gold_bio, pred_bio)
    f1 = f1_score(gold_bio, pred_bio)
    rep_dict = classification_report(gold_bio, pred_bio, output_dict=True, zero_division=0)
    rep_text = classification_report(gold_bio, pred_bio, digits=4, zero_division=0)

    print("\n================ HUMAN-GOLD EVALUATION RESULTS ================")
    print(f"Precision: {p*100:.2f}% | Recall: {r*100:.2f}% | Micro F1: {f1*100:.2f}%")
    print(f"Macro F1:  {rep_dict['macro avg']['f1-score']*100:.2f}%")
    print("\n" + rep_text)
    print("===============================================================")

    # Save to report
    out_dir = Path("reports/audit_final")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / "human_gold_evaluation.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Evaluation on Human-Verified GOLD Benchmark Set\n\n")
        f.write(f"**Date:** 21 October 2026  \n")
        f.write(f"**Model Checkpoint:** `{model_dir}`  \n")
        f.write(f"**Inference Mode:** Conservative Hybrid  \n")
        f.write(f"**Verified Sentences:** {len(gold_records)} human-gold sentences  \n\n")
        f.write("## Overall Metrics\n\n")
        f.write(f"- **Strict Micro Precision:** {p*100:.2f}%\n")
        f.write(f"- **Strict Micro Recall:** {r*100:.2f}%\n")
        f.write(f"- **Strict Micro F1:** **{f1*100:.2f}%**\n")
        f.write(f"- **Strict Macro F1:** {rep_dict['macro avg']['f1-score']*100:.2f}%\n\n")
        f.write("## Per-Class Breakdown\n\n```\n")
        f.write(rep_text)
        f.write("\n```\n")

    print(f"Saved evaluation report to {report_file}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate on human-verified gold set")
    parser.add_argument("--gold_file", default="data/review/human_gold_300.jsonl", help="Path to verified gold JSONL")
    parser.add_argument("--model_dir", default="models/final", help="Path to model checkpoint")
    args = parser.parse_args()

    evaluate_gold(Path(args.gold_file), model_dir=args.model_dir)

if __name__ == "__main__":
    main()
