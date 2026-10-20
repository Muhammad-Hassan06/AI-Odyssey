# Path Audit Report: Old & Hard-Coded Data Paths

**Date:** 2026-10-21  
**Auditor:** Senior ML Engineer  
**Total Occurrences Found:** 47

| # | File | Line | Matched Pattern | Code Snippet |
| :--- | :--- | :---: | :--- | :--- |
| 1 | [`COLAB_RUN.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/COLAB_RUN.md#L5) | 5 | `train.jsonl` | `**Dataset:** 'v2_frozen/' (if present) or 'v2/' ('train.jsonl' = 7,998 sentences, 'dev.jsonl' = 887 ` |
| 2 | [`COLAB_RUN.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/COLAB_RUN.md#L53) | 53 | `v2/dev.jsonl` | `python src/evaluate.py --data_path v2/dev.jsonl --split dev --mode model --model_path models/final` |
| 3 | [`COLAB_RUN.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/COLAB_RUN.md#L56) | 56 | `v2/dev.jsonl` | `python src/evaluate.py --data_path v2/dev.jsonl --split dev --mode rules` |
| 4 | [`COLAB_RUN.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/COLAB_RUN.md#L59) | 59 | `v2/dev.jsonl` | `python src/evaluate.py --data_path v2/dev.jsonl --split dev --mode hybrid --model_path models/final` |
| 5 | [`PROGRESS.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/PROGRESS.md#L17) | 17 | `data/processed` | `\| **Phase D** \| Annotation Pipeline & Synthesis \| **COMPLETED** \| ['src/synth.py'](src/synth.py)` |
| 6 | [`README.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/README.md#L61) | 61 | `train.jsonl` | `│   ├── train.jsonl          # 7,998 sentences, 13,128 mentions (5.00% synthetic)` |
| 7 | [`README.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/README.md#L62) | 62 | `dev.jsonl` | `│   ├── dev.jsonl            # 887 sentences, 1,400 mentions (Gold real text)` |
| 8 | [`README.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/README.md#L63) | 63 | `benchmark.jsonl` | `│   ├── benchmark.jsonl      # 1,035 sentences, 1,823 mentions (Gold held-out)` |
| 9 | [`README.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/README.md#L107) | 107 | `v2/benchmark.jsonl` | `python src/evaluate.py --data_path v2/benchmark.jsonl --split benchmark --mode hybrid` |
| 10 | [`README.md`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/README.md#L118) | 118 | `v2/train.jsonl` | `python src/train.py --train_file v2/train.jsonl --dev_file v2/dev.jsonl --output_dir models/best_ner` |
| 11 | [`train_colab.ipynb`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/train_colab.ipynb#L44) | 44 | `train.jsonl` | `"if os.path.exists('v2_frozen/train.jsonl'):\n",` |
| 12 | [`train_colab.ipynb`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/train_colab.ipynb#L46) | 46 | `v2/train.jsonl` | `"elif os.path.exists('v2/train.jsonl'):\n",` |
| 13 | [`train_colab.ipynb`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/train_colab.ipynb#L58) | 58 | `train.jsonl` | `"for split in ['train.jsonl', 'dev.jsonl', 'benchmark.jsonl']:\n",` |
| 14 | [`train_colab.ipynb`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/train_colab.ipynb#L130) | 130 | `train.jsonl` | `"    --train_file \"{DATA_DIR}/train.jsonl\" \\\n",` |
| 15 | [`train_colab.ipynb`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/train_colab.ipynb#L131) | 131 | `dev.jsonl` | `"    --dev_file \"{DATA_DIR}/dev.jsonl\" \\\n",` |
| 16 | [`app/app.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/app/app.py#L30) | 30 | `train.jsonl` | `data_dir = os.path.join(base_dir, "v2_frozen") if os.path.exists(os.path.join(base_dir, "v2_frozen",` |
| 17 | [`scripts/audit_paths.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/audit_paths.py#L6) | 6 | `data/processed` | `r"data/processed",` |
| 18 | [`scripts/audit_paths.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/audit_paths.py#L7) | 7 | `processed/train` | `r"processed/train",` |
| 19 | [`scripts/audit_paths.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/audit_paths.py#L8) | 8 | `processed/dev` | `r"processed/dev",` |
| 20 | [`scripts/audit_paths.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/audit_paths.py#L9) | 9 | `processed/test` | `r"processed/test",` |
| 21 | [`scripts/audit_paths.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/audit_paths.py#L10) | 10 | `data/benchmark` | `r"data/benchmark",` |
| 22 | [`scripts/leakage_and_sanity.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/leakage_and_sanity.py#L17) | 17 | `train.jsonl` | `data_dir = os.path.join(base_dir, "v2_frozen") if os.path.exists(os.path.join(base_dir, "v2_frozen",` |
| 23 | [`scripts/test_conservative_merge.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/test_conservative_merge.py#L13) | 13 | `dev.jsonl` | `dev_path = os.path.join(base_dir, "v2", "dev.jsonl")` |
| 24 | [`scripts/three_mode_eval.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/three_mode_eval.py#L7) | 7 | `v2/dev.jsonl` | `Across v2/dev.jsonl and v2/benchmark.jsonl (read-only).` |
| 25 | [`scripts/three_mode_eval.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/three_mode_eval.py#L282) | 282 | `dev.jsonl` | `dev_path = os.path.join(base_dir, "v2", "dev.jsonl")` |
| 26 | [`scripts/three_mode_eval.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/scripts/three_mode_eval.py#L283) | 283 | `benchmark.jsonl` | `bench_path = os.path.join(base_dir, "v2", "benchmark.jsonl")` |
| 27 | [`src/baseline.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/baseline.py#L89) | 89 | `train.jsonl` | `data_dir = os.path.join(base_dir, "v2_frozen") if os.path.exists(os.path.join(base_dir, "v2_frozen",` |
| 28 | [`src/baseline.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/baseline.py#L92) | 92 | `dev.jsonl` | `parser.add_argument("--data_path", type=str, default=None, help="Path to evaluation JSONL (defaults ` |
| 29 | [`src/baseline.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/baseline.py#L96) | 96 | `dev.jsonl` | `target_data_rel = args.data_path or os.path.join(data_dir, "dev.jsonl")` |
| 30 | [`src/dataset.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/dataset.py#L159) | 159 | `train.jsonl` | `and save train.jsonl, dev.jsonl, benchmark.jsonl with zero leakage.` |
| 31 | [`src/dataset.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/dataset.py#L252) | 252 | `train.jsonl` | `train_path = os.path.join(processed_dir, "train.jsonl")` |
| 32 | [`src/dataset.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/dataset.py#L253) | 253 | `dev.jsonl` | `dev_path = os.path.join(processed_dir, "dev.jsonl")` |
| 33 | [`src/dataset.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/dataset.py#L254) | 254 | `benchmark.jsonl` | `bench_path = os.path.join(benchmark_dir, "benchmark.jsonl")` |
| 34 | [`src/dataset.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/dataset.py#L328) | 328 | `train.jsonl` | `s_train = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "synthetic_train.jsonl"` |
| 35 | [`src/dataset.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/dataset.py#L329) | 329 | `dev.jsonl` | `s_dev = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "synthetic_dev.jsonl")` |
| 36 | [`src/dataset.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/dataset.py#L330) | 330 | `benchmark.jsonl` | `s_bench = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "synthetic_benchmark.js` |
| 37 | [`src/evaluate.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/evaluate.py#L343) | 343 | `train.jsonl` | `data_dir = os.path.join(base_dir, "v2_frozen") if os.path.exists(os.path.join(base_dir, "v2_frozen",` |
| 38 | [`src/review_queue.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/review_queue.py#L191) | 191 | `train.jsonl` | `train_v2 = os.path.join(os.path.dirname(__file__), "..", "v2", "train.jsonl")` |
| 39 | [`src/synth.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/synth.py#L666) | 666 | `train.jsonl` | `train_path = os.path.join(out_dir, "synthetic_train.jsonl")` |
| 40 | [`src/synth.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/synth.py#L667) | 667 | `dev.jsonl` | `dev_path = os.path.join(out_dir, "synthetic_dev.jsonl")` |
| 41 | [`src/synth.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/synth.py#L668) | 668 | `benchmark.jsonl` | `bench_path = os.path.join(out_dir, "synthetic_benchmark.jsonl")` |
| 42 | [`src/train.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/train.py#L141) | 141 | `train.jsonl` | `if os.path.exists(os.path.join(base_dir, "v2_frozen", "train.jsonl")):` |
| 43 | [`src/train.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/train.py#L148) | 148 | `train.jsonl` | `parser.add_argument("--data_dir", type=str, default=default_data_dir, help="Directory containing tra` |
| 44 | [`src/train.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/train.py#L149) | 149 | `train.jsonl` | `parser.add_argument("--train_file", type=str, default=None, help="Explicit path to train.jsonl")` |
| 45 | [`src/train.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/train.py#L150) | 150 | `dev.jsonl` | `parser.add_argument("--dev_file", type=str, default=None, help="Explicit path to dev.jsonl")` |
| 46 | [`src/train.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/train.py#L167) | 167 | `train.jsonl` | `train_rel = args.train_file or os.path.join(args.data_dir, "train.jsonl")` |
| 47 | [`src/train.py`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/train.py#L168) | 168 | `dev.jsonl` | `dev_rel = args.dev_file or os.path.join(args.data_dir, "dev.jsonl")` |
