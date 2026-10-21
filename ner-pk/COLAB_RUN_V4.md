# 📓 Google Colab Training Runbook (`v4` Real-Only Retraining Package)

**Model Architecture:** `xlm-roberta-base`  
**Dataset Version:** `v4` Real-Only Text (`v4/train_real.jsonl` - 5,282 sents, `v4/dev_real.jsonl` - 454 sents)  
**Schema:** Strictly 20 Competition Classes (41 BIO labels)  
**Target Hardware:** Google Colab GPU Runtime (T4 / V100 / A100)  
**Target Output Folder:** Google Drive `best_ner_model_v4`  

---

## ⚠️ CRITICAL WARNING: Nested Git Clone Path

> [!CAUTION]
> When cloning the repository in Colab, executing duplicate clone commands creates a nested subfolder:  
> `/content/AI-Odyssey/ner-pk/AI-Odyssey/ner-pk/`  
> **Always verify your working directory before running training:**
> ```python
> import os
> os.chdir("/content/AI-Odyssey/ner-pk")
> print("Current Working Directory:", os.getcwd())
> assert not os.path.exists("/content/AI-Odyssey/ner-pk/AI-Odyssey/ner-pk"), "Duplicate clone detected!"
> assert os.path.exists("v4/train_real.jsonl"), "Error: v4/train_real.jsonl not found! Check directory path."
> ```

---

## ⚙️ Hyperparameter Configuration

- **Pretrained Backbone:** `xlm-roberta-base`
- **Training Epochs:** `8`
- **Learning Rate:** `2.5e-5` (with 10% linear warmup and weight decay `0.01`)
- **Per-Device Batch Size:** `16`
- **Max Sequence Length:** `256`
- **Mixed Precision:** `fp16=True` (automatic mixed precision on GPU)
- **Class Imbalance Handling:** Class-weighted cross-entropy loss (`o_weight=0.20`, smoothed inverse frequency for rare classes)
- **Checkpoint Selection:** `load_best_model_at_end=True`, `metric_for_best_model="f1"` (strict seqeval micro-F1 on `dev_real`)
- **Random Seed:** `42` (fixed deterministic seed)
- **Train-Only Augmentation:** `--augment_casing` (5% ALL-CAPS and 5% lowercase copies of real sentences; dev and benchmark remain 100% untouched real text)
- **PII Handling:** `--include_synthetic_pii` flag is available but **OFF by default**. Real text contains 0 PII sentences; `PHONE_NUMBER` and `ID_NUMBER` are handled strictly via deterministic regex rules in hybrid inference.
- **Library Environment:** Standard modern Google Colab runtime (**NO library downgrades**).

---

## 📁 Dataset Integrity & Checksums (`v4`)

| Split / File Path | Sentence Count | Mention Count | SHA256 Checksum |
| :--- | :---: | :---: | :--- |
| `v4/train_real.jsonl` | 5,282 | 8,602 | `32029081b1427dfb3ec0bf94568333d78f83ee89b2df783b3a4456a24451cdab` |
| `v4/dev_real.jsonl` | 454 | 740 | `e18f91170b1b927a932a7ff7f4a9b4f7c8449b92394c4aa9ff45d2b6d8eeddbd` |
| `v4/benchmark_real.jsonl` | 615 | 1,177 | `ad007eea98ba0c0ff422745e008ab98f8f1efa9d4daa890cb46a3e7c547490ae` |

---

## 🚀 Execution Steps in Google Colab

### 1. Select GPU Runtime
Go to `Runtime` -> `Change runtime type` -> `T4 GPU` (or A100/V100).

### 2. Mount Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

### 3. Clone Repository and Validate Directory
```bash
%cd /content
!git clone https://github.com/Muhammad-Hassan06/AI-Odyssey.git
%cd /content/AI-Odyssey/ner-pk
!pwd
```

### 4. Verify Library Versions and Data Checksums
```python
import hashlib, torch, transformers, seqeval
from pathlib import Path

def get_sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print(f"PyTorch Version:      {torch.__version__} (CUDA: {torch.cuda.is_available()})")
print(f"Transformers Version: {transformers.__version__}")
print(f"Seqeval Version:      {seqeval.__version__}")

print("\nv4 Real-Only Data Checksums:")
for fname in ["v4/train_real.jsonl", "v4/dev_real.jsonl", "v4/benchmark_real.jsonl"]:
    p = Path(fname)
    assert p.exists(), f"Missing {fname}!"
    print(f"  {fname:<26}: {get_sha256(p)}")
```

### 5. Validate Schema
```bash
!python scripts/validate_schema.py v4/train_real.jsonl
!python scripts/validate_schema.py v4/dev_real.jsonl
!python scripts/validate_schema.py v4/benchmark_real.jsonl
```

### 6. Launch Training
```bash
!python src/train.py \
    --model_name xlm-roberta-base \
    --data_dir v4 \
    --train_file v4/train_real.jsonl \
    --dev_file v4/dev_real.jsonl \
    --output_dir /content/drive/MyDrive/best_ner_model_v4 \
    --epochs 8 \
    --lr 2.5e-5 \
    --batch_size 16 \
    --max_length 256 \
    --fp16 \
    --use_class_weights \
    --augment_casing \
    --seed 42
```

### 7. Verify Checkpoint and Package for Download
```python
import os, json
model_dir = "/content/drive/MyDrive/best_ner_model_v4"
assert os.path.exists(os.path.join(model_dir, "model.safetensors")), "model.safetensors missing!"
assert os.path.exists(os.path.join(model_dir, "config.json")), "config.json missing!"

with open(os.path.join(model_dir, "config.json")) as f:
    cfg = json.load(f)
assert len(cfg["id2label"]) == 41, f"Expected 41 labels, got {len(cfg['id2label'])}"
print("✔ Checkpoint verified: 41 BIO labels strictly matching 20 competition classes!")

!zip -r /content/best_ner_model_v4.zip /content/drive/MyDrive/best_ner_model_v4
```

---

## ⚖️ Model-Swap Decision Rule

> [!IMPORTANT]
> **DO NOT automatically overwrite `models/final/`.**  
> Swap `models/final/` with the newly trained checkpoint ONLY IF all three conditions are satisfied:
> 1. **DEV Generalization Superiority:** The new checkpoint must beat the current checkpoint on `v4/dev_real.jsonl`:
>    - **Current Checkpoint Baseline (Live Computed):**
>      - Macro-F1: **60.06%**
>      - Micro-F1: **82.69%**
>    - The new checkpoint must achieve **Macro-F1 > 60.06%** AND **Micro-F1 > 82.69%**.
> 2. **Schema & Tag Integrity:** The new model config and predictions must pass `scripts/validate_schema.py` with 100% validity and 0 unknown tags.
> 3. **Auditor Explicit Approval:** You must manually inspect the live dev evaluation and approve the replacement.

---

## 📦 Git Commands to Push `v4/` and Notebooks to GitHub

Run these commands from your local machine to push the new data and training files to your remote repository so Colab can pull them:

```bash
git add v4/ train_colab_v4.ipynb COLAB_RUN_V4.md src/train.py
git commit -m "Add v4 real-only data splits, Colab v4 retraining package, and train casing augmentation"
git push origin main
```
