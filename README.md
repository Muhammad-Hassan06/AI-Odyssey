# AI-Odyssey: Pakistani-Context Named Entity Recognition (NER) System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Seqeval F1: 94.31%](https://img.shields.io/badge/Strict_Micro_F1-94.31%25-brightgreen.svg)]()
[![Bilingual: EN + UR](https://img.shields.io/badge/Languages-English%20%7C%20Urdu-orange.svg)]()

> **TechFest NER Challenge: Dory's Data Dive (Round 2)**  
> An industrial-grade, hybrid Named Entity Recognition system engineered specifically for Pakistani civic, legal, financial, and sports discourse across **English**, **Urdu Script**, and **Roman Urdu**.

---

## 🌟 Key Highlights & Performance

- **Exact 20-Class Schema Compliance:** Strict extraction across the competition's 20 exact entity classes.
- **Top Benchmark Performance:** Evaluated on an untouched, held-out benchmark of 935 sentences (1,829 entities) isolated at the document level:
  - **Strict IOB2 Micro Precision:** **92.26%**
  - **Strict IOB2 Micro Recall:** **96.45%**
  - **Strict IOB2 Micro F1 Score:** **94.31%**
  - **Relaxed / Partial Overlap F1 Score:** **95.86%**
- **First-Class Urdu NER Extension (Major Ranking Advantage):**
  - Unicode NFKC standardisation & Arabic-to-Urdu letter unification via `src/urdu_normalize.py`.
  - Native support for **Eastern Arabic-Indic Numerals (`۰-۹`)** for CNIC (`۴۲۱۰۱-۱۲۳۴۵۶۷-۱`), mobile numbers (`۰۳۰۰-۱۲۳۴۵۶۷`), percentages (`۵.۲ فیصد`), and clock times (`شام ۶ بجے`).
  - Bilingual domain gazetteers covering high courts, laws, universities, political parties, and media outlets in both English and Urdu.
  - **100.0% Entity Recall** on out-of-domain Urdu script stress test sentences.
- **Strict Privacy Compliance (Rule 3):** 100% synthetic, non-real generation for all `PHONE_NUMBER` and `ID_NUMBER` entities with zero real citizen PII.
- **Zero-Leakage Assurance:** Strict document-level partitioning with an automated 3-tier audit (0 shared doc IDs, 0 exact sentence collisions, 0 near-duplicates).
- **Sub-3ms Inference Speed:** Average CPU prediction latency of **~2.1 ms per sentence**.

---

## 📂 Repository Structure

```
AI-Odyssey/
├── README.md                           # Master Project Overview
├── .gitignore                          # Git ignore configuration
└── ner-pk/                             # Core NER Project Directory
    ├── annotation/
    │   ├── guidelines.md               # Formal 20-class positive/negative boundary specification
    │   └── label_studio_config.xml     # Label Studio XML template
    ├── app/
    │   └── app.py                      # Interactive Gradio web demonstration
    ├── data/
    │   ├── sources.csv                 # Complete scraping provenance & robots.txt compliance
    │   ├── processed/                  # Train (3,366) and Dev (787) splits
    │   └── benchmark/                  # Held-out Benchmark (935) split
    ├── reports/
    │   ├── report.md                   # Full 11-section technical research report
    │   ├── presentation_and_qa.md      # 12-slide presentation outline & Judge Q&A defense
    │   ├── figures/                    # Class distribution & evaluation charts
    │   └── tables/                     # Precision/Recall/F1 breakdowns & error analysis
    ├── src/
    │   ├── constants.py                # Exact 20 entity types & BIO label mapping
    │   ├── urdu_normalize.py           # Urdu script orthographic normalizer & digit mapper
    │   ├── rules.py                    # Deterministic regex engine (ASCII + Eastern digits)
    │   ├── build_gazetteers.py         # Bilingual Pakistani gazetteer compiler
    │   ├── gazetteers/                 # Curated bilingual JSON gazetteers
    │   ├── synth.py                    # Privacy-compliant synthetic data generator
    │   ├── dataset.py                  # Document-level splitting & zero-leakage validator
    │   ├── postprocess.py              # Boundary cleaner & priority conflict resolver
    │   ├── evaluate.py                 # Seqeval evaluation & stress test runner
    │   └── infer.py                    # Unified CLI predictor (spans, BIO, CoNLL, JSON)
    ├── tests/
    │   └── test_rules.py               # Unit test suite (47/47 passing tests)
    ├── train_colab.ipynb               # Google Colab GPU training notebook
    ├── requirements.txt                # Python dependencies
    └── Makefile                        # Reproducibility commands
```

---

## 🚀 Quickstart & Usage

### 1. Installation
```bash
cd ner-pk
pip install -r requirements.txt
```

### 2. Run Test Suite (47 Passing Tests)
```bash
python -m unittest tests/test_rules.py
```

### 3. Run Benchmark Inference CLI
```bash
# Tricky English and Urdu benchmark test
python src/infer.py --benchmark_test

# Single sentence prediction
python src/infer.py --text "Supreme Court of Pakistan heard case in Islamabad at 11:45 PM."

# Urdu sentence prediction
python src/infer.py --text "امیدوار کا شناختی کارڈ نمبر ۴۲۱۰۱-۱۲۳۴۵۶۷-۱ ہے اور رابطہ نمبر ۰۳۰۰-۱۲۳۴۵۶۷ ہے۔"
```

### 4. Launch Interactive Web UI
```bash
python app/app.py
```
Open your browser at `http://127.0.0.1:7860`.

### 5. Reproduce Evaluation Metrics
```bash
python src/evaluate.py --split benchmark
```

---

## 👥 Authors & Team
- **Team:** AI-Odyssey
- **Competition:** TechFest NER Challenge — Dory's Data Dive (Round 2)
- **Year:** 2026
