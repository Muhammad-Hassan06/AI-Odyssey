import os
import sys
import json
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor

def run_tests():
    predictor = UnifiedNERPredictor(model_dir="models/final", mode="hybrid")
    cases_file = PROJECT_ROOT / "tests" / "parsed_boss_cases.json"
    with open(cases_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("=" * 70)
    print("RUNNING 15 BOSS-LEVEL ADVERSARIAL TEST CASES")
    print("=" * 70)

    total_cases = len(cases)
    passed_cases = 0

    for idx, c in enumerate(cases, 1):
        title = c["title"]
        text = c["text"]
        expected_str = c["expected_str"]

        # Parse expected entities: format is "Entity Text (LABEL)" separated by "|"
        expected_items = []
        for part in expected_str.split("|"):
            part = part.strip()
            if not part:
                continue
            # extract text and label: e.g. Mian Saqib Nisar (PERSON) or فواد چوہدری (PERSON — "ملزم" stripped)
            import re
            m = re.match(r"^(.*?)\s*\(([A-Z_]+)(?:[^)]*)?\)$", part)
            if m:
                expected_items.append((m.group(1).strip(), m.group(2).strip()))
            else:
                expected_items.append((part, "UNKNOWN"))

        preds = predictor.predict_single(text)
        pred_items = [(p["text"].strip(), p["label"]) for p in preds]

        # Check match
        # Let's see differences
        exp_set = set(expected_items)
        pred_set = set(pred_items)

        matched = (exp_set == pred_set)
        if matched:
            passed_cases += 1
            print(f"[{idx}/15] PASS: {title[:60]}")
        else:
            print(f"[{idx}/15] FAIL: {title[:60]}")
            print(f"   Text: {text}")
            print(f"   Missing / Unmatched in Pred: {exp_set - pred_set}")
            print(f"   Unexpected / Extra in Pred: {pred_set - exp_set}")
            print(f"   Full Expected: {expected_items}")
            print(f"   Full Predicted: {pred_items}")
            print("-" * 70)

    print("=" * 70)
    print(f"TOTAL RESULT: {passed_cases} / {total_cases} PASSED")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
