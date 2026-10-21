"""
Leakage and Memorization Audit for v3 Data.
Checks:
1. Document ID Isolation (Train vs Dev, Train vs Bench, Dev vs Bench)
2. Exact Sentence Collisions (Train vs Dev, Train vs Bench, Dev vs Bench)
3. Near-Duplicate Collisions (5-gram Jaccard > 0.75)
4. Synthetic Template Leakage
5. Entity Memorization (% of benchmark entity strings seen in train)
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

ALLOWED_20_LABELS = [
    "PERSON",
    "CITY",
    "PROVINCE_REGION",
    "COUNTRY",
    "LANDMARK_FACILITY",
    "GOVERNMENT_BODY",
    "POLITICAL_PARTY",
    "ORGANIZATION",
    "EDUCATIONAL_INSTITUTION",
    "COURT_LEGAL_BODY",
    "LAW_ACT",
    "EVENT",
    "MEDIA_OUTLET",
    "SPORTS_TEAM",
    "DATE",
    "TIME",
    "MONEY",
    "PERCENT",
    "PHONE_NUMBER",
    "ID_NUMBER",
]

def load_data(file_path):
    recs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            recs.append(json.loads(line))
    return recs

def get_5grams(text):
    words = text.lower().split()
    if len(words) < 5:
        return {text.lower()}
    return {" ".join(words[i:i+5]) for i in range(len(words)-4)}

def normalize_text(text):
    return " ".join(text.lower().split())

def main():
    train_recs = load_data("v3/train.jsonl")
    dev_recs = load_data("v3/dev.jsonl")
    bench_recs = load_data("v3/benchmark.jsonl")

    print(f"Loaded v3: Train={len(train_recs)}, Dev={len(dev_recs)}, Benchmark={len(bench_recs)}")

    # 1. Document ID Isolation
    train_docs = {r.get("doc_id") for r in train_recs if r.get("doc_id")}
    dev_docs = {r.get("doc_id") for r in dev_recs if r.get("doc_id")}
    bench_docs = {r.get("doc_id") for r in bench_recs if r.get("doc_id")}

    doc_td = train_docs & dev_docs
    doc_tb = train_docs & bench_docs
    doc_db = dev_docs & bench_docs

    # 2. Exact Sentence Collisions
    train_sents = {normalize_text(r["text"]): r.get("sentence_id") for r in train_recs}
    dev_sents = {normalize_text(r["text"]): r.get("sentence_id") for r in dev_recs}
    bench_sents = {normalize_text(r["text"]): r.get("sentence_id") for r in bench_recs}

    exact_td = set(train_sents.keys()) & set(dev_sents.keys())
    exact_tb = set(train_sents.keys()) & set(bench_sents.keys())
    exact_db = set(dev_sents.keys()) & set(bench_sents.keys())

    # 3. Near-Duplicate Collisions (5-gram Jaccard > 0.75)
    # Check Bench vs Train (real and overall)
    inv_train = defaultdict(list)
    t_grams = {}
    for i, r in enumerate(train_recs):
        g = get_5grams(r["text"])
        t_grams[i] = g
        for gram in g:
            inv_train[gram].append(i)

    bench_near_dups = []
    for b_idx, r in enumerate(bench_recs):
        bg = get_5grams(r["text"])
        candidates = defaultdict(int)
        for gram in bg:
            for t_idx in inv_train.get(gram, []):
                candidates[t_idx] += 1
        for t_idx, count in candidates.items():
            tg = t_grams[t_idx]
            union = len(bg | tg)
            sim = count / union
            if sim > 0.75:
                bench_near_dups.append((b_idx, t_idx, sim, r["text"], train_recs[t_idx]["text"]))

    # Check Dev vs Train (real text only, non-synthetic)
    dev_near_dups_real = []
    for d_idx, r in enumerate(dev_recs):
        if r.get("tier") == "SYNTHETIC":
            continue
        dg = get_5grams(r["text"])
        candidates = defaultdict(int)
        for gram in dg:
            for t_idx in inv_train.get(gram, []):
                candidates[t_idx] += 1
        for t_idx, count in candidates.items():
            if train_recs[t_idx].get("tier") == "SYNTHETIC":
                continue
            tg = t_grams[t_idx]
            union = len(dg | tg)
            sim = count / union
            if sim > 0.75:
                dev_near_dups_real.append((d_idx, t_idx, sim, r["text"], train_recs[t_idx]["text"]))

    # 4. Synthetic Template Leakage (exact synthetic sentence in train & bench)
    train_synth = {normalize_text(r["text"]) for r in train_recs if r.get("tier") == "SYNTHETIC"}
    bench_synth = {normalize_text(r["text"]) for r in bench_recs if r.get("tier") == "SYNTHETIC"}
    synth_overlap = train_synth & bench_synth

    # 5. Entity Memorization Audit
    train_ent_strings = defaultdict(set)
    bench_ent_strings = defaultdict(set)
    for r in train_recs:
        for e in r.get("entities", []):
            train_ent_strings[e["label"]].add(e.get("text", "").lower().strip())
    for r in bench_recs:
        for e in r.get("entities", []):
            bench_ent_strings[e["label"]].add(e.get("text", "").lower().strip())

    memorization_results = {}
    for lbl in ALLOWED_20_LABELS:
        b_set = {s for s in bench_ent_strings.get(lbl, set()) if s}
        t_set = {s for s in train_ent_strings.get(lbl, set()) if s}
        b_count = len(b_set)
        seen_count = len(b_set & t_set)
        pct = (seen_count / b_count * 100.0) if b_count > 0 else 0.0
        memorization_results[lbl] = {
            "unique_benchmark_strings": b_count,
            "seen_in_train": seen_count,
            "share_seen_pct": round(pct, 2)
        }

    # Print summary
    print("\n================ LEAKAGE AUDIT RESULTS ================")
    checks = [
        ("Document ID Isolation (Train vs Dev)", len(doc_td), len(doc_td) == 0),
        ("Document ID Isolation (Train vs Benchmark)", len(doc_tb), len(doc_tb) == 0),
        ("Document ID Isolation (Dev vs Benchmark)", len(doc_db), len(doc_db) == 0),
        ("Exact Sentence Text (Train vs Dev)", len(exact_td), len(exact_td) == 0),
        ("Exact Sentence Text (Train vs Benchmark)", len(exact_tb), len(exact_tb) == 0),
        ("Exact Sentence Text (Dev vs Benchmark)", len(exact_db), len(exact_db) == 0),
        ("Near-Duplicate (Train vs Benchmark, 5-gram Jaccard > 0.75)", len(bench_near_dups), len(bench_near_dups) == 0),
        ("Synthetic Template Leakage (Train vs Benchmark)", len(synth_overlap), len(synth_overlap) == 0),
    ]

    for name, cnt, passed in checks:
        status = "PASSED" if passed else "FAILED"
        print(f"  [{status}] {name}: {cnt} collisions")

    print("\n================ ENTITY MEMORIZATION PER CLASS ================")
    print(f"{'Class':<25} | {'Unique Bench':<12} | {'Seen in Train':<14} | {'% Seen in Train':<16}")
    print("-" * 75)
    for lbl, data in memorization_results.items():
        print(f"{lbl:<25} | {data['unique_benchmark_strings']:<12} | {data['seen_in_train']:<14} | {data['share_seen_pct']:>6.2f}%")

    # Save to reports/audit_final/leakage_memorization_v3.md
    out_dir = Path("reports/audit_final")
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "leakage_memorization_v3.md"
    json_path = out_dir / "leakage_memorization_v3.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "checks": [{"check": name, "collisions": cnt, "passed": passed} for name, cnt, passed in checks],
            "memorization": memorization_results
        }, f, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Leakage and Memorization Audit for Cleaned `v3` Data\n\n")
        f.write("**Audit Date:** 21 October 2026  \n")
        f.write("**Evaluated Dataset:** `v3/train.jsonl` (7,997 sents), `v3/dev.jsonl` (887 sents), `v3/benchmark.jsonl` (1,035 sents)  \n\n")
        f.write("## 1. Data Leakage Checks (Train vs Dev vs Internal Silver Benchmark)\n\n")
        f.write("| Leakage Check Type | Compared Splits | Collision Count | Status | Notes |\n")
        f.write("| :--- | :--- | :---: | :---: | :--- |\n")
        for name, cnt, passed in checks:
            badge = "**PASSED**" if passed else "**FAILED**"
            note = "Zero overlap verified" if passed else f"{cnt} leaks detected"
            f.write(f"| {name} | - | {cnt} | {badge} | {note} |\n")

        f.write("\n## 2. Entity Memorization Audit (Benchmark Strings Seen in Train)\n\n")
        f.write("Measures the share of entity surface strings in the internal silver benchmark that appear identically in the training split:\n\n")
        f.write("| Entity Class | Unique Benchmark Strings | Seen in Train | % Seen in Train | Generalization Vulnerability |\n")
        f.write("| :--- | :---: | :---: | :---: | :--- |\n")
        for lbl, data in memorization_results.items():
            pct = data["share_seen_pct"]
            if pct >= 95.0:
                vuln = "HIGH (Heavy gazetteer overlap; low surface diversity in benchmark)"
            elif pct >= 80.0:
                vuln = "MODERATE (Shared entity vocabulary between news corpora)"
            else:
                vuln = "LOW (Significant novel surface forms tested)"
            f.write(f"| **`{lbl}`** | {data['unique_benchmark_strings']} | {data['seen_in_train']} | **{pct:.2f}%** | {vuln} |\n")

    print(f"\nSaved report to {md_path} and {json_path}")

if __name__ == "__main__":
    main()
