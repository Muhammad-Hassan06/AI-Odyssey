# Pakistani-Context NER: Corpus Data Statistics (Phase 2)
**Audit Status:** PASSED (Zero Leakage Verified) | **Target Directory:** `ner-pk/v2/`

## 1. Class Distribution Across Splits (V2 Enhanced)

| Entity Type | Train Mentions | Dev Mentions | Benchmark Mentions | Total Mentions | Status (Target Met) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PERSON** | 828 | 7 | 15 | 850 | ⚠️ |
| **CITY** | 2,341 | 448 | 744 | 3,533 | ✅ |
| **PROVINCE_REGION** | 700 | 48 | 128 | 876 | ✅ |
| **COUNTRY** | 1,237 | 226 | 286 | 1,749 | ✅ |
| **LANDMARK_FACILITY** | 188 | 13 | 42 | 243 | ⚠️ |
| **GOVERNMENT_BODY** | 103 | 14 | 9 | 126 | ⚠️ |
| **POLITICAL_PARTY** | 1,203 | 11 | 8 | 1,222 | ⚠️ |
| **ORGANIZATION** | 72 | 15 | 9 | 96 | ❌ |
| **EDUCATIONAL_INSTITUTION** | 375 | 34 | 51 | 460 | ✅ |
| **COURT_LEGAL_BODY** | 784 | 43 | 49 | 876 | ✅ |
| **LAW_ACT** | 362 | 48 | 38 | 448 | ✅ |
| **EVENT** | 204 | 28 | 32 | 264 | ⚠️ |
| **MEDIA_OUTLET** | 533 | 52 | 56 | 641 | ✅ |
| **SPORTS_TEAM** | 496 | 23 | 24 | 543 | ⚠️ |
| **DATE** | 416 | 34 | 41 | 491 | ✅ |
| **TIME** | 264 | 44 | 41 | 349 | ⚠️ |
| **MONEY** | 521 | 45 | 38 | 604 | ✅ |
| **PERCENT** | 234 | 85 | 52 | 371 | ⚠️ |
| **PHONE_NUMBER** | 822 | 86 | 80 | 988 | ✅ |
| **ID_NUMBER** | 842 | 96 | 80 | 1,018 | ✅ |
| **TOTAL MENTIONS** | **13,128** | **1,400** | **1,823** | **16,351** | |

## 2. Dataset Split Sizes & Tiers
- **Train Set:** 7,998 sentences
  - Gold Real Sentences: 3,366
  - High-Confidence Silver Sentences (Tier B): 3,232
  - Real Negative Sentences (0 entities): 600
  - Synthetic PII (Rule 3): 400 (5.00% of Train)
  - Robustness Augmentations: 400
- **Development (Dev) Set:** 887 sentences (100% Gold real text + verified negatives)
- **Held-Out Benchmark Set:** 1,035 sentences (100% Gold real text + verified negatives)
- **Zero-Leakage Document Isolation:** **PASSED (Zero Leakage Verified)**
