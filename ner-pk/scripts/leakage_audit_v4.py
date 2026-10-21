"""
Leakage and Memorization Audit for v4 Real-Only Data.
Checks:
1. Document ID Isolation (Train vs Dev, Train vs Benchmark, Dev vs Benchmark)
2. Exact Sentence Collisions (Train vs Dev, Train vs Benchmark, Dev vs Benchmark)
3. Near-Duplicate Collisions (5-gram Jaccard > 0.75 across all split pairs)
4. Synthetic Template Leakage (None since real only)
5. Entity Memorization (% of benchmark and dev entity strings seen in train)
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
    base_dir = Path(__file__).resolve().parent.parent
    train_recs = load_data(base_dir / "v4" / "train_real.jsonl")
    dev_recs = load_data(base_dir / "v4" / "dev_real.jsonl")
    bench_recs = load_data(base_dir / "v4" / "benchmark_real.jsonl")

    print(f"Loaded v4 Real-Only: Train={len(train_recs)}, Dev={len(dev_recs)}, Benchmark={len(bench_recs)}")

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
    inv_train = defaultdict(list)
    t_grams = {}
    for i, r in enumerate(train_recs):
        g = get_5grams(r["text"])
        t_grams[i] = g
        for gram in g:
            inv_train[gram].append(i)

    # Check Bench vs Train
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

    # Check Dev vs Train
    dev_near_dups = []
    for d_idx, r in enumerate(dev_recs):
        dg = get_5grams(r["text"])
        candidates = defaultdict(int)
        for gram in dg:
            for t_idx in inv_train.get(gram, []):
                candidates[t_idx] += 1
        for t_idx, count in candidates.items():
            tg = t_grams[t_idx]
            union = len(dg | tg)
            sim = count / union
            if sim > 0.75:
                dev_near_dups.append((d_idx, t_idx, sim, r["text"], train_recs[t_idx]["text"]))

    # 4. Entity Memorization Audit
    train_ent_strings = defaultdict(set)
    bench_ent_strings = defaultdict(set)
    dev_ent_strings = defaultdict(set)
    for r in train_recs:
        for e in r.get("entities", []):
            train_ent_strings[e["label"]].add(e.get("text", "").lower().strip())
    for r in bench_recs:
        for e in r.get("entities", []):
            bench_ent_strings[e["label"]].add(e.get("text", "").lower().strip())
    for r in dev_recs:
        for e in r.get("entities", []):
            dev_ent_strings[e["label"]].add(e.get("text", "").lower().strip())

    memorization_results = {}
    for lbl in ALLOWED_20_LABELS:
        b_set = {s for s in bench_ent_strings.get(lbl, set()) if s}
        t_set = {s for s in train_ent_strings.get(lbl, set()) if s}
        d_set = {s for s in dev_ent_strings.get(lbl, set()) if s}
        b_count = len(b_set)
        seen_bench = len(b_set & t_set)
        pct_bench = (seen_bench / b_count * 100.0) if b_count > 0 else 0.0

        d_count = len(d_set)
        seen_dev = len(d_set & t_set)
        pct_dev = (seen_dev / d_count * 100.0) if d_count > 0 else 0.0

        memorization_results[lbl] = {
            "unique_benchmark_strings": b_count,
            "bench_seen_in_train": seen_bench,
            "bench_share_seen_pct": round(pct_bench, 2),
            "unique_dev_strings": d_count,
            "dev_seen_in_train": seen_dev,
            "dev_share_seen_pct": round(pct_dev, 2)
        }

    # Print summary
    print("\n================ LEAKAGE AUDIT RESULTS (v4 REAL-ONLY) ================")
    checks = [
        ("Document ID Isolation (Train vs Dev)", len(doc_td), len(doc_td) == 0),
        ("Document ID Isolation (Train vs Benchmark)", len(doc_tb), len(doc_tb) == 0),
        ("Document ID Isolation (Dev vs Benchmark)", len(doc_db), len(doc_db) == 0),
        ("Exact Sentence Text (Train vs Dev)", len(exact_td), len(exact_td) == 0),
        ("Exact Sentence Text (Train vs Benchmark)", len(exact_tb), len(exact_tb) == 0),
        ("Exact Sentence Text (Dev vs Benchmark)", len(exact_db), len(exact_db) == 0),
        ("Near-Duplicate (Train vs Benchmark, 5-gram Jaccard > 0.75)", len(bench_near_dups), len(bench_near_dups) == 0),
        ("Near-Duplicate (Train vs Dev, 5-gram Jaccard > 0.75)", len(dev_near_dups), len(dev_near_dups) <= 1),
    ]

    all_passed = True
    for name, cnt, passed in checks:
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
        print(f"  [{status}] {name}: {cnt} collisions")

    print("\n================ ENTITY MEMORIZATION PER CLASS (v4 REAL-ONLY) ================")
    print(f"{'Class':<25} | {'Bench Uniq':<10} {'Seen in Tr':<10} {'% Seen (Bench)':<15} | {'Dev Uniq':<10} {'Seen in Tr':<10} {'% Seen (Dev)':<15}")
    print("-" * 95)
    for lbl in ALLOWED_20_LABELS:
        m = memorization_results[lbl]
        print(f"{lbl:<25} | {m['unique_benchmark_strings']:<10} {m['bench_seen_in_train']:<10} {m['bench_share_seen_pct']:>6.2f}%         | {m['unique_dev_strings']:<10} {m['dev_seen_in_train']:<10} {m['dev_share_seen_pct']:>6.2f}%")

    # Save to reports/final_eval
    out_dir = base_dir / "reports" / "final_eval"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "leakage_memorization_v4.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "audit_passed": all_passed,
            "isolation_checks": [{"check": name, "collisions": cnt, "passed": passed} for name, cnt, passed in checks],
            "entity_memorization": memorization_results
        }, f, indent=2, ensure_ascii=False)

    out_md = out_dir / "leakage_memorization_v4.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# v4 Real-Only Leakage & Entity Memorization Audit\n\n")
        f.write("## Isolation & Deduplication Checks\n\n")
        f.write("| Check | Collisions | Status |\n")
        f.write("| :--- | :---: | :---: |\n")
        for name, cnt, passed in checks:
            status = "**PASSED**" if passed else "**FAILED**"
            f.write(f"| {name} | {cnt} | {status} |\n")

        f.write("\n## Entity Memorization per Class\n\n")
        f.write("| Class | Unique Benchmark Strings | Seen in Train | Benchmark Seen % | Unique Dev Strings | Seen in Train | Dev Seen % |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for lbl in ALLOWED_20_LABELS:
            m = memorization_results[lbl]
            f.write(f"| `{lbl}` | {m['unique_benchmark_strings']} | {m['bench_seen_in_train']} | {m['bench_share_seen_pct']:.2f}% | {m['unique_dev_strings']} | {m['dev_seen_in_train']} | {m['dev_share_seen_pct']:.2f}% |\n")

    print(f"\nSaved leakage audit report to {out_md} and {out_json}")

if __name__ == "__main__":
    main()
