# 📓 Google Colab Training Runbook (v3 Retraining Package)
**Model Architecture:** `xlm-roberta-base`  
**Dataset Version:** `v3` (`v3/train.jsonl` - 7,997 sents, `v3/dev.jsonl` - 887 sents)  
**Schema:** Strictly 20 Competition Classes (41 BIO labels)  
**Target Hardware:** Google Colab GPU Runtime (T4 / V100 / A100)  

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
> assert os.path.exists("v3/train.jsonl"), "Error: v3/train.jsonl not found! Check directory path."
> ```

---

## ⚙️ Hyperparameter Configuration
- **Model:** `xlm-roberta-base`
- **Epochs:** `8`
- **Learning Rate:** `2.5e-5` (with 10% linear warmup and weight decay `0.01`)
- **Batch Size:** `16` per device
- **Max Sequence Length:** `256`
- **Precision:** `fp16=True` (automatic mixed precision on GPU)
- **Loss Function:** Class-weighted cross-entropy (`o_weight=0.20`, smoothed inverse frequency for rare classes)
- **Checkpoint Selection:** `load_best_model_at_end=True`, `metric_for_best_model="f1"` (strict seqeval micro-F1 on DEV)
- **Library Environment:** Standard modern Google Colab runtime (**NO library downgrades**).

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

print("\nData File Checksums:")
for fname in ["v3/train.jsonl", "v3/dev.jsonl", "v3/benchmark.jsonl"]:
    p = Path(fname)
    assert p.exists(), f"Missing {fname}!"
    print(f"  {fname:<20}: {get_sha256(p)}")
```

### 5. Launch Training
```bash
!python src/train.py \
    --model_name xlm-roberta-base \
    --data_dir v3 \
    --output_dir /content/drive/MyDrive/ner_pk_models_v3/best_model \
    --epochs 8 \
    --lr 2.5e-5 \
    --batch_size 16 \
    --max_length 256 \
    --fp16 \
    --use_class_weights \
    --seed 42
```

### 6. Verify Checkpoint and Package for Download
```python
import os, json
model_dir = "/content/drive/MyDrive/ner_pk_models_v3/best_model"
assert os.path.exists(os.path.join(model_dir, "model.safetensors")), "model.safetensors not found!"
assert os.path.exists(os.path.join(model_dir, "config.json")), "config.json not found!"

# Verify exactly 41 BIO labels
with open(os.path.join(model_dir, "config.json")) as f:
    cfg = json.load(f)
assert len(cfg["id2label"]) == 41, f"Expected 41 labels, got {len(cfg['id2label'])}"
print("Checkpoint strictly verified against 20-class schema!")

# Zip checkpoint for rapid download
!zip -r /content/best_ner_model_v3.zip /content/drive/MyDrive/ner_pk_models_v3/best_model
print("Packaged to /content/best_ner_model_v3.zip")
```

---

## 🛑 Post-Training Decision Rule
Before swapping any model into production:
1. Copy weights to `models/final/`.
2. Run `python scripts/step2_real_model_eval.py` to evaluate on `v3/dev.jsonl`.
3. Checkpoint may only replace current model if:
   - DEV Macro-F1 strictly exceeds **85.87%**
   - DEV Micro-F1 strictly exceeds **91.63%**
   - Inference latency remains under **80ms / sentence** on CPU.
