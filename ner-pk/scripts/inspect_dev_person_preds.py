import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from predict import UnifiedNERPredictor

predictor = UnifiedNERPredictor(model_dir="models/final", mode="model")

with open("v4/dev_real.jsonl", "r", encoding="utf-8") as f:
    dev_data = [json.loads(line) for line in f]

print("Scanning Dev Set for Model PERSON predictions:")
count = 0
for i, d in enumerate(dev_data):
    preds = predictor.predict_single(d["text"])
    model_persons = [p for p in preds if p["label"] == "PERSON"]
    gold_persons = [e for e in d.get("entities", []) if e["label"] == "PERSON"]
    if model_persons:
        count += len(model_persons)
        print(f"\n--- Sent {i} ---")
        print("Text:", d["text"])
        print("Gold Persons:", [g["text"] for g in gold_persons])
        print("Model Persons:", [m["text"] for m in model_persons])
        if count >= 10:
            break
