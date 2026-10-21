# Live Evaluation Report: Real-Only Data (`v4`)

**Evaluation Constraint:** Evaluated on real collected text only (`v4/dev_real.jsonl` and `v4/benchmark_real.jsonl`).
**Benchmark Status:** Internal silver benchmark, real text only, 0 human-gold sentences.

## DEV Split (`v4/dev_real.jsonl`)

| Mode | Precision | Recall | Micro F1 | 95% CI (Micro) | Macro F1 | 95% CI (Macro) | Ex-PII F1 | Token Acc | Exact-Match Sent Acc |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model-Only (XLM-R Checkpoint)** | 79.93% | 86.62% | **83.14%** | [75.22, 87.96] | **64.91%** | [34.13, 68.30] | 83.14% | 97.39% | 68.94% |
| **Rules-Only (Regex + Gazetteers)** | 87.50% | 96.49% | **91.77%** | [85.07, 93.38] | **74.42%** | [39.15, 76.01] | 91.77% | 98.72% | 83.04% |
| **Old Hybrid (Model Overrides Rules)** | 76.91% | 95.00% | **85.01%** | [77.74, 86.46] | **65.96%** | [35.25, 69.19] | 85.01% | 97.67% | 71.15% |
| **Conservative Hybrid (Rules Priority)** | 78.64% | 97.03% | **86.87%** | [79.66, 88.75] | **68.16%** | [37.48, 71.40] | 86.87% | 97.87% | 72.91% |

## BENCHMARK Split (`v4/benchmark_real.jsonl` - Internal Silver Benchmark)

| Mode | Precision | Recall | Micro F1 | 95% CI (Micro) | Macro F1 | 95% CI (Macro) | Ex-PII F1 | Token Acc | Exact-Match Sent Acc |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model-Only (XLM-R Checkpoint)** | 76.27% | 90.40% | **82.74%** | [78.35, 84.08] | **53.84%** | [33.87, 56.24] | 82.74% | 97.26% | 62.28% |
| **Rules-Only (Regex + Gazetteers)** | 89.78% | 98.56% | **93.97%** | [85.02, 96.60] | **77.01%** | [45.59, 78.69] | 93.97% | 99.15% | 84.39% |
| **Old Hybrid (Model Overrides Rules)** | 74.01% | 95.33% | **83.33%** | [75.42, 85.34] | **56.82%** | [36.46, 59.16] | 83.33% | 97.26% | 60.98% |
| **Conservative Hybrid (Rules Priority)** | 76.62% | 98.56% | **86.21%** | [77.00, 88.93] | **65.62%** | [39.40, 67.78] | 86.21% | 97.65% | 63.90% |

## Dev Per-Class Metrics: Winning Mode (`rules_only`)

| Class | Precision | Recall | F1-Score | Support | Reliability | 95% Bootstrap CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `PERSON` | 23.08% | 85.71% | **36.36%** | 7 | `UNRELIABLE` | [0.00, 58.33] |
| `CITY` | 99.55% | 99.10% | **99.33%** | 223 | `RELIABLE` | [99.02, 100.00] |
| `PROVINCE_REGION` | 93.62% | 91.67% | **92.63%** | 48 | `RELIABLE` | [84.20, 100.00] |
| `COUNTRY` | 90.00% | 95.58% | **92.70%** | 226 | `RELIABLE` | [73.86, 96.04] |
| `LANDMARK_FACILITY` | 81.25% | 100.00% | **89.66%** | 13 | `UNRELIABLE` | [0.00, 100.00] |
| `GOVERNMENT_BODY` | 46.67% | 100.00% | **63.64%** | 7 | `UNRELIABLE` | [0.00, 87.50] |
| `POLITICAL_PARTY` | 100.00% | 100.00% | **100.00%** | 7 | `UNRELIABLE` | [0.00, 100.00] |
| `ORGANIZATION` | 68.18% | 100.00% | **81.08%** | 15 | `UNRELIABLE` | [0.00, 100.00] |
| `EDUCATIONAL_INSTITUTION` | 100.00% | 90.00% | **94.74%** | 10 | `UNRELIABLE` | [0.00, 100.00] |
| `COURT_LEGAL_BODY` | 100.00% | 100.00% | **100.00%** | 1 | `UNRELIABLE` | [0.00, 100.00] |
| `LAW_ACT` | 100.00% | 100.00% | **100.00%** | 6 | `UNRELIABLE` | [0.00, 100.00] |
| `EVENT` | 100.00% | 100.00% | **100.00%** | 4 | `UNRELIABLE` | [0.00, 100.00] |
| `MEDIA_OUTLET` | 90.62% | 90.62% | **90.62%** | 32 | `RELIABLE` | [0.00, 100.00] |
| `SPORTS_TEAM` | 100.00% | 100.00% | **100.00%** | 4 | `UNRELIABLE` | [0.00, 100.00] |
| `DATE` | 53.70% | 85.29% | **65.91%** | 34 | `RELIABLE` | [34.77, 84.00] |
| `TIME` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `MONEY` | 69.23% | 100.00% | **81.82%** | 18 | `UNRELIABLE` | [0.00, 89.47] |
| `PERCENT` | 100.00% | 100.00% | **100.00%** | 85 | `RELIABLE` | [0.00, 100.00] |
| `PHONE_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `ID_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |

## Dev Per-Class Metrics: Model-Only Checkpoint (`model_only`)

| Class | Precision | Recall | F1-Score | Support | Reliability | 95% Bootstrap CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `PERSON` | 16.22% | 85.71% | **27.27%** | 7 | `UNRELIABLE` | [0.00, 40.00] |
| `CITY` | 92.89% | 99.55% | **96.10%** | 223 | `RELIABLE` | [90.32, 100.00] |
| `PROVINCE_REGION` | 82.35% | 87.50% | **84.85%** | 48 | `RELIABLE` | [79.01, 91.68] |
| `COUNTRY` | 87.70% | 94.69% | **91.06%** | 226 | `RELIABLE` | [79.59, 94.04] |
| `LANDMARK_FACILITY` | 54.17% | 100.00% | **70.27%** | 13 | `UNRELIABLE` | [0.00, 96.78] |
| `GOVERNMENT_BODY` | 50.00% | 100.00% | **66.67%** | 7 | `UNRELIABLE` | [0.00, 73.68] |
| `POLITICAL_PARTY` | 77.78% | 100.00% | **87.50%** | 7 | `UNRELIABLE` | [0.00, 100.00] |
| `ORGANIZATION` | 86.67% | 86.67% | **86.67%** | 15 | `UNRELIABLE` | [0.00, 100.00] |
| `EDUCATIONAL_INSTITUTION` | 88.89% | 80.00% | **84.21%** | 10 | `UNRELIABLE` | [0.00, 100.00] |
| `COURT_LEGAL_BODY` | 100.00% | 100.00% | **100.00%** | 1 | `UNRELIABLE` | [0.00, 100.00] |
| `LAW_ACT` | 75.00% | 100.00% | **85.71%** | 6 | `UNRELIABLE` | [0.00, 100.00] |
| `EVENT` | 80.00% | 100.00% | **88.89%** | 4 | `UNRELIABLE` | [0.00, 100.00] |
| `MEDIA_OUTLET` | 76.19% | 100.00% | **86.49%** | 32 | `RELIABLE` | [28.52, 96.85] |
| `SPORTS_TEAM` | 50.00% | 100.00% | **66.67%** | 4 | `UNRELIABLE` | [0.00, 100.00] |
| `DATE` | 66.67% | 58.82% | **62.50%** | 34 | `RELIABLE` | [31.36, 79.52] |
| `TIME` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `MONEY` | 58.62% | 94.44% | **72.34%** | 18 | `UNRELIABLE` | [0.00, 72.73] |
| `PERCENT` | 67.57% | 29.41% | **40.98%** | 85 | `RELIABLE` | [0.00, 83.33] |
| `PHONE_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `ID_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |

## Methodological Disclosure on Rule Circularity

Rules-only and Hybrid modes achieve near-perfect metrics on several gazetteer classes because the dev and benchmark datasets were created through silver gazetteer annotation. This creates a circular dependency where rules evaluate themselves. Only Model-Only provides an un-tainted assessment of neural generalizability.
