# Colab GPU Training Guide (Pakistani-Context NER)

**Notebook:** [`train_colab.ipynb`](train_colab.ipynb)  
**Target Architecture:** `xlm-roberta-base`  
**Dataset:** `v2_frozen/` (if present) or `v2/` (`train.jsonl` = 7,998 sentences, `dev.jsonl` = 887 sentences)  
**Output Checkpoint:** Google Drive `/content/drive/MyDrive/ner_pk_models/best_ner_model_v2` and zip package.

---

## Step 1: Open Notebook in Google Colab
1. Navigate to [Google Colab](https://colab.research.google.com/).
2. Select **File** > **Open Notebook** > **GitHub** (or **Upload** `ner-pk/train_colab.ipynb`).
3. Enter repository: `Muhammad-Hassan06/AI-Odyssey` and open `ner-pk/train_colab.ipynb`.

---

## Step 2: Choose Hardware Accelerator (T4 GPU)
1. In Colab menu bar, click **Runtime** > **Change runtime type**.
2. Under **Hardware accelerator**, select **T4 GPU** (Standard).
3. Click **Save**.

---

## Step 3: Run Cells in Sequence
1. **Cell 0 (Clone Repo & Pull Latest):** Clones the repository and pulls the latest commit.
2. **Cell 1 (Verify Dataset):** Automatically detects `v2_frozen` or `v2`, verifies file presence, counts sentences, and computes sha256 checksums.
3. **Cell 2 (GPU Check):** Verifies CUDA availability on the allocated T4 GPU.
4. **Cell 3 (Install Missing Packages):** Upgrades pip/wheel and installs `seqeval` and `pyyaml` (does **not** downgrade PyTorch, Transformers, or Accelerate).
5. **Cell 4 (Mount Drive):** Connects your Google Drive to save the checkpoint to `/content/drive/MyDrive/ner_pk_models/best_ner_model_v2`.
6. **Cell 5 (Launch Training):**
   - Hyperparameters: Batch size 16, 5 epochs, lr `3e-5`, max length 128, class weights enabled, fp16 enabled, seed 42.
   - **Expected Runtime on T4 GPU:** ~12–15 minutes total (~2.5 minutes per epoch for 7,998 sentences).
7. **Cell 6 (Package Zip):** Automatically packages the final model weights, tokenizer, config, and `training_run_config.json` into `/content/drive/MyDrive/ner_pk_models/best_ner_model_v2.zip`.

---

## Step 4: Download and Place Checkpoint Locally
1. Download `best_ner_model_v2.zip` from your Google Drive.
2. Create directory `ner-pk/models/final/` in your local repository.
3. Unzip the contents into `ner-pk/models/final/`. The directory should contain:
   - `model.safetensors`
   - `config.json`
   - `tokenizer.json`
   - `tokenizer_config.json`
   - `label_map.json`
   - `training_run_config.json`

---

## Step 5: Run Evaluation Locally
```bash
# Model-only evaluation
python src/evaluate.py --data_path v2/dev.jsonl --split dev --mode model --model_path models/final

# Rules-only evaluation
python src/evaluate.py --data_path v2/dev.jsonl --split dev --mode rules

# Hybrid evaluation
python src/evaluate.py --data_path v2/dev.jsonl --split dev --mode hybrid --model_path models/final
```
