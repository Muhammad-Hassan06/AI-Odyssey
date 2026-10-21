# Leakage and Memorization Audit for Cleaned `v3` Data

**Audit Date:** 21 October 2026  
**Evaluated Dataset:** `v3/train.jsonl` (7,997 sents), `v3/dev.jsonl` (887 sents), `v3/benchmark.jsonl` (1,035 sents)  

## 1. Data Leakage Checks (Train vs Dev vs Internal Silver Benchmark)

| Leakage Check Type | Compared Splits | Collision Count | Status | Notes |
| :--- | :--- | :---: | :---: | :--- |
| Document ID Isolation (Train vs Dev) | - | 0 | **PASSED** | Zero overlap verified |
| Document ID Isolation (Train vs Benchmark) | - | 0 | **PASSED** | Zero overlap verified |
| Document ID Isolation (Dev vs Benchmark) | - | 0 | **PASSED** | Zero overlap verified |
| Exact Sentence Text (Train vs Dev) | - | 0 | **PASSED** | Zero overlap verified |
| Exact Sentence Text (Train vs Benchmark) | - | 0 | **PASSED** | Zero overlap verified |
| Exact Sentence Text (Dev vs Benchmark) | - | 0 | **PASSED** | Zero overlap verified |
| Near-Duplicate (Train vs Benchmark, 5-gram Jaccard > 0.75) | - | 0 | **PASSED** | Zero overlap verified |
| Synthetic Template Leakage (Train vs Benchmark) | - | 0 | **PASSED** | Zero overlap verified |

## 2. Entity Memorization Audit (Benchmark Strings Seen in Train)

Measures the share of entity surface strings in the internal silver benchmark that appear identically in the training split:

| Entity Class | Unique Benchmark Strings | Seen in Train | % Seen in Train | Generalization Vulnerability |
| :--- | :---: | :---: | :---: | :--- |
| **`PERSON`** | 7 | 7 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`CITY`** | 33 | 32 | **96.97%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`PROVINCE_REGION`** | 10 | 8 | **80.00%** | MODERATE (Shared entity vocabulary between news corpora) |
| **`COUNTRY`** | 13 | 12 | **92.31%** | MODERATE (Shared entity vocabulary between news corpora) |
| **`LANDMARK_FACILITY`** | 15 | 14 | **93.33%** | MODERATE (Shared entity vocabulary between news corpora) |
| **`GOVERNMENT_BODY`** | 6 | 6 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`POLITICAL_PARTY`** | 6 | 6 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`ORGANIZATION`** | 7 | 4 | **57.14%** | LOW (Significant novel surface forms tested) |
| **`EDUCATIONAL_INSTITUTION`** | 22 | 20 | **90.91%** | MODERATE (Shared entity vocabulary between news corpora) |
| **`COURT_LEGAL_BODY`** | 14 | 14 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`LAW_ACT`** | 13 | 13 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`EVENT`** | 13 | 13 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`MEDIA_OUTLET`** | 21 | 21 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`SPORTS_TEAM`** | 13 | 13 | **100.00%** | HIGH (Heavy gazetteer overlap; low surface diversity in benchmark) |
| **`DATE`** | 39 | 6 | **15.38%** | LOW (Significant novel surface forms tested) |
| **`TIME`** | 38 | 13 | **34.21%** | LOW (Significant novel surface forms tested) |
| **`MONEY`** | 38 | 1 | **2.63%** | LOW (Significant novel surface forms tested) |
| **`PERCENT`** | 47 | 7 | **14.89%** | LOW (Significant novel surface forms tested) |
| **`PHONE_NUMBER`** | 80 | 0 | **0.00%** | LOW (Significant novel surface forms tested) |
| **`ID_NUMBER`** | 80 | 0 | **0.00%** | LOW (Significant novel surface forms tested) |
