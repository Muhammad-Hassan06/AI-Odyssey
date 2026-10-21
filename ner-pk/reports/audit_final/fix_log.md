# Rule, Gazetteer, and Merge Fix Log (DEV-Guided)

**Date:** 21 October 2026  
**Evaluation Split:** `v3/dev.jsonl` (887 sentences, 1,388 entities)  

## 1. Summary of Changes and DEV Impact

| Fix / Component | Before Fix (DEV) | After Fix (DEV) | Macro F1 Delta | Decision | Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **DATE Pattern Hardening** | 101 False Positives | 25 False Positives | +0.42% Macro F1 | **KEPT** | Eliminates bare weekday and lowercase spurious matches |
| **EVENT Gazetteer Expansion** | 77.78% Rule Recall | 98.25% Rule Recall | +0.58% Macro F1 | **KEPT** | Captures Pakistani events (PSL 10, Federal Budget 2025-26) |
| **Conservative Confidence Merge** | Macro F1: 85.74% | Macro F1: 85.87% | +0.12% | **KEPT** | Suppresses low-confidence hallucinations on open-domain classes |

## 2. Before vs After Comprehensive Metric Comparison on DEV

| Metric | Model-Only | Baseline Conservative Hybrid | Tuned Conservative Hybrid | Delta (Tuned vs Baseline) |
| :--- | :---: | :---: | :---: | :---: |
| **Micro Precision** | 84.41% | 85.30% | 85.56% | +0.27% |
| **Micro Recall** | 93.23% | 98.63% | 98.63% | +0.00% |
| **Micro F1** | 88.60% | 91.48% | 91.63% | +0.15% |
| **Macro F1** | 81.26% | 85.74% | 85.87% | +0.12% |

