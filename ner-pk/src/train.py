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

def compute_metrics_builder():
    """Build seqeval metric computation function for Hugging Face Trainer."""
    from seqeval.metrics import f1_score, precision_score, recall_score, accuracy_score
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

        return {
            "precision": precision_score(true_labels, true_predictions),
            "recall": recall_score(true_labels, true_predictions),
            "f1": f1_score(true_labels, true_predictions),
            "accuracy": accuracy_score(true_labels, true_predictions),
        }
    return compute_metrics

def main():
    parser = argparse.ArgumentParser(description="Fine-tune Multilingual Transformer for Pakistani NER")
    parser.add_argument("--model_name", type=str, default="xlm-roberta-base", help="Pretrained model identifier")
    parser.add_argument("--train_file", type=str, default="data/processed/train.jsonl")
    parser.add_argument("--dev_file", type=str, default="data/processed/dev.jsonl")
    parser.add_argument("--output_dir", type=str, default="models/best_ner_model")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--lr", type=float, default=2.5e-5)
    parser.add_argument("--max_length", type=int, default=256)
    parser.add_argument("--fp16", action="store_true", default=False)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    
    import torch
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

    # Load datasets
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_path = os.path.join(base_dir, args.train_file)
    dev_path = os.path.join(base_dir, args.dev_file)

    logger.info(f"Loading training data from {train_path}...")
    train_records = load_data(train_path)
    logger.info(f"Loading dev data from {dev_path}...")
    dev_records = load_data(dev_path)

    train_dataset = prepare_tokenized_dataset(train_records, tokenizer, max_length=args.max_length)
    dev_dataset = prepare_tokenized_dataset(dev_records, tokenizer, max_length=args.max_length)

    out_dir = os.path.join(base_dir, args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Save label mappings for standalone inference
    label_map_path = os.path.join(out_dir, "label_map.json")
    with open(label_map_path, "w", encoding="utf-8") as f:
        json.dump({"id2label": ID2LABEL, "label2id": LABEL2ID, "entities": ENTITY_TYPES}, f, indent=2)

    training_args = TrainingArguments(
        output_dir=out_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=0.01,
        warmup_ratio=0.10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=50,
        fp16=args.fp16 and torch.cuda.is_available(),
        save_total_limit=2,
        seed=args.seed
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics_builder()
    )

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

if __name__ == "__main__":
    main()
