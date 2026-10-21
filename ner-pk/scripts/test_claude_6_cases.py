import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor

def test_claude_cases():
    print("=" * 80)
    print("TESTING CLAUDE'S 6 ADVERSARIAL BENCHMARK CASES")
    print("=" * 80)

    predictor = UnifiedNERPredictor(model_dir="models/final", mode="hybrid")

    cases = [
        {
            "id": "H1",
            "name": "Legal & Distractors",
            "text": "Chief Justice Yahya Afridi ne Islamabad High Court mein PECA 2016 ke tahat NADRA ko CNIC 35201-7770123-9 par ۲۸ فروری ۲۰۲۵ تک jawab dene ka hukam diya, jabke Invoice 03217766 aur Zip 44000 ka is se koi talluq nahi.",
            "expected": [
                ("Yahya Afridi", "PERSON"),
                ("Islamabad High Court", "COURT_LEGAL_BODY"),
                ("PECA 2016", "LAW_ACT"),
                ("NADRA", "GOVERNMENT_BODY"),
                ("35201-7770123-9", "ID_NUMBER"),
                ("۲۸ فروری ۲۰۲۵", "DATE")
            ]
        },
        {
            "id": "H2",
            "name": "Urdu State Bank of Pakistan Integrity",
            "text": "وزیراعظم شہباز شریف نے اسلام آباد میں پاکستان مسلم لیگ ن کے اجلاس کے بعد ۱۲ ارب روپے کے بجٹ اور ۸.۵ فیصد افراط زر پر سٹیٹ بینک آف پاکستان کو رات ۱۰:۳۰ بجے طلب کیا۔",
            "expected": [
                ("شہباز شریف", "PERSON"),
                ("اسلام آباد", "CITY"),
                ("پاکستان مسلم لیگ ن", "POLITICAL_PARTY"),
                ("۱۲ ارب روپے", "MONEY"),
                ("۸.۵ فیصد", "PERCENT"),
                ("سٹیٹ بینک آف پاکستان", "GOVERNMENT_BODY"),
                ("رات ۱۰:۳۰ بجے", "TIME")
            ]
        },
        {
            "id": "H3",
            "name": "Bank Names & Sports/Gov/Edu Entities",
            "text": "Karachi Kings ke owner ne Karachi University, Sindh Bank aur Bank Alfalah Limited ke saath Sindh Police ki Lahore office mein Pakistan Super League ka meeting kiya.",
            "expected": [
                ("Karachi Kings", "SPORTS_TEAM"),
                ("Karachi University", "EDUCATIONAL_INSTITUTION"),
                ("Sindh Bank", "ORGANIZATION"),
                ("Bank Alfalah Limited", "ORGANIZATION"),
                ("Sindh Police", "GOVERNMENT_BODY"),
                ("Lahore", "CITY"),
                ("Pakistan Super League", "EVENT")
            ]
        },
        {
            "id": "H4",
            "name": "Sentence-Start Personal Names & Phone Distractors",
            "text": "Muhammad Bilal ka number +92 300 5551234 hai, landline 021-5551200, aur ۰۳۱۰-۵۵۵۱۲۳۴ bhi use karta hai, lekin Tracking 0300555 aur Ref 35201777 phone ya CNIC nahi hain.",
            "expected": [
                ("Muhammad Bilal", "PERSON"),
                ("+92 300 5551234", "PHONE_NUMBER"),
                ("021-5551200", "PHONE_NUMBER"),
                ("۰۳۱۰-۵۵۵۱۲۳۴", "PHONE_NUMBER")
            ]
        },
        {
            "id": "H5",
            "name": "PKR Numeric Currency Integrity",
            "text": "Federal Budget 2025-26 mein FBR ne Rs 14.1 trillion ka target rakha, PKR 450,000 ki tankhwah par 12.5 per cent tax, aur 50 ارب ڈالر ka qarza 1 July 2025 se ۳۰ جون ۲۰۲۶ tak chukana hai.",
            "expected": [
                ("Federal Budget 2025-26", "EVENT"),
                ("FBR", "GOVERNMENT_BODY"),
                ("Rs 14.1 trillion", "MONEY"),
                ("PKR 450,000", "MONEY"),
                ("12.5 per cent", "PERCENT"),
                ("50 ارب ڈالر", "MONEY"),
                ("1 July 2025", "DATE"),
                ("۳۰ جون ۲۰۲۶", "DATE")
            ]
        },
        {
            "id": "H6",
            "name": "Urdu Script Cricketer Names in Code-Mixed Text",
            "text": "Peshawar Zalmi vs Quetta Gladiators ka PSL 10 match National Stadium Karachi mein ۷:۳۰ PM par hoga, Babar Azam aur شاہین آفریدی ke saath, jise Geo News, ARY News aur Express News live dikhayenge.",
            "expected": [
                ("Peshawar Zalmi", "SPORTS_TEAM"),
                ("Quetta Gladiators", "SPORTS_TEAM"),
                ("PSL 10", "EVENT"),
                ("National Stadium Karachi", "LANDMARK_FACILITY"),
                ("۷:۳۰ PM", "TIME"),
                ("Babar Azam", "PERSON"),
                ("شاہین آفریدی", "PERSON"),
                ("Geo News", "MEDIA_OUTLET"),
                ("ARY News", "MEDIA_OUTLET"),
                ("Express News", "MEDIA_OUTLET")
            ]
        }
    ]

    total = len(cases)
    passed_count = 0

    for i, c in enumerate(cases, 1):
        print(f"\n[{i}/{total}] Testing Case {c['id']}: {c['name']}")
        preds = predictor.predict_single(c["text"])
        pred_tuples = [(p["text"], p["label"]) for p in preds]

        exp_set = set(c["expected"])
        pred_set = set(pred_tuples)

        if exp_set == pred_set:
            passed_count += 1
            print(f"  ✔ PASS! All {len(exp_set)} entities matched exactly.")
            print(f"    Predictions: {pred_tuples}")
        else:
            print(f"  ❌ FAIL!")
            print(f"    Missing: {exp_set - pred_set}")
            print(f"    Extra / Unexpected: {pred_set - exp_set}")
            print(f"    Actual Predictions: {pred_tuples}")

    print("\n" + "=" * 80)
    print(f"CLAUDE TEST SUITE RESULT: {passed_count} / {total} PASSED")
    print("=" * 80)

if __name__ == "__main__":
    test_claude_cases()
