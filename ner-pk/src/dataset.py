"""
Dataset processing, document-level splitting, zero-leakage overlap validation,
and subword token-label alignment for Pakistani-context NER.
"""

import os
import sys
import re
import json
import random
import hashlib
from typing import List, Dict, Any, Tuple, Set

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES, BIO_LABELS, LABEL2ID, ID2LABEL, set_seed

set_seed(42)

def tokenize_with_offsets(text: str) -> List[Tuple[str, int, int]]:
    """
    Split text into words/tokens with exact start and end character offsets.
    Handles alphanumeric tokens, punctuation, and Urdu script words.
    """
    tokens = []
    # Match sequences of word characters or individual punctuation symbols
    for match in re.finditer(r"\w+|[^\w\s]", text, re.UNICODE):
        tokens.append((match.group(0), match.start(), match.end()))
    return tokens

def spans_to_bio(text: str, entities: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    Convert character-offset entity spans to token-level BIO tags.
    Returns (tokens, bio_tags).
    """
    token_tuples = tokenize_with_offsets(text)
    tokens = [t[0] for t in token_tuples]
    bio_tags = ["O"] * len(tokens)

    for ent in entities:
        ent_start, ent_end = ent["start"], ent["end"]
        ent_label = ent["label"]

        first_token = True
        for idx, (_, tok_start, tok_end) in enumerate(token_tuples):
            # Check overlap between token span and entity span
            if tok_start >= ent_start and tok_end <= ent_end:
                if first_token:
                    bio_tags[idx] = f"B-{ent_label}"
                    first_token = False
                else:
                    bio_tags[idx] = f"I-{ent_label}"
            elif tok_start < ent_end and tok_end > ent_start:
                # Partial boundary overlap
                if first_token:
                    bio_tags[idx] = f"B-{ent_label}"
                    first_token = False
                else:
                    bio_tags[idx] = f"I-{ent_label}"

    return tokens, bio_tags

def align_subwords_and_labels(tokens: List[str], bio_tags: List[str], tokenizer, max_length: int = 256) -> Dict[str, Any]:
    """
    Align token-level labels with fast tokenizer subwords.
    Assigns label ID to the first subword of each token; assigns -100 to subsequent subwords.
    """
    tokenized_inputs = tokenizer(
        tokens,
        is_split_into_words=True,
        max_length=max_length,
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )

    labels = []
    word_ids = tokenized_inputs.word_ids(batch_index=0)
    previous_word_idx = None

    for word_idx in word_ids:
        if word_idx is None:
            # Special tokens (<s>, </s>, <pad>) receive -100
            labels.append(-100)
        elif word_idx != previous_word_idx:
            # First subword of the word receives the token's label ID
            tag = bio_tags[word_idx] if word_idx < len(bio_tags) else "O"
            labels.append(LABEL2ID.get(tag, 0))
        else:
            # Subsequent subwords within the same word receive -100
            labels.append(-100)
        previous_word_idx = word_idx

    tokenized_inputs["labels"] = labels
    return tokenized_inputs

def verify_zero_overlap(train_records: List[Dict], dev_records: List[Dict], bench_records: List[Dict]) -> Dict[str, Any]:
    """
    Perform rigorous zero-overlap validation across splits:
    1. Document-level exclusivity (shared doc_ids == 0)
    2. Exact sentence text matches (shared exact strings == 0)
    3. Near-duplicate n-gram Jaccard similarity > 0.80 (must be 0)
    """
    train_docs = {r["doc_id"] for r in train_records}
    dev_docs = {r["doc_id"] for r in dev_records}
    bench_docs = {r["doc_id"] for r in bench_records}

    train_dev_docs = train_docs.union(dev_docs)
    shared_docs = train_dev_docs.intersection(bench_docs)

    train_dev_texts = {r["text"].strip().lower() for r in train_records + dev_records}
    bench_texts = {r["text"].strip().lower() for r in bench_records}
    exact_matches = train_dev_texts.intersection(bench_texts)

    # Near duplicate check on sample
    def get_5grams(text):
        words = text.split()
        return {" ".join(words[i:i+5]) for i in range(len(words)-4)} if len(words) >= 5 else {text}

    train_dev_5grams = [get_5grams(t) for t in list(train_dev_texts)[:1000]]
    near_dupes = 0
    for bt in list(bench_texts)[:300]:
        bg = get_5grams(bt)
        for tg in train_dev_5grams:
            inter = len(bg.intersection(tg))
            union = len(bg.union(tg))
            if union > 0 and (inter / union) > 0.80:
                near_dupes += 1
                break

    report = {
        "shared_documents_count": len(shared_docs),
        "exact_sentence_matches_count": len(exact_matches),
        "near_duplicate_matches_count": near_dupes,
        "is_leakage_free": (len(shared_docs) == 0 and len(exact_matches) == 0 and near_dupes == 0)
    }

    print("\n--- ZERO-OVERLAP LEAKAGE AUDIT ---")
    print(f"Shared document IDs with Benchmark: {len(shared_docs)}")
    print(f"Exact string matches with Benchmark: {len(exact_matches)}")
    print(f"Near-duplicate matches (>80% Jaccard): {near_dupes}")
    print(f"Audit Status: {'PASSED (Zero Leakage)' if report['is_leakage_free'] else 'FAILED'}")
    print("----------------------------------\n")

    assert report["is_leakage_free"], "CRITICAL: Data leakage detected between train/dev and benchmark!"
    return report

def partition_and_save_splits(
    silver_path: str,
    synth_train_path: str,
    synth_dev_path: str,
    synth_bench_path: str,
    processed_dir: str,
    benchmark_dir: str
):
    """
    Split at the ARTICLE/DOCUMENT level, add tokens and BIO tags,
    and save train.jsonl, dev.jsonl, benchmark.jsonl with zero leakage.
    """
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(benchmark_dir, exist_ok=True)

    # 1. Load silver corpus and group by doc_id
    scraped_by_doc: Dict[str, List[Dict]] = {}
    with open(silver_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                scraped_by_doc.setdefault(item["doc_id"], []).append(item)

    all_doc_ids = sorted(list(scraped_by_doc.keys()))
    random.seed(42)
    random.shuffle(all_doc_ids)

    # Allocate documents for Benchmark (~500 sentences)
    bench_docs = []
    bench_scraped_records = []
    for doc_id in all_doc_ids:
        if len(bench_scraped_records) < 500:
            bench_docs.append(doc_id)
            bench_scraped_records.extend(scraped_by_doc[doc_id])

    # Allocate documents for Dev (~350 sentences)
    remaining_docs = [d for d in all_doc_ids if d not in bench_docs]
    dev_docs = []
    dev_scraped_records = []
    for doc_id in remaining_docs:
        if len(dev_scraped_records) < 350:
            dev_docs.append(doc_id)
            dev_scraped_records.extend(scraped_by_doc[doc_id])

    # Remaining documents for Train
    train_docs = [d for d in remaining_docs if d not in dev_docs]
    train_scraped_records = []
    for d in train_docs:
        train_scraped_records.extend(scraped_by_doc[d])

    # 2. Load isolated synthetic splits
    def load_jsonl(path):
        records = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        return records

    synth_train = load_jsonl(synth_train_path)
    synth_dev = load_jsonl(synth_dev_path)
    synth_bench = load_jsonl(synth_bench_path)

    # Combine into initial splits
    initial_bench = bench_scraped_records + synth_bench
    initial_dev = dev_scraped_records + synth_dev
    initial_train = train_scraped_records + synth_train

    # Deduplicate against benchmark to guarantee 0 string overlap & 0 near-duplicates
    bench_seen_texts = {r["text"].strip().lower() for r in initial_bench}
    
    def get_5grams(text):
        words = text.lower().split()
        return {" ".join(words[i:i+5]) for i in range(len(words)-4)} if len(words) >= 5 else {text.lower()}

    bench_5grams = [get_5grams(r["text"]) for r in initial_bench]

    def is_near_bench(text):
        tg = get_5grams(text)
        for bg in bench_5grams:
            inter = len(bg.intersection(tg))
            union = len(bg.union(tg))
            if union > 0 and (inter / union) > 0.75:
                return True
        return False

    final_bench = initial_bench
    final_dev = [r for r in initial_dev if r["text"].strip().lower() not in bench_seen_texts and not is_near_bench(r["text"])]
    dev_seen_texts = {r["text"].strip().lower() for r in final_dev}.union(bench_seen_texts)
    final_train = [r for r in initial_train if r["text"].strip().lower() not in dev_seen_texts and not is_near_bench(r["text"])]

    # Add tokens and BIO tags to every record
    for split_records in [final_train, final_dev, final_bench]:
        for r in split_records:
            tokens, bio_tags = spans_to_bio(r["text"], r.get("entities", []))
            r["tokens"] = tokens
            r["bio_tags"] = bio_tags

    # Run strict zero-overlap verification
    verify_zero_overlap(final_train, final_dev, final_bench)

    # Save splits
    train_path = os.path.join(processed_dir, "train.jsonl")
    dev_path = os.path.join(processed_dir, "dev.jsonl")
    bench_path = os.path.join(benchmark_dir, "benchmark.jsonl")

    for path, records in [(train_path, final_train), (dev_path, final_dev), (bench_path, final_bench)]:
        with open(path, "w", encoding="utf-8") as out_f:
            for r in records:
                out_f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Saved Train: {len(final_train)} sentences -> {train_path}")
    print(f"Saved Dev:   {len(final_dev)} sentences -> {dev_path}")
    print(f"Saved Bench: {len(final_bench)} sentences -> {bench_path}")

    # Generate Class Distribution Statistics
    stats = {
        "Entity": ENTITY_TYPES,
        "Train": [0] * len(ENTITY_TYPES),
        "Dev": [0] * len(ENTITY_TYPES),
        "Benchmark": [0] * len(ENTITY_TYPES),
        "Total": [0] * len(ENTITY_TYPES)
    }
    label_to_idx = {name: i for i, name in enumerate(ENTITY_TYPES)}

    for col_name, records in [("Train", final_train), ("Dev", final_dev), ("Benchmark", final_bench)]:
        for r in records:
            for ent in r.get("entities", []):
                lbl = ent["label"]
                if lbl in label_to_idx:
                    stats[col_name][label_to_idx[lbl]] += 1
                    stats["Total"][label_to_idx[lbl]] += 1

    # Save summary table CSV
    tables_dir = os.path.join(os.path.dirname(__file__), "..", "reports", "tables")
    figures_dir = os.path.join(os.path.dirname(__file__), "..", "reports", "figures")
    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    csv_path = os.path.join(tables_dir, "dataset_splits_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("Entity,Train,Dev,Benchmark,Total\n")
        for i, ent in enumerate(ENTITY_TYPES):
            f.write(f"{ent},{stats['Train'][i]},{stats['Dev'][i]},{stats['Benchmark'][i]},{stats['Total'][i]}\n")
    print(f"Dataset split summary written to {csv_path}")

    # Plot class distribution chart
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        x = np.arange(len(ENTITY_TYPES))
        width = 0.25

        fig, ax = plt.subplots(figsize=(14, 7))
        rects1 = ax.bar(x - width, stats["Train"], width, label="Train", color="#1E88E5")
        rects2 = ax.bar(x, stats["Dev"], width, label="Dev", color="#FB8C00")
        rects3 = ax.bar(x + width, stats["Benchmark"], width, label="Benchmark", color="#43A047")

        ax.set_ylabel("Number of Mentions", fontsize=12)
        ax.set_title("Pakistani-Context NER: Entity Class Distribution Across Splits", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(ENTITY_TYPES, rotation=45, ha="right", fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plot_path = os.path.join(figures_dir, "class_distribution.png")
        plt.savefig(plot_path, dpi=300)
        plt.close()
        print(f"Saved class distribution chart to {plot_path}")
    except Exception as e:
        print(f"Could not generate plot: {e}")

    return stats

if __name__ == "__main__":
    silver = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "silver_annotated.jsonl")
    s_train = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "synthetic_train.jsonl")
    s_dev = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "synthetic_dev.jsonl")
    s_bench = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "synthetic_benchmark.jsonl")
    proc = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    bench = os.path.join(os.path.dirname(__file__), "..", "data", "benchmark")

    partition_and_save_splits(silver, s_train, s_dev, s_bench, proc, bench)
