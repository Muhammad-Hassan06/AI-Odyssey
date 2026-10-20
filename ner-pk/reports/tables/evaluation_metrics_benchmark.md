# Evaluation Results: Pakistani-Context NER (BENCHMARK Split)

| Metric | Strict IOB2 | Relaxed / Partial Overlap |
| :--- | :---: | :---: |
| **Precision** | 91.02% | 91.48% |
| **Recall** | 98.46% | 98.96% |
| **F1 Score** | 94.60% | 95.07% |

## Per-Entity Breakdown (Seqeval Strict)

```
                         precision    recall  f1-score   support

                   CITY     0.9529    0.9798    0.9662       744
                COUNTRY     0.9088    0.9755    0.9410       286
       COURT_LEGAL_BODY     1.0000    1.0000    1.0000        49
                   DATE     0.3280    1.0000    0.4940        41
EDUCATIONAL_INSTITUTION     1.0000    0.9804    0.9901        51
                  EVENT     0.8438    0.8438    0.8438        32
        GOVERNMENT_BODY     0.6000    1.0000    0.7500         9
              ID_NUMBER     1.0000    1.0000    1.0000        80
      LANDMARK_FACILITY     1.0000    1.0000    1.0000        42
                LAW_ACT     1.0000    1.0000    1.0000        38
           MEDIA_OUTLET     1.0000    1.0000    1.0000        56
                  MONEY     1.0000    1.0000    1.0000        38
           ORGANIZATION     0.8182    1.0000    0.9000         9
                PERCENT     1.0000    1.0000    1.0000        52
                 PERSON     1.0000    1.0000    1.0000        15
           PHONE_NUMBER     1.0000    1.0000    1.0000        80
        POLITICAL_PARTY     1.0000    1.0000    1.0000         8
        PROVINCE_REGION     0.8889    1.0000    0.9412       128
            SPORTS_TEAM     1.0000    1.0000    1.0000        24
                   TIME     1.0000    1.0000    1.0000        41

              micro avg     0.9102    0.9846    0.9460      1823
              macro avg     0.9170    0.9890    0.9413      1823
           weighted avg     0.9380    0.9846    0.9567      1823

```
