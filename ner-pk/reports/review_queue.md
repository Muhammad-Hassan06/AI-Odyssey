# Human-in-the-Loop Review Queue Summary (Phase 3)

- **Total Sentences Screened:** 7,998
- **Sentences Flagged for Verification:** 2,473 (30.9%)
- **Export File (Label Studio Format):** [`C:\Users\muham\OneDrive\Desktop\AI-Odyssey\ner-pk\src\..\annotation\review_queue_label_studio.json`](file:///C:/Users/muham/OneDrive/Desktop/AI-Odyssey/ner-pk/src/../annotation/review_queue_label_studio.json)

## 1. Flagging Criteria & Breakdown

| Trigger Criteria | Sentences / Events Flagged | Description |
| :--- | :--- | :--- |
| **Rare Class Instances** | 1976 | Sentences containing LAW_ACT, COURT_LEGAL_BODY, EDU, MEDIA, SPORTS |
| **Rule vs Annotation Confusions** | 632 | Disagreements between gazetteer/rule layer and annotation |
| **Unannotated Candidate Entities** | 88 | High-confidence patterns detected by rules but absent in silver tags |
| **Boundary Edge Cases** | 0 | Trailing punctuation or possessive clitics requiring human sign-off |

## 2. Rare Class Verification Tally

| Entity Type | Total Instances Queued for Audit |
| :--- | :--- |
| `COURT_LEGAL_BODY` | 784 |
| `EDUCATIONAL_INSTITUTION` | 375 |
| `LAW_ACT` | 362 |
| `MEDIA_OUTLET` | 533 |
| `SPORTS_TEAM` | 496 |

## 3. Label Studio Import Instructions

1. Open Label Studio (`localhost:8080`) and create project `Pakistani-NER-Phase3-Review`.
2. Configure labeling interface with the standard 20 entity classes.
3. Upload `review_queue_label_studio.json` via the UI or Label Studio REST API.
4. Annotators inspect pre-populated spans in `predictions` and accept or correct flagged instances.
