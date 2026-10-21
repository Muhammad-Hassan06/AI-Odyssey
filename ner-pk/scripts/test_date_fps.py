import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rules import extract_regex_entities


sys.stdout.reconfigure(encoding="utf-8")

with open("v3/dev.jsonl", "r", encoding="utf-8") as f:
    dev = [json.loads(l) for l in f]

fps = []
for idx, r in enumerate(dev):
    text = r["text"]
    gold_dates = [e for e in r["entities"] if e["label"] == "DATE"]
    preds = [e for e in extract_regex_entities(text) if e["label"] == "DATE"]
    for p in preds:
        matched = False
        for g in gold_dates:
            if p["start"] == g["start"] and p["end"] == g["end"]:
                matched = True
                break
        if not matched:
            fps.append((idx, p["text"], text))

print(f"Total current DATE regex false positives on DEV: {len(fps)}")
print(f"\nShowing up to 50 Before False Positives:")
for i, (idx, p_text, full_text) in enumerate(fps[:50]):
    print(f"  {i+1:2d}. Dev #{idx}: '{p_text}' in: {full_text}")
