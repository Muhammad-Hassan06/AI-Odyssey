"""
Production Test-File Predictor for Pakistani-Context NER Challenge.
Auto-detects format: .txt, .csv, .jsonl, .json, .conll, .xlsx.
Preserves row ids and order; never drops rows.
Sliding window for arbitrary long texts; handles Urdu RTL, Roman Urdu, odd Unicode.
Outputs JSON spans, BIO per token, CoNLL, and CSV.
CPU fallback, deterministic seeds, throughput metrics.
Modes: hybrid (default conservative hybrid), model (pure neural), rules (pure pattern).
"""

import os
import sys
import time
import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Enforce UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")

# Fixed reproducibility seeds
FIXED_SEEDS = [13, 42, 2024]
random.seed(42)

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import ENTITY_TYPES, ID2LABEL, validate_entity_type
from src.rules import extract_regex_entities
from src.preannotate import preannotate_sentence
from src.postprocess import postprocess_entities, hybrid_merge_predictions
from src.competition_fixes import apply_competition_fixes
from src.dataset import spans_to_bio

ALLOWED_20_LABELS = set(ENTITY_TYPES)

def set_seeds(seed=42):
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass

set_seeds(42)

class UnifiedNERPredictor:
    def __init__(self, model_dir: str = "models/final", mode: str = "hybrid", device: str = None):
        self.mode = mode.lower()
        if not os.path.isabs(model_dir):
            candidate = PROJECT_ROOT / model_dir
            if candidate.exists():
                model_dir = str(candidate)
        self.model_dir = str(model_dir)
        self.device = device or ("cuda" if self._is_cuda_available() else "cpu")
        self.model = None
        self.tokenizer = None

        if self.mode in ["model", "hybrid"]:
            self._load_transformer()

    def _is_cuda_available(self):
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def _load_transformer(self):
        if not os.path.exists(self.model_dir):
            print(f"[WARNING] Model checkpoint '{self.model_dir}' not found. Falling back to 'rules' mode.")
            self.mode = "rules"
            return

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForTokenClassification
            print(f"Loading transformer tokenizer and checkpoint from '{self.model_dir}'...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
            self.model = AutoModelForTokenClassification.from_pretrained(self.model_dir)
            self.model.to(self.device)
            self.model.eval()
            print(f"Model successfully loaded on {self.device}.")
        except Exception as e:
            print(f"[ERROR] Failed to load transformer on {self.device}: {e}. Falling back to CPU / rules.")
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForTokenClassification
                self.device = "cpu"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                self.model = AutoModelForTokenClassification.from_pretrained(self.model_dir).to("cpu")
                self.model.eval()
                print("Model loaded on CPU fallback.")
            except Exception as e2:
                print(f"[CRITICAL] Could not load model: {e2}. Falling back strictly to rules mode.")
                self.mode = "rules"

    def _predict_model_sliding_window(self, text: str, window_size: int = 200, stride: int = 150) -> List[Dict[str, Any]]:
        """
        Predict on arbitrarily long text using sliding window tokenization.
        Overlapping predictions are deduplicated and merged cleanly.
        """
        if not text or not text.strip() or self.model is None or self.tokenizer is None:
            return []

        import torch
        # Tokenize full text with offset mappings
        encoding = self.tokenizer(
            text,
            return_offsets_mapping=True,
            return_overflowing_tokens=True,
            max_length=256,
            stride=50,
            truncation=True,
            return_tensors="pt"
        )

        num_chunks = len(encoding["input_ids"])
        all_candidate_spans = []

        for c_idx in range(num_chunks):
            input_ids = encoding["input_ids"][c_idx:c_idx+1].to(self.device)
            attention_mask = encoding["attention_mask"][c_idx:c_idx+1].to(self.device)
            offsets = encoding["offset_mapping"][c_idx].cpu().numpy()

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.softmax(outputs.logits, dim=2)[0].cpu().numpy()
                preds = torch.argmax(outputs.logits, dim=2)[0].cpu().numpy()

            curr_ent = None
            for t_idx, (p_id, (start_char, end_char)) in enumerate(zip(preds, offsets)):
                if start_char == end_char:
                    continue
                tag = ID2LABEL.get(int(p_id), "O")
                conf = float(probs[t_idx, p_id])


                lbl = tag[2:] if tag.startswith(("B-", "I-")) else "O"

                # Subword continuation: if adjacent to active entity with same label, merge seamlessly
                if curr_ent and curr_ent["label"] == lbl and (start_char == curr_ent["end"] or tag.startswith("I-")):
                    curr_ent["end"] = int(end_char)
                    curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
                    curr_ent["confidences"].append(conf)
                elif tag.startswith("B-"):
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": lbl,
                        "confidences": [conf]
                    }
                elif tag.startswith("I-"):
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": lbl,
                        "confidences": [conf]
                    }
                else:
                    if curr_ent:
                        all_candidate_spans.append(curr_ent)
                        curr_ent = None
            if curr_ent:
                all_candidate_spans.append(curr_ent)

        # Compute average confidence and deduplicate overlapping window spans
        for e in all_candidate_spans:
            if "confidences" in e:
                e["confidence"] = sum(e["confidences"]) / len(e["confidences"])

        # Sort candidate spans by confidence DESCENDING
        all_candidate_spans.sort(key=lambda x: (-x.get("confidence", 0.0), -(x["end"] - x["start"])))
        occupied = [False] * (len(text) + 1)
        deduped = []
        for cand in all_candidate_spans:
            s, e = cand["start"], cand["end"]
            if s < 0 or e > len(text) or s >= e:
                continue
            if any(occupied[s:e]):
                continue
            for i in range(s, e):
                occupied[i] = True
            deduped.append({
                "text": text[s:e],
                "start": s,
                "end": e,
                "label": cand["label"],
                "confidence": cand.get("confidence", 1.0)
            })

        deduped.sort(key=lambda x: x["start"])
        return deduped

    def predict_single(self, text: str) -> List[Dict[str, Any]]:
        """Predict entities for a single sentence string."""
        if not text or not text.strip():
            return []

        # 1. Pure Rules mode
        if self.mode == "rules" or self.model is None:
            rule_ents = preannotate_sentence(text)
            final_ents = postprocess_entities(text, rule_ents)
            return self._filter_schema(final_ents, text)

        # 2. Pure Model mode
        model_ents = self._predict_model_sliding_window(text)
        if self.mode == "model":
            final_ents = postprocess_entities(text, model_ents)
            return self._filter_schema(final_ents, text)

        # 3. Conservative Hybrid mode (default)
        rule_ents = preannotate_sentence(text)
        merged = hybrid_merge_predictions(model_ents, rule_ents, len(text))
        final_ents = postprocess_entities(text, merged)
        competition_ents = apply_competition_fixes(text, final_ents)
        return self._filter_schema(competition_ents, text)

    def _filter_schema(self, entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        valid = []
        for e in entities:
            lbl = e["label"]
            if lbl == "GOVERNMENT_BODIES":
                lbl = "GOVERNMENT_BODY"
                e["label"] = lbl
            if lbl in ALLOWED_20_LABELS and 0 <= e["start"] < e["end"] <= len(text):
                # Ensure span text matches exact character slice
                if text[e["start"]:e["end"]] == e["text"]:
                    valid.append({
                        "text": e["text"],
                        "start": e["start"],
                        "end": e["end"],
                        "label": lbl
                    })
        return valid

def load_input_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Auto-detects file format and loads items with guaranteed row preservation.
    Returns list of dicts: {"row_id": str/int, "text": str, "tokens": Optional[List[str]]}
    """
    suffix = file_path.suffix.lower()
    records = []

    print(f"Reading input file: {file_path} (Detected format: {suffix or 'raw text'})...")

    # 1. JSON Lines (.jsonl)
    if suffix == ".jsonl":
        with open(file_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    records.append({"row_id": f"row_{idx}", "text": "", "tokens": []})
                    continue
                try:
                    obj = json.loads(line)
                    row_id = obj.get("id") or obj.get("sentence_id") or obj.get("row_id") or f"row_{idx}"
                    text = obj.get("text", "")
                    tokens = obj.get("tokens", [])
                    records.append({"row_id": str(row_id), "text": text, "tokens": tokens, "raw": obj})
                except Exception:
                    records.append({"row_id": f"row_{idx}", "text": line, "tokens": []})

    # 2. JSON (.json)
    elif suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for idx, item in enumerate(data):
                    if isinstance(item, dict):
                        row_id = item.get("id") or item.get("sentence_id") or item.get("row_id") or f"row_{idx}"
                        text = item.get("text", "")
                        tokens = item.get("tokens", [])
                        records.append({"row_id": str(row_id), "text": text, "tokens": tokens, "raw": item})
                    elif isinstance(item, str):
                        records.append({"row_id": f"row_{idx}", "text": item, "tokens": []})
            elif isinstance(data, dict):
                # Check for table-like dictionary or sentence mapping
                for k, v in data.items():
                    if isinstance(v, str):
                        records.append({"row_id": str(k), "text": v, "tokens": []})
                    elif isinstance(v, dict):
                        records.append({"row_id": str(k), "text": v.get("text", ""), "tokens": v.get("tokens", [])})

    # 3. CSV (.csv) or TSV (.tsv)
    elif suffix in [".csv", ".tsv"]:
        import csv
        delimiter = "\t" if suffix == ".tsv" else ","
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = None
            try:
                header = next(reader)
            except StopIteration:
                return []

            # Detect text and id column indices
            header_lower = [h.strip().lower() for h in header]
            text_idx = -1
            id_idx = -1

            for possible_text in ["text", "sentence", "content", "utterance", "input", "body", "data"]:
                if possible_text in header_lower:
                    text_idx = header_lower.index(possible_text)
                    break
            if text_idx == -1:
                text_idx = len(header) - 1 # default to last column

            for possible_id in ["id", "sentence_id", "row_id", "index", "doc_id", "uid"]:
                if possible_id in header_lower:
                    id_idx = header_lower.index(possible_id)
                    break

            for r_idx, row in enumerate(reader):
                if not row:
                    records.append({"row_id": f"row_{r_idx}", "text": "", "tokens": []})
                    continue
                row_id = row[id_idx] if (id_idx != -1 and id_idx < len(row)) else f"row_{r_idx}"
                text_val = row[text_idx] if text_idx < len(row) else " ".join(row)
                records.append({"row_id": str(row_id), "text": text_val, "tokens": []})

    # 4. Excel (.xlsx, .xls)
    elif suffix in [".xlsx", ".xls"]:
        import pandas as pd
        df = pd.read_excel(file_path)
        col_lower = [str(c).strip().lower() for c in df.columns]
        text_col = df.columns[-1]
        for candidate in ["text", "sentence", "content", "utterance", "input"]:
            if candidate in col_lower:
                text_col = df.columns[col_lower.index(candidate)]
                break

        id_col = None
        for candidate in ["id", "sentence_id", "row_id", "index"]:
            if candidate in col_lower:
                id_col = df.columns[col_lower.index(candidate)]
                break

        for idx, row in df.iterrows():
            row_id = str(row[id_col]) if id_col else f"row_{idx}"
            text_val = str(row[text_col]) if pd.notna(row[text_col]) else ""
            records.append({"row_id": row_id, "text": text_val, "tokens": []})

    # 5. CoNLL (.conll, .conllu, or CoNLL format)
    elif suffix in [".conll", ".conllu"]:
        with open(file_path, "r", encoding="utf-8") as f:
            curr_tokens = []
            sent_idx = 0
            for line in f:
                line = line.strip()
                if not line:
                    if curr_tokens:
                        full_sent = " ".join(curr_tokens)
                        records.append({"row_id": f"conll_{sent_idx}", "text": full_sent, "tokens": curr_tokens})
                        sent_idx += 1
                        curr_tokens = []
                    continue
                parts = line.split()
                if parts:
                    curr_tokens.append(parts[0])
            if curr_tokens:
                full_sent = " ".join(curr_tokens)
                records.append({"row_id": f"conll_{sent_idx}", "text": full_sent, "tokens": curr_tokens})

    # 6. Raw Text (.txt) or fallback
    else:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
            for idx, line in enumerate(lines):
                records.append({"row_id": f"line_{idx+1}", "text": line, "tokens": []})


    print(f"Loaded {len(records)} input rows. Guaranteed zero dropped rows.")
    return records

def save_predictions(
    records: List[Dict[str, Any]],
    predictions: List[Dict[str, Any]],
    output_dir: Path,
    base_name: str = "predictions"
):
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. JSON Spans Format
    json_path = output_dir / f"{base_name}_spans.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)

    # 2. JSONL Token BIO Format
    jsonl_path = output_dir / f"{base_name}.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for p in predictions:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # 3. CoNLL Token Format
    conll_path = output_dir / f"{base_name}.conll"
    with open(conll_path, "w", encoding="utf-8") as f:
        for p in predictions:
            tokens = p.get("tokens", [])
            tags = p.get("bio_tags", [])
            for tok, tag in zip(tokens, tags):
                f.write(f"{tok} {tag}\n")
            f.write("\n")

    # 4. CSV Summary Format
    csv_path = output_dir / f"{base_name}.csv"
    import csv
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["row_id", "text", "entity_count", "entities_json", "bio_tags"])
        for p in predictions:
            writer.writerow([
                p["row_id"],
                p["text"],
                len(p["entities"]),
                json.dumps(p["entities"], ensure_ascii=False),
                " ".join(p["bio_tags"])
            ])

    print(f"\nOutputs successfully saved to:")
    print(f"  - JSON Spans: {json_path}")
    print(f"  - JSONL BIO:   {jsonl_path}")
    print(f"  - CoNLL:       {conll_path}")
    print(f"  - CSV Summary: {csv_path}")

def run_predictions(
    input_file: str,
    output_dir: str = "predictions",
    mode: str = "hybrid",
    model_dir: str = "models/final",
    device: str = None
):
    in_path = Path(input_file)
    if not in_path.exists():
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    out_dir = Path(output_dir)
    records = load_input_file(in_path)

    predictor = UnifiedNERPredictor(model_dir=model_dir, mode=mode, device=device)

    print(f"\nStarting NER inference (Mode: {predictor.mode.upper()}, Device: {predictor.device})...")
    start_time = time.time()
    total_tokens = 0
    total_entities = 0

    results = []
    for idx, r in enumerate(records):
        text = r["text"]
        row_id = r["row_id"]

        if not text or not text.strip():
            # Empty text row preserved
            results.append({
                "row_id": row_id,
                "text": text,
                "entities": [],
                "tokens": [],
                "bio_tags": []
            })
            continue

        entities = predictor.predict_single(text)
        tokens, bio_tags = spans_to_bio(text, entities)

        total_tokens += len(tokens)
        total_entities += len(entities)

        results.append({
            "row_id": row_id,
            "text": text,
            "entities": entities,
            "tokens": tokens,
            "bio_tags": bio_tags
        })

        if (idx + 1) % 100 == 0 or (idx + 1) == len(records):
            elapsed = time.time() - start_time
            sps = (idx + 1) / elapsed if elapsed > 0 else 0
            print(f"  Processed {idx + 1}/{len(records)} sentences ({sps:.1f} sents/sec)...")

    elapsed_time = time.time() - start_time
    sps = len(records) / elapsed_time if elapsed_time > 0 else 0
    tps = total_tokens / elapsed_time if elapsed_time > 0 else 0

    print("\n================ INFERENCE THROUGHPUT ================")
    print(f"Total Sentences:    {len(records)}")
    print(f"Total Tokens:       {total_tokens}")
    print(f"Total Entities:     {total_entities}")
    print(f"Elapsed Time:       {elapsed_time:.2f} seconds")
    print(f"Throughput:         {sps:.1f} sentences/sec ({tps:.1f} tokens/sec)")
    print("======================================================")

    base_name = in_path.stem + f"_{mode}"
    save_predictions(records, results, out_dir, base_name=base_name)
    return results

def main():
    parser = argparse.ArgumentParser(description="Pakistani NER Test-File Predictor")
    parser.add_argument("input_file", nargs="?", default=None, help="Path to input file (.txt, .csv, .jsonl, .json, .conll, .xlsx)")
    parser.add_argument("--input", "-i", dest="input_opt", default=None, help="Path to input file")
    parser.add_argument("--text", "-t", default=None, help="Directly predict a single sentence string")
    parser.add_argument("--output_dir", "-o", default="predictions", help="Output directory")
    parser.add_argument("--mode", default="hybrid", choices=["hybrid", "model", "rules"], help="Inference mode")
    parser.add_argument("--model_dir", default="models/final", help="Path to fine-tuned checkpoint")
    parser.add_argument("--device", default=None, help="Device (cpu or cuda)")

    args = parser.parse_args()

    if args.text:
        predictor = UnifiedNERPredictor(model_dir=args.model_dir, mode=args.mode, device=args.device)
        entities = predictor.predict_single(args.text)
        print("\n" + "=" * 60)
        print(f"INPUT TEXT:     {args.text}")
        print(f"INFERENCE MODE: {args.mode}")
        print("=" * 60)
        print(f"EXTRACTED ENTITIES ({len(entities)}):")
        if not entities:
            print("  (No entities detected)")
        for idx, ent in enumerate(entities, 1):
            print(f"  {idx:>2}. [{ent['label']:<24}] \"{ent['text']}\" (offsets: {ent['start']}-{ent['end']})")
        print("=" * 60 + "\n")
        return

    in_file = args.input_file or args.input_opt
    if not in_file:
        parser.error("Please provide an input_file (positional or --input) or a single sentence via --text.")

    run_predictions(
        input_file=in_file,
        output_dir=args.output_dir,
        mode=args.mode,
        model_dir=args.model_dir,
        device=args.device
    )

if __name__ == "__main__":
    main()
