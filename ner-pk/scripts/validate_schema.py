"""
Schema validation script for TechFest NER Challenge.
Validates JSONL and CoNLL files strictly against the 20-label schema.
Fails loudly (sys.exit(1)) on any schema violation, unknown label, corrupted span, or BIO inconsistency.
"""

import sys
import json
import argparse
from pathlib import Path

ALLOWED_LABELS = {
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

ALLOWED_BIO = {"O"} | {f"B-{lbl}" for lbl in ALLOWED_LABELS} | {f"I-{lbl}" for lbl in ALLOWED_LABELS}
ALLOWED_TIERS = {"GOLD", "SILVER-HC", "SILVER", "SYNTHETIC", "gold", "silver", "synthetic"}

def validate_jsonl(file_path: Path):
    print(f"Validating JSONL: {file_path}...")
    errors = []
    line_count = 0
    total_entities = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line_count += 1
            line = line.strip()
            if not line:
                errors.append(f"Line {line_num}: Empty line in JSONL")
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                errors.append(f"Line {line_num}: JSON parse error: {e}")
                continue

            text = rec.get("text", "")
            entities = rec.get("entities", [])
            tokens = rec.get("tokens", [])
            bio_tags = rec.get("bio_tags", [])
            tier = rec.get("tier", "")

            # Tier check if present
            if tier and tier not in ALLOWED_TIERS:
                errors.append(f"Line {line_num}: Invalid tier '{tier}'")

            # Entity span checks
            for ent_idx, ent in enumerate(entities):
                total_entities += 1
                label = ent.get("label", "")
                start = ent.get("start", -1)
                end = ent.get("end", -1)
                ent_text = ent.get("text", "")

                if label not in ALLOWED_LABELS:
                    errors.append(f"Line {line_num}, Ent {ent_idx}: Disallowed label '{label}'")

                if start < 0:
                    errors.append(f"Line {line_num}, Ent {ent_idx}: Negative start index ({start}) for label '{label}'")

                if end <= start:
                    errors.append(f"Line {line_num}, Ent {ent_idx}: Invalid span end <= start ({start}, {end}) for '{label}'")

                if not ent_text or not str(ent_text).strip():
                    errors.append(f"Line {line_num}, Ent {ent_idx}: Empty entity text for label '{label}'")

                # Span match
                if 0 <= start < len(text) and 0 <= end <= len(text):
                    actual_slice = text[start:end]
                    if actual_slice != ent_text:
                        errors.append(f"Line {line_num}, Ent {ent_idx}: Span mismatch! text[{start}:{end}]='{actual_slice}' != ent['text']='{ent_text}'")
                elif start >= 0:
                    errors.append(f"Line {line_num}, Ent {ent_idx}: Span [{start}:{end}] out of bounds for text length {len(text)}")

            # Tokens and BIO checks
            if tokens or bio_tags:
                if len(tokens) != len(bio_tags):
                    errors.append(f"Line {line_num}: Length mismatch tokens ({len(tokens)}) vs bio_tags ({len(bio_tags)})")

                prev_tag = "O"
                for t_idx, tag in enumerate(bio_tags):
                    if tag not in ALLOWED_BIO:
                        errors.append(f"Line {line_num}, Token {t_idx}: Disallowed BIO tag '{tag}'")
                    if tag.startswith("I-"):
                        curr_class = tag[2:]
                        if prev_tag == "O" or prev_tag[2:] != curr_class:
                            errors.append(f"Line {line_num}, Token {t_idx}: Invalid BIO sequence: '{prev_tag}' -> '{tag}'")
                    prev_tag = tag

    if errors:
        print(f"FAILED: {len(errors)} validation errors found in {file_path}:")
        for err in errors[:25]:
            print(f"  [ERROR] {err}")
        if len(errors) > 25:
            print(f"  ... and {len(errors) - 25} more errors.")
        return False, len(errors), line_count, total_entities
    else:
        print(f"PASSED: {file_path} (Sentences: {line_count}, Entities: {total_entities})")
        return True, 0, line_count, total_entities

def validate_conll(file_path: Path):
    print(f"Validating CoNLL: {file_path}...")
    errors = []
    line_count = 0
    sent_count = 0
    token_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        prev_tag = "O"
        for line_num, line in enumerate(f, 1):
            line_count += 1
            line = line.strip()
            if not line:
                sent_count += 1
                prev_tag = "O"
                continue
            parts = line.split()
            if len(parts) < 2:
                errors.append(f"Line {line_num}: Malformed CoNLL line '{line}'")
                continue
            token, tag = parts[0], parts[-1]
            token_count += 1
            if tag not in ALLOWED_BIO:
                errors.append(f"Line {line_num}: Disallowed BIO tag '{tag}'")
            if tag.startswith("I-"):
                curr_class = tag[2:]
                if prev_tag == "O" or prev_tag[2:] != curr_class:
                    errors.append(f"Line {line_num}: Invalid BIO transition '{prev_tag}' -> '{tag}'")
            prev_tag = tag

    if errors:
        print(f"FAILED: {len(errors)} validation errors found in {file_path}:")
        for err in errors[:25]:
            print(f"  [ERROR] {err}")
        return False, len(errors), sent_count, token_count
    else:
        print(f"PASSED: {file_path} (Sentences: {sent_count}, Tokens: {token_count})")
        return True, 0, sent_count, token_count

def main():
    parser = argparse.ArgumentParser(description="Strict schema validator for 20-class NER")
    parser.add_argument("paths", nargs="+", help="Files or directories to validate")
    args = parser.parse_args()

    all_passed = True
    for p_str in args.paths:
        p = Path(p_str)
        if p.is_dir():
            files = list(p.glob("*.jsonl")) + list(p.glob("*.conll"))
        else:
            files = [p]

        for f in files:
            if f.suffix == ".jsonl":
                passed, err_cnt, _, _ = validate_jsonl(f)
                if not passed:
                    all_passed = False
            elif f.suffix == ".conll":
                passed, err_cnt, _, _ = validate_conll(f)
                if not passed:
                    all_passed = False

    if not all_passed:
        print("\nSCHEMA VALIDATION FAILED!")
        sys.exit(1)
    else:
        print("\nALL FILES PASSED STRICT SCHEMA VALIDATION.")
        sys.exit(0)

if __name__ == "__main__":
    main()
