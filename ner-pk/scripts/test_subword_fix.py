"""
Test subword merging repair in inference on v4/dev_real.jsonl.
Evaluates model-only under:
1. Baseline (original logic)
2. Fixed Subword Continuation (re-joining intra-word B- tags where start_char == curr_ent['end'])
Prints: Precision, Recall, Micro-F1, Macro-F1, and boundary fragmentation counts.
"""

import os
import sys
import json
import torch
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from transformers import AutoTokenizer, AutoModelForTokenClassification
from seqeval.metrics import classification_report
from seqeval.scheme import IOB2
from src.constants import ID2LABEL, ENTITY_TYPES
from src.dataset import spans_to_bio

sys.stdout.reconfigure(encoding="utf-8")

tokenizer = AutoTokenizer.from_pretrained("models/final")
model = AutoModelForTokenClassification.from_pretrained("models/final")
model.eval()

dev = [json.loads(l) for l in open("v4/dev_real.jsonl", encoding="utf-8")]
texts = [r["text"] for r in dev]
gold_bios = [r["bio_tags"] for r in dev]

def predict_batch(texts, fix_subwords=False, batch_size=32):
    all_spans = []
    total = len(texts)
    for i in range(0, total, batch_size):
        b_texts = texts[i:i+batch_size]
        encoding = tokenizer(
            b_texts,
            padding=True,
            truncation=True,
            max_length=256,
            return_offsets_mapping=True,
            return_tensors="pt"
        )
        offsets = encoding["offset_mapping"].cpu().numpy()
        input_ids = encoding["input_ids"]
        attention_mask = encoding["attention_mask"]

        with torch.no_grad():
            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
            preds = torch.argmax(logits, dim=2).cpu().numpy()

        for b_idx, text in enumerate(b_texts):
            curr_ent = None
            spans = []
            for p_id, (s_char, e_char) in zip(preds[b_idx], offsets[b_idx]):
                if s_char == e_char:
                    continue
                tag = ID2LABEL.get(int(p_id), "O")

                if tag.startswith("B-"):
                    lbl = tag[2:]
                    # If fix_subwords is enabled: check if this is an intra-word continuation
                    if fix_subwords and curr_ent and curr_ent["end"] == s_char and curr_ent["label"] == lbl:
                        # Intra-word continuation: extend current entity
                        curr_ent["end"] = int(e_char)
                        curr_ent["text"] = text[curr_ent["start"]:int(e_char)]
                    else:
                        if curr_ent:
                            spans.append(curr_ent)
                        curr_ent = {
                            "start": int(s_char),
                            "end": int(e_char),
                            "label": lbl,
                            "text": text[s_char:e_char]
                        }
                elif tag.startswith("I-"):
                    lbl = tag[2:]
                    if curr_ent and curr_ent["label"] == lbl:
                        curr_ent["end"] = int(e_char)
                        curr_ent["text"] = text[curr_ent["start"]:int(e_char)]
                    else:
                        if curr_ent:
                            spans.append(curr_ent)
                        curr_ent = {
                            "start": int(s_char),
                            "end": int(e_char),
                            "label": lbl,
                            "text": text[s_char:e_char]
                        }
                else:
                    if curr_ent:
                        spans.append(curr_ent)
                        curr_ent = None
            if curr_ent:
                spans.append(curr_ent)

            valid = [e for e in spans if e["start"] < e["end"] and text[e["start"]:e["end"]] == e["text"]]
            all_spans.append(valid)
    return all_spans

print("Evaluating Baseline Model-Only on dev_real...")
base_spans = predict_batch(texts, fix_subwords=False)
base_bios = [spans_to_bio(t, s)[1] for t, s in zip(texts, base_spans)]
rep_base = classification_report(gold_bios, base_bios, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)
macro_base = np.mean([float(rep_base[c]["f1-score"])*100 for c in ENTITY_TYPES if c in rep_base])

print(f"Baseline: Micro P={rep_base['micro avg']['precision']*100:.2f}%, R={rep_base['micro avg']['recall']*100:.2f}%, F1={rep_base['micro avg']['f1-score']*100:.2f}%, Macro F1={macro_base:.2f}%")

print("\nEvaluating Fixed Model-Only on dev_real...")
fixed_spans = predict_batch(texts, fix_subwords=True)
fixed_bios = [spans_to_bio(t, s)[1] for t, s in zip(texts, fixed_spans)]
rep_fixed = classification_report(gold_bios, fixed_bios, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)
macro_fixed = np.mean([float(rep_fixed[c]["f1-score"])*100 for c in ENTITY_TYPES if c in rep_fixed])

print(f"Fixed:    Micro P={rep_fixed['micro avg']['precision']*100:.2f}%, R={rep_fixed['micro avg']['recall']*100:.2f}%, F1={rep_fixed['micro avg']['f1-score']*100:.2f}%, Macro F1={macro_fixed:.2f}%")

delta_micro = rep_fixed['micro avg']['f1-score']*100 - rep_base['micro avg']['f1-score']*100
delta_macro = macro_fixed - macro_base
print(f"\nDelta Micro F1: {delta_micro:+.2f}%")
print(f"Delta Macro F1: {delta_macro:+.2f}%")
