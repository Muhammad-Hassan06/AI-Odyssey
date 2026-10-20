# Evaluation Results: Pakistani-Context NER (BENCHMARK Split)

| Metric | Strict IOB2 | Relaxed / Partial Overlap |
| :--- | :---: | :---: |
| **Precision** | 91.77% | 93.28% |
| **Recall** | 96.28% | 97.87% |
| **F1 Score** | 93.97% | 95.52% |

## Per-Entity Breakdown (Seqeval Strict)

```
                         precision    recall  f1-score   support

                   CITY     0.9529    0.9720    0.9624       750
                COUNTRY     0.9555    0.9755    0.9654       286
       COURT_LEGAL_BODY     0.8214    0.9388    0.8762        49
                   DATE     0.3796    1.0000    0.5503        41
EDUCATIONAL_INSTITUTION     1.0000    0.9804    0.9901        51
                  EVENT     0.7619    0.5000    0.6038        32
        GOVERNMENT_BODY     0.6364    0.7778    0.7000         9
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

              micro avg     0.9177    0.9628    0.9397      1829
              macro avg     0.9081    0.9409    0.9156      1829
           weighted avg     0.9367    0.9628    0.9459      1829

```
