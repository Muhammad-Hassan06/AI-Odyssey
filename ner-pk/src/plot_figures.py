"""
Plotting Script for Pakistani-Context NER System.
Generates:
1. Per-Entity F1 Score bar chart.
2. 21x21 Confusion Matrix heatmap.
3. Architecture comparison summary chart.
"""

import os
import sys
import re
import csv
import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "reports", "figures")
TABLES_DIR = os.path.join(os.path.dirname(__file__), "..", "reports", "tables")
os.makedirs(FIGURES_DIR, exist_ok=True)

def load_benchmark_f1() -> dict:
    bench_md = os.path.join(TABLES_DIR, "evaluation_metrics_benchmark.md")
    f1_dict = {}
    if not os.path.exists(bench_md):
        return f1_dict

    with open(bench_md, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Match line with format: ENTITY_NAME  p  r  f1  support
            m = re.match(r"^([A-Z_]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+(\d+)$", line)
            if m:
                label, p, r, f1, support = m.groups()
                if label not in ["MICRO", "MACRO", "WEIGHTED"]:
                    f1_dict[label] = float(f1)
    return f1_dict

def plot_per_entity_f1():
    bench_f1 = load_benchmark_f1()
    if not bench_f1:
        print("Warning: No benchmark F1 scores parsed.")
        return

    labels = sorted(list(bench_f1.keys()))
    scores = [bench_f1[k] * 100 for k in labels]

    plt.figure(figsize=(15, 6))
    bars = plt.bar(labels, scores, color="#0284c7", edgecolor="#0369a1", alpha=0.9, width=0.6)

    # Highlight 100% scores in emerald green
    for bar, score in zip(bars, scores):
        if score >= 99.9:
            bar.set_color("#059669")
        elif score < 60.0:
            bar.set_color("#f59e0b")

    plt.axhline(94.60, color="#dc2626", linestyle="--", linewidth=1.8, label="Benchmark Overall Micro F1 (94.60%)")
    plt.ylabel("Strict IOB2 F1 Score (%)", fontsize=12, fontweight="bold")
    plt.title("Pakistani-Context NER: Strict IOB2 Entity F1 Scores on Held-Out Benchmark", fontsize=14, fontweight="bold", pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=9, fontweight="bold")
    plt.ylim(0, 115)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    
    # Annotate bar values
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f"{height:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.legend(fontsize=11, loc="lower right")
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "per_entity_f1.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved {out_path}")

def plot_confusion_matrix_heatmap():
    cm_csv = os.path.join(TABLES_DIR, "confusion_matrix_benchmark.csv")
    if not os.path.exists(cm_csv):
        return

    with open(cm_csv, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        header = reader[0][1:]
        rows = [r[0] for r in reader[1:]]
        data = np.array([[float(val) for val in r[1:]] for r in reader[1:]])

    # Normalize row-wise for percentage visualization
    row_sums = data.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    norm_data = data / row_sums

    plt.figure(figsize=(13, 11))
    im = plt.imshow(norm_data, cmap="Blues", interpolation="nearest")
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.title("Normalized Confusion Matrix: Pakistani NER Benchmark Evaluation", fontsize=14, fontweight="bold", pad=12)
    plt.xticks(range(len(header)), header, rotation=90, fontsize=8, fontweight="bold")
    plt.yticks(range(len(rows)), rows, fontsize=8, fontweight="bold")
    plt.xlabel("Predicted Class", fontsize=11, fontweight="bold")
    plt.ylabel("True Gold Class", fontsize=11, fontweight="bold")
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "confusion_matrix.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved {out_path}")

if __name__ == "__main__":
    plot_per_entity_f1()
    plot_confusion_matrix_heatmap()
