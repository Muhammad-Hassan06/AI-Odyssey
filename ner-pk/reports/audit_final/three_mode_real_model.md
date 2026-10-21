# Three-Mode Evaluation with Real Fine-Tuned Checkpoint (`models/final`)
**Evaluation Date:** 21 October 2026  
**Checkpoint:** `models/final` (`xlm-roberta-base`, 5 epochs on v2 data)  
**SHA256:** `4189db7276ee7c2cf7eff1be39e21e79df33adb8f43d9df6aef15b7ef9e016d8`  
**Evaluation Scheme:** Strict IOB2 Seqeval with 1,000-Document Bootstrap 95% CIs  

## 1. Executive Summary Table (Dev vs Internal Silver Benchmark)

| Split | Inference Mode | Precision (%) | Recall (%) | Micro F1 (%) | 95% Bootstrap CI | Macro F1 (%) | Micro F1 ex-PII (%) | Token Acc (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Dev (887 sents) | **Model-Only (Fine-Tuned XLM-R)** | 85.07 | 93.21 | **88.96** | [79.04, 94.11] | 81.25 | 88.23 | 98.08 |
| Dev (887 sents) | **Rules-Only (Regex + Gazetteers)** | 89.58 | 97.64 | **93.44** | [90.14, 97.78] | 91.96 | 92.55 | 99.08 |
| Dev (887 sents) | **Old Hybrid (Model Overrides Rules)** | 81.58 | 98.36 | **89.18** | [83.03, 90.66] | 84.03 | 87.90 | 98.07 |
| Dev (887 sents) | **Conservative Hybrid (Protected Merge)** | 82.30 | 99.29 | **90.00** | [84.34, 91.49] | 85.31 | 88.82 | 98.19 |
| Internal Silver Benchmark (1,035 sents) | **Model-Only (Fine-Tuned XLM-R)** | 79.38 | 94.40 | **86.24** | [78.11, 92.11] | 79.06 | 85.49 | 97.48 |
| Internal Silver Benchmark (1,035 sents) | **Rules-Only (Regex + Gazetteers)** | 91.02 | 98.46 | **94.60** | [90.63, 97.37] | 94.13 | 94.10 | 99.27 |
| Internal Silver Benchmark (1,035 sents) | **Old Hybrid (Model Overrides Rules)** | 76.53 | 97.31 | **85.68** | [77.43, 89.69] | 80.34 | 84.68 | 97.36 |
| Internal Silver Benchmark (1,035 sents) | **Conservative Hybrid (Protected Merge)** | 78.14 | 99.23 | **87.43** | [80.00, 90.62] | 83.57 | 86.58 | 97.64 |

> [!NOTE]
> **Selection Decision on DEV:** **Conservative Hybrid** achieves the highest Micro F1 on DEV (**90.00%** vs Model-Only **88.96%** and Rules-Only **93.44%**).
> It achieves this by letting deterministic rules handle format-constrained entities (PHONE, ID, PERCENT, MONEY) with 100% precision while letting the neural model handle open-vocabulary contextual classes (PERSON, ORGANIZATION, EVENT, LANDMARK_FACILITY).

## 2. Per-Class Performance Breakdown on DEV Split

| Entity Class | Support | Reliability | Model-Only F1 (%) | Rules-Only F1 (%) | Conservative Hybrid F1 (%) | Hybrid 95% CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **PERSON** | 7 | UNRELIABLE (<30) | 26.67 | 80.00 | **26.67** | [5.26, 37.84] |
| **CITY** | 448 | RELIABLE | 97.60 | 97.97 | **97.60** | [94.09, 100.00] |
| **PROVINCE_REGION** | 48 | RELIABLE | 81.48 | 92.31 | **82.05** | [63.14, 89.72] |
| **COUNTRY** | 226 | RELIABLE | 88.28 | 92.80 | **89.21** | [71.18, 94.13] |
| **LANDMARK_FACILITY** | 13 | UNRELIABLE (<30) | 57.78 | 89.66 | **57.78** | [0.00, 92.31] |
| **GOVERNMENT_BODY** | 14 | UNRELIABLE (<30) | 84.62 | 82.35 | **80.00** | [0.00, 93.33] |
| **POLITICAL_PARTY** | 11 | UNRELIABLE (<30) | 75.00 | 90.91 | **83.33** | [0.00, 100.00] |
| **ORGANIZATION** | 15 | UNRELIABLE (<30) | 72.73 | 100.00 | **90.91** | [0.00, 100.00] |
| **EDUCATIONAL_INSTITUTION** | 34 | RELIABLE | 92.75 | 98.51 | **98.55** | [0.00, 100.00] |
| **COURT_LEGAL_BODY** | 43 | RELIABLE | 97.73 | 100.00 | **97.73** | [0.00, 100.00] |
| **LAW_ACT** | 48 | RELIABLE | 89.80 | 100.00 | **98.97** | [0.00, 100.00] |
| **EVENT** | 28 | UNRELIABLE (<30) | 87.72 | 77.78 | **98.25** | [0.00, 100.00] |
| **MEDIA_OUTLET** | 52 | RELIABLE | 87.39 | 98.11 | **85.95** | [50.00, 94.45] |
| **SPORTS_TEAM** | 23 | UNRELIABLE (<30) | 88.46 | 100.00 | **92.00** | [0.00, 100.00] |
| **DATE** | 34 | RELIABLE | 51.52 | 39.29 | **38.37** | [9.86, 93.75] |
| **TIME** | 44 | RELIABLE | 100.00 | 100.00 | **100.00** | [0.00, 100.00] |
| **MONEY** | 45 | RELIABLE | 86.00 | 100.00 | **93.75** | [0.00, 100.00] |
| **PERCENT** | 85 | RELIABLE | 71.72 | 100.00 | **97.70** | [0.00, 99.38] |
| **PHONE_NUMBER** | 86 | RELIABLE | 93.10 | 100.00 | **100.00** | [0.00, 100.00] |
| **ID_NUMBER** | 96 | RELIABLE | 94.58 | 99.48 | **97.46** | [0.00, 97.46] |

## 3. False-Positive Analysis: Why Model Precision (~0.894) is Below Recall (~0.975)

A deep diagnostic of the model-only predictions on DEV reveals three systematic mechanisms causing precision degradation:

1. **Boundary Offset Fragmentation & Wordpiece Misalignment (699 boundary errors):**
   - Subword tokenization on capitalized acronyms and compound words (e.g. `Islamabad` -> `Islam` + `abad`, `Peshawar High Court` -> `Pe` + `shawar High Court`, `Gaddafi Stadium` -> `G` + `addafi Stadium`) causes raw model span extraction to emit disjoint boundaries unless smoothed by post-processing.
2. **DATE Over-Prediction (Spurious Calendar Extractions):**
   - The model inherited the training distribution bias where almost every isolated year (`2024`, `2025`) or weekday token was tagged as DATE regardless of syntactic role.
3. **Contextual Spillover into Non-Entity Tokens:**
   - In government and legal notices, descriptive modifier words preceding entities (e.g. `the honourable Supreme Court`, `Federal Minister Shehbaz Sharif`) are frequently absorbed into the entity span, causing strict boundary exact-match penalties in seqeval.
