"""
Comprehensive Three-Mode Evaluation with Strict IOB2 Seqeval & 1,000-Document Bootstrap CIs.
Evaluates:
(a) Model-only (smoke-test checkpoint)
(b) Rules-only (regex + gazetteers, no neural model)
(c) Hybrid (current pipeline)
Across v2/dev.jsonl and v2/benchmark.jsonl (read-only).
Optimized with batch tokenization and shared model inference caching for maximum throughput.
"""

import os
import sys
import json
import csv
import numpy as np
from collections import defaultdict
from seqeval.metrics import classification_report
from seqeval.scheme import IOB2

# Add ner-pk root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants import ENTITY_TYPES, BIO_LABELS, ID2LABEL, validate_entity_type, set_seed
from src.rules import extract_regex_entities
from src.preannotate import preannotate_sentence
from src.postprocess import postprocess_entities, hybrid_merge_predictions
from src.dataset import spans_to_bio

set_seed(42)

def remove_phone_id_tags(bio_seqs):
    """Replace PHONE_NUMBER and ID_NUMBER tags with O for non-synthetic evaluation."""
    clean_seqs = []
    for seq in bio_seqs:
        new_seq = []
        for tag in seq:
            if "PHONE_NUMBER" in tag or "ID_NUMBER" in tag:
                new_seq.append("O")
            else:
                new_seq.append(tag)
        clean_seqs.append(new_seq)
    return clean_seqs

def compute_metrics_dict(gold_bios, pred_bios):
    """Compute strict IOB2 metrics: micro-F1, macro-F1, per-class F1/P/R/support, and micro-F1 ex-PII."""
    report = classification_report(
        gold_bios,
        pred_bios,
        mode="strict",
        scheme=IOB2,
        output_dict=True,
        zero_division=0
    )
    
    gold_no_pii = remove_phone_id_tags(gold_bios)
    pred_no_pii = remove_phone_id_tags(pred_bios)
    report_no_pii = classification_report(
        gold_no_pii,
        pred_no_pii,
        mode="strict",
        scheme=IOB2,
        output_dict=True,
        zero_division=0
    )
    micro_f1_no_pii = float(report_no_pii["micro avg"]["f1-score"])

    class_metrics = {}
    macro_f1s = []
    for c in ENTITY_TYPES:
        if c in report:
            p = float(report[c]["precision"])
            r = float(report[c]["recall"])
            f1 = float(report[c]["f1-score"])
            sup = int(report[c]["support"])
            class_metrics[c] = {"precision": p, "recall": r, "f1": f1, "support": sup}
            macro_f1s.append(f1)
        else:
            class_metrics[c] = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 0}
            macro_f1s.append(0.0)

    return {
        "micro_precision": float(report["micro avg"]["precision"]),
        "micro_recall": float(report["micro avg"]["recall"]),
        "micro_f1": float(report["micro avg"]["f1-score"]),
        "macro_f1": float(np.mean(macro_f1s)),
        "micro_f1_no_pii": micro_f1_no_pii,
        "classes": class_metrics
    }

def run_bootstrap_ci(gold_bios, pred_bios, doc_to_indices, n_resamples=1000, seed=42):
    """Perform document-level bootstrap resampling (1,000 rounds) to estimate 95% CIs."""
    rng = np.random.RandomState(seed)
    doc_keys = list(doc_to_indices.keys())
    n_docs = len(doc_keys)

    micro_f1_list = []
    macro_f1_list = []
    micro_no_pii_list = []
    per_class_f1_list = {c: [] for c in ENTITY_TYPES}

    for _ in range(n_resamples):
        sampled_docs = rng.choice(doc_keys, size=n_docs, replace=True)
        sampled_indices = []
        for d in sampled_docs:
            sampled_indices.extend(doc_to_indices[d])
        
        s_gold = [gold_bios[i] for i in sampled_indices]
        s_pred = [pred_bios[i] for i in sampled_indices]
        
        s_rep = classification_report(s_gold, s_pred, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)
        micro_f1_list.append(float(s_rep["micro avg"]["f1-score"]))
        
        s_c_f1s = []
        for c in ENTITY_TYPES:
            f1_c = float(s_rep[c]["f1-score"]) if c in s_rep else 0.0
            per_class_f1_list[c].append(f1_c)
            s_c_f1s.append(f1_c)
        macro_f1_list.append(float(np.mean(s_c_f1s)))

        s_gold_nopii = remove_phone_id_tags(s_gold)
        s_pred_nopii = remove_phone_id_tags(s_pred)
        s_rep_nopii = classification_report(s_gold_nopii, s_pred_nopii, mode="strict", scheme=IOB2, output_dict=True, zero_division=0)
        micro_no_pii_list.append(float(s_rep_nopii["micro avg"]["f1-score"]))

    ci_micro = (float(np.percentile(micro_f1_list, 2.5)), float(np.percentile(micro_f1_list, 97.5)))
    ci_macro = (float(np.percentile(macro_f1_list, 2.5)), float(np.percentile(macro_f1_list, 97.5)))
    ci_no_pii = (float(np.percentile(micro_no_pii_list, 2.5)), float(np.percentile(micro_no_pii_list, 97.5)))
    ci_per_class = {c: (float(np.percentile(per_class_f1_list[c], 2.5)), float(np.percentile(per_class_f1_list[c], 97.5))) for c in ENTITY_TYPES}

    return {
        "ci_micro": ci_micro,
        "ci_macro": ci_macro,
        "ci_no_pii": ci_no_pii,
        "ci_per_class": ci_per_class
    }

def batch_predict_neural_model(texts, model_dir, batch_size=32):
    """Run batched inference through neural checkpoint on CPU."""
    if not model_dir or not os.path.exists(model_dir):
        return [[] for _ in texts]
        
    import torch
    from transformers import AutoTokenizer, AutoModelForTokenClassification
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir).to(device)
    model.eval()
    
    all_entities = []
    total = len(texts)
    
    for i in range(0, total, batch_size):
        batch_texts = texts[i:i+batch_size]
        encoding = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_offsets_mapping=True,
            return_tensors="pt"
        )
        offset_mappings = encoding["offset_mapping"].cpu().numpy()
        input_ids = encoding["input_ids"].to(device)
        attention_mask = encoding["attention_mask"].to(device)
        
        with torch.no_grad():
            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
            preds = torch.argmax(logits, dim=2).cpu().numpy()
            
        for b_idx, text in enumerate(batch_texts):
            curr_ent = None
            sent_entities = []
            for p_id, (start_char, end_char) in zip(preds[b_idx], offset_mappings[b_idx]):
                if start_char == end_char:
                    continue
                tag = ID2LABEL.get(int(p_id), "O")
                if tag.startswith("B-"):
                    if curr_ent:
                        sent_entities.append(curr_ent)
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": tag[2:]
                    }
                elif tag.startswith("I-"):
                    lbl = tag[2:]
                    if curr_ent and curr_ent["label"] == lbl:
                        curr_ent["end"] = int(end_char)
                        curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
                    else:
                        if curr_ent:
                            sent_entities.append(curr_ent)
                        curr_ent = {
                            "text": text[start_char:end_char],
                            "start": int(start_char),
                            "end": int(end_char),
                            "label": lbl
                        }
                else:
                    if curr_ent:
                        sent_entities.append(curr_ent)
                        curr_ent = None
            if curr_ent:
                sent_entities.append(curr_ent)
                
            valid = [e for e in sent_entities if validate_entity_type(e["label"]) and e["start"] < e["end"] and text[e["start"]:e["end"]] == e["text"]]
            all_entities.append(valid)
            
        if (i // batch_size + 1) % 10 == 0 or (i + batch_size) >= total:
            print(f"Neural model predicted {min(i + batch_size, total)}/{total} sentences...", flush=True)
            
    return all_entities

def evaluate_split(split_name, split_path, model_dir):
    print(f"\n==========================================", flush=True)
    print(f"Evaluating Split: {split_name} ({split_path})", flush=True)
    print(f"==========================================", flush=True)
    
    with open(split_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    
    texts = [r["text"] for r in records]
    gold_bios = [r["bio_tags"] for r in records]

    # Map documents to sentence indices
    doc_to_indices = defaultdict(list)
    for idx, r in enumerate(records):
        doc_key = r.get("doc_id") or r.get("sentence_id") or f"sent_{idx}"
        doc_to_indices[doc_key].append(idx)
        
    # 1. Batched Neural Model predictions
    print(f"Generating model-only predictions (batched)...", flush=True)
    model_ents_list = batch_predict_neural_model(texts, model_dir, batch_size=32)
    model_bios = [spans_to_bio(t, ents)[1] for t, ents in zip(texts, model_ents_list)]

    # 2. Rules-only predictions
    print(f"Generating rules-only predictions...", flush=True)
    rules_ents_list = []
    for t in texts:
        r_ents = preannotate_sentence(t)
        f_ents = postprocess_entities(t, r_ents)
        v_ents = [e for e in f_ents if validate_entity_type(e["label"])]
        rules_ents_list.append(v_ents)
    rules_bios = [spans_to_bio(t, ents)[1] for t, ents in zip(texts, rules_ents_list)]

    # 3. Hybrid predictions (merge cached model + rules)
    print(f"Generating hybrid predictions...", flush=True)
    hybrid_ents_list = []
    for t, m_ents, r_ents in zip(texts, model_ents_list, rules_ents_list):
        merged = hybrid_merge_predictions(m_ents, r_ents, len(t))
        f_ents = postprocess_entities(t, merged)
        v_ents = [e for e in f_ents if validate_entity_type(e["label"]) and e["start"] < e["end"] and t[e["start"]:e["end"]] == e["text"]]
        hybrid_ents_list.append(v_ents)
    hybrid_bios = [spans_to_bio(t, ents)[1] for t, ents in zip(texts, hybrid_ents_list)]

    split_results = {}
    modes = [
        ("model", "model-only (smoke-test checkpoint)", model_bios),
        ("rules", "rules-only", rules_bios),
        ("hybrid", "hybrid", hybrid_bios)
    ]

    for mode_key, mode_label, pred_bios in modes:
        print(f"\nComputing metrics and bootstrap CIs for {mode_label}...", flush=True)
        metrics = compute_metrics_dict(gold_bios, pred_bios)
        cis = run_bootstrap_ci(gold_bios, pred_bios, doc_to_indices, n_resamples=1000)
        metrics["cis"] = cis
        metrics["mode_label"] = mode_label
        split_results[mode_key] = metrics
        
        print(f"Results for {mode_label}:", flush=True)
        print(f"  Micro F1: {metrics['micro_f1']*100:.2f}% (95% CI: [{cis['ci_micro'][0]*100:.2f}%, {cis['ci_micro'][1]*100:.2f}%])", flush=True)
        print(f"  Macro F1: {metrics['macro_f1']*100:.2f}% (95% CI: [{cis['ci_macro'][0]*100:.2f}%, {cis['ci_macro'][1]*100:.2f}%])", flush=True)
        print(f"  Micro F1 (Excl. PHONE/ID): {metrics['micro_f1_no_pii']*100:.2f}% (95% CI: [{cis['ci_no_pii'][0]*100:.2f}%, {cis['ci_no_pii'][1]*100:.2f}%])", flush=True)

    return split_results

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dev_path = os.path.join(base_dir, "v2", "dev.jsonl")
    bench_path = os.path.join(base_dir, "v2", "benchmark.jsonl")
    model_dir = os.path.join(base_dir, "models", "smoke_test_model")
    
    out_dir = os.path.join(base_dir, "reports", "verification")
    os.makedirs(out_dir, exist_ok=True)
    
    all_results = {
        "dev": evaluate_split("dev", dev_path, model_dir),
        "benchmark": evaluate_split("benchmark", bench_path, model_dir)
    }

    # Save to CSV
    csv_path = os.path.join(out_dir, "three_mode_eval.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "split", "mode", "entity_class", "precision", "recall", "f1",
            "ci_95_lower", "ci_95_upper", "support", "reliability_flag"
        ])
        
        for split_key, split_data in all_results.items():
            for mode_key, mdata in split_data.items():
                mode_lbl = mdata["mode_label"]
                writer.writerow([
                    split_key, mode_lbl, "OVERALL_MICRO",
                    f"{mdata['micro_precision']*100:.2f}",
                    f"{mdata['micro_recall']*100:.2f}",
                    f"{mdata['micro_f1']*100:.2f}",
                    f"{mdata['cis']['ci_micro'][0]*100:.2f}",
                    f"{mdata['cis']['ci_micro'][1]*100:.2f}",
                    sum(c["support"] for c in mdata["classes"].values()),
                    "RELIABLE"
                ])
                writer.writerow([
                    split_key, mode_lbl, "OVERALL_MACRO",
                    "-", "-",
                    f"{mdata['macro_f1']*100:.2f}",
                    f"{mdata['cis']['ci_macro'][0]*100:.2f}",
                    f"{mdata['cis']['ci_macro'][1]*100:.2f}",
                    sum(c["support"] for c in mdata["classes"].values()),
                    "RELIABLE"
                ])
                writer.writerow([
                    split_key, mode_lbl, "MICRO_EXCLUDING_PHONE_AND_ID",
                    "-", "-",
                    f"{mdata['micro_f1_no_pii']*100:.2f}",
                    f"{mdata['cis']['ci_no_pii'][0]*100:.2f}",
                    f"{mdata['cis']['ci_no_pii'][1]*100:.2f}",
                    "-",
                    "RELIABLE"
                ])
                for c in ENTITY_TYPES:
                    cdata = mdata["classes"][c]
                    sup = cdata["support"]
                    rel = "UNRELIABLE (support < 30)" if sup < 30 else "RELIABLE"
                    ci_l, ci_u = mdata["cis"]["ci_per_class"][c]
                    writer.writerow([
                        split_key, mode_lbl, c,
                        f"{cdata['precision']*100:.2f}",
                        f"{cdata['recall']*100:.2f}",
                        f"{cdata['f1']*100:.2f}",
                        f"{ci_l*100:.2f}",
                        f"{ci_u*100:.2f}",
                        sup,
                        rel
                    ])
    print(f"\nSaved CSV report to {csv_path}", flush=True)

    # Save to Markdown
    md_path = os.path.join(out_dir, "three_mode_eval.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Three-Mode Verification Evaluation Report\n\n")
        f.write("**Date:** 2026-10-21  \n")
        f.write("**Evaluation Harness:** Strict IOB2 Seqeval with 1,000-Document Bootstrap 95% Confidence Intervals  \n")
        f.write("**Note on Model-Only Evaluation:** The model-only numbers evaluate `models/smoke_test_model/` (CPU smoke-test, 4 steps, 16 samples, eval_f1: 0.0). No full neural model exists yet.\n\n")

        for split_key in ["dev", "benchmark"]:
            split_data = all_results[split_key]
            f.write(f"## {split_key.upper()} Split (Read-Only Evaluation)\n\n")
            f.write("### High-Level Summary Table\n\n")
            f.write("| Mode | Strict Micro-F1 (95% CI) | Strict Macro-F1 (95% CI) | Micro-F1 Excl. PHONE & ID (95% CI) |\n")
            f.write("| :--- | :---: | :---: | :---: |\n")
            for mode_key in ["model", "rules", "hybrid"]:
                m = split_data[mode_key]
                lbl = m["mode_label"]
                ci_mic = m["cis"]["ci_micro"]
                ci_mac = m["cis"]["ci_macro"]
                ci_nopii = m["cis"]["ci_no_pii"]
                f.write(f"| **{lbl}** | {m['micro_f1']*100:.2f}% [{ci_mic[0]*100:.2f}%, {ci_mic[1]*100:.2f}%] | {m['macro_f1']*100:.2f}% [{ci_mac[0]*100:.2f}%, {ci_mac[1]*100:.2f}%] | {m['micro_f1_no_pii']*100:.2f}% [{ci_nopii[0]*100:.2f}%, {ci_nopii[1]*100:.2f}%] |\n")
            f.write("\n")

            f.write("### Detailed Per-Class Breakdown (Rules-Only vs Hybrid vs Model-Only)\n\n")
            f.write("| Entity Class | Support | Status (<30) | Rules P / R / F1 (95% CI) | Hybrid P / R / F1 (95% CI) | Model-Only (Smoke-Test) F1 |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
            for c in ENTITY_TYPES:
                r_c = split_data["rules"]["classes"][c]
                h_c = split_data["hybrid"]["classes"][c]
                m_c = split_data["model"]["classes"][c]
                sup = r_c["support"]
                status = "⚠️ **UNRELIABLE**" if sup < 30 else "OK"
                r_ci = split_data["rules"]["cis"]["ci_per_class"][c]
                h_ci = split_data["hybrid"]["cis"]["ci_per_class"][c]
                
                rules_str = f"{r_c['precision']*100:.1f} / {r_c['recall']*100:.1f} / **{r_c['f1']*100:.1f}%** [{r_ci[0]*100:.1f}%, {r_ci[1]*100:.1f}%]"
                hybrid_str = f"{h_c['precision']*100:.1f} / {h_c['recall']*100:.1f} / **{h_c['f1']*100:.1f}%** [{h_ci[0]*100:.1f}%, {h_ci[1]*100:.1f}%]"
                model_str = f"{m_c['f1']*100:.1f}%"
                f.write(f"| `{c}` | {sup} | {status} | {rules_str} | {hybrid_str} | {model_str} |\n")
            f.write("\n---\n\n")

    print(f"Saved Markdown report to {md_path}", flush=True)

if __name__ == "__main__":
    main()
