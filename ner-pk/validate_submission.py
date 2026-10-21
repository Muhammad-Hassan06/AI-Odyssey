"""
Submission Validator for TechFest NER Challenge.
Validates submission prediction files against original test input files.
Checks:
1. Row count and row IDs strictly match input file in exact order.
2. Only the 20 allowed entity labels exist in entities and BIO tags.
3. Strict IOB2 BIO tag transition consistency.
4. Spans strictly inside text bounds and match character slices.
5. Output is non-empty.
Exits with code 0 on PASSED, code 1 on FAILED.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

sys.stdout.reconfigure(encoding="utf-8")

ALLOWED_20_LABELS = {
    "PERSON",
    "CITY",
    "PROVINCE_REGION",
    "COUNTRY",
    "LANDMARK_FACILITY",
    "GOVERNMENT_BODY",
    "POLITICAL_PARTY",
    "ORGANIZATION",
    "EDUCATIONAL_INSTITUTION",
    "COURT_LEGAL_BODY",
    "LAW_ACT",
    "EVENT",
    "MEDIA_OUTLET",
    "SPORTS_TEAM",
    "DATE",
    "TIME",
    "MONEY",
    "PERCENT",
    "PHONE_NUMBER",
    "ID_NUMBER",
}

ALLOWED_BIO = {"O"} | {f"B-{lbl}" for lbl in ALLOWED_20_LABELS} | {f"I-{lbl}" for lbl in ALLOWED_20_LABELS}

def load_rows_from_input(file_path: Path) -> List[Dict[str, Any]]:
    # Reuse load_input_file from predict.py
    from predict import load_input_file
    return load_input_file(file_path)

def load_submission(file_path: Path) -> List[Dict[str, Any]]:
    suffix = file_path.suffix.lower()
    preds = []
    if suffix == ".jsonl":
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    preds.append(json.loads(line))
    elif suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                preds = data
            elif isinstance(data, dict):
                preds = list(data.values())
    elif suffix in [".conll", ".conllu"]:
        with open(file_path, "r", encoding="utf-8") as f:
            curr_tokens = []
            curr_tags = []
            sent_idx = 0
            for line in f:
                line = line.strip()
                if not line:
                    if curr_tokens:
                        preds.append({
                            "row_id": f"conll_{sent_idx}",
                            "text": " ".join(curr_tokens),
                            "tokens": curr_tokens,
                            "bio_tags": curr_tags,
                            "entities": []
                        })
                        sent_idx += 1
                        curr_tokens, curr_tags = [], []
                    continue
                parts = line.split()
                if parts:
                    curr_tokens.append(parts[0])
                    curr_tags.append(parts[-1])
            if curr_tokens:
                preds.append({
                    "row_id": f"conll_{sent_idx}",
                    "text": " ".join(curr_tokens),
                    "tokens": curr_tokens,
                    "bio_tags": curr_tags,
                    "entities": []
                })
    elif suffix == ".csv":
        import csv
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ents = json.loads(row.get("entities_json", "[]")) if "entities_json" in row else []
                bio = row.get("bio_tags", "").split()
                preds.append({
                    "row_id": row.get("row_id"),
                    "text": row.get("text", ""),
                    "entities": ents,
                    "tokens": row.get("text", "").split(),
                    "bio_tags": bio
                })
    return preds

def validate_submission(input_file: Path, submission_file: Path) -> bool:
    print(f"\n================ VALIDATING SUBMISSION ================")
    print(f"Input File:      {input_file}")
    print(f"Submission File: {submission_file}")

    if not submission_file.exists():
        print(f"[FATAL ERROR] Submission file '{submission_file}' does not exist!")
        return False

    input_rows = load_rows_from_input(input_file)
    pred_rows = load_submission(submission_file)

    errors = []

    # Check 1: Non-empty output
    if not pred_rows:
        errors.append("Submission file is completely empty!")
        print(f"FAILED: {errors[0]}")
        return False

    # Check 2: Row count matches input
    if len(input_rows) != len(pred_rows):
        errors.append(f"Row count mismatch! Input has {len(input_rows)} rows, submission has {len(pred_rows)} rows.")

    # Check 3: Row IDs match in exact order
    id_mismatches = 0
    for idx, (inp, pred) in enumerate(zip(input_rows, pred_rows)):
        inp_id = str(inp["row_id"])
        pred_id = str(pred.get("row_id", ""))
        if inp_id != pred_id:
            id_mismatches += 1
            if id_mismatches <= 5:
                errors.append(f"Row {idx} ID mismatch: expected '{inp_id}', got '{pred_id}'")
    if id_mismatches > 5:
        errors.append(f"... and {id_mismatches - 5} additional row ID mismatches.")

    # Check 4: Label and span validation
    disallowed_labels = set()
    span_errors = 0
    bio_errors = 0

    for idx, pred in enumerate(pred_rows):
        text = pred.get("text", "")
        entities = pred.get("entities", [])
        tokens = pred.get("tokens", [])
        bio_tags = pred.get("bio_tags", [])

        # Entities check
        for e_idx, ent in enumerate(entities):
            lbl = ent.get("label", "")
            s = ent.get("start", -1)
            e = ent.get("end", -1)
            t = ent.get("text", "")

            if lbl not in ALLOWED_20_LABELS:
                disallowed_labels.add(lbl)
                if len(disallowed_labels) <= 5:
                    errors.append(f"Row {idx}, Entity {e_idx}: Disallowed entity label '{lbl}'")

            if s < 0 or e > len(text) or s >= e:
                span_errors += 1
                if span_errors <= 5:
                    errors.append(f"Row {idx}: Span [{s}:{e}] out of bounds for text length {len(text)}")
            elif text and text[s:e] != t:
                span_errors += 1
                if span_errors <= 5:
                    errors.append(f"Row {idx}: Span slice text mismatch: text[{s}:{e}]='{text[s:e]}' != ent['text']='{t}'")

        # BIO checks
        if bio_tags:
            if tokens and len(tokens) != len(bio_tags):
                bio_errors += 1
                if bio_errors <= 5:
                    errors.append(f"Row {idx}: Length mismatch tokens ({len(tokens)}) vs bio_tags ({len(bio_tags)})")

            prev = "O"
            for t_idx, tag in enumerate(bio_tags):
                if tag not in ALLOWED_BIO:
                    disallowed_labels.add(tag)
                    if len(disallowed_labels) <= 5:
                        errors.append(f"Row {idx}, Token {t_idx}: Disallowed BIO tag '{tag}'")
                if tag.startswith("I-"):
                    cls = tag[2:]
                    if prev == "O" or prev[2:] != cls:
                        bio_errors += 1
                        if bio_errors <= 5:
                            errors.append(f"Row {idx}, Token {t_idx}: Invalid BIO transition '{prev}' -> '{tag}'")
                prev = tag

    if disallowed_labels:
        errors.append(f"Disallowed labels found in predictions: {disallowed_labels}")
    if span_errors > 5:
        errors.append(f"... and {span_errors - 5} additional span errors.")
    if bio_errors > 5:
        errors.append(f"... and {bio_errors - 5} additional BIO transition errors.")

    # Results
    if errors:
        print(f"\n[STATUS: FAILED] {len(errors)} validation checks failed:")
        for err in errors[:20]:
            print(f"  ❌ {err}")
        return False
    else:
        total_ents = sum(len(p.get("entities", [])) for p in pred_rows)
        print(f"\n[STATUS: PASSED] All submission criteria strictly satisfied:")
        print(f"  ✔ Row Count: {len(pred_rows)} rows match input exactly")
        print(f"  ✔ Row Order & IDs: 100% matched")
        print(f"  ✔ Schema: 100% strictly within the 20 allowed labels")
        print(f"  ✔ BIO Transitions: 100% valid IOB2 sequences")
        print(f"  ✔ Character Spans: 100% within bounds and exact text slice matches")
        print(f"  ✔ Entities Extracted: {total_ents} total entity mentions")
        return True

def main():
    parser = argparse.ArgumentParser(description="Submission validator for NER challenge")
    parser.add_argument("input_file", help="Path to original input test file")
    parser.add_argument("submission_file", help="Path to predicted submission file")
    args = parser.parse_args()

    passed = validate_submission(Path(args.input_file), Path(args.submission_file))
    if not passed:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
