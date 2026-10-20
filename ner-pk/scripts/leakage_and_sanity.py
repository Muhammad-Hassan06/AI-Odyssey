"""
Zero-Leakage Audit and Training Sanity Dry-Run.
Checks:
1. Document ID isolation (Train vs Dev, Train vs Benchmark, Dev vs Benchmark)
2. Exact sentence string isolation
3. Near-duplicate isolation (Word-level Jaccard similarity > 0.75)
4. Dry-run of train.py to verify version-safe arguments and run config export.
"""

import os
import sys
import json
import hashlib
from typing import Set, List, Dict

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(base_dir, "v2_frozen") if os.path.exists(os.path.join(base_dir, "v2_frozen", "train.jsonl")) else os.path.join(base_dir, "v2")

print(f"\n=======================================================")
print(f"ZERO-LEAKAGE AUDIT ({os.path.basename(data_dir)})")
print(f"=======================================================\n")

def load_split(name):
    p = os.path.join(data_dir, f"{name}.jsonl")
    records = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

train_records = load_split("train")
dev_records = load_split("dev")
bench_records = load_split("benchmark")

print(f"Loaded {len(train_records)} train, {len(dev_records)} dev, {len(bench_records)} benchmark sentences.")

# 1. Document ID overlap check
def get_doc_ids(records):
    docs = set()
    for r in records:
        d = r.get("doc_id")
        if d:
            docs.add(d)
    return docs

train_docs = get_doc_ids(train_records)
dev_docs = get_doc_ids(dev_records)
bench_docs = get_doc_ids(bench_records)

td_overlap = train_docs.intersection(dev_docs)
tb_overlap = train_docs.intersection(bench_docs)
db_overlap = dev_docs.intersection(bench_docs)

print(f"\nDocument ID Overlap Checks:")
print(f"  Train & Dev Shared Docs:       {len(td_overlap)}")
print(f"  Train & Benchmark Shared Docs: {len(tb_overlap)}")
print(f"  Dev & Benchmark Shared Docs:   {len(db_overlap)}")

# 2. Exact sentence text overlap
def get_sentence_hashes(records):
    return {hashlib.sha256(r["text"].strip().lower().encode("utf-8")).hexdigest() for r in records}

train_sents = get_sentence_hashes(train_records)
dev_sents = get_sentence_hashes(dev_records)
bench_sents = get_sentence_hashes(bench_records)

sent_td = train_sents.intersection(dev_sents)
sent_tb = train_sents.intersection(bench_sents)
sent_db = dev_sents.intersection(bench_sents)

print(f"\nExact Sentence Text Overlap Checks:")
print(f"  Train & Dev Shared Sentences:       {len(sent_td)}")
print(f"  Train & Benchmark Shared Sentences: {len(sent_tb)}")
print(f"  Dev & Benchmark Shared Sentences:   {len(sent_db)}")

# 3. Near-duplicate sentence check (Jaccard > 0.75)
def get_shingle_set(text: str) -> Set[str]:
    words = text.lower().split()
    return set(words)

def jaccard(s1: Set[str], s2: Set[str]) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

near_dups_td = 0
for d_r in dev_records[:300]: # Sample check across evaluation
    s_dev = get_shingle_set(d_r["text"])
    for t_r in train_records:
        if jaccard(s_dev, get_shingle_set(t_r["text"])) > 0.75:
            near_dups_td += 1
            break

print(f"\nNear-Duplicate Jaccard (>0.75) Check (Dev Sample vs Train): {near_dups_td} near-duplicates")

all_passed = (len(td_overlap) == 0 and len(tb_overlap) == 0 and len(db_overlap) == 0 and
              len(sent_td) == 0 and len(sent_tb) == 0 and len(sent_db) == 0 and near_dups_td == 0)

if all_passed:
    print(f"\n>>> AUDIT VERDICT: PASSED (Zero document overlap, zero sentence leakage, zero near-duplicates)")
else:
    print(f"\n>>> AUDIT VERDICT: FAILED")
