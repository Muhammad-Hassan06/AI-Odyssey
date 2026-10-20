"""
Baseline Evaluator for Pakistani NER.
Evaluates the deterministic Regex + Gazetteer rule-based layer on the exact BIO tokens
using strict IOB2 entity-level metrics via seqeval.
Provides the foundational ablation benchmark required for the final report.
"""

import os
import sys
import json
from typing import List, Dict, Any
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES, BIO_LABELS
from src.preannotate import preannotate_sentence
from src.dataset import spans_to_bio

def evaluate_rule_baseline(data_path: str, output_report_path: str = None) -> Dict[str, Any]:
    """
    Evaluate the rules + gazetteer pipeline against gold annotations in data_path.
    Calculates strict seqeval entity-level metrics.
    """
    print(f"Evaluating Rules + Gazetteer Baseline on {data_path}...")
    
    gold_tags_all: List[List[str]] = []
    pred_tags_all: List[List[str]] = []
    
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            text = item["text"]
            gold_bio = item.get("bio_tags", [])
            tokens = item.get("tokens", [])

            # Extract entities using deterministic rules + gazetteers
            pred_entities = preannotate_sentence(text)
            _, pred_bio = spans_to_bio(text, pred_entities)

            # Ensure lengths match
            if len(pred_bio) < len(gold_bio):
                pred_bio.extend(["O"] * (len(gold_bio) - len(pred_bio)))
            elif len(pred_bio) > len(gold_bio):
                pred_bio = pred_bio[:len(gold_bio)]

            gold_tags_all.append(gold_bio)
            pred_tags_all.append(pred_bio)

    strict_p = precision_score(gold_tags_all, pred_tags_all)
    strict_r = recall_score(gold_tags_all, pred_tags_all)
    strict_f1 = f1_score(gold_tags_all, pred_tags_all)
    report_str = classification_report(gold_tags_all, pred_tags_all, digits=4)

    results = {
        "precision": float(strict_p),
        "recall": float(strict_r),
        "f1": float(strict_f1),
        "classification_report": report_str
    }

    print("\n--- RULES + GAZETTEER BASELINE RESULTS ---")
    print(f"Strict Overall Precision : {strict_p * 100:.2f}%")
    print(f"Strict Overall Recall    : {strict_r * 100:.2f}%")
    print(f"Strict Overall F1 Score  : {strict_f1 * 100:.2f}%\n")
    print(report_str)
    print("------------------------------------------\n")

    if output_report_path:
        os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
        with open(output_report_path, "w", encoding="utf-8") as out_f:
            out_f.write(f"# Baseline Evaluation Report: Rules + Gazetteers\n\n")
            out_f.write(f"- **Overall Precision:** {strict_p * 100:.2f}%\n")
            out_f.write(f"- **Overall Recall:** {strict_r * 100:.2f}%\n")
            out_f.write(f"- **Overall F1 Score:** {strict_f1 * 100:.2f}%\n\n")
            out_f.write("```\n")
            out_f.write(report_str)
            out_f.write("\n```\n")
        print(f"Saved baseline report to {output_report_path}")

    return results

if __name__ == "__main__":
    dev_file = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "dev.jsonl")
    report_file = os.path.join(os.path.dirname(__file__), "..", "reports", "tables", "baseline_rules_report.md")
    evaluate_rule_baseline(dev_file, report_file)
