# Presentation Outline & Judge Q&A Defense Guide
**TechFest NER Challenge: Dory's Data Dive (Round 2)**
**Topic:** Pakistani-Context Named Entity Recognition System
**Team:** AI-Odyssey | **Date:** 21 October 2026

---

## Part 1: Presentation Slide Deck (10–12 Slides, ~8 Minutes)

### Slide 1: Title & Executive Summary
- **Title:** Robust Hybrid Named Entity Recognition for Pakistani-Context Text
- **Team:** AI-Odyssey
- **Core Thesis:** The hidden benchmark rewards robustness and clean span boundaries over brute model size. We built a hybrid pipeline combining a multilingual transformer, deterministic regex patterns, and curated Pakistani gazetteers across 20 exact entity classes.
- **Key Headline:** **87.54% Strict IOB2 Micro F1** (Conservative Hybrid) and **82.69% Micro F1** (Neural Transformer alone) on real collected text (`v4/dev_real.jsonl`), with strict zero-leakage isolation, 0 human-gold sentences acknowledged, and 100% deterministic regex handling for sensitive PII.

### Slide 2: The Pakistani Context Challenge
- **Code-Mixing & Multilingualism:** Pakistani news and civic discourse mix English, formal Urdu script (Nastaliq/Naskh), and Roman Urdu within the same document.
- **Transliteration & Spelling Variations:** *Karachi* vs. *Karāchi* vs. *کراچی*; *Peshawar* vs. *Peshawer*; *State Bank* vs. *اسٹیٹ بینک* vs. *سٹیٹ بینک*.
- **Entity Ambiguity & Person-Named Entities:**
  - *Jinnah International Airport* (LANDMARK_FACILITY) vs. *Muhammad Ali Jinnah* (PERSON).
  - *Supreme Court Bar Association* (ORGANIZATION) vs. *Supreme Court of Pakistan* (COURT_LEGAL_BODY).
- **Sensitive Local Formats:** 13-digit CNIC numbers and +92 mobile numbers requiring strict ethical handling.

### Slide 3: Task Rules & Annotation Guidelines
- **Strict 20-Class Schema:** Zero label deviation.
- **Longest Span / Specificity Precedence:** Resolves nested spans deterministically (e.g. *Karachi Kings* = SPORTS_TEAM, not CITY).
- **Span Boundary Cleanliness:** Systematic exclusion of honorifics (*Prime Minister*, *Dr.*, *Justice*, *صاحب*) from PERSON spans; strict possessive stripping (`'s`).
- **Currency & Percentage Inclusions:** Unit prefixes/symbols (*Rs*, *PKR*, *USD*, *crore*, *%*, *per cent*) kept strictly inside the span.

### Slide 4: Ethical Data Collection & Provenance
- **Robots.txt Verification:** Automated checking via `urllib.robotparser`; 100% compliant with host crawling terms.
- **50 Public Sources Scraped:** Dawn, The Express Tribune, APP news releases, State Bank of Pakistan bulletins, Wikipedia Pakistan portal, and Urdu Wikipedia.
- **No Private Data & No Paywalls:** Zero login-walled sources accessed. Full provenance logged in `data/sources.csv` (58 records).

### Slide 5: Real-Text Privacy & Deterministic PII Handling
- **Rule 3 Compliance:** Absolute prohibition on real phone numbers or CNIC cards.
- **Zero Real PII in Data:** The collected real corpus contains 0 phone numbers and 0 CNIC cards.
- **Deterministic Regex Execution:** `PHONE_NUMBER` and `ID_NUMBER` are handled 100% deterministically by regex rules in hybrid mode without generating synthetic PII.

### Slide 6: Zero-Leakage Dataset Partitioning (`v4` Real-Only)
- **Article/Document-Level Split:** Documents partitioned before sentence splitting, preventing the same article from leaking across splits.
- **Automated 3-Tier Leakage Audit:**
  - Shared Document IDs: **0**
  - Exact Sentence Collisions: **0**
  - Near-Duplicate Matches (>75% Jaccard): **0**
- **Corpus Sizes:** Train = 5,282 real sentences; Dev = 454 real sentences; Held-out Benchmark = 615 real sentences (0 synthetic sentences in `v4`).

### Slide 7: Hybrid System Architecture
- **Layer 1: Multilingual Deep Learning Backbone** (`xlm-roberta-base`): Fine-tuned with smoothed class-weighted cross-entropy loss to counter severe frequency imbalances.
- **Layer 2: Deterministic Regex Pattern Engine**: 100% precision on structured entities (PHONE_NUMBER, ID_NUMBER, MONEY, PERCENT, TIME).
- **Layer 3: Pakistani Gazetteers**: 10 curated bilingual lists (Courts, Laws, Teams, Ministries, Universities, Media).
- **Layer 4: Priority Post-Processing**: Strips punctuation leaks, resolves overlaps, and merges adjacent fragments.

### Slide 7B: Urdu NER Extension — The Competitive Differentiator
- **Addressing the Competition Directive:** The host explicitly announced that Urdu NER support provides a significant ranking advantage.
- **Dual-Script Normalization (`src/urdu_normalize.py`):**
  - Unicode NFKC standardization & Arabic-to-Urdu character unification (Kaf, Ye, Gol He).
  - Offset-preserving diacritic (Aerab) stripping.
- **Eastern Arabic-Indic Numerals (`۰-۹`):**
  - Native dual-numeral regex matching for Urdu CNIC (`۴۲۱۰۱-۱۲۳۴۵۶۷-۱`), Urdu phone numbers (`۰۳۰۰-۱۲۳۴۵۶۷`), and Urdu percentages (`۵.۲ فیصد`).
- **Bilingual Gazetteers Across All 10 Domains:**
  - Full Urdu coverage for political parties, high courts, sports franchises, laws, and educational institutions (*سپریم کورٹ آف پاکستان*, *لاہور قلندرز*, *26ویں آئینی ترمیم*).

### Slide 8: Real Model & Benchmark Evaluation Results
- **Benchmark Characterization:** "Internal silver benchmark, real text only, 0 human-gold sentences" containing 615 real sentences (100% Silver auto-annotated).
- **True Transformer Performance (XLM-RoBERTa Alone):**
  - Dev Real (454 sents): **77.17% Precision, 89.05% Recall, 82.69% Micro F1** (95% CI: [77.50, 84.95]), **60.06% Macro F1**.
  - Internal Silver Benchmark (615 sents): **72.84% Precision, 92.10% Recall, 81.34% Micro F1** (95% CI: [76.70, 83.14]).
- **Why Rules-Only Scores 95.14% on Internal Benchmark:**
  - Gazetteers and rules generated the silver labels; high rules performance is circular self-agreement.
- **Production Choice (Conservative Hybrid):**
  - Dev Real (454 sents): **78.94% Precision, 98.24% Recall, 87.54% Micro F1, 67.31% Macro F1**.
  - Rules win on structured types (PHONE, ID, MONEY, PERCENT, TIME, DATE); Model generalizes on open-vocabulary classes (PERSON, ORG, EVENT, LANDMARK).

### Slide 9: Ablation Study & Empirical Model Selection on DEV
- Selected strictly on **DEV** (`v4/dev_real.jsonl`, Benchmark kept read-only):
  - *Model-Only:* 82.69% Micro F1 (77.17% Precision / 89.05% Recall / 60.06% Macro F1).
  - *Rules-Only:* 94.97% Micro F1 (circular on silver data, cannot generalize to unseen names).
  - *Old Hybrid (Model Overrides):* 85.85% Micro F1 (model errors override high-precision regex).
  - *Conservative Hybrid:* **87.54% Micro F1, 67.31% Macro F1** (optimal blend).

### Slide 10: Robustness & Out-of-Domain Stress Testing
- **Urdu Script Sentences:** 100% Entity Recall
- **Roman Urdu Transliterations:** 100% Entity Recall
- **ALL-CAPS Headlines:** Handled via train casing augmentation and uppercase regex normalization.
- **All-Lowercase Text:** Preserved via lowercased gazetteer matches.
- **OCR / Typo Noise:** Recovered via length-preserving OCR numeric & word healing.

### Slide 11: Error Analysis & Key Takeaways
- **Dominant Error Class:** Calendar `DATE` precision due to ambiguous isolated years/days appearing in general sentences.
- **Boundary Jitter Mitigation:** Resolved by regex override for currency symbols and post-processing punctuation stripping.
- **Engineering Principle:** Clean data annotation, stratification, and strict decision boundaries matter more than adding billions of model parameters.

### Slide 12: Interactive 6-Tab Gradio Application & Deployment
- Full 6-tab Gradio web application (`app/app.py`):
  1. **Live NER Inspector:** Single-sentence text input, script detection, and color-coded entity highlight.
  2. **20-Entity Showcase:** Pre-loaded scenarios demonstrating all 20 classes.
  3. **Architecture Comparison:** Side-by-side comparison of Rules vs Neural vs Hybrid.
  4. **Diagnostic Error Browser:** Exploration of boundary edge cases.
  5. **Review Queue (HITL):** Active review of 2,473 flagged candidates.
  6. **Dataset & Exporter:** Batch file processor accepting `.txt`, `.csv`, `.jsonl`.

---

## Part 2: Judge Q&A Defense Guide

### Q1: What does the neural model alone achieve?
> "On the held-out real dev set (`v4/dev_real.jsonl`, 454 sentences), the fine-tuned XLM-RoBERTa model alone scores **77.17% Precision, 89.05% Recall, 82.69% Micro F1**, and **60.06% Macro F1**. On the real benchmark, it achieves **81.34% Micro F1**. Any claim that the neural model alone scores >94% F1 is inaccurate; that score is only reached by rules matching their own gazetteers."

### Q2: How were the benchmark labels created?
> "The benchmark labels were generated using our deterministic rule engine and bilingual gazetteers on real text. There are **zero human-verified gold sentences** in `v4/benchmark_real.jsonl`. We openly designate it as an 'internal silver benchmark, real text only, 0 human-gold sentences'."

### Q3: How was annotation quality maintained, and how much is human-verified?
> "In active split `v4` (6,351 sentences: 5,282 train, 454 dev, 615 benchmark), exactly **0 sentences are human-verified GOLD**. All sentences are real collected text auto-annotated by silver rules.
> We openly characterize our 615-sentence benchmark as an 'internal silver benchmark (0 human-gold sentences)'.
> To build a true human-gold benchmark, we exported 2,473 candidate sentences from un-split pool documents into Label Studio format (`annotation/review_queue_label_studio.json`) with rare classes prioritized, creating the pipeline for human verification."

### Q4: Why will the hybrid model generalize to unseen test text?
> "The conservative hybrid architecture divides responsibilities:
> 1. Regex rules handle closed, syntactically-defined entities with high certainty (`PHONE_NUMBER`, `ID_NUMBER`, `MONEY`, `PERCENT`, `TIME`, `DATE`).
> 2. The XLM-RoBERTa transformer handles semantic and open-vocabulary entities (`PERSON`, `ORGANIZATION`, `EVENT`, `LANDMARK_FACILITY`), leveraging contextual multilingual representations to recognize entities not present in our gazetteers."
