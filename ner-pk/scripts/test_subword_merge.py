import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from src.constants import ID2LABEL

tokenizer = AutoTokenizer.from_pretrained('models/final')
model = AutoModelForTokenClassification.from_pretrained('models/final')

text = 'At dawn, while listening to smooth jazz, Anchor Kamran Khan from Geo News met Jazz executives at Gaddafi Stadium.'
enc = tokenizer(text, return_offsets_mapping=True, return_tensors='pt')
offsets = enc['offset_mapping'][0].numpy()
with torch.no_grad():
    logits = model(**{k: v for k, v in enc.items() if k != 'offset_mapping'}).logits[0]
preds = torch.argmax(logits, dim=1).numpy()

all_spans = []
curr_ent = None

for p_id, (start_char, end_char) in zip(preds, offsets):
    if start_char == end_char:
        continue
    tag = ID2LABEL.get(int(p_id), "O")
    if tag == "O":
        if curr_ent:
            all_spans.append(curr_ent)
            curr_ent = None
        continue

    lbl = tag[2:]
    # Check if this subword is directly adjacent to curr_ent and same label (subword continuation)
    if curr_ent and curr_ent["label"] == lbl and start_char == curr_ent["end"]:
        curr_ent["end"] = int(end_char)
        curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
    elif tag.startswith("B-"):
        if curr_ent:
            all_spans.append(curr_ent)
        curr_ent = {
            "text": text[start_char:end_char],
            "start": int(start_char),
            "end": int(end_char),
            "label": lbl
        }
    elif tag.startswith("I-"):
        if curr_ent and curr_ent["label"] == lbl:
            curr_ent["end"] = int(end_char)
            curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
        else:
            if curr_ent:
                all_spans.append(curr_ent)
            curr_ent = {
                "text": text[start_char:end_char],
                "start": int(start_char),
                "end": int(end_char),
                "label": lbl
            }

if curr_ent:
    all_spans.append(curr_ent)

print("RAW MERGED SPANS:")
for s in all_spans:
    print(s)
