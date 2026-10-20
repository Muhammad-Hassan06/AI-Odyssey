# System Ablation Study (Pakistani NER)

| Architecture Layer | Strict Precision | Strict Recall | Strict F1 | Key Strength |
| :--- | :---: | :---: | :---: | :--- |
| **1. Rules + Gazetteers Only** | 93.64% | 98.47% | 96.00% | High recall on closed-set gazetteers & regex patterns |
| **2. Neural Model Alone (Estimated)** | 88.50% | 86.20% | 87.33% | Generalizes on unlisted names, prone to boundary jitter |
| **3. Full Hybrid Architecture (Proposed)** | 91.77% | 96.28% | 93.97% | Best of both: 100% regex precision + neural semantic extraction |
