# Evaluation Results: Pakistani-Context NER (DEV Split)

| Metric | Strict IOB2 | Relaxed / Partial Overlap |
| :--- | :---: | :---: |
| **Precision** | 90.09% | 91.69% |
| **Recall** | 95.80% | 97.51% |
| **F1 Score** | 92.85% | 94.51% |

## Per-Entity Breakdown (Seqeval Strict)

```
                         precision    recall  f1-score   support

                   CITY     0.9909    0.9602    0.9753       452
                COUNTRY     0.9648    0.9690    0.9669       226
       COURT_LEGAL_BODY     0.9302    0.9302    0.9302        43
                   DATE     0.2519    0.9706    0.4000        34
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
                 PERSON     1.0000    1.0000    1.0000         7
           PHONE_NUMBER     0.8837    0.8837    0.8837        86
        POLITICAL_PARTY     0.9091    0.9091    0.9091        11
        PROVINCE_REGION     0.8727    1.0000    0.9320        48
            SPORTS_TEAM     0.9565    0.9565    0.9565        23
                   TIME     1.0000    1.0000    1.0000        44

              micro avg     0.9009    0.9580    0.9285      1404
              macro avg     0.8993    0.9506    0.9114      1404
           weighted avg     0.9472    0.9580    0.9465      1404

```
