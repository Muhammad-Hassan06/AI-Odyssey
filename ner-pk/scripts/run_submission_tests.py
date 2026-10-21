import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import tests.test_submission_pipeline as tsp

def run_all():
    print("Running Submission Pipeline Verification Suite...")
    predictor = tsp.predictor()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        print("1. Testing empty and whitespace preservation...")
        tsp.test_empty_and_whitespace_preservation(tmp_path, predictor)
        print("   -> PASS")

        print("2. Testing long text sliding window (>1,000 chars)...")
        tsp.test_long_text_sliding_window(predictor)
        print("   -> PASS")

        print("3. Testing Urdu RTL & Unicode encoding...")
        tsp.test_urdu_rtl_and_unicode_handling(predictor)
        print("   -> PASS")

        print("4. Testing multi-format loading (.txt, .csv, .jsonl, .json, .conll)...")
        tsp.test_multi_format_loading(tmp_path)
        print("   -> PASS")

        print("5. Testing 20-sentence smoke test & submission validator...")
        tsp.test_20_sentence_smoke_test(tmp_path)
        print("   -> PASS")

        print("6. Testing CoNLL round trip...")
        tsp.test_conll_round_trip(tmp_path)
        print("   -> PASS")

    print("=" * 60)
    print("ALL SUBMISSION PIPELINE TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    run_all()
