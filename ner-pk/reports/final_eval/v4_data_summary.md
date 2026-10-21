# v4 Real-Only Dataset Audit & Summary

**Audit Rule:** Real collected text only. 0 synthetic sentences, 0 template-generated sentences, 0 synthetic PII.

## File Metadata & SHA256

| Split | Sentences | Mentions | English | Urdu | JSONL Path | SHA256 |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **train** | 5282 | 8602 | 4970 | 312 | `C:\Users\muham\OneDrive\Desktop\AI-Odyssey\ner-pk\v4\train_real.jsonl` | `32029081b1427dfb3ec0bf94568333d78f83ee89b2df783b3a4456a24451cdab` |
| **dev** | 454 | 740 | 323 | 131 | `C:\Users\muham\OneDrive\Desktop\AI-Odyssey\ner-pk\v4\dev_real.jsonl` | `e18f91170b1b927a932a7ff7f4a9b4f7c8449b92394c4aa9ff45d2b6d8eeddbd` |
| **benchmark** | 615 | 1177 | 615 | 0 | `C:\Users\muham\OneDrive\Desktop\AI-Odyssey\ner-pk\v4\benchmark_real.jsonl` | `ad007eea98ba0c0ff422745e008ab98f8f1efa9d4daa890cb46a3e7c547490ae` |

## Per-Class Mention Counts & Reliability Flags

> **Thresholds:** Train `THIN` if support < 300. Dev/Benchmark `UNRELIABLE` if support < 30.

| Entity Class | Train Count | Train Flag | Dev Count | Dev Flag | Benchmark Count | Benchmark Flag |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `PERSON` | 812 | RELIABLE | 7 | UNRELIABLE | 15 | UNRELIABLE |
| `CITY` | 1119 | RELIABLE | 223 | RELIABLE | 522 | RELIABLE |
| `PROVINCE_REGION` | 668 | RELIABLE | 48 | RELIABLE | 128 | RELIABLE |
| `COUNTRY` | 1103 | RELIABLE | 226 | RELIABLE | 286 | RELIABLE |
| `LANDMARK_FACILITY` | 183 | THIN | 13 | UNRELIABLE | 42 | RELIABLE |
| `GOVERNMENT_BODY` | 678 | RELIABLE | 7 | UNRELIABLE | 3 | UNRELIABLE |
| `POLITICAL_PARTY` | 1182 | RELIABLE | 7 | UNRELIABLE | 5 | UNRELIABLE |
| `ORGANIZATION` | 64 | THIN | 15 | UNRELIABLE | 9 | UNRELIABLE |
| `EDUCATIONAL_INSTITUTION` | 247 | THIN | 10 | UNRELIABLE | 24 | UNRELIABLE |
| `COURT_LEGAL_BODY` | 555 | RELIABLE | 1 | UNRELIABLE | 12 | UNRELIABLE |
| `LAW_ACT` | 148 | THIN | 6 | UNRELIABLE | 1 | UNRELIABLE |
| `EVENT` | 62 | THIN | 4 | UNRELIABLE | 1 | UNRELIABLE |
| `MEDIA_OUTLET` | 425 | RELIABLE | 32 | RELIABLE | 28 | UNRELIABLE |
| `SPORTS_TEAM` | 361 | RELIABLE | 4 | UNRELIABLE | 1 | UNRELIABLE |
| `DATE` | 381 | RELIABLE | 34 | RELIABLE | 41 | RELIABLE |
| `TIME` | 51 | THIN | 0 | UNRELIABLE | 0 | UNRELIABLE |
| `MONEY` | 338 | RELIABLE | 18 | UNRELIABLE | 7 | UNRELIABLE |
| `PERCENT` | 225 | THIN | 85 | RELIABLE | 52 | RELIABLE |
| `PHONE_NUMBER` | 0 | THIN | 0 | UNRELIABLE | 0 | UNRELIABLE |
| `ID_NUMBER` | 0 | THIN | 0 | UNRELIABLE | 0 | UNRELIABLE |
