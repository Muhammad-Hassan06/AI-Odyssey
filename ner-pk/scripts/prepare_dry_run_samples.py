"""
Prepare 50-sentence test samples for dry run:
- data/dry_run_samples/sample_50.txt
- data/dry_run_samples/sample_50.csv
- data/dry_run_samples/sample_50.conll
"""

import sys
import json
import csv
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

base_dir = Path(__file__).resolve().parent.parent
v4_dev = base_dir / "v4" / "dev_real.jsonl"
out_dir = base_dir / "data" / "dry_run_samples"
out_dir.mkdir(parents=True, exist_ok=True)

# Load first 50 sentences from dev_real
recs = []
with open(v4_dev, "r", encoding="utf-8") as f:
    for line in f:
        recs.append(json.loads(line))
        if len(recs) == 50:
            break

# 1. Write .txt (50 lines)
txt_path = out_dir / "sample_50.txt"
with open(txt_path, "w", encoding="utf-8") as f:
    for r in recs:
        # replace newlines if any
        line = r["text"].replace("\r", " ").replace("\n", " ").strip()
        f.write(line + "\n")
print(f"Created {txt_path} (50 lines)")

# 2. Write .csv (id, text)
csv_path = out_dir / "sample_50.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "text"])
    for idx, r in enumerate(recs, 1):
        line = r["text"].replace("\r", " ").replace("\n", " ").strip()
        writer.writerow([f"row_{idx:03d}", line])
print(f"Created {csv_path} (50 rows)")

# 3. Write .conll (token per line, blank line between sentences)
conll_path = out_dir / "sample_50.conll"
with open(conll_path, "w", encoding="utf-8") as f:
    for r in recs:
        for tok in r["tokens"]:
            f.write(f"{tok}\n")
        f.write("\n")
print(f"Created {conll_path} (50 sentences)")
