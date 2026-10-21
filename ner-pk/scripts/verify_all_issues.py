import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor

def audit_all_issues():
    print("=" * 80)
    print("FINAL RIGOROUS SYSTEM AUDIT: VERIFYING ALL REPORTED EDGE CASES")
    print("Predictor Mode: HYBRID (Active v4 XLM-RoBERTa + Hardened Postprocessing)")
    print("=" * 80)

    predictor = UnifiedNERPredictor(model_dir="models/final", mode="hybrid")

    test_checks = [
        {
            "category": "1. Verb vs Acronym (nab vs NAB)",
            "text": "NAB officials arrived to nab corrupt individuals in Islamabad.",
            "must_contain": [("NAB", "GOVERNMENT_BODY"), ("Islamabad", "CITY")],
            "must_not_contain": [("nab", "GOVERNMENT_BODY"), ("nab", "ORGANIZATION")]
        },
        {
            "category": "2. Subword Fragment & Lowercase Media (n dawn vs Dawn)",
            "text": "At dawn, while reading Dawn in Karachi, reporters gathered at 06:00 AM.",
            "must_contain": [("Dawn", "MEDIA_OUTLET"), ("Karachi", "CITY"), ("06:00 AM", "TIME")],
            "must_not_contain": [("dawn", "MEDIA_OUTLET"), ("n", "MEDIA_OUTLET"), ("daw", "MEDIA_OUTLET")]
        },
        {
            "category": "3. The Full User Sentence (dawn, jazz, Anchor, Kamran Khan, Gaddafi Stadium)",
            "text": "At dawn, while listening to smooth jazz, Anchor Kamran Khan from Geo News met Jazz executives at Gaddafi Stadium.",
            "must_contain": [
                ("Kamran Khan", "PERSON"),
                ("Geo News", "MEDIA_OUTLET"),
                ("Jazz", "ORGANIZATION"),
                ("Gaddafi Stadium", "LANDMARK_FACILITY")
            ],
            "must_not_contain": [
                ("n", "MEDIA_OUTLET"),
                ("daw", "MEDIA_OUTLET"),
                ("dawn", "MEDIA_OUTLET"),
                ("smooth jazz", "ORGANIZATION"),
                ("jazz", "ORGANIZATION"),
                ("Anchor", "PERSON"),
                ("Anchor Kamran Khan", "PERSON")
            ]
        },
        {
            "category": "4. Stacked Complex Titles with (Retd.)",
            "text": "Chief Justice (Retd.) Mian Saqib Nisar and Lt. Gen. (Retd.) Asim Saleem Bajwa met in Rawalpindi.",
            "must_contain": [
                ("Mian Saqib Nisar", "PERSON"),
                ("Asim Saleem Bajwa", "PERSON"),
                ("Rawalpindi", "CITY")
            ],
            "must_not_contain": [
                ("Chief Justice", "PERSON"),
                ("Chief Justice (Retd.) Mian Saqib Nisar", "PERSON"),
                ("Lt. Gen.", "PERSON"),
                ("Lt. Gen. (Retd.) Asim Saleem Bajwa", "PERSON")
            ]
        },
        {
            "category": "5. Hyphenated Names & Academic Prefixes",
            "text": "Prof. Dr. Atta-ur-Rahman addressed a seminar at Karachi University.",
            "must_contain": [
                ("Atta-ur-Rahman", "PERSON"),
                ("Karachi University", "EDUCATIONAL_INSTITUTION")
            ],
            "must_not_contain": [
                ("Prof. Dr.", "PERSON"),
                ("Prof. Dr. Atta-ur-Rahman", "PERSON")
            ]
        },
        {
            "category": "6. Roman Urdu Prefix & Suffix (Mohtarma... Sahiba, Sahibzada)",
            "text": "Mohtarma Maryam Nawaz Sahiba aur Sahibzada Hamid Raza ne Lahore mein press conference ki.",
            "must_contain": [
                ("Maryam Nawaz", "PERSON"),
                ("Hamid Raza", "PERSON"),
                ("Lahore", "CITY")
            ],
            "must_not_contain": [
                ("Mohtarma Maryam Nawaz Sahiba", "PERSON"),
                ("Sahibzada Hamid Raza", "PERSON"),
                ("Sahiba", "PERSON")
            ]
        },
        {
            "category": "7. Urdu Titles (جسٹس (ر) ... صاحب, ملزم)",
            "text": "جسٹس (ر) قاضی فائز عیسیٰ صاحب اور ملزم فواد چوہدری عدالت میں پیش ہوئے۔",
            "must_contain": [
                ("قاضی فائز عیسیٰ", "PERSON"),
                ("فواد چوہدری", "PERSON")
            ],
            "must_not_contain": [
                ("جسٹس", "PERSON"),
                ("صاحب", "PERSON"),
                ("حب", "CITY"), # Ensure Hab city does not match inside Sahib!
                ("ملزم", "PERSON")
            ]
        },
        {
            "category": "8. Ratio 50:50 vs Valid Time (11:45 PM, رات ۱۱:۳۰ بجے)",
            "text": "The 50:50 ratio was finalized at 11:45 PM and رات ۱۱:۳۰ بجے in Lahore.",
            "must_contain": [
                ("11:45 PM", "TIME"),
                ("رات ۱۱:۳۰ بجے", "TIME"),
                ("Lahore", "CITY")
            ],
            "must_not_contain": [
                ("50:50", "TIME"),
                ("رات", "MEDIA_OUTLET")
            ]
        },
        {
            "category": "9. 14-Digit CNIC & 13-Digit Phone Distractors",
            "text": "Ticket #42101-0000000-88 and account 0300-123456789 are fake, but CNIC 42101-0000000-7 and cell 0300-1234567 are real.",
            "must_contain": [
                ("42101-0000000-7", "ID_NUMBER"),
                ("0300-1234567", "PHONE_NUMBER")
            ],
            "must_not_contain": [
                ("42101-0000000-88", "ID_NUMBER"),
                ("0300-123456789", "PHONE_NUMBER")
            ]
        },
        {
            "category": "10. Statutory Sections vs Case Numbers",
            "text": "FIR 302/2025 was registered under Section 302 of the Pakistan Penal Code in Peshawar.",
            "must_contain": [
                ("Section 302", "LAW_ACT"),
                ("Pakistan Penal Code", "LAW_ACT"),
                ("Peshawar", "CITY")
            ],
            "must_not_contain": [
                ("302/2025", "LAW_ACT"),
                ("FIR 302", "LAW_ACT")
            ]
        }
    ]

    all_passed = True

    for i, chk in enumerate(test_checks, 1):
        print(f"\n[{i}/{len(test_checks)}] Testing: {chk['category']}")
        print(f"  Input: {chk['text']}")

        preds = predictor.predict_single(chk["text"])
        pred_tuples = [(p["text"], p["label"]) for p in preds]

        passed = True
        failures = []

        # Check must_contain
        for req in chk["must_contain"]:
            if req not in pred_tuples:
                passed = False
                failures.append(f"MISSING: {req}")

        # Check must_not_contain
        for forbidden in chk["must_not_contain"]:
            if forbidden in pred_tuples:
                passed = False
                failures.append(f"UNWANTED FALSE POSITIVE: {forbidden}")

        if passed:
            print(f"  ✔ RESULT: PASSED")
            print(f"  Extracted Entities: {pred_tuples}")
        else:
            print(f"  ❌ RESULT: FAILED")
            for f in failures:
                print(f"     ! {f}")
            print(f"  Extracted Entities: {pred_tuples}")
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("OVERALL AUDIT: 100% PERFECT! ALL 10 TARGET CHECKS PASSED WITH ZERO FLAWS!")
    else:
        print("OVERALL AUDIT: FAILURES DETECTED!")
    print("=" * 80)

if __name__ == "__main__":
    audit_all_issues()
