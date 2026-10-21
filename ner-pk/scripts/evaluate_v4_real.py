"""
Step 2 Live Evaluation: Evaluates Current Checkpoint on v4 Real-Only Data.
Evaluates 4 modes on v4/dev_real.jsonl and v4/benchmark_real.jsonl:
1. model_only
2. rules_only
3. old_hybrid
4. conservative_hybrid

Computes:
- Precision, Recall, Micro-F1, Macro-F1 (20 classes)
- Micro-F1 ex-PII (excluding PHONE_NUMBER and ID_NUMBER)
- Token-level accuracy
- Entity-level exact-match accuracy (% sentences with exact entity set match)
- 1,000-resample document bootstrap 95% CIs
- Per-class table with precision, recall, F1, support, and UNRELIABLE (<30 support) flags.
- Full per-class table for the best mode on Dev.
Saves to:
- reports/final_eval/live_eval_real_only.md
- reports/final_eval/live_eval_real_only.csv
- reports/final_eval/live_eval_real_only.json
"""

import os
import sys
import json
import csv
import time
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from seqeval.metrics import classification_report
from seqeval.scheme import IOB2

from src.constants import ENTITY_TYPES, ID2LABEL, set_seed
from src.rules import extract_regex_entities
from src.preannotate import preannotate_sentence
from src.postprocess import postprocess_entities, hybrid_merge_predictions
from src.dataset import spans_to_bio

set_seed(42)
np.random.seed(42)

model_dir = base_dir / "models" / "final"
v4_dir = base_dir / "v4"
dev_path = v4_dir / "dev_real.jsonl"
bench_path = v4_dir / "benchmark_real.jsonl"
reports_dir = base_dir / "reports" / "final_eval"
reports_dir.mkdir(parents=True, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading checkpoint from {model_dir} on device: {device}...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
model = AutoModelForTokenClassification.from_pretrained(str(model_dir)).to(device)
model.eval()
print("Model loaded successfully.", flush=True)

def load_data(file_path):
    recs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                recs.append(json.loads(line))
    return recs

def batch_predict_model(texts, batch_size=32):
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
        input_ids = encoding["input_ids"].to(device)
        attention_mask = encoding["attention_mask"].to(device)

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
                    if curr_ent:
                        spans.append(curr_ent)
                    curr_ent = {
                        "start": int(s_char),
                        "end": int(e_char),
                        "label": tag[2:],
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
        print(f"  Inference progress: {min(i+batch_size, total)}/{total} sentences...", flush=True)
    return all_spans

def old_hybrid_merge(model_entities, rule_entities, text_len):
    """Legacy naive merge: model entities take priority, rules fill gaps."""
    occupied = [False] * (text_len + 1)
    resolved = []
    for m in model_entities:
        s, e = m["start"], m["end"]
        if s < 0 or e > text_len or s >= e:
            continue
        for i in range(s, e):
            occupied[i] = True
        resolved.append(m)

    for r in rule_entities:
        s, e = r["start"], r["end"]
        if s < 0 or e > text_len or s >= e:
            continue
        if not any(occupied[s:e]):
            for i in range(s, e):
                occupied[i] = True
            resolved.append(r)

    resolved.sort(key=lambda x: x["start"])
    return resolved

def extract_bio_entities(bio_seq):
    entities = []
    curr = None
    for idx, tag in enumerate(bio_seq):
        if tag.startswith("B-"):
            if curr:
                entities.append(curr)
            curr = (idx, idx + 1, tag[2:])
        elif tag.startswith("I-"):
            lbl = tag[2:]
            if curr and curr[2] == lbl:
                curr = (curr[0], idx + 1, lbl)
            else:
                if curr:
                    entities.append(curr)
                curr = (idx, idx + 1, lbl)
        else:
            if curr:
                entities.append(curr)
                curr = None
    if curr:
        entities.append(curr)
    return entities

def remove_pii(bio_seqs):
    clean = []
    for seq in bio_seqs:
        new_s = []
        for tag in seq:
            if "PHONE_NUMBER" in tag or "ID_NUMBER" in tag:
                new_s.append("O")
            else:
                new_s.append(tag)
        clean.append(new_s)
    return clean

def compute_metrics(gold_bios, pred_bios):
    rep = classification_report(gold_bios, pred_bios, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)

    gold_nopii = remove_pii(gold_bios)
    pred_nopii = remove_pii(pred_bios)
    rep_nopii = classification_report(gold_nopii, pred_nopii, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)

    # Token accuracy
    total_tokens = 0
    correct_tokens = 0
    for g_seq, p_seq in zip(gold_bios, pred_bios):
        for g, p in zip(g_seq, p_seq):
            total_tokens += 1
            if g == p:
                correct_tokens += 1
    token_acc = round(correct_tokens / max(1, total_tokens) * 100, 2)

    # Sentence-level exact match accuracy
    exact_matches = 0
    for g_seq, p_seq in zip(gold_bios, pred_bios):
        g_ents = set(extract_bio_entities(g_seq))
        p_ents = set(extract_bio_entities(p_seq))
        if g_ents == p_ents:
            exact_matches += 1
    sentence_exact_match_acc = round(exact_matches / max(1, len(gold_bios)) * 100, 2)

    classes_dict = {}
    macro_f1s = []
    for c in ENTITY_TYPES:
        if c in rep:
            p = float(rep[c]["precision"]) * 100
            r = float(rep[c]["recall"]) * 100
            f1 = float(rep[c]["f1-score"]) * 100
            sup = int(rep[c]["support"])
            flag = "UNRELIABLE" if sup < 30 else "RELIABLE"
            classes_dict[c] = {"precision": p, "recall": r, "f1": f1, "support": sup, "flag": flag}
            macro_f1s.append(f1)
        else:
            classes_dict[c] = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 0, "flag": "UNRELIABLE"}
            macro_f1s.append(0.0)

    return {
        "precision": float(rep["micro avg"]["precision"]) * 100,
        "recall": float(rep["micro avg"]["recall"]) * 100,
        "micro_f1": float(rep["micro avg"]["f1-score"]) * 100,
        "macro_f1": float(np.mean(macro_f1s)),
        "micro_f1_nopii": float(rep_nopii["micro avg"]["f1-score"]) * 100,
        "token_accuracy": token_acc,
        "exact_match_accuracy": sentence_exact_match_acc,
        "classes": classes_dict
    }

def bootstrap_ci_vectorized(gold_bios, pred_bios, doc_to_indices, n_resamples=1000):
    doc_keys = list(doc_to_indices.keys())
    n_docs = len(doc_keys)
    class_to_idx = {c: i for i, c in enumerate(ENTITY_TYPES)}
    num_classes = len(ENTITY_TYPES)

    doc_tp = np.zeros((n_docs, num_classes), dtype=np.int32)
    doc_fp = np.zeros((n_docs, num_classes), dtype=np.int32)
    doc_fn = np.zeros((n_docs, num_classes), dtype=np.int32)

    for d_idx, d_key in enumerate(doc_keys):
        s_indices = doc_to_indices[d_key]
        for s_i in s_indices:
            g_ents = set(extract_bio_entities(gold_bios[s_i]))
            p_ents = set(extract_bio_entities(pred_bios[s_i]))

            for ent in (g_ents & p_ents):
                lbl = ent[2]
                if lbl in class_to_idx:
                    doc_tp[d_idx, class_to_idx[lbl]] += 1
            for ent in (p_ents - g_ents):
                lbl = ent[2]
                if lbl in class_to_idx:
                    doc_fp[d_idx, class_to_idx[lbl]] += 1
            for ent in (g_ents - p_ents):
                lbl = ent[2]
                if lbl in class_to_idx:
                    doc_fn[d_idx, class_to_idx[lbl]] += 1

    rng = np.random.RandomState(42)
    boot_indices = rng.choice(n_docs, size=(n_resamples, n_docs), replace=True)
    non_pii_mask = np.array([c not in ["PHONE_NUMBER", "ID_NUMBER"] for c in ENTITY_TYPES], dtype=bool)

    boot_micro = []
    boot_macro = []
    boot_nopii = []
    boot_classes = {c: [] for c in ENTITY_TYPES}

    for b in range(n_resamples):
        sample_rows = boot_indices[b]
        s_tp = np.sum(doc_tp[sample_rows], axis=0)
        s_fp = np.sum(doc_fp[sample_rows], axis=0)
        s_fn = np.sum(doc_fn[sample_rows], axis=0)

        tot_tp = np.sum(s_tp)
        tot_fp = np.sum(s_fp)
        tot_fn = np.sum(s_fn)
        denom_micro = 2 * tot_tp + tot_fp + tot_fn
        micro_f1 = (2 * tot_tp / denom_micro * 100) if denom_micro > 0 else 0.0
        boot_micro.append(micro_f1)

        nopii_tp = np.sum(s_tp[non_pii_mask])
        nopii_fp = np.sum(s_fp[non_pii_mask])
        nopii_fn = np.sum(s_fn[non_pii_mask])
        denom_nopii = 2 * nopii_tp + nopii_fp + nopii_fn
        nopii_f1 = (2 * nopii_tp / denom_nopii * 100) if denom_nopii > 0 else 0.0
        boot_nopii.append(nopii_f1)

        denoms_class = 2 * s_tp + s_fp + s_fn
        f1_class = np.where(denoms_class > 0, (2 * s_tp / denoms_class) * 100, 0.0)
        boot_macro.append(np.mean(f1_class))
        for c_idx, c in enumerate(ENTITY_TYPES):
            boot_classes[c].append(f1_class[c_idx])

    return {
        "ci_micro": (float(np.percentile(boot_micro, 2.5)), float(np.percentile(boot_micro, 97.5))),
        "ci_macro": (float(np.percentile(boot_macro, 2.5)), float(np.percentile(boot_macro, 97.5))),
        "ci_nopii": (float(np.percentile(boot_nopii, 2.5)), float(np.percentile(boot_nopii, 97.5))),
        "ci_classes": {c: (float(np.percentile(boot_classes[c], 2.5)), float(np.percentile(boot_classes[c], 97.5))) for c in ENTITY_TYPES}
    }

def evaluate_split(records, split_name):
    print(f"\n{'='*70}", flush=True)
    print(f"EVALUATING SPLIT: {split_name} ({len(records)} real sentences)", flush=True)
    print(f"{'='*70}", flush=True)

    texts = [r["text"] for r in records]
    gold_bios = [r["bio_tags"] for r in records]

    doc_to_indices = defaultdict(list)
    for idx, r in enumerate(records):
        d_key = r.get("doc_id") or r.get("sentence_id") or f"s_{idx}"
        doc_to_indices[d_key].append(idx)

    # 1. Model-Only
    print("\n1. Running Model-Only Batched Inference...", flush=True)
    t0 = time.time()
    raw_model_spans = batch_predict_model(texts, batch_size=32)
    model_bios = [spans_to_bio(t, spans)[1] for t, spans in zip(texts, raw_model_spans)]
    print(f"   Model-Only complete in {time.time()-t0:.2f}s", flush=True)

    # 2. Rules-Only
    print("2. Running Rules-Only Inference...", flush=True)
    rules_spans = []
    for t in texts:
        r_ents = preannotate_sentence(t)
        f_ents = postprocess_entities(t, r_ents)
        rules_spans.append(f_ents)
    rules_bios = [spans_to_bio(t, spans)[1] for t, spans in zip(texts, rules_spans)]

    # 3. Old Hybrid (Model overrides Rules)
    print("3. Running Old Hybrid Inference (Model priority)...", flush=True)
    old_hybrid_spans = []
    for t, m_ents, r_ents in zip(texts, raw_model_spans, rules_spans):
        merged = old_hybrid_merge(m_ents, r_ents, len(t))
        f_ents = postprocess_entities(t, merged)
        old_hybrid_spans.append(f_ents)
    old_hybrid_bios = [spans_to_bio(t, spans)[1] for t, spans in zip(texts, old_hybrid_spans)]

    # 4. Conservative Hybrid (Rules priority on regex/gazetteer, model contextual)
    print("4. Running Conservative Hybrid Inference (Protected Merge)...", flush=True)
    cons_hybrid_spans = []
    for t, m_ents, r_ents in zip(texts, raw_model_spans, rules_spans):
        merged = hybrid_merge_predictions(m_ents, r_ents, len(t))
        f_ents = postprocess_entities(t, merged)
        cons_hybrid_spans.append(f_ents)
    cons_hybrid_bios = [spans_to_bio(t, spans)[1] for t, spans in zip(texts, cons_hybrid_spans)]

    modes = [
        ("model_only", "Model-Only (XLM-R Checkpoint)", model_bios, raw_model_spans),
        ("rules_only", "Rules-Only (Regex + Gazetteers)", rules_bios, rules_spans),
        ("old_hybrid", "Old Hybrid (Model Overrides Rules)", old_hybrid_bios, old_hybrid_spans),
        ("conservative_hybrid", "Conservative Hybrid (Rules Priority)", cons_hybrid_bios, cons_hybrid_spans)
    ]

    split_results = {}
    for m_key, m_name, pred_bios, pred_spans in modes:
        print(f"\nComputing metrics and 1000 CIs for [{m_name}]...", flush=True)
        m_dict = compute_metrics(gold_bios, pred_bios)
        ci_dict = bootstrap_ci_vectorized(gold_bios, pred_bios, doc_to_indices, n_resamples=1000)
        m_dict["ci"] = ci_dict
        m_dict["name"] = m_name
        split_results[m_key] = m_dict

        print(f"  {m_name}:")
        print(f"    Precision: {m_dict['precision']:.2f}% | Recall: {m_dict['recall']:.2f}%")
        print(f"    Micro-F1:  {m_dict['micro_f1']:.2f}% [95% CI: {ci_dict['ci_micro'][0]:.2f} - {ci_dict['ci_micro'][1]:.2f}]")
        print(f"    Macro-F1:  {m_dict['macro_f1']:.2f}% [95% CI: {ci_dict['ci_macro'][0]:.2f} - {ci_dict['ci_macro'][1]:.2f}]")
        print(f"    Ex-PII F1: {m_dict['micro_f1_nopii']:.2f}% [95% CI: {ci_dict['ci_nopii'][0]:.2f} - {ci_dict['ci_nopii'][1]:.2f}]")
        print(f"    Token Acc: {m_dict['token_accuracy']:.2f}% | Exact-Match Sent Acc: {m_dict['exact_match_accuracy']:.2f}%")

    return split_results

def main():
    dev_records = load_data(dev_path)
    bench_records = load_data(bench_path)

    print(f"Loaded v4 Data: Dev={len(dev_records)} sentences, Benchmark={len(bench_records)} sentences (internal silver benchmark, real text only, 0 human-gold sentences).", flush=True)

    dev_results = evaluate_split(dev_records, "DEV (v4/dev_real.jsonl)")
    bench_results = evaluate_split(bench_records, "BENCHMARK (v4/benchmark_real.jsonl - internal silver benchmark, real text only, 0 human-gold)")

    # Find winning mode on DEV by Macro-F1
    best_dev_mode = max(dev_results.keys(), key=lambda k: dev_results[k]["macro_f1"])
    print(f"\n=======================================================", flush=True)
    print(f"WINNING MODE ON DEV REAL: [{best_dev_mode}] ({dev_results[best_dev_mode]['name']})", flush=True)
    print(f"NOTE ON CIRCULARITY: Rules-only and Hybrid modes benefit from circularity because silver benchmark and dev labels were originally produced by the same regex and gazetteer rules.", flush=True)
    print(f"=======================================================", flush=True)

    # Print Full Per-Class Table for the Best Mode on DEV
    print("\n" + "="*95, flush=True)
    print(f"FULL PER-CLASS TABLE FOR BEST DEV MODE: [{best_dev_mode}] ({dev_results[best_dev_mode]['name']})", flush=True)
    print("="*95, flush=True)
    print(f"{'Class':<25} | {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8} {'Flag':<12} {'95% Bootstrap CI':<20}", flush=True)
    print("-" * 95, flush=True)
    for c in ENTITY_TYPES:
        c_stats = dev_results[best_dev_mode]["classes"][c]
        ci = dev_results[best_dev_mode]["ci"]["ci_classes"][c]
        print(f"{c:<25} | {c_stats['precision']:>7.2f}%   {c_stats['recall']:>7.2f}%   {c_stats['f1']:>7.2f}%   {c_stats['support']:<8} {c_stats['flag']:<12} [{ci[0]:>6.2f} - {ci[1]:>6.2f}]", flush=True)

    # Also print Model-Only Per-Class Table on DEV for audit transparency
    print("\n" + "="*95, flush=True)
    print(f"FULL PER-CLASS TABLE FOR MODEL-ONLY ON DEV (Pure Checkpoint Evaluation)", flush=True)
    print("="*95, flush=True)
    print(f"{'Class':<25} | {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8} {'Flag':<12} {'95% Bootstrap CI':<20}", flush=True)
    print("-" * 95, flush=True)
    for c in ENTITY_TYPES:
        c_stats = dev_results["model_only"]["classes"][c]
        ci = dev_results["model_only"]["ci"]["ci_classes"][c]
        print(f"{c:<25} | {c_stats['precision']:>7.2f}%   {c_stats['recall']:>7.2f}%   {c_stats['f1']:>7.2f}%   {c_stats['support']:<8} {c_stats['flag']:<12} [{ci[0]:>6.2f} - {ci[1]:>6.2f}]", flush=True)

    # Save to JSON
    json_path = reports_dir / "live_eval_real_only.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "dev_results": dev_results,
            "benchmark_results": bench_results,
            "winning_mode_dev": best_dev_mode
        }, f, indent=2, ensure_ascii=False)

    # Save to CSV
    csv_path = reports_dir / "live_eval_real_only.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["split", "mode_key", "mode_name", "precision", "recall", "micro_f1", "ci_micro_low", "ci_micro_high", "macro_f1", "ci_macro_low", "ci_macro_high", "micro_f1_nopii", "token_accuracy", "exact_match_sent_acc"])
        for s_name, res in [("dev", dev_results), ("benchmark", bench_results)]:
            for m_key, m_val in res.items():
                ci = m_val["ci"]
                writer.writerow([
                    s_name, m_key, m_val["name"],
                    round(m_val["precision"], 2), round(m_val["recall"], 2),
                    round(m_val["micro_f1"], 2), round(ci["ci_micro"][0], 2), round(ci["ci_micro"][1], 2),
                    round(m_val["macro_f1"], 2), round(ci["ci_macro"][0], 2), round(ci["ci_macro"][1], 2),
                    round(m_val["micro_f1_nopii"], 2), round(m_val["token_accuracy"], 2), round(m_val["exact_match_accuracy"], 2)
                ])

    # Save to Markdown
    md_path = reports_dir / "live_eval_real_only.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Live Evaluation Report: Real-Only Data (`v4`)\n\n")
        f.write("**Evaluation Constraint:** Evaluated on real collected text only (`v4/dev_real.jsonl` and `v4/benchmark_real.jsonl`).\n")
        f.write("**Benchmark Status:** Internal silver benchmark, real text only, 0 human-gold sentences.\n\n")

        for s_title, res in [("DEV Split (`v4/dev_real.jsonl`)", dev_results), ("BENCHMARK Split (`v4/benchmark_real.jsonl` - Internal Silver Benchmark)", bench_results)]:
            f.write(f"## {s_title}\n\n")
            f.write("| Mode | Precision | Recall | Micro F1 | 95% CI (Micro) | Macro F1 | 95% CI (Macro) | Ex-PII F1 | Token Acc | Exact-Match Sent Acc |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
            for m_key in ["model_only", "rules_only", "old_hybrid", "conservative_hybrid"]:
                m = res[m_key]
                ci = m["ci"]
                f.write(f"| **{m['name']}** | {m['precision']:.2f}% | {m['recall']:.2f}% | **{m['micro_f1']:.2f}%** | [{ci['ci_micro'][0]:.2f}, {ci['ci_micro'][1]:.2f}] | **{m['macro_f1']:.2f}%** | [{ci['ci_macro'][0]:.2f}, {ci['ci_macro'][1]:.2f}] | {m['micro_f1_nopii']:.2f}% | {m['token_accuracy']:.2f}% | {m['exact_match_accuracy']:.2f}% |\n")
            f.write("\n")

        f.write(f"## Dev Per-Class Metrics: Winning Mode (`{best_dev_mode}`)\n\n")
        f.write("| Class | Precision | Recall | F1-Score | Support | Reliability | 95% Bootstrap CI |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for c in ENTITY_TYPES:
            st = dev_results[best_dev_mode]["classes"][c]
            ci = dev_results[best_dev_mode]["ci"]["ci_classes"][c]
            f.write(f"| `{c}` | {st['precision']:.2f}% | {st['recall']:.2f}% | **{st['f1']:.2f}%** | {st['support']} | `{st['flag']}` | [{ci[0]:.2f}, {ci[1]:.2f}] |\n")

        f.write(f"\n## Dev Per-Class Metrics: Model-Only Checkpoint (`model_only`)\n\n")
        f.write("| Class | Precision | Recall | F1-Score | Support | Reliability | 95% Bootstrap CI |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for c in ENTITY_TYPES:
            st = dev_results["model_only"]["classes"][c]
            ci = dev_results["model_only"]["ci"]["ci_classes"][c]
            f.write(f"| `{c}` | {st['precision']:.2f}% | {st['recall']:.2f}% | **{st['f1']:.2f}%** | {st['support']} | `{st['flag']}` | [{ci[0]:.2f}, {ci[1]:.2f}] |\n")

        f.write("\n## Methodological Disclosure on Rule Circularity\n\n")
        f.write("Rules-only and Hybrid modes achieve near-perfect metrics on several gazetteer classes because the dev and benchmark datasets were created through silver gazetteer annotation. This creates a circular dependency where rules evaluate themselves. Only Model-Only provides an un-tainted assessment of neural generalizability.\n")

    print(f"\nSaved live evaluation reports to:\n  - {md_path}\n  - {csv_path}\n  - {json_path}", flush=True)

if __name__ == "__main__":
    main()
