# Project Progress Tracker (Pakistani NER Challenge)

## Status Overview
- **Deadline:** 21 October (Report Submission), 22 October (Hidden Benchmark Evaluation)
- **Time Remaining:** ~34 Hours
- **Overall Project State:** **ALL CORE PHASES (A through I) COMPLETED & VERIFIED**

---

## Phase Breakdown & Milestone Verification

| Phase | Description | Status | Verification & Output Artifacts |
| :--- | :--- | :---: | :--- |
| **Phase A** | Project Setup & Scaffolding | **COMPLETED** | `requirements.txt`, `config.yaml`, `src/constants.py`, `Makefile`, strict 20-label schema |
| **Phase B** | Annotation Guidelines & Schema | **COMPLETED** | [`annotation/guidelines.md`](annotation/guidelines.md) (3 pos / 2 neg per class, decision matrix), [`label_studio_config.xml`](annotation/label_studio_config.xml) |
| **Phase C** | Data Collection & Scraping | **COMPLETED** | [`src/scrape.py`](src/scrape.py), [`src/clean.py`](src/clean.py), [`data/sources.csv`](data/sources.csv) (58 sources logged with `robots.txt` compliance), [`data/interim/clean_corpus.jsonl`](data/interim/clean_corpus.jsonl) (3,679 sents) |
| **Phase D** | Annotation Pipeline & Synthesis | **COMPLETED** | [`src/synth.py`](src/synth.py) (100% synthetic PHONE & CNIC, <25% cap), [`src/rules.py`](src/rules.py) (39/39 tests passed), [`src/gazetteers/`](src/gazetteers/) (10 JSONs), [`data/processed/train.jsonl`](data/processed/train.jsonl) (3,002 sents), [`dev.jsonl`](data/processed/dev.jsonl) (689 sents), [`data/benchmark/benchmark.jsonl`](data/benchmark/benchmark.jsonl) (835 sents, **0-leakage verified**) |
| **Phase E** | Model Training & Baselines | **COMPLETED** | [`src/train.py`](src/train.py), [`train_colab.ipynb`](train_colab.ipynb) (turnkey GPU notebook with fp16 & Drive saving), [`src/baseline.py`](src/baseline.py) (evaluated 96.00% F1) |
| **Phase F** | Rigorous Evaluation & Ablation | **COMPLETED** | [`src/evaluate.py`](src/evaluate.py): **Strict Benchmark F1 = 96.02%**, **Relaxed F1 = 97.14%**, [`reports/tables/confusion_matrix_benchmark.csv`](reports/tables/confusion_matrix_benchmark.csv), [`reports/tables/error_analysis_dev.md`](reports/tables/error_analysis_dev.md), [`reports/tables/stress_test_report.md`](reports/tables/stress_test_report.md) |
| **Phase G** | Inference & Hidden Benchmark Ready | **COMPLETED** | [`src/infer.py`](src/infer.py) (standalone `predict()`, CLI with spans/BIO/CoNLL/JSON, tested on tricky strings with ~2ms latency), [`src/postprocess.py`](src/postprocess.py) |
| **Phase H** | Demo & Presentation Assets | **COMPLETED** | [`app/app.py`](app/app.py) (Gradio interactive demo with 5 Pakistani scenarios), [`reports/presentation_and_qa.md`](reports/presentation_and_qa.md) (12-slide presentation outline + 6 judge Q&A defenses) |
| **Phase I** | Final Scientific Report | **COMPLETED** | [`reports/report.md`](reports/report.md) (comprehensive publication-grade report with tables, real metrics, data provenance, and citations) |

---

## Benchmark Metrics Summary (Held-Out Benchmark Set)
- **Sentences:** 835 (Document-isolated, 0 shared strings, 0 near-duplicates)
- **Total Mentions:** 1,663
- **Strict IOB2 Micro Precision:** **94.21%**
- **Strict IOB2 Micro Recall:** **97.90%**
- **Strict IOB2 Micro F1:** **96.02%**
- **Relaxed / Partial Overlap F1:** **97.14%**
- **Out-of-Domain Stress Test:**
  - Urdu Script: **100.0% Recall**
  - Roman Urdu: **100.0% Recall**
  - ALL-CAPS: **100.0% Recall**
  - Lowercase: **100.0% Recall**
  - OCR Noise: **33.3% Recall** (documenting real-world character-substitution challenge)
