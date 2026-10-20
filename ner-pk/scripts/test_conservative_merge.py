import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.infer import PakistaniNERPredictor
from src.dataset import spans_to_bio
from seqeval.metrics import classification_report
from seqeval.scheme import IOB2

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dev_path = os.path.join(base_dir, "v2", "dev.jsonl")

with open(dev_path, "r", encoding="utf-8") as f:
    dev = [json.loads(l) for l in f]

# Test on first 200 dev sentences for fast verification
dev_sample = dev[:200]
print(f"Testing on {len(dev_sample)} Dev sentences...")

p_hybrid = PakistaniNERPredictor(os.path.join(base_dir, "models", "smoke_test_model"), mode="hybrid")
p_rules = PakistaniNERPredictor(mode="rules")

golds = [x["bio_tags"] for x in dev_sample]
preds_hybrid = []
preds_rules = []

for x in dev_sample:
    preds_hybrid.append(spans_to_bio(x["text"], p_hybrid.predict(x["text"]))[1])
    preds_rules.append(spans_to_bio(x["text"], p_rules.predict(x["text"]))[1])

rep_hybrid = classification_report(golds, preds_hybrid, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)
rep_rules = classification_report(golds, preds_rules, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)

h_micro = rep_hybrid["micro avg"]["f1-score"] * 100
h_macro = rep_hybrid["macro avg"]["f1-score"] * 100
r_micro = rep_rules["micro avg"]["f1-score"] * 100
r_macro = rep_rules["macro avg"]["f1-score"] * 100

print(f"Rules-Only Micro F1: {r_micro:.2f}% | Macro F1: {r_macro:.2f}%")
print(f"Conservative Hybrid (with smoke-test): Micro F1: {h_micro:.2f}% | Macro F1: {h_macro:.2f}%")

if h_micro > 50:
    print("SUCCESS: Hybrid merge no longer collapses when model is poor! Rules and gazetteers are protected.")
else:
    print("FAILURE: Hybrid merge still collapsing.")
