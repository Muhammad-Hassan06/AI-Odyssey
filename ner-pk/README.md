# Pakistani-Context NER System (TechFest NER Challenge)
**Dory's Data Dive — Round 2**

A high-performance, robust Named Entity Recognition (NER) pipeline tailored specifically for Pakistani-context text across English, Urdu script, and Roman Urdu.

## 1. System Overview
- **Exact 20 Entity Categories:** `PERSON`, `CITY`, `PROVINCE_REGION`, `COUNTRY`, `LANDMARK_FACILITY`, `GOVERNMENT_BODY`, `POLITICAL_PARTY`, `ORGANIZATION`, `EDUCATIONAL_INSTITUTION`, `COURT_LEGAL_BODY`, `LAW_ACT`, `EVENT`, `MEDIA_OUTLET`, `SPORTS_TEAM`, `DATE`, `TIME`, `MONEY`, `PERCENT`, `PHONE_NUMBER`, `ID_NUMBER`.
- **Hybrid Architecture:**
  - Fine-tuned Multilingual Transformer (`xlm-roberta-large` / fallback `xlm-roberta-base`) for semantic entities.
  - High-precision Regex / Pattern Layer for structured entities (`PHONE_NUMBER`, `ID_NUMBER`, `MONEY`, `PERCENT`, `TIME`, `DATE`).
  - Curated Pakistani Gazetteers for closed-class and domain-specific entities (provinces, major cities, ministries, courts, parties, media, sports teams).
  - Priority-based merging and boundary normalization.
- **Strict Ethics & Compliance:**
  - Automated `robots.txt` compliance checking and gentle request throttling.
  - Zero scraping of login-walled or copyrighted private content.
  - 100% synthetic generation for `PHONE_NUMBER` and `ID_NUMBER` (CNIC format). No real personal identifiers used.
  - Guaranteed zero data leakage: document-level provenance hashing and explicit overlap testing.

## 2. Directory Structure
```
ner-pk/
  ├── data/
  │   ├── raw/           # Raw scraped documents with source provenance
  │   ├── interim/       # Cleaned, sentence-split, de-duplicated texts
  │   ├── processed/     # Silver & gold BIO annotations (train, dev)
  │   ├── benchmark/     # Untouched, hand-verified gold benchmark
  │   └── sources.csv    # Mandatory provenance & terms compliance log
  ├── src/
  │   ├── constants.py   # 20 entity schemas, BIO mapping, determinism seeds
  │   ├── scrape.py      # Polite public scraper respecting robots.txt
  │   ├── clean.py       # Boilerplate removal, deduplication, Urdu punctuation
  │   ├── synth.py       # Synthetic generator for PHONE, ID, and rare templates
  │   ├── rules.py       # Deterministic regex engine for pattern entities
  │   ├── gazetteers/    # JSON gazetteers for Pakistani entities
  │   ├── preannotate.py # Hybrid silver annotator (rules + gazetteers + heuristics)
  │   ├── dataset.py     # Subword alignment (-100 mask) and HF dataset builder
  │   ├── train.py       # XLM-RoBERTa fine-tuning with fp16 & class weighting
  │   ├── evaluate.py    # Seqeval strict IOB2 & partial overlap evaluations
  │   ├── infer.py       # Unified robust prediction pipeline (spans & BIO)
  │   └── postprocess.py # Boundary cleanup and systematic conflict resolution
  ├── annotation/
  │   ├── guidelines.md          # Comprehensive annotation rules & boundary guide
  │   └── label_studio_config.xml# Label Studio config for gold review
  ├── reports/
  │   ├── figures/       # Evaluation charts, confusion matrices, class distribution
  │   ├── tables/        # Per-entity P/R/F1, ablation tables, error analysis
  │   └── report.md      # Final scientific report
  ├── app/
  │   └── app.py         # Gradio visual demonstration interface
  ├── config.yaml        # Central hyperparameters and runtime settings
  ├── requirements.txt   # Pinned dependencies
  ├── PROGRESS.md        # Real-time development progress tracker
  └── Makefile           # Convenient execution shortcuts
```

## 3. Quick Start
```bash
cd ner-pk
pip install -r requirements.txt
make test
```
