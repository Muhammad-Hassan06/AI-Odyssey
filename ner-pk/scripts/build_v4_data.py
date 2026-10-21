"""
Build v4 real-only data from v3:
Filters out all synthetic, template-generated, augmented, and synthetic PII sentences.
Saves:
  v4/train_real.jsonl, v4/train_real.conll
  v4/dev_real.jsonl, v4/dev_real.conll
  v4/benchmark_real.jsonl, v4/benchmark_real.conll
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from collections import Counter

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

def compute_sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def detect_language(rec):
    lang = rec.get("language")
    if lang in ("en", "ur"):
        return lang
    text = rec.get("text", "")
    if re.search(r"[\u0600-\u06FF]", text):
        return "ur"
    return "en"

def is_synthetic(rec):
    src = str(rec.get("source", ""))
    doc = str(rec.get("doc_id", ""))
    sid = str(rec.get("sentence_id", ""))
    art = str(rec.get("article_id", ""))
    syn = rec.get("synthetic")

    # 1. Source explicitly notes Synthetic Generator
    if "synthetic" in src.lower():
        return True, "source_is_synthetic_generator"
    # 2. Document ID or Sentence ID marked synthetic
    if "synthetic" in doc.lower():
        return True, "doc_id_is_synthetic"
    if "synthetic" in sid.lower():
        return True, "sentence_id_is_synthetic"
    # 3. Article ID indicates synthetic PII or all-caps augmentation
    if art.startswith("synthetic"):
        return True, "article_is_synthetic_pii"
    if art.startswith("aug"):
        return True, "article_is_augmented"
    # 4. Synthetic boolean flag is True
    if syn is True:
        return True, "synthetic_flag_true"

    return False, "real_collected_text"

def process_split(in_jsonl_path, out_jsonl_path, out_conll_path, split_name):
    print(f"\n================ Processing {split_name} ================")
    print(f"Source file: {in_jsonl_path}")
    
    total_in = 0
    real_records = []
    excluded_reasons = Counter()

    with open(in_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            total_in += 1
            rec = json.loads(line)
            synthetic, reason = is_synthetic(rec)
            if synthetic:
                excluded_reasons[reason] += 1
            else:
                # Ensure tier is SILVER (honest silver, real text only, 0 human-gold)
                rec["tier"] = "SILVER"
                real_records.append(rec)

    print(f"Total input sentences: {total_in}")
    print(f"Excluded synthetic sentences: {sum(excluded_reasons.values())}")
    for r_name, r_cnt in excluded_reasons.most_common():
        print(f"  - {r_name}: {r_cnt}")
    print(f"Retained real sentences: {len(real_records)}")

    # Write out JSONL
    os.makedirs(os.path.dirname(out_jsonl_path), exist_ok=True)
    with open(out_jsonl_path, "w", encoding="utf-8") as f:
        for rec in real_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Write out CoNLL
    with open(out_conll_path, "w", encoding="utf-8") as f:
        for rec in real_records:
            for tok, tag in zip(rec["tokens"], rec["bio_tags"]):
                f.write(f"{tok} {tag}\n")
            f.write("\n")

    # Compute stats
    lang_counts = Counter()
    entity_counts = Counter()
    total_mentions = 0

    for rec in real_records:
        lang = detect_language(rec)
        lang_counts[lang] += 1
        for ent in rec.get("entities", []):
            lbl = ent["label"]
            entity_counts[lbl] += 1
            total_mentions += 1

    sha_jsonl = compute_sha256(out_jsonl_path)
    sha_conll = compute_sha256(out_conll_path)

    print(f"\nSaved v4 files:")
    print(f"  JSONL: {out_jsonl_path} (SHA256: {sha_jsonl})")
    print(f"  CoNLL: {out_conll_path} (SHA256: {sha_conll})")
    print(f"Language breakdown: English={lang_counts['en']}, Urdu={lang_counts['ur']}")
    print(f"Total entity mentions: {total_mentions}")

    return {
        "split": split_name,
        "input_total": total_in,
        "excluded_synthetic": sum(excluded_reasons.values()),
        "exclusion_breakdown": dict(excluded_reasons),
        "retained_real": len(real_records),
        "languages": dict(lang_counts),
        "total_mentions": total_mentions,
        "entity_counts": dict(entity_counts),
        "jsonl_path": str(out_jsonl_path),
        "jsonl_sha256": sha_jsonl,
        "conll_path": str(out_conll_path),
        "conll_sha256": sha_conll,
    }

def main():
    base_dir = Path(__file__).resolve().parent.parent
    v4_dir = base_dir / "v4"
    reports_dir = base_dir / "reports" / "final_eval"
    v4_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    splits = [
        ("train", base_dir / "v3" / "train.jsonl", v4_dir / "train_real.jsonl", v4_dir / "train_real.conll"),
        ("dev", base_dir / "v3" / "dev.jsonl", v4_dir / "dev_real.jsonl", v4_dir / "dev_real.conll"),
        ("benchmark", base_dir / "v3" / "benchmark.jsonl", v4_dir / "benchmark_real.jsonl", v4_dir / "benchmark_real.conll"),
    ]

    all_stats = {}
    for split_name, in_j, out_j, out_c in splits:
        stats = process_split(in_j, out_j, out_c, split_name)
        all_stats[split_name] = stats

    # Print Per-Class Mention Table with THIN / UNRELIABLE Flags
    print("\n" + "="*80)
    print("PER-CLASS MENTION COUNTS & SUPPORT RELIABILITY AUDIT (v4 REAL-ONLY)")
    print("="*80)
    print(f"{'Class':<25} | {'Train':<8} {'Train Flag':<10} | {'Dev':<6} {'Dev Flag':<12} | {'Bench':<6} {'Bench Flag':<12}")
    print("-" * 80)

    table_rows = []
    for lbl in ALLOWED_20_LABELS:
        t_cnt = all_stats["train"]["entity_counts"].get(lbl, 0)
        d_cnt = all_stats["dev"]["entity_counts"].get(lbl, 0)
        b_cnt = all_stats["benchmark"]["entity_counts"].get(lbl, 0)

        t_flag = "THIN" if t_cnt < 300 else "RELIABLE"
        d_flag = "UNRELIABLE" if d_cnt < 30 else "RELIABLE"
        b_flag = "UNRELIABLE" if b_cnt < 30 else "RELIABLE"

        print(f"{lbl:<25} | {t_cnt:<8} {t_flag:<10} | {d_cnt:<6} {d_flag:<12} | {b_cnt:<6} {b_flag:<12}")
        table_rows.append({
            "class": lbl,
            "train_count": t_cnt,
            "train_flag": t_flag,
            "dev_count": d_cnt,
            "dev_flag": d_flag,
            "bench_count": b_cnt,
            "bench_flag": b_flag,
        })

    # Save summary json
    summary_json_path = reports_dir / "v4_data_summary.json"
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "splits": all_stats,
            "per_class_table": table_rows
        }, f, indent=2, ensure_ascii=False)
    print(f"\nSaved v4 data summary to {summary_json_path}")

    # Save summary markdown
    summary_md_path = reports_dir / "v4_data_summary.md"
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("# v4 Real-Only Dataset Audit & Summary\n\n")
        f.write("**Audit Rule:** Real collected text only. 0 synthetic sentences, 0 template-generated sentences, 0 synthetic PII.\n\n")
        f.write("## File Metadata & SHA256\n\n")
        f.write("| Split | Sentences | Mentions | English | Urdu | JSONL Path | SHA256 |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :--- | :--- |\n")
        for s_name in ["train", "dev", "benchmark"]:
            st = all_stats[s_name]
            f.write(f"| **{s_name}** | {st['retained_real']} | {st['total_mentions']} | {st['languages'].get('en', 0)} | {st['languages'].get('ur', 0)} | `{st['jsonl_path']}` | `{st['jsonl_sha256']}` |\n")
        
        f.write("\n## Per-Class Mention Counts & Reliability Flags\n\n")
        f.write("> **Thresholds:** Train `THIN` if support < 300. Dev/Benchmark `UNRELIABLE` if support < 30.\n\n")
        f.write("| Entity Class | Train Count | Train Flag | Dev Count | Dev Flag | Benchmark Count | Benchmark Flag |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for row in table_rows:
            f.write(f"| `{row['class']}` | {row['train_count']} | {row['train_flag']} | {row['dev_count']} | {row['dev_flag']} | {row['bench_count']} | {row['bench_flag']} |\n")

    print(f"Saved v4 data summary markdown to {summary_md_path}")

if __name__ == "__main__":
    main()
