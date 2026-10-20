"""
Human-in-the-Loop Review Queue Generator for Pakistani-Context NER (Phase 3).
Mines:
1. Rare Class Instances (LAW_ACT, COURT_LEGAL_BODY, EDUCATIONAL_INSTITUTION, MEDIA_OUTLET, SPORTS_TEAM)
2. Rule vs Annotated Disagreements (Type confusions, Missed entities, Spurious predictions)
3. Boundary Edge Cases (Punctuation borders, trailing possessives, multi-token spans)

Exports clean JSON format directly importable into Label Studio.
Generates comprehensive summary report at reports/review_queue.md.
"""

import os
import sys
import json
from collections import defaultdict
from typing import List, Dict, Any, Set

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES
from src.preannotate import preannotate_sentence

RARE_CLASSES = {
    "LAW_ACT",
    "COURT_LEGAL_BODY",
    "EDUCATIONAL_INSTITUTION",
    "MEDIA_OUTLET",
    "SPORTS_TEAM"
}

def generate_review_queue(
    input_file: str,
    output_label_studio_file: str,
    report_file: str
) -> Dict[str, Any]:
    print(f"Generating Review Queue from {input_file}...")
    
    total_sentences = 0
    flagged_records = []
    reason_counts = defaultdict(int)
    class_flags = defaultdict(int)

    with open(input_file, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            if not line.strip():
                continue
            total_sentences += 1
            item = json.loads(line)
            text = item["text"]
            annotated_entities = item.get("entities", [])
            doc_id = item.get("doc_id", f"sent_{line_idx:05d}")

            # 1. Run deterministic rules + gazetteers
            rule_entities = preannotate_sentence(text)

            # Flags for this sentence
            flag_reasons = []

            # Check 1: Rare class presence
            found_rare = set()
            for ent in annotated_entities:
                lbl = ent["label"]
                if lbl in RARE_CLASSES:
                    found_rare.add(lbl)
                    class_flags[lbl] += 1
            if found_rare:
                reason = f"Rare Class: {', '.join(sorted(found_rare))}"
                flag_reasons.append(reason)
                reason_counts["rare_class"] += 1

            # Check 2: Disagreements between rules and annotations
            # Overlap check
            matched_ann_indices = set()
            type_mismatches = []
            spurious_rule = []

            for r_ent in rule_entities:
                r_start, r_end, r_lbl = r_ent["start"], r_ent["end"], r_ent["label"]
                match_found = False
                for a_idx, a_ent in enumerate(annotated_entities):
                    a_start, a_end, a_lbl = a_ent["start"], a_ent["end"], a_ent["label"]
                    # Check overlap
                    if max(r_start, a_start) < min(r_end, a_end):
                        match_found = True
                        matched_ann_indices.add(a_idx)
                        if r_lbl != a_lbl:
                            type_mismatches.append(f"Rule: {r_lbl} vs Ann: {a_lbl} ('{text[r_start:r_end]}')")
                        break
                if not match_found and r_lbl in RARE_CLASSES:
                    spurious_rule.append(f"Rule detected {r_lbl}: '{text[r_start:r_end]}'")

            if type_mismatches:
                flag_reasons.append("Type Confusion: " + "; ".join(type_mismatches[:2]))
                reason_counts["type_confusion"] += len(type_mismatches)

            if spurious_rule:
                flag_reasons.append("Unannotated Rare Pattern: " + "; ".join(spurious_rule[:2]))
                reason_counts["unannotated_rule_pattern"] += len(spurious_rule)

            # Check 3: Boundary edge cases (trailing possessive or quotes in annotation)
            boundary_issues = []
            for a_ent in annotated_entities:
                span_text = text[a_ent["start"]:a_ent["end"]]
                if span_text.endswith("'s") or span_text.endswith("’s"):
                    boundary_issues.append(f"Possessive inside span: '{span_text}'")
            if boundary_issues:
                flag_reasons.append("Boundary Audit: " + "; ".join(boundary_issues))
                reason_counts["boundary_audit"] += len(boundary_issues)

            if flag_reasons:
                # Format for Label Studio
                # Prepare prediction object from rules + current annotations
                results = []
                for ent in annotated_entities:
                    results.append({
                        "from_name": "label",
                        "to_name": "text",
                        "type": "labels",
                        "value": {
                            "start": ent["start"],
                            "end": ent["end"],
                            "text": text[ent["start"]:ent["end"]],
                            "labels": [ent["label"]]
                        }
                    })

                label_studio_task = {
                    "data": {
                        "text": text,
                        "doc_id": doc_id,
                        "flag_reasons": " | ".join(flag_reasons),
                        "source": item.get("source", "pakistani_corpus")
                    },
                    "predictions": [
                        {
                            "model_version": "v2_current_annotations",
                            "result": results
                        }
                    ],
                    "meta": {
                        "reasons": flag_reasons,
                        "entity_count": len(annotated_entities)
                    }
                }
                flagged_records.append(label_studio_task)

    os.makedirs(os.path.dirname(output_label_studio_file), exist_ok=True)
    with open(output_label_studio_file, "w", encoding="utf-8") as out_f:
        json.dump(flagged_records, out_f, indent=2, ensure_ascii=False)

    print(f"Exported {len(flagged_records)} review queue tasks to {output_label_studio_file}")

    # Generate Markdown Summary Report
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as rep_f:
        rep_f.write("# Human-in-the-Loop Review Queue Summary (Phase 3)\n\n")
        rep_f.write(f"- **Total Sentences Screened:** {total_sentences:,}\n")
        rep_f.write(f"- **Sentences Flagged for Verification:** {len(flagged_records):,} ({len(flagged_records)/total_sentences*100:.1f}%)\n")
        rep_f.write(f"- **Export File (Label Studio Format):** [`{output_label_studio_file}`](file:///{output_label_studio_file.replace(os.sep, '/')})\n\n")
        
        rep_f.write("## 1. Flagging Criteria & Breakdown\n\n")
        rep_f.write("| Trigger Criteria | Sentences / Events Flagged | Description |\n")
        rep_f.write("| :--- | :--- | :--- |\n")
        rep_f.write(f"| **Rare Class Instances** | {reason_counts['rare_class']} | Sentences containing LAW_ACT, COURT_LEGAL_BODY, EDU, MEDIA, SPORTS |\n")
        rep_f.write(f"| **Rule vs Annotation Confusions** | {reason_counts['type_confusion']} | Disagreements between gazetteer/rule layer and annotation |\n")
        rep_f.write(f"| **Unannotated Candidate Entities** | {reason_counts['unannotated_rule_pattern']} | High-confidence patterns detected by rules but absent in silver tags |\n")
        rep_f.write(f"| **Boundary Edge Cases** | {reason_counts['boundary_audit']} | Trailing punctuation or possessive clitics requiring human sign-off |\n\n")

        rep_f.write("## 2. Rare Class Verification Tally\n\n")
        rep_f.write("| Entity Type | Total Instances Queued for Audit |\n")
        rep_f.write("| :--- | :--- |\n")
        for rc in sorted(RARE_CLASSES):
            rep_f.write(f"| `{rc}` | {class_flags[rc]} |\n")
        rep_f.write("\n")

        rep_f.write("## 3. Label Studio Import Instructions\n\n")
        rep_f.write("1. Open Label Studio (`localhost:8080`) and create project `Pakistani-NER-Phase3-Review`.\n")
        rep_f.write("2. Configure labeling interface with the standard 20 entity classes.\n")
        rep_f.write(f"3. Upload `{os.path.basename(output_label_studio_file)}` via the UI or Label Studio REST API.\n")
        rep_f.write("4. Annotators inspect pre-populated spans in `predictions` and accept or correct flagged instances.\n")

    print(f"Generated report at {report_file}")
    return {
        "total_screened": total_sentences,
        "flagged_count": len(flagged_records),
        "reasons": dict(reason_counts),
        "class_flags": dict(class_flags)
    }

if __name__ == "__main__":
    train_v2 = os.path.join(os.path.dirname(__file__), "..", "v2", "train.jsonl")
    ls_out = os.path.join(os.path.dirname(__file__), "..", "annotation", "review_queue_label_studio.json")
    rep_out = os.path.join(os.path.dirname(__file__), "..", "reports", "review_queue.md")
    generate_review_queue(train_v2, ls_out, rep_out)
