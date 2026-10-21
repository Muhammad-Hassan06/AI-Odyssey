# Live Evaluation Report: Real-Only Data (`v4`)

**Evaluation Constraint:** Evaluated on real collected text only (`v4/dev_real.jsonl` and `v4/benchmark_real.jsonl`).
**Benchmark Status:** Internal silver benchmark, real text only, 0 human-gold sentences.

## DEV Split (`v4/dev_real.jsonl`)

| Mode | Precision | Recall | Micro F1 | 95% CI (Micro) | Macro F1 | 95% CI (Macro) | Ex-PII F1 | Token Acc | Exact-Match Sent Acc |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model-Only (XLM-R Checkpoint)** | 77.17% | 89.05% | **82.69%** | [77.50, 84.95] | **60.06%** | [32.48, 64.76] | 82.69% | 97.53% | 68.06% |
| **Rules-Only (Regex + Gazetteers)** | 92.24% | 97.97% | **95.02%** | [88.56, 96.45] | **80.78%** | [41.05, 82.56] | 95.02% | 99.35% | 89.21% |
| **Old Hybrid (Model Overrides Rules)** | 77.42% | 96.35% | **85.85%** | [79.21, 87.46] | **64.26%** | [34.77, 68.42] | 85.85% | 97.81% | 71.59% |
| **Conservative Hybrid (Rules Priority)** | 78.94% | 98.24% | **87.54%** | [81.02, 90.01] | **67.31%** | [35.89, 71.44] | 87.54% | 97.99% | 73.35% |

## BENCHMARK Split (`v4/benchmark_real.jsonl` - Internal Silver Benchmark)

| Mode | Precision | Recall | Micro F1 | 95% CI (Micro) | Macro F1 | 95% CI (Macro) | Ex-PII F1 | Token Acc | Exact-Match Sent Acc |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model-Only (XLM-R Checkpoint)** | 72.52% | 92.61% | **81.34%** | [76.70, 83.14] | **52.65%** | [35.62, 55.49] | 81.34% | 96.96% | 58.05% |
| **Rules-Only (Regex + Gazetteers)** | 91.52% | 99.07% | **95.14%** | [87.81, 97.49] | **80.20%** | [49.40, 81.55] | 95.14% | 99.37% | 87.15% |
| **Old Hybrid (Model Overrides Rules)** | 70.83% | 95.92% | **81.49%** | [74.65, 83.73] | **54.14%** | [36.64, 57.33] | 81.49% | 96.88% | 58.05% |
| **Conservative Hybrid (Rules Priority)** | 73.10% | 98.81% | **84.03%** | [76.74, 86.28] | **60.51%** | [38.65, 63.60] | 84.03% | 97.24% | 60.33% |

## Dev Per-Class Metrics: Winning Mode (`rules_only`)

| Class | Precision | Recall | F1-Score | Support | Reliability | 95% Bootstrap CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `PERSON` | 75.00% | 85.71% | **80.00%** | 7 | `UNRELIABLE` | [0.00, 100.00] |
| `CITY` | 99.55% | 99.10% | **99.33%** | 223 | `RELIABLE` | [99.02, 100.00] |
| `PROVINCE_REGION` | 94.12% | 100.00% | **96.97%** | 48 | `RELIABLE` | [86.96, 100.00] |
| `COUNTRY` | 90.12% | 96.90% | **93.39%** | 226 | `RELIABLE` | [74.70, 96.80] |
| `LANDMARK_FACILITY` | 81.25% | 100.00% | **89.66%** | 13 | `UNRELIABLE` | [0.00, 100.00] |
| `GOVERNMENT_BODY` | 87.50% | 100.00% | **93.33%** | 7 | `UNRELIABLE` | [0.00, 100.00] |
| `POLITICAL_PARTY` | 100.00% | 100.00% | **100.00%** | 7 | `UNRELIABLE` | [0.00, 100.00] |
| `ORGANIZATION` | 100.00% | 100.00% | **100.00%** | 15 | `UNRELIABLE` | [0.00, 100.00] |
| `EDUCATIONAL_INSTITUTION` | 100.00% | 100.00% | **100.00%** | 10 | `UNRELIABLE` | [0.00, 100.00] |
| `COURT_LEGAL_BODY` | 100.00% | 100.00% | **100.00%** | 1 | `UNRELIABLE` | [0.00, 100.00] |
| `LAW_ACT` | 100.00% | 100.00% | **100.00%** | 6 | `UNRELIABLE` | [0.00, 100.00] |
| `EVENT` | 100.00% | 100.00% | **100.00%** | 4 | `UNRELIABLE` | [0.00, 100.00] |
| `MEDIA_OUTLET` | 94.12% | 100.00% | **96.97%** | 32 | `RELIABLE` | [50.00, 100.00] |
| `SPORTS_TEAM` | 100.00% | 100.00% | **100.00%** | 4 | `UNRELIABLE` | [0.00, 100.00] |
| `DATE` | 53.70% | 85.29% | **65.91%** | 34 | `RELIABLE` | [34.77, 84.00] |
| `TIME` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `MONEY` | 100.00% | 100.00% | **100.00%** | 18 | `UNRELIABLE` | [0.00, 100.00] |
| `PERCENT` | 100.00% | 100.00% | **100.00%** | 85 | `RELIABLE` | [0.00, 100.00] |
| `PHONE_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `ID_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |

## Dev Per-Class Metrics: Model-Only Checkpoint (`model_only`)

| Class | Precision | Recall | F1-Score | Support | Reliability | 95% Bootstrap CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `PERSON` | 15.79% | 85.71% | **26.67%** | 7 | `UNRELIABLE` | [0.00, 37.21] |
| `CITY` | 92.89% | 99.55% | **96.10%** | 223 | `RELIABLE` | [90.32, 100.00] |
| `PROVINCE_REGION` | 73.33% | 91.67% | **81.48%** | 48 | `RELIABLE` | [76.92, 100.00] |
| `COUNTRY` | 83.79% | 93.81% | **88.52%** | 226 | `RELIABLE` | [74.81, 92.91] |
| `LANDMARK_FACILITY` | 41.94% | 100.00% | **59.09%** | 13 | `UNRELIABLE` | [0.00, 88.12] |
| `GOVERNMENT_BODY` | 80.00% | 57.14% | **66.67%** | 7 | `UNRELIABLE` | [0.00, 66.67] |
| `POLITICAL_PARTY` | 66.67% | 85.71% | **75.00%** | 7 | `UNRELIABLE` | [0.00, 90.91] |
| `ORGANIZATION` | 66.67% | 80.00% | **72.73%** | 15 | `UNRELIABLE` | [0.00, 87.50] |
| `EDUCATIONAL_INSTITUTION` | 72.73% | 80.00% | **76.19%** | 10 | `UNRELIABLE` | [0.00, 100.00] |
| `COURT_LEGAL_BODY` | 33.33% | 100.00% | **50.00%** | 1 | `UNRELIABLE` | [0.00, 66.67] |
| `LAW_ACT` | 75.00% | 100.00% | **85.71%** | 6 | `UNRELIABLE` | [0.00, 100.00] |
| `EVENT` | 80.00% | 100.00% | **88.89%** | 4 | `UNRELIABLE` | [0.00, 100.00] |
| `MEDIA_OUTLET` | 72.73% | 100.00% | **84.21%** | 32 | `RELIABLE` | [40.00, 96.55] |
| `SPORTS_TEAM` | 40.00% | 100.00% | **57.14%** | 4 | `UNRELIABLE` | [0.00, 66.67] |
| `DATE` | 53.12% | 50.00% | **51.52%** | 34 | `RELIABLE` | [18.16, 73.99] |
| `TIME` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `MONEY` | 57.14% | 88.89% | **69.57%** | 18 | `UNRELIABLE` | [0.00, 69.77] |
| `PERCENT` | 86.67% | 61.18% | **71.72%** | 85 | `RELIABLE` | [0.00, 76.92] |
| `PHONE_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |
| `ID_NUMBER` | 0.00% | 0.00% | **0.00%** | 0 | `UNRELIABLE` | [0.00, 0.00] |

## Methodological Disclosure on Rule Circularity

Rules-only and Hybrid modes achieve near-perfect metrics on several gazetteer classes because the dev and benchmark datasets were created through silver gazetteer annotation. This creates a circular dependency where rules evaluate themselves. Only Model-Only provides an un-tainted assessment of neural generalizability.
