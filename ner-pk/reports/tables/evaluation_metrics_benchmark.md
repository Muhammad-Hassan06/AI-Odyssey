# Evaluation Results: Pakistani-Context NER (BENCHMARK Split)

| Metric | Strict IOB2 | Relaxed / Partial Overlap |
| :--- | :---: | :---: |
| **Precision** | 92.26% | 93.78% |
| **Recall** | 96.45% | 98.03% |
| **F1 Score** | 94.31% | 95.86% |

## Per-Entity Breakdown (Seqeval Strict)

```
                         precision    recall  f1-score   support

                   CITY     0.9529    0.9720    0.9624       750
                COUNTRY     0.9559    0.9860    0.9707       286
       COURT_LEGAL_BODY     0.9388    0.9388    0.9388        49
                   DATE     0.3796    1.0000    0.5503        41
EDUCATIONAL_INSTITUTION     1.0000    0.9804    0.9901        51
                  EVENT     0.7619    0.5000    0.6038        32
        GOVERNMENT_BODY     0.8750    0.7778    0.8235         9
              ID_NUMBER     1.0000    1.0000    1.0000        80
      LANDMARK_FACILITY     1.0000    1.0000    1.0000        42
                LAW_ACT     1.0000    0.9737    0.9867        38
           MEDIA_OUTLET     1.0000    1.0000    1.0000        56
                  MONEY     1.0000    1.0000    1.0000        38
           ORGANIZATION     1.0000    1.0000    1.0000         9
                PERCENT     1.0000    1.0000    1.0000        52
                 PERSON     1.0000    1.0000    1.0000        15
           PHONE_NUMBER     0.8250    0.8250    0.8250        80
        POLITICAL_PARTY     1.0000    1.0000    1.0000         8
        PROVINCE_REGION     0.9552    1.0000    0.9771       128
            SPORTS_TEAM     0.8750    0.8750    0.8750        24
                   TIME     1.0000    1.0000    1.0000        41

              micro avg     0.9226    0.9645    0.9431      1829
              macro avg     0.9260    0.9414    0.9252      1829
           weighted avg     0.9411    0.9645    0.9490      1829

```
