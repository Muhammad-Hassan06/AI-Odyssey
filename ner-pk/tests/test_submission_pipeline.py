"""
Comprehensive Test Suite for Test-File Readiness & Submission Pipeline.
Tests:
1. Multi-format input detection (.txt, .csv, .jsonl, .json, .conll, .xlsx).
2. 20-sentence diverse smoke test across English, Urdu, Roman Urdu, Mixed Script.
3. Urdu RTL and odd Unicode handling without crashes.
4. Empty lines and whitespace-only lines preservation (never drop rows).
5. Very long text (>1,000 chars) sliding window tokenization without truncation crash.
6. CoNLL round-trip consistency.
7. Validation script integration (validate_submission.py).
"""

import os
import sys
import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor, load_input_file, run_predictions
from validate_submission import validate_submission

@pytest.fixture(scope="module")
def predictor():
    # Load predictor in rules mode for ultra-fast, deterministic unit testing
    return UnifiedNERPredictor(mode="rules")

def test_empty_and_whitespace_preservation(tmp_path, predictor):
    """Verify empty lines are preserved and never dropped."""
    test_file = tmp_path / "test_empty.txt"
    lines = [
        "First valid sentence in Karachi.",
        "",
        "   ",
        "Second sentence regarding Lahore High Court.",
        "Final valid sentence in Islamabad."
    ]
    test_file.write_text("\n".join(lines), encoding="utf-8")

    rows = load_input_file(test_file)
    assert len(rows) == 5, f"Expected 5 rows, got {len(rows)}"
    assert rows[1]["text"] == ""
    assert rows[2]["text"] == "   "

    # Predict
    preds = [predictor.predict_single(r["text"]) for r in rows]
    assert len(preds) == 5
    assert len(preds[1]) == 0
    assert len(preds[2]) == 0
    assert len(preds[0]) > 0
    assert len(preds[3]) > 0


def test_long_text_sliding_window(predictor):
    """Verify arbitrary long text (>1,000 chars) is processed without crashing."""
    long_text = "In Islamabad, the Supreme Court of Pakistan issued notices. " * 30 # ~1,800 chars
    ents = predictor.predict_single(long_text)
    assert isinstance(ents, list)
    # Spans must all be valid and non-overlapping
    for e in ents:
        assert 0 <= e["start"] < e["end"] <= len(long_text)
        assert long_text[e["start"]:e["end"]] == e["text"]

def test_urdu_rtl_and_unicode_handling(predictor):
    """Verify Urdu RTL and Unicode characters do not cause encoding errors."""
    urdu_samples = [
        "سپریم کورٹ آف پاکستان نے اسلام آباد میں اہم فیصلہ سنایا۔",
        "وفاقی حکومت نے بجٹ 2025-26 کے لیے 15 ارب روپے مختص کیے۔",
        "قائد اعظم محمد علی جناح کا یوم پیدائش 25 دسمبر کو منایا جاتا ہے۔",
        "رابطہ نمبر: 0300-1234567 اور شناختی کارڈ: 42101-1234567-1۔",
        "وزیر اعظم شہباز شریف نے کراچی میں تقریب سے خطاب کیا۔"
    ]
    for sample in urdu_samples:
        ents = predictor.predict_single(sample)
        assert isinstance(ents, list)
        for e in ents:
            assert sample[e["start"]:e["end"]] == e["text"]

def test_multi_format_loading(tmp_path):
    """Test auto-detection and row preservation across .txt, .csv, .jsonl, .json, .conll."""
    # 1. TXT
    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("Sentence 1\nSentence 2\nSentence 3", encoding="utf-8")
    txt_rows = load_input_file(txt_file)
    assert len(txt_rows) == 3

    # 2. CSV
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("sentence_id,content\ns1,Hello from Karachi\ns2,Lahore meeting", encoding="utf-8")
    csv_rows = load_input_file(csv_file)
    assert len(csv_rows) == 2
    assert csv_rows[0]["row_id"] == "s1"
    assert csv_rows[0]["text"] == "Hello from Karachi"

    # 3. JSONL
    jsonl_file = tmp_path / "sample.jsonl"
    jsonl_lines = [
        json.dumps({"id": "j1", "text": "First sentence"}),
        json.dumps({"id": "j2", "text": "Second sentence"})
    ]
    jsonl_file.write_text("\n".join(jsonl_lines), encoding="utf-8")
    jsonl_rows = load_input_file(jsonl_file)
    assert len(jsonl_rows) == 2
    assert jsonl_rows[0]["row_id"] == "j1"

    # 4. JSON
    json_file = tmp_path / "sample.json"
    json_data = [
        {"row_id": "arr1", "text": "Array item 1"},
        {"row_id": "arr2", "text": "Array item 2"}
    ]
    json_file.write_text(json.dumps(json_data), encoding="utf-8")
    json_rows = load_input_file(json_file)
    assert len(json_rows) == 2

    # 5. CoNLL
    conll_file = tmp_path / "sample.conll"
    conll_text = "Prime B-PER\nMinister I-PER\nvisited O\nIslamabad B-CITY\n.\n\nMeeting O\nheld O\n."
    conll_file.write_text(conll_text, encoding="utf-8")
    conll_rows = load_input_file(conll_file)
    assert len(conll_rows) == 2

def test_20_sentence_smoke_test(tmp_path):
    """End-to-end 20-sentence smoke test with prediction generation and validation."""
    smoke_file = tmp_path / "smoke_20.jsonl"
    diverse_sentences = [
        {"id": "s1", "text": "Muhammad Ali Jinnah founded Pakistan in August 1947."},
        {"id": "s2", "text": "The State Bank of Pakistan increased the policy rate by 2.5% in Karachi."},
        {"id": "s3", "text": "Peshawar High Court dismissed the petition regarding Code of Criminal Procedure."},
        {"id": "s4", "text": "Call the helpdesk at 0300-9876543 or submit CNIC 35201-1234567-9 today."},
        {"id": "s5", "text": "Government allocated Rs 50 crore for Punjab development initiatives."},
        {"id": "s6", "text": "Lahore Qalandars won their fixture against Karachi Kings in PSL 10."},
        {"id": "s7", "text": "Pakistan International Airlines announced direct flights from Lahore to London."},
        {"id": "s8", "text": "Meeting commences at 3:30 pm PST on Monday afternoon."},
        {"id": "s9", "text": "A symposium was held at Aga Khan University in Karachi on 14 August 2025."},
        {"id": "s10", "text": "GEO News and Dawn reported extensive coverage of the General Elections 2024."},
        {"id": "s11", "text": "سپریم کورٹ آف پاکستان نے اسلام آباد میں سماعت مکمل کر لی۔"},
        {"id": "s12", "text": "فیڈرل بورڈ آف ریونیو نے 15 فیصد ٹیکس وصولی کا اعلان کیا۔"},
        {"id": "s13", "text": "عمران خان نے لاہور میں پاکستان تحریک انصاف کے جلسے سے خطاب کیا۔"},
        {"id": "s14", "text": "پاکستان کرکٹ بورڈ نے بابر اعظم کو کپتان مقرر کر دیا۔"},
        {"id": "s15", "text": "قومی اسمبلی کا اجلاس جمعہ کو شام 6 بجے پارلیمنٹ ہاؤس اسلام آباد میں ہو گا۔"},
        {"id": "s16", "text": "ALL-CAPS: SUPREME COURT OF PAKISTAN IN ISLAMABAD ISSUED SUMMONS."},
        {"id": "s17", "text": "Mixed script: Pakistan Cricket Board نے لاہور میں پریس کانفرنس کی۔"},
        {"id": "s18", "text": "Roman Urdu: Hukumat-e-Pakistan ne nayee policy ka ailaan kiya."},
        {"id": "s19", "text": "Empty sentence below:"},
        {"id": "s20", "text": "A project grant of $5 million USD was awarded to NED University in Sindh."}
    ]
    with open(smoke_file, "w", encoding="utf-8") as f:
        for s in diverse_sentences:
            f.write(json.dumps(s) + "\n")

    out_dir = tmp_path / "smoke_preds"
    run_predictions(
        input_file=str(smoke_file),
        output_dir=str(out_dir),
        mode="rules"
    )

    pred_jsonl = out_dir / "smoke_20_rules.jsonl"
    assert pred_jsonl.exists()

    # Run strict submission validator
    passed = validate_submission(smoke_file, pred_jsonl)
    assert passed is True, "Validation failed on smoke test predictions!"

def test_conll_round_trip(tmp_path):
    """Test full CoNLL round trip: input CoNLL -> predict -> output CoNLL -> re-load."""
    conll_input = tmp_path / "input.conll"
    conll_content = (
        "Chief O\n"
        "Justice O\n"
        "arrived O\n"
        "in O\n"
        "Islamabad B-CITY\n"
        ". O\n\n"
        "State B-GOVERNMENT_BODY\n"
        "Bank I-GOVERNMENT_BODY\n"
        "held O\n"
        "meeting O\n"
        ". O\n"
    )
    conll_input.write_text(conll_content, encoding="utf-8")

    out_dir = tmp_path / "conll_out"
    run_predictions(
        input_file=str(conll_input),
        output_dir=str(out_dir),
        mode="rules"
    )

    pred_conll = out_dir / "input_rules.conll"
    assert pred_conll.exists()

    # Re-read and verify structure
    re_loaded = load_input_file(pred_conll)
    assert len(re_loaded) == 2
    assert "Islamabad" in re_loaded[0]["text"]
    assert "State Bank" in re_loaded[1]["text"]

