"""
Unified Inference Engine for Pakistani-Context NER System.
Provides a single robust predict(text) function, format converters (character spans,
token BIO tags, CoNLL, JSON), and strict validation against the exact 20 entity classes.
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any, Union

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES, BIO_LABELS, validate_entity_type
from src.rules import extract_regex_entities
from src.preannotate import preannotate_sentence
from src.postprocess import postprocess_entities, hybrid_merge_predictions
from src.dataset import spans_to_bio

class PakistaniNERPredictor:
    """
    Unified predictor supporting:
    1. Pure rule/gazetteer mode
    2. Fine-tuned Neural Transformer mode
    3. Hybrid ensemble mode (Model + Rules + Gazetteers)
    """
    def __init__(self, model_dir: str = None, mode: str = "hybrid"):
        self.mode = mode
        self.model_dir = model_dir
        self.model = None
        self.tokenizer = None
        self.device = "cpu"

        if model_dir and os.path.exists(model_dir) and mode in ["model", "hybrid"]:
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForTokenClassification
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
                self.model = AutoModelForTokenClassification.from_pretrained(model_dir).to(self.device)
                self.model.eval()
            except (ImportError, OSError, Exception) as e:
                print(f"Warning: Could not load transformer model from {model_dir}: {e}. Falling back to rule mode.")
                self.mode = "rules"

    def predict(self, text: str) -> List[Dict[str, Any]]:
        """
        Main prediction API.
        Takes raw string input, returns list of valid entity spans:
        [{"text": str, "start": int, "end": int, "label": str}]
        """
        if not text or not text.strip():
            return []

        # 1. Pure Model mode (no rules, no gazetteers, no post-processing)
        if self.mode == "model":
            if self.model is None or self.tokenizer is None:
                return []
            model_entities = []
            import torch
            from src.constants import ID2LABEL
            encoding = self.tokenizer(
                text,
                return_offsets_mapping=True,
                return_tensors="pt",
                truncation=True,
                max_length=256
            )
            offset_mapping = encoding["offset_mapping"][0].cpu().numpy()
            input_ids = encoding["input_ids"].to(self.device)
            attention_mask = encoding["attention_mask"].to(self.device)

            with torch.no_grad():
                logits = self.model(input_ids=input_ids, attention_mask=attention_mask).logits
                preds = torch.argmax(logits, dim=2)[0].cpu().numpy()

            curr_ent = None
            for p_id, (start_char, end_char) in zip(preds, offset_mapping):
                if start_char == end_char:
                    continue
                tag = ID2LABEL.get(int(p_id), "O")
                if tag.startswith("B-"):
                    if curr_ent:
                        model_entities.append(curr_ent)
                    lbl = tag[2:]
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": lbl
                    }
                elif tag.startswith("I-"):
                    lbl = tag[2:]
                    if curr_ent and curr_ent["label"] == lbl:
                        curr_ent["end"] = int(end_char)
                        curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
                    else:
                        if curr_ent:
                            model_entities.append(curr_ent)
                        curr_ent = {
                            "text": text[start_char:end_char],
                            "start": int(start_char),
                            "end": int(end_char),
                            "label": lbl
                        }
                else:
                    if curr_ent:
                        model_entities.append(curr_ent)
                        curr_ent = None
            if curr_ent:
                model_entities.append(curr_ent)

            valid_entities = []
            for e in model_entities:
                if validate_entity_type(e["label"]) and e["start"] < e["end"]:
                    if text[e["start"]:e["end"]] == e["text"]:
                        valid_entities.append(e)
            return valid_entities

        # 2. Rule & Gazetteer entities
        rule_entities = preannotate_sentence(text)

        # 3. Pure rule mode
        if self.mode == "rules" or self.model is None:
            final_entities = postprocess_entities(text, rule_entities)
            # Validate strict 20 labels
            return [e for e in final_entities if validate_entity_type(e["label"])]

        # 3. Model prediction (if loaded)
        model_entities = []
        if self.model is not None and self.tokenizer is not None:
            import torch
            from src.constants import ID2LABEL
            encoding = self.tokenizer(
                text,
                return_offsets_mapping=True,
                return_tensors="pt",
                truncation=True,
                max_length=256
            )
            offset_mapping = encoding["offset_mapping"][0].cpu().numpy()
            input_ids = encoding["input_ids"].to(self.device)
            attention_mask = encoding["attention_mask"].to(self.device)

            with torch.no_grad():
                logits = self.model(input_ids=input_ids, attention_mask=attention_mask).logits
                probs = torch.softmax(logits, dim=2)[0].cpu().numpy()
                preds = torch.argmax(logits, dim=2)[0].cpu().numpy()

            curr_ent = None
            for t_idx, (p_id, (start_char, end_char)) in enumerate(zip(preds, offset_mapping)):
                if start_char == end_char:
                    continue
                tag = ID2LABEL.get(int(p_id), "O")
                conf = float(probs[t_idx, p_id])

                if tag.startswith("B-"):
                    if curr_ent:
                        model_entities.append(curr_ent)
                    lbl = tag[2:]
                    curr_ent = {
                        "text": text[start_char:end_char],
                        "start": int(start_char),
                        "end": int(end_char),
                        "label": lbl,
                        "confidences": [conf]
                    }
                elif tag.startswith("I-"):
                    lbl = tag[2:]
                    if curr_ent and curr_ent["label"] == lbl:
                        curr_ent["end"] = int(end_char)
                        curr_ent["text"] = text[curr_ent["start"]:int(end_char)]
                        curr_ent["confidences"].append(conf)
                    else:
                        if curr_ent:
                            model_entities.append(curr_ent)
                        curr_ent = {
                            "text": text[start_char:end_char],
                            "start": int(start_char),
                            "end": int(end_char),
                            "label": lbl,
                            "confidences": [conf]
                        }
                else:
                    if curr_ent:
                        model_entities.append(curr_ent)
                        curr_ent = None
            if curr_ent:
                model_entities.append(curr_ent)

            for e in model_entities:
                if "confidences" in e:
                    e["confidence"] = sum(e["confidences"]) / len(e["confidences"])

        # 4. Hybrid Merge & Postprocess
        merged = hybrid_merge_predictions(model_entities, rule_entities, len(text))
        final_entities = postprocess_entities(text, merged)

        # Strict validation: never emit any label outside the exact 20
        valid_entities = []
        for e in final_entities:
            lbl = e["label"]
            if lbl == "GOVERNMENT_BODIES":
                lbl = "GOVERNMENT_BODY"
                e["label"] = lbl
            if validate_entity_type(lbl) and e["start"] < e["end"]:
                # Ensure span matches text exactly
                if text[e["start"]:e["end"]] == e["text"]:
                    valid_entities.append(e)

        return valid_entities

    def predict_formatted(self, text: str, output_format: str = "spans") -> Any:
        """
        Configurable output layer for hidden-benchmark readiness:
        - 'spans': [{"text": ..., "start": ..., "end": ..., "label": ...}]
        - 'bio': (tokens, bio_tags)
        - 'conll': str formatted in CoNLL format (token \t tag)
        - 'json': JSON string
        """
        spans = self.predict(text)

        if output_format == "spans":
            return spans
        elif output_format == "bio":
            tokens, tags = spans_to_bio(text, spans)
            return {"tokens": tokens, "bio_tags": tags}
        elif output_format == "conll":
            tokens, tags = spans_to_bio(text, spans)
            lines = [f"{tok}\t{tag}" for tok, tag in zip(tokens, tags)]
            return "\n".join(lines)
        elif output_format == "json":
            return json.dumps({"text": text, "entities": spans}, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unknown output format: {output_format}")

# Global default predictor instance
_DEFAULT_PREDICTOR = PakistaniNERPredictor(mode="rules")

def predict(text: str) -> List[Dict[str, Any]]:
    """Standalone predict function conforming strictly to competition spec."""
    return _DEFAULT_PREDICTOR.predict(text)

def main():
    parser = argparse.ArgumentParser(description="CLI for Pakistani NER Prediction")
    parser.add_argument("--text", type=str, help="Single input sentence")
    parser.add_argument("--input_file", type=str, help="Input text or JSONL file")
    parser.add_argument("--output_file", type=str, help="Output destination file")
    parser.add_argument("--format", type=str, default="spans", choices=["spans", "bio", "conll", "json"])
    parser.add_argument("--benchmark_test", action="store_true", help="Run tricky benchmark string tests")
    args = parser.parse_args()

    predictor = PakistaniNERPredictor(mode="rules")

    if args.benchmark_test:
        tricky_strings = [
            "Candidate with CNIC 42101-1234567-1 contacted helpline +92 300 1234567.",
            "The budget of Rs 1.5 billion was approved with a 5.2 per cent discount on Jan 5, 2025.",
            "Petitioner approached Supreme Court of Pakistan under Article 63-A of the Constitution.",
            "Match scheduled in Karachi between Karachi Kings and Lahore Qalandars at 11:45 PM.",
            "LUMS announced admissions in Lahore with PKR 500,000 fee for foreign candidates.",
            "امیدوار کا شناختی کارڈ نمبر ۴۲۱۰۱-۱۲۳۴۵۶۷-۱ ہے اور رابطہ نمبر ۰۳۰۰-۱۲۳۴۵۶۷ ہے۔",
            "سپریم کورٹ آف پاکستان نے اسلام آباد میں 26ویں آئینی ترمیم کے تحت سماعت شام ۶ بجے تک ملتوی کر دی۔",
            "حکومت نے 15 کروڑ روپے کی لاگت سے لاہور قلندرز اور کراچی کنگز کے میچ کا انعقاد 14 اگست 2025 کو کیا۔"
        ]
        print("\n--- TRICKY HIDDEN BENCHMARK STRINGS TEST ---")
        for s in tricky_strings:
            start_t = time.time()
            res = predictor.predict(s)
            elapsed_ms = (time.time() - start_t) * 1000
            print(f"\nText: {s}")
            print(f"Latency: {elapsed_ms:.2f} ms")
            print("Extracted Entities:")
            for ent in res:
                print(f"  [{ent['label']:22s}] '{ent['text']}' ({ent['start']}:{ent['end']})")
        print("\n--------------------------------------------\n")
        return

    if args.text:
        out = predictor.predict_formatted(args.text, output_format=args.format)
        if isinstance(out, str):
            print(out)
        else:
            print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
