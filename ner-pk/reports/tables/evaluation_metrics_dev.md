# Evaluation Results: Pakistani-Context NER (DEV Split)

| Metric | Strict IOB2 | Relaxed / Partial Overlap |
| :--- | :---: | :---: |
| **Precision** | 89.40% | 90.13% |
| **Recall** | 97.00% | 97.79% |
| **F1 Score** | 93.05% | 93.80% |

## Per-Entity Breakdown (Seqeval Strict)

```
                         precision    recall  f1-score   support

                   CITY     0.9909    0.9688    0.9797       448
                COUNTRY     0.8831    0.9690    0.9241       226
       COURT_LEGAL_BODY     1.0000    1.0000    1.0000        43
                   DATE     0.2463    0.9706    0.3929        34
EDUCATIONAL_INSTITUTION     1.0000    0.9706    0.9851        34
                  EVENT     0.7500    0.5357    0.6250        28
        GOVERNMENT_BODY     0.7000    1.0000    0.8235        14
              ID_NUMBER     1.0000    0.9896    0.9948        96
      LANDMARK_FACILITY     0.8125    1.0000    0.8966        13
                LAW_ACT     1.0000    0.9375    0.9677        48
           MEDIA_OUTLET     0.9630    1.0000    0.9811        52
                  MONEY     1.0000    1.0000    1.0000        45
           ORGANIZATION     1.0000    1.0000    1.0000        15
                PERCENT     1.0000    1.0000    1.0000        85
                 PERSON     0.7500    0.8571    0.8000         7
           PHONE_NUMBER     1.0000    1.0000    1.0000        86
        POLITICAL_PARTY     0.9091    0.9091    0.9091        11
        PROVINCE_REGION     0.8571    1.0000    0.9231        48
            SPORTS_TEAM     1.0000    1.0000    1.0000        23
                   TIME     1.0000    1.0000    1.0000        44

              micro avg     0.8940    0.9700    0.9305      1400
              macro avg     0.8931    0.9554    0.9101      1400
           weighted avg     0.9419    0.9700    0.9494      1400

```
