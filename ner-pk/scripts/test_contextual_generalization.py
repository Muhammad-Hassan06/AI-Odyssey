import sys
from pathlib import Path

NER_PK_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NER_PK_DIR))

from predict import UnifiedNERPredictor

predictor = UnifiedNERPredictor()

test_cases = [
    {
        "desc": "Contextual Metonymy: Pakistan as SPORTS_TEAM in match",
        "text": "Pakistan defeated New Zealand by 5 wickets at Gaddafi Stadium on Sunday.",
        "expected": [("Pakistan", "SPORTS_TEAM"), ("New Zealand", "SPORTS_TEAM"), ("Gaddafi Stadium", "LANDMARK_FACILITY"), ("Sunday", "DATE")]
    },
    {
        "desc": "Contextual Metonymy: Pakistan as COUNTRY in diplomatic talks",
        "text": "A diplomatic delegation from Pakistan attended the regional economic summit in China.",
        "expected": [("Pakistan", "COUNTRY"), ("China", "COUNTRY")]
    },
    {
        "desc": "Unseen Name: Legal petition filed by completely unseen person",
        "text": "The constitutional petition was filed by Bakhtawar Lund in the Supreme Court of Pakistan.",
        "expected": [("Bakhtawar Lund", "PERSON"), ("Supreme Court of Pakistan", "COURT_LEGAL_BODY")]
    },
    {
        "desc": "Unseen Names: Accused and parentage in criminal proceedings",
        "text": "The accused, Zeeshan Khawaja, son of Farrukh Khawaja, was granted bail by the Lahore High Court.",
        "expected": [("Zeeshan Khawaja", "PERSON"), ("Farrukh Khawaja", "PERSON"), ("Lahore High Court", "COURT_LEGAL_BODY")]
    },
    {
        "desc": "Unseen Name: Communication / interview invitation",
        "text": "Dear Zubair Mengal, your interview is scheduled for Monday at 10:00 AM.",
        "expected": [("Zubair Mengal", "PERSON"), ("Monday", "DATE"), ("10:00 AM", "TIME")]
    }
]

print("=" * 80)
print("TESTING CONTEXTUAL SYNTACTIC GENERALIZATION (UNSEEN NAMES & METONYMY)")
print("=" * 80)

all_passed = True
for idx, tc in enumerate(test_cases, 1):
    print(f"\n[{idx}/{len(test_cases)}] {tc['desc']}")
    print(f"  Input: \"{tc['text']}\"")
    preds = predictor.predict_single(tc["text"])
    pred_tuples = [(p["text"], p["label"]) for p in preds]
    print(f"  Extracted: {pred_tuples}")

    for exp_text, exp_label in tc["expected"]:
        found = any(p[0] == exp_text and p[1] == exp_label for p in pred_tuples)
        if not found:
            print(f"  ❌ FAILED: Expected ({exp_text!r}, {exp_label!r}) not found in predictions!")
            all_passed = False
        else:
            print(f"  ✔ Correct: ({exp_text}, {exp_label})")

print("\n" + "=" * 80)
if all_passed:
    print("SUCCESS: ALL UNSEEN CONTEXTUAL TEST CASES PASSED!")
else:
    print("WARNING: SOME CONTEXTUAL CASES FAILED!")
print("=" * 80)
