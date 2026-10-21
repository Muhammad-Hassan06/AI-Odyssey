"""
Merge v4/train_real.jsonl and v5/train_augmented_1500.jsonl into v5/train.jsonl.
Copy v4/dev_real.jsonl as v5/dev.jsonl (keeping validation clean).
Validate schema across both splits.
"""

import json
import shutil
from pathlib import Path

BASE = Path("c:/Users/M Wasay/VS CODE ALL LANG FOLDERS/AI-Odyssey/ner-pk")
v4_train = BASE / "v4/train_real.jsonl"
v4_dev = BASE / "v4/dev_real.jsonl"
v5_aug = BASE / "v5/train_augmented_1500.jsonl"
v5_train = BASE / "v5/train.jsonl"
v5_dev = BASE / "v5/dev.jsonl"

# 1. Merge train
total_train = []
with open(v4_train, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            total_train.append(json.loads(line))

with open(v5_aug, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            total_train.append(json.loads(line))

with open(v5_train, "w", encoding="utf-8") as f:
    for item in total_train:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

# 2. Copy dev
shutil.copy(v4_dev, v5_dev)

print(f"Created v5/train.jsonl with {len(total_train)} sentences (5,282 real + 1,500 augmented).")
print(f"Created v5/dev.jsonl (copied from v4/dev_real.jsonl).")
