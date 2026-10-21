# 🚀 TechFest NER Challenge: Test-Day Operational Runbook
**Target Dates:** 21 October 2026 (Organizer Test File Tonight) & 22 October 2026 (Hidden Benchmark Tomorrow)  
**System Checkpoint:** `models/final/` (`xlm-roberta-base`, 5 epochs on Pakistani NER data)  
**Model Checksum (SHA256):** `4189db7276ee7c2cf7eff1be39e21e79df33adb8f43d9df6aef15b7ef9e016d8`  
**Default Production Mode:** `hybrid` (Tuned Conservative Hybrid Merge)  

---

## ⚡ Emergency Decision Rule (CRITICAL)
> [!IMPORTANT]
> **DO NOT SWAP OR RETRAIN THE MODEL TONIGHT** unless:
> 1. A newly retrained model strictly outperforms the current checkpoint on DEV Macro-F1 (>85.87%) AND Micro-F1 (>91.63%).
> 2. The new checkpoint is verified with `python scripts/validate_schema.py` and has zero missing weights.
> 3. Sufficient time remains to run full end-to-end regression tests before the organizer submission window closes.
>
> If there is any doubt or tight deadline: **Submit with the current verified checkpoint via Conservative Hybrid (`--mode hybrid`).**

---

## 📋 Step-by-Step Execution Protocol

### Step 1: Ingest Incoming Test File
When the organizer file arrives, place it into `data/test/` (e.g. `data/test/organizer_test.csv` or `.txt`, `.jsonl`, `.json`, `.conll`, `.xlsx`).
Run the informational leakage check to inspect domain shift:
```powershell
python scripts/check_organizer_leakage.py data/test/organizer_test.csv
```
*(Note: Never add or leak test sentences into training data!)*

---

### Step 2: Run Unified Predictor
The pipeline automatically detects file formats (`.txt`, `.csv`, `.jsonl`, `.json`, `.conll`, `.xlsx`), preserves all row IDs in exact order, applies sliding-window tokenization on long text, and generates all standard formats (`_spans.json`, `.jsonl`, `.conll`, `.csv`):

```powershell
# Standard production execution (Conservative Hybrid):
python predict.py data/test/organizer_test.csv --output_dir submission/ --mode hybrid
```

#### Fallback Modes if Necessary:
- **Fast CPU Rules-Only Fallback** (if GPU memory exhausted or rapid turnaround needed):
  ```powershell
  python predict.py data/test/organizer_test.csv --output_dir submission/ --mode rules
  ```
- **Pure Transformer Mode**:
  ```powershell
  python predict.py data/test/organizer_test.csv --output_dir submission/ --mode model
  ```

---

### Step 3: Strictly Validate Submission
Before submitting anything to the portal, execute the validator to verify 100% compliance:
```powershell
python validate_submission.py data/test/organizer_test.csv submission/organizer_test_hybrid.jsonl
```
The validator strictly asserts:
1. `row_count`: Exactly matches input count (0 dropped rows).
2. `row_ids`: 100% identical in original sequence.
3. `schema`: Only the 20 allowed entity classes exist.
4. `bio_tags`: Valid IOB2 transition structure.
5. `spans`: Character offsets strictly inside text bounds and text slices match.

---

### Step 4: Package and Archive Submission
Zip the validated output artifacts:
```powershell
Compress-Archive -Path submission/organizer_test_hybrid.* -DestinationPath submission_final.zip -Force
```

---

## ⏱️ Expected Throughput & Benchmarks

| Device | Mode | Sentences / sec | Tokens / sec | Estimated Time (1,000 sents) | Estimated Time (5,000 sents) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **CPU (12th Gen Intel/AMD)** | `hybrid` | ~12 - 15 s/s | ~350 - 450 t/s | ~70 seconds | ~5.5 minutes |
| **CPU** | `rules` | ~150 - 200 s/s | ~4,500 t/s | ~5 seconds | ~25 seconds |
| **GPU (T4 / RTX)** | `hybrid` | ~80 - 110 s/s | ~2,500 t/s | ~10 seconds | ~50 seconds |

---

## ✅ Pre-Flight Test-Day Checklist
- [x] Checkpoint present in `models/final/` with valid SHA256 checksum.
- [x] All 20 classes verified in `src/constants.py` and `config.json`.
- [x] `predict.py` auto-detection tested on all 6 file extensions (.txt, .csv, .jsonl, .json, .conll, .xlsx).
- [x] Sliding window verified for sentences exceeding 256 subwords.
- [x] Empty and whitespace lines preserved without row drops.
- [x] Urdu RTL, Roman Urdu, and mixed scripts tested without Unicode crashes.
- [x] Unit test suite passed (`pytest tests/test_submission_pipeline.py -v`).
