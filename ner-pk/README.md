# 🇵🇰 Pakistani-Context NER System (TechFest NER Challenge)
**Dory's Data Dive — Round 2 | Team AI-Odyssey**

A production-grade, hybrid multilingual Named Entity Recognition (NER) system tailored specifically for Pakistani-context text across **English**, **Urdu script (Nastaliq/Naskh)**, and **Roman Urdu**.

---

## 1. Benchmark Performance Highlights
Evaluated on an untouched, zero-leakage benchmark of **1,035 sentences (1,823 entity mentions)** isolated strictly at the document level:
- **Strict IOB2 Micro F1:** **94.60%** (Precision: **91.02%**, Recall: **98.46%**)
- **Strict IOB2 Macro F1:** **94.13%**
- **Relaxed / Partial Overlap F1:** **95.07%**
- **11 Perfect Classes (100% Strict F1):** `PERSON`, `ID_NUMBER`, `PHONE_NUMBER`, `MONEY`, `PERCENT`, `TIME`, `COURT_LEGAL_BODY`, `LAW_ACT`, `LANDMARK_FACILITY`, `MEDIA_OUTLET`, `POLITICAL_PARTY`.
- **Out-of-Domain Stress Recall:** **100.0%** across Urdu script, Roman Urdu transliterations, all-caps wire headlines, all-lowercase text, and OCR typo noise.
- **Privacy Compliance:** 100% synthetic generation for sensitive identifiers (`PHONE_NUMBER`, `ID_NUMBER`), strictly capped at 5.00% of the training corpus (limit: $\le 25\%$).

---

## 2. System Architecture & Components
Our architecture addresses Pakistani code-mixing, multi-word institutional nomenclature, and privacy boundaries via a 4-tier hybrid pipeline:

```
Raw Text Input (English / Urdu Script / Roman Urdu)
      │
      ├───► [Orthographic Normalizer & Digit Mapper] (NFKC, Eastern ۰-۹ preserved)
      │           │
      ├───► [Deterministic Regex Engine] ──► PHONE, ID, MONEY, PERCENT, TIME, DATE
      │
      ├───► [Bilingual Gazetteers Engine] ─► COURTS, LAWS, PARTIES, CITIES, ORGS
      │
      └───► [Multilingual Transformer] ───► Semantic PERSON, ORG, GOV, EVENT
                  │
                  ▼
      [Priority Merger & Post-Processor] (Longest span, Punctuation strip)
                  │
                  ▼
         Exact 20-Class Entities (Character Spans / BIO Tokens / CoNLL)
```

1. **Multilingual Deep Learning Backbone (`xlm-roberta-base`):**
   - 560M parameters pre-trained across 100 languages.
   - Fine-tuned with **smoothed class-weighted cross-entropy loss** ($w_c = \sqrt{N / (N_c + 1)}$) with background `'O'` tokens downweighted to prevent majority-class collapse.
   - Subword alignment with `-100` masking on continuation subwords and offset mapping decoding.
2. **Deterministic Pattern Engine:**
   - 100% precision on mathematical/structured formats (`PHONE_NUMBER`, `ID_NUMBER`, `MONEY`, `PERCENT`, `TIME`, `DATE`).
   - Native dual-numeral support for ASCII (`0-9`) and Eastern Arabic-Indic numerals (`۰-۹`).
   - Length-preserving OCR typo healing layer (`heal_ocr_numeric_noise`).
3. **Curated Pakistani Gazetteers:**
   - 10 domain gazetteers pairing English terms with exact Urdu script counterparts (Courts, Laws, Teams, Ministries, Universities, Media).
4. **Active Learning Review Queue:**
   - 2,473 mined candidates in Label Studio format (`annotation/review_queue_label_studio.json`).
5. **Interactive 6-Tab Gradio Application (`app/app.py`):**
   - Live NER Inspector, Pakistani Entity Showcase, Model Comparison, Error Explorer, Review Queue (HITL), and Dataset Explorer.

---

## 3. Directory Structure
```
ner-pk/
  ├── v2/                      # Official v2 zero-leakage dataset splits (JSONL & CoNLL)
  │   ├── train.jsonl          # 7,998 sentences, 13,128 mentions (5.00% synthetic)
  │   ├── dev.jsonl            # 887 sentences, 1,400 mentions (Gold real text)
  │   ├── benchmark.jsonl      # 1,035 sentences, 1,823 mentions (Gold held-out)
  │   └── *.conll              # CoNLL-2003 tab-delimited exports
  ├── src/
  │   ├── constants.py         # 20 entity schemas, BIO mapping, determinism seeds
  │   ├── rules.py             # Deterministic regex engine with dual-numeral & OCR healing
  │   ├── urdu_normalize.py    # Unicode NFKC standardizer & offset-preserving diacritic stripper
  │   ├── preannotate.py       # Gazetteer matcher & conflict resolution engine
  │   ├── dataset.py           # Subword alignment & leakage audit verification
  │   ├── train.py             # Class-weighted Trainer & experiment logging
  │   ├── evaluate.py          # Strict seqeval, relaxed metrics, confusion matrix & error logger
  │   ├── infer.py             # Unified PakistaniNERPredictor inference API
  │   ├── postprocess.py       # Punctuation stripping, span merging & priority resolution
  │   ├── review_queue.py      # Disagreement & rare-class mining engine
  │   ├── plot_figures.py      # Automated publication-quality chart generator
  │   └── gazetteers/          # 10 bilingual Pakistani domain gazetteers
  ├── app/
  │   └── app.py               # Interactive 6-tab Gradio web application
  ├── annotation/
  │   ├── review_queue_label_studio.json # 2,473 mined active learning review tasks
  │   └── label_studio_config.xml        # Label Studio UI config
  ├── reports/
  │   ├── final_report.md      # Comprehensive 11-section technical report
  │   ├── presentation_and_qa.md # Slide deck presentation & judge defense guide
  │   ├── training_log.md      # Model experiment log
  │   ├── figures/             # Per-entity F1 bar chart & confusion matrix heatmap
  │   └── tables/              # Evaluation metrics, error breakdown & ablation study
  └── requirements.txt         # Pinned python dependencies
```

---

## 4. Quick Start & Execution

### Setup Environment
```bash
git clone <repo-url>
cd ner-pk
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### Run Evaluation on Held-Out Benchmark
```bash
python src/evaluate.py --data_path v2/benchmark.jsonl --split benchmark --mode hybrid
```

### Launch Interactive 6-Tab Gradio Application
```bash
python app/app.py
```
Open `http://localhost:7860` in your browser.

### Run Model Training Pipeline
```bash
python src/train.py --train_file v2/train.jsonl --dev_file v2/dev.jsonl --output_dir models/best_ner_model --use_class_weights --batch_size 16 --epochs 6
```
*(For GPU acceleration, use `train_colab.ipynb` on Google Colab / Kaggle).*

---

## 5. Team & Declarations
- **Team:** AI-Odyssey
- **Competition:** TechFest NER Challenge: Pakistani Context (Round 2)
- **Zero Real Data Guarantee:** 0 real phone numbers or CNIC cards stored or scraped.
- **Reproducibility:** Seed 42 across Python, NumPy, PyTorch.
