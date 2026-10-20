"""
Model Training Script for Pakistani-Context NER System.
Fine-tunes XLM-RoBERTa (or mDeBERTa) for token classification with subword alignment,
class-weighted cross-entropy loss for imbalance handling, and seqeval evaluation.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import ENTITY_TYPES, BIO_LABELS, LABEL2ID, ID2LABEL, set_seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train")

def load_data(file_path: str) -> List[Dict[str, Any]]:
    """Load JSONL data containing tokens and bio_tags."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def prepare_tokenized_dataset(records: List[Dict[str, Any]], tokenizer, max_length: int = 256):
    """
    Align subwords with word tokens using word_ids().
    Assigns the token label to the first subword; assigns -100 to subsequent subwords and special tokens.
    """
    import torch
    from torch.utils.data import Dataset

    class NERDataset(Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item["labels"] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    raw_tokens = [r["tokens"] for r in records]
    raw_tags = [r["bio_tags"] for r in records]

    tokenized_inputs = tokenizer(
        raw_tokens,
        is_split_into_words=True,
        max_length=max_length,
        padding="max_length",
        truncation=True
    )

    aligned_labels = []
    for i, tags in enumerate(raw_tags):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                tag = tags[word_idx] if word_idx < len(tags) else "O"
                label_ids.append(LABEL2ID.get(tag, 0))
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        aligned_labels.append(label_ids)

    return NERDataset(tokenized_inputs, aligned_labels)

def compute_class_weights(records: List[Dict[str, Any]], bio_labels: List[str], o_weight: float = 0.20):
    """
    Compute smoothed inverse frequency weights for token classification cross-entropy loss.
    Downweights background 'O' class to prevent suppression of rare entities.
    """
    import torch
    import math
    from collections import Counter

    tag_counts = Counter()
    for r in records:
        for tag in r.get("bio_tags", []):
            tag_counts[tag] += 1

    total = sum(tag_counts.values()) or 1
    weights = []
    for tag in bio_labels:
        if tag == "O":
            weights.append(o_weight)
        else:
            cnt = tag_counts.get(tag, 1)
            # smoothed inverse frequency
            w = math.sqrt(total / max(cnt, 1))
            weights.append(min(max(w, 1.0), 15.0))

    return torch.tensor(weights, dtype=torch.float)

def compute_metrics_builder():
    """Build seqeval metric computation function for Hugging Face Trainer."""
    from seqeval.metrics import f1_score, precision_score, recall_score, accuracy_score, classification_report
    import numpy as np

    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)

        true_predictions = [
            [ID2LABEL[p_id] for (p_id, l_id) in zip(prediction, label) if l_id != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [ID2LABEL[l_id] for (p_id, l_id) in zip(prediction, label) if l_id != -100]
            for prediction, label in zip(predictions, labels)
        ]

        p = precision_score(true_labels, true_predictions)
        r = recall_score(true_labels, true_predictions)
        f1 = f1_score(true_labels, true_predictions)
        acc = accuracy_score(true_labels, true_predictions)

        return {
            "precision": float(p),
            "recall": float(r),
            "f1": float(f1),
            "accuracy": float(acc)
        }
    return compute_metrics

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(base_dir, "v2_frozen", "train.jsonl")):
        default_data_dir = "v2_frozen"
    else:
        default_data_dir = "v2"

    parser = argparse.ArgumentParser(description="Fine-tune Multilingual Transformer for Pakistani NER")
    parser.add_argument("--model_name", type=str, default="xlm-roberta-base", help="Pretrained model identifier")
    parser.add_argument("--data_dir", type=str, default=default_data_dir, help="Directory containing train.jsonl and dev.jsonl")
    parser.add_argument("--train_file", type=str, default=None, help="Explicit path to train.jsonl")
    parser.add_argument("--dev_file", type=str, default=None, help="Explicit path to dev.jsonl")
    parser.add_argument("--output_dir", type=str, default="models/best_ner_model")
    parser.add_argument("--experiment_name", type=str, default="XLM-R V2 Train")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--max_length", type=int, default=128)
    parser.add_argument("--use_class_weights", action="store_true", default=False)
    parser.add_argument("--fp16", action="store_true", default=False)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_train_samples", type=int, default=None, help="Truncate train samples for fast debugging/smoke tests")
    parser.add_argument("--max_eval_samples", type=int, default=None, help="Truncate eval samples for fast debugging/smoke tests")
    args = parser.parse_args()

    set_seed(args.seed)

    # 1. Resolve dataset paths from DATA_DIR
    train_rel = args.train_file or os.path.join(args.data_dir, "train.jsonl")
    dev_rel = args.dev_file or os.path.join(args.data_dir, "dev.jsonl")
    train_path = os.path.join(base_dir, train_rel) if not os.path.isabs(train_rel) else train_rel
    dev_path = os.path.join(base_dir, dev_rel) if not os.path.isabs(dev_rel) else dev_rel

    if not os.path.exists(train_path) or os.path.getsize(train_path) == 0:
        logger.error(f"FATAL: Training file is missing or empty at {train_path}")
        sys.exit(1)
    if not os.path.exists(dev_path) or os.path.getsize(dev_path) == 0:
        logger.error(f"FATAL: Dev evaluation file is missing or empty at {dev_path}")
        sys.exit(1)

    import hashlib
    def get_file_info(p):
        with open(p, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest(), data.count(b"\n")

    train_sha, train_count = get_file_info(train_path)
    dev_sha, dev_count = get_file_info(dev_path)

    logger.info("=" * 60)
    logger.info(f"DATASET CONFIGURATION ({args.data_dir})")
    logger.info(f"Train File: {train_path} ({train_count} lines, sha256={train_sha})")
    logger.info(f"Dev File:   {dev_path} ({dev_count} lines, sha256={dev_sha})")
    logger.info("=" * 60)
    
    import torch
    import transformers
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        TrainingArguments,
        Trainer,
        DataCollatorForTokenClassification
    )

    logger.info(f"Using device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    logger.info(f"Loading tokenizer & model: {args.model_name}")

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(
        args.model_name,
        num_labels=len(BIO_LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )

    # Load records
    logger.info(f"Loading training data from {train_path}...")
    train_records = load_data(train_path)
    if args.max_train_samples:
        train_records = train_records[:args.max_train_samples]
        logger.info(f"Subsampled train records to {len(train_records)}")
    logger.info(f"Loading dev data from {dev_path}...")
    dev_records = load_data(dev_path)
    if args.max_eval_samples:
        dev_records = dev_records[:args.max_eval_samples]
        logger.info(f"Subsampled dev records to {len(dev_records)}")

    train_dataset = prepare_tokenized_dataset(train_records, tokenizer, max_length=args.max_length)
    dev_dataset = prepare_tokenized_dataset(dev_records, tokenizer, max_length=args.max_length)

    out_dir = os.path.join(base_dir, args.output_dir) if not os.path.isabs(args.output_dir) else args.output_dir
    os.makedirs(out_dir, exist_ok=True)

    # Save label mappings for standalone inference
    label_map_path = os.path.join(out_dir, "label_map.json")
    with open(label_map_path, "w", encoding="utf-8") as f:
        json.dump({"id2label": ID2LABEL, "label2id": LABEL2ID, "entities": ENTITY_TYPES}, f, indent=2)

    # Save training_run_config.json
    run_config = {
        "data_dir": args.data_dir,
        "train_file": train_path,
        "train_sha256": train_sha,
        "train_sentences": train_count,
        "dev_file": dev_path,
        "dev_sha256": dev_sha,
        "dev_sentences": dev_count,
        "model_name": args.model_name,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "max_length": args.max_length,
        "use_class_weights": args.use_class_weights,
        "seed": args.seed,
        "fp16": bool(args.fp16 and torch.cuda.is_available()),
        "package_versions": {
            "torch": torch.__version__,
            "transformers": transformers.__version__
        }
    }
    with open(os.path.join(out_dir, "training_run_config.json"), "w", encoding="utf-8") as f:
        json.dump(run_config, f, indent=2)

    # Version-safe TrainingArguments
    import inspect
    import math
    sig = inspect.signature(TrainingArguments.__init__).parameters

    total_training_steps = math.ceil(len(train_records) / args.batch_size) * args.epochs
    t_args_kwargs = {
        "output_dir": out_dir,
        "num_train_epochs": args.epochs,
        "per_device_train_batch_size": args.batch_size,
        "per_device_eval_batch_size": args.batch_size,
        "learning_rate": args.lr,
        "weight_decay": 0.01,
        "load_best_model_at_end": True,
        "metric_for_best_model": "f1",
        "greater_is_better": True,
        "logging_steps": 50,
        "fp16": args.fp16 and torch.cuda.is_available(),
        "save_total_limit": 2,
        "seed": args.seed
    }

    if "eval_strategy" in sig:
        t_args_kwargs["eval_strategy"] = "epoch"
        t_args_kwargs["save_strategy"] = "epoch"
    else:
        t_args_kwargs["evaluation_strategy"] = "epoch"
        t_args_kwargs["save_strategy"] = "epoch"

    if "warmup_ratio" in sig:
        t_args_kwargs["warmup_ratio"] = 0.10
    else:
        t_args_kwargs["warmup_steps"] = max(1, int(0.10 * total_training_steps))

    training_args = TrainingArguments(**t_args_kwargs)

    class CustomClassWeightedTrainer(Trainer):
        def __init__(self, *t_args, class_weights=None, **t_kwargs):
            super().__init__(*t_args, **t_kwargs)
            self.class_weights = class_weights

        def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
            labels = inputs.pop("labels")
            outputs = model(**inputs)
            logits = outputs.logits
            if self.class_weights is not None:
                loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device), ignore_index=-100)
            else:
                loss_fct = torch.nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
            return (loss, outputs) if return_outputs else loss

    class_weights = None
    if args.use_class_weights:
        logger.info("Computing class weights for imbalanced handling...")
        class_weights = compute_class_weights(train_records, BIO_LABELS, o_weight=0.20)
        logger.info(f"Class weights computed. Min: {class_weights.min():.2f}, Max: {class_weights.max():.2f}")

    import inspect
    trainer_kwargs = {
        "model": model,
        "args": training_args,
        "train_dataset": train_dataset,
        "eval_dataset": dev_dataset,
        "compute_metrics": compute_metrics_builder(),
        "class_weights": class_weights
    }
    if "processing_class" in inspect.signature(Trainer.__init__).parameters:
        trainer_kwargs["processing_class"] = tokenizer
    else:
        trainer_kwargs["tokenizer"] = tokenizer

    trainer = CustomClassWeightedTrainer(**trainer_kwargs)

    logger.info("Starting training loop...")
    train_result = trainer.train()

    logger.info("Evaluating on Dev set...")
    eval_metrics = trainer.evaluate()
    logger.info(f"Dev Evaluation Results: {eval_metrics}")

    # Save best model and tokenizer
    trainer.save_model(out_dir)
    tokenizer.save_pretrained(out_dir)
    logger.info(f"Saved best model checkpoint & tokenizer to {out_dir}")

    # Save metrics to reports
    reports_file = os.path.join(base_dir, "reports", "tables", "training_eval_results.json")
    os.makedirs(os.path.dirname(reports_file), exist_ok=True)
    with open(reports_file, "w", encoding="utf-8") as f:
        json.dump(eval_metrics, f, indent=2)

    # Append to reports/training_log.md
    log_md_path = os.path.join(base_dir, "reports", "training_log.md")
    os.makedirs(os.path.dirname(log_md_path), exist_ok=True)
    
    file_exists = os.path.exists(log_md_path)
    with open(log_md_path, "a", encoding="utf-8") as log_f:
        if not file_exists:
            log_f.write("# Model Training & Experiment Log (Priority 4)\n\n")
            log_f.write("| Experiment Name | Model Backbone | Train Split | Dev Split | Epochs | Class Weights | Dev Precision | Dev Recall | Dev F1 | Dev Accuracy |\n")
            log_f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        dev_p = eval_metrics.get("eval_precision", 0.0) * 100
        dev_r = eval_metrics.get("eval_recall", 0.0) * 100
        dev_f1 = eval_metrics.get("eval_f1", 0.0) * 100
        dev_acc = eval_metrics.get("eval_accuracy", 0.0) * 100
        cw_str = "Yes (smoothed)" if args.use_class_weights else "No (uniform)"
        
        log_f.write(f"| {args.experiment_name} | {args.model_name} | {args.train_file} | {args.dev_file} | {args.epochs} | {cw_str} | {dev_p:.2f}% | {dev_r:.2f}% | {dev_f1:.2f}% | {dev_acc:.2f}% |\n")
    logger.info(f"Updated training log at {log_md_path}")

if __name__ == "__main__":
    main()

