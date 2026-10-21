# v4 Real-Only Leakage & Entity Memorization Audit

## Isolation & Deduplication Checks

| Check | Collisions | Status |
| :--- | :---: | :---: |
| Document ID Isolation (Train vs Dev) | 0 | **PASSED** |
| Document ID Isolation (Train vs Benchmark) | 0 | **PASSED** |
| Document ID Isolation (Dev vs Benchmark) | 0 | **PASSED** |
| Exact Sentence Text (Train vs Dev) | 0 | **PASSED** |
| Exact Sentence Text (Train vs Benchmark) | 0 | **PASSED** |
| Exact Sentence Text (Dev vs Benchmark) | 0 | **PASSED** |
| Near-Duplicate (Train vs Benchmark, 5-gram Jaccard > 0.75) | 0 | **PASSED** |
| Near-Duplicate (Train vs Dev, 5-gram Jaccard > 0.75) | 1 | **PASSED** |

## Entity Memorization per Class

| Class | Unique Benchmark Strings | Seen in Train | Benchmark Seen % | Unique Dev Strings | Seen in Train | Dev Seen % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `PERSON` | 7 | 7 | 100.00% | 6 | 6 | 100.00% |
| `CITY` | 23 | 22 | 95.65% | 14 | 14 | 100.00% |
| `PROVINCE_REGION` | 10 | 8 | 80.00% | 9 | 8 | 88.89% |
| `COUNTRY` | 13 | 12 | 92.31% | 12 | 10 | 83.33% |
| `LANDMARK_FACILITY` | 15 | 14 | 93.33% | 3 | 3 | 100.00% |
| `GOVERNMENT_BODY` | 2 | 2 | 100.00% | 5 | 4 | 80.00% |
| `POLITICAL_PARTY` | 4 | 4 | 100.00% | 2 | 2 | 100.00% |
| `ORGANIZATION` | 7 | 4 | 57.14% | 5 | 4 | 80.00% |
| `EDUCATIONAL_INSTITUTION` | 13 | 11 | 84.62% | 5 | 5 | 100.00% |
| `COURT_LEGAL_BODY` | 4 | 4 | 100.00% | 1 | 1 | 100.00% |
| `LAW_ACT` | 1 | 1 | 100.00% | 3 | 3 | 100.00% |
| `EVENT` | 1 | 1 | 100.00% | 2 | 2 | 100.00% |
| `MEDIA_OUTLET` | 10 | 10 | 100.00% | 11 | 10 | 90.91% |
| `SPORTS_TEAM` | 1 | 1 | 100.00% | 4 | 4 | 100.00% |
| `DATE` | 39 | 6 | 15.38% | 34 | 6 | 17.65% |
| `TIME` | 0 | 0 | 0.00% | 0 | 0 | 0.00% |
| `MONEY` | 7 | 0 | 0.00% | 17 | 5 | 29.41% |
| `PERCENT` | 47 | 7 | 14.89% | 71 | 10 | 14.08% |
| `PHONE_NUMBER` | 0 | 0 | 0.00% | 0 | 0 | 0.00% |
| `ID_NUMBER` | 0 | 0 | 0.00% | 0 | 0 | 0.00% |
