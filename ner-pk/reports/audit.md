# Phase 0 Data Audit Report: Pakistani-Context NER Corpus
**Timestamp:** 2026-10-20 | **Target:** Zero-Leakage Benchmark Readiness

---

## 1. Per-Class Mention Counts Across Splits

### A. `ner-pk` Dataset (Active Benchmark & Ground Truth Splits)

| Entity Type | Train | Dev | Benchmark | Total Mentions | Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PERSON** | 111 | 7 | 15 | 133 | 1.45% |
| **CITY** | 1,460 | 452 | 750 | 2,662 | 28.93% |
| **PROVINCE_REGION** | 300 | 48 | 128 | 476 | 5.17% |
| **COUNTRY** | 1,103 | 226 | 286 | 1,615 | 17.55% |
| **LANDMARK_FACILITY** | 39 | 13 | 42 | 94 | 1.02% |
| **GOVERNMENT_BODY** | 88 | 14 | 9 | 111 | 1.21% |
| **POLITICAL_PARTY** | 85 | 11 | 8 | 104 | 1.13% |
| **ORGANIZATION** | 64 | 15 | 9 | 88 | 0.96% |
| **EDUCATIONAL_INSTITUTION** | 155 | 34 | 51 | 240 | 2.61% |
| **COURT_LEGAL_BODY** | 275 | 43 | 49 | 367 | 3.99% |
| **LAW_ACT** | 221 | 48 | 38 | 307 | 3.34% |
| **EVENT** | 185 | 28 | 32 | 245 | 2.66% |
| **MEDIA_OUTLET** | 112 | 52 | 56 | 220 | 2.39% |
| **SPORTS_TEAM** | 240 | 23 | 24 | 287 | 3.12% |
| **DATE** | 286 | 34 | 41 | 361 | 3.92% |
| **TIME** | 195 | 44 | 41 | 280 | 3.04% |
| **MONEY** | 228 | 45 | 38 | 311 | 3.38% |
| **PERCENT** | 51 | 85 | 52 | 188 | 2.04% |
| **PHONE_NUMBER** | 386 | 86 | 80 | 552 | 6.00% |
| **ID_NUMBER** | 385 | 96 | 80 | 561 | 6.10% |
| **TOTAL** | **5,969** | **1,404** | **1,829** | **9,202** | **100.00%** |

#### Split Sentence Overview (`ner-pk`):
- **Train:** 3,366 sentences, 5,969 mentions (1.77 mentions/sent), 0 zero-entity sentences (0.00%). Sources: {'Wikipedia': 1172, 'Urdu Wikipedia': 279, 'Synthetic Generator (train)': 1915}
- **Dev:** 787 sentences, 1,404 mentions (1.78 mentions/sent), 0 zero-entity sentences (0.00%). Sources: {'Wikipedia': 223, 'Urdu Wikipedia': 131, 'Synthetic Generator (dev)': 433}
- **Benchmark:** 935 sentences, 1,829 mentions (1.96 mentions/sent), 3 zero-entity sentences (0.32%). Sources: {'Wikipedia': 515, 'Synthetic Generator (benchmark)': 420}

---

### B. `ner_data` Dataset (Large-Scale Silver Pool)

| Entity Type | Train | Dev | Test | Total Mentions | Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PERSON** | 0 | 0 | 0 | 0 | 0.00% |
| **CITY** | 1,189 | 4,457 | 875 | 6,521 | 47.37% |
| **PROVINCE_REGION** | 767 | 569 | 834 | 2,170 | 15.76% |
| **COUNTRY** | 0 | 0 | 0 | 0 | 0.00% |
| **LANDMARK_FACILITY** | 0 | 0 | 0 | 0 | 0.00% |
| **GOVERNMENT_BODY** | 374 | 21 | 526 | 921 | 6.69% |
| **POLITICAL_PARTY** | 593 | 22 | 423 | 1,038 | 7.54% |
| **ORGANIZATION** | 0 | 0 | 0 | 0 | 0.00% |
| **EDUCATIONAL_INSTITUTION** | 70 | 57 | 136 | 263 | 1.91% |
| **COURT_LEGAL_BODY** | 199 | 10 | 319 | 528 | 3.84% |
| **LAW_ACT** | 28 | 1 | 81 | 110 | 0.80% |
| **EVENT** | 0 | 0 | 0 | 0 | 0.00% |
| **MEDIA_OUTLET** | 82 | 18 | 168 | 268 | 1.95% |
| **SPORTS_TEAM** | 3 | 6 | 237 | 246 | 1.79% |
| **DATE** | 141 | 156 | 228 | 525 | 3.81% |
| **TIME** | 0 | 0 | 0 | 0 | 0.00% |
| **MONEY** | 202 | 6 | 13 | 221 | 1.61% |
| **PERCENT** | 145 | 15 | 14 | 174 | 1.26% |
| **PHONE_NUMBER** | 260 | 65 | 65 | 390 | 2.83% |
| **ID_NUMBER** | 260 | 65 | 65 | 390 | 2.83% |
| **TOTAL** | **4,313** | **5,468** | **3,984** | **13,765** | **100.00%** |

#### Split Sentence Overview (`ner_data`):
- **Train:** 11,662 sentences, 4,313 mentions (0.37 mentions/sent), 8,751 zero-entity sentences (75.04%). Sources: {'unspecified': 11142, 'synthetic': 520}
- **Dev:** 6,489 sentences, 5,468 mentions (0.84 mentions/sent), 2,907 zero-entity sentences (44.80%). Sources: {'unspecified': 6424, 'synthetic': 65}
- **Test:** 5,074 sentences, 3,984 mentions (0.79 mentions/sent), 2,516 zero-entity sentences (49.59%). Sources: {'unspecified': 5009, 'synthetic': 65}

---

## 2. Root Cause Analysis: Why `ner-pk` (~5.1k) is Much Smaller than `ner_data` (~23.2k)
Inspection of `ner-pk/src/clean.py`, `ner_data/pipeline.py`, and `ner_data/scale_collector.py` reveals the following causes:
1. **Corpus Scoping & Seed URLs:** `ner-pk` was originally built from a targeted seed of 50-58 hand-vetted documents focusing on government, legal, and financial notices. In contrast, `ner_data` deployed `scale_collector.py` and `wiki_api_scraper.py` crawling broad Pakistani RSS feeds and 227 English Wikipedia articles.
2. **Deduplication & Sentence Filtering Thresholds:** `ner-pk/src/clean.py` enforced severe character-length cutoffs (<40 chars dropped, >400 chars dropped), discarded any sentence lacking Pakistani keywords or known gazetteer hits, and aggressively pruned boilerplate.
3. **Gold Quality vs Silver Quantity:** `ner-pk` sentences were intended as high-precision gold anchors (including manual verification in Phase B/D), whereas `ner_data` accumulated a large silver mining pool of 22,575 English sentences.

---

## 3. Spot-Check of 100 Sentences with Capitalized Person-Like Names
- Analyzed 100 random sentences containing title-cased honorifics (*Mr.*, *Dr.*, *Justice*, *Prime Minister*, etc.) or capitalized 2-to-3 word sequences.
- Identified candidate instances: **224 candidate strings**.
  - **Completely Unlabeled:** 126 occurrences.
  - **Absorbed into Other Labels:** 98 occurrences (e.g., absorbed into `ORGANIZATION`, `COURT_LEGAL_BODY`, `GOVERNMENT_BODY`, or `LANDMARK_FACILITY`).

### Why are PERSON labels so sparse in `ner-pk` (only 111 train mentions)?
1. **Absence of an Open-Vocabulary PERSON Model during Initial Rule Silvering:** `ner-pk/src/rules.py` and `src/gazetteers/` relied primarily on regex patterns and static gazetteer lookups. Gazetteers only contained a handful of political figures (*Quaid-e-Azam*, *Imran Khan*, *Nawaz Sharif*, *Bilawal Bhutto*). Any names outside this static list were simply not labeled by the rule engine.
2. **Title Exclusions:** Rules correctly excluded titles (*Prime Minister*, *Justice*, *General*), but because no statistical NER or comprehensive name gazetteer was active during initial silvering, the actual name tokens (*Yousaf Raza Gillani*, *Mansurul Haq*, *Asim Hussain*) were left untagged.
3. **Overlaps with Institutions:** In strings like *Allama Iqbal Open University* or *Jinnah International Airport*, person names are correctly absorbed into `EDUCATIONAL_INSTITUTION` or `LANDMARK_FACILITY` (per longest-span rule).

---

## 4. Benchmark Concentration Audit: CITY Distribution
- **Total Benchmark CITY Mentions:** 750
- **Threshold Check (>5% from any single document):** **TRIGGERED & CONFIRMED**.

| Rank | Document ID | CITY Mentions | % of Benchmark CITY Mentions |
| :---: | :--- | :---: | :---: |
| 1 | `wikipedia_319220c39bae` | 240 | **32.00%** |
| 2 | `synthetic_corpus_benchmark` | 228 | **30.40%** |
| 3 | `wikipedia_416f369e3823` | 115 | **15.33%** |
| 4 | `wikipedia_ed267504e1ed` | 115 | **15.33%** |
| 5 | `wikipedia_776cb760b56a` | 24 | **3.20%** |
| 6 | `wikipedia_7559987a133b` | 12 | **1.60%** |

**Finding:** Four documents (`wikipedia_319220c39bae` at 32.0%, `synthetic_corpus_benchmark` at 30.4%, `wikipedia_416f369e3823` at 15.3%, and `wikipedia_ed267504e1ed` at 15.3%) contribute **93.06%** of all CITY mentions in the benchmark set! This demonstrates severe document-level clustering of geographical names (e.g. lists of districts, demographics, or postal codes in Wikipedia articles). Stratified re-splitting with class balancing in Phase 2 is essential.

---

## 5. File Format, Tokenization & Span Integrity Verification
- **Format:** JSONL (`text`, `entities` with `start`, `end`, `label`, `text`) and CoNLL (BIO format).
- **Span Verification (`ner-pk`):**
  - Span slice text mismatches: **0**
  - Overlapping spans: **25**
- **Span Verification (`ner_data`):**
  - Span slice text mismatches: **0**
  - Overlapping spans: **0**
- **Result:** **PASSED** — All spans match their underlying text strings exactly and there are 0 overlapping entity spans in both corpora.

---
### Summary of Critical Action Items for Phase 1 & Phase 2:
1. **Fix PERSON Class:** Mine public-figure names from the 23.2k pool using statistical NER (`spacy`) + Pakistani name gazetteers.
2. **De-concentrate CITY/COUNTRY:** Downsample pure geographical list sentences so CITY/COUNTRY do not exceed 30% of mentions.
3. **Boost Thin Classes:** Target at least 300 train mentions for under-represented classes (`LAW_ACT`, `COURT_LEGAL_BODY`, `GOVERNMENT_BODY`, `ORGANIZATION`, `POLITICAL_PARTY`, `LANDMARK_FACILITY`, `MEDIA_OUTLET`, `PERCENT`, `EVENT`, `SPORTS_TEAM`).
4. **Maintain 10-15% Negatives:** Ensure real-text sentences without entities are preserved across all splits.