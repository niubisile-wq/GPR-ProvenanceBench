# 4TU Task Baseline: Construction workers

Rows: 93
Seed: 20260810

## Split Counts

| split | count |
| --- | ---: |
| train | 54 |
| val | 15 |
| test | 24 |

## Label Counts

| label | count |
| --- | ---: |
| None | 24 |
| New installation of utilities | 51 |
| Replacement and new installation of utilities | 10 |
| Replacement of utilities | 8 |

## Split Label Coverage

Viable smoke target: `True`
Reason: `ok`

| split | class_count | label_counts |
| --- | ---: | --- |
| train | 2 | `{'None': 24, 'New installation of utilities': 30}` |
| val | 2 | `{'New installation of utilities': 7, 'Replacement of utilities': 8}` |
| test | 2 | `{'New installation of utilities': 14, 'Replacement and new installation of utilities': 10}` |

## Model Comparison

| model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |
| --- | ---: | ---: | ---: | ---: |
| dummy_majority | 0.500 | 0.500 | 0.318 | 0.368 |
| extra_trees | 0.143 | 0.000 | 0.148 | 0.000 |
| rbf_svm | 0.286 | 0.107 | 0.222 | 0.105 |

## Boundary

This is a 4TU task-metadata smoke baseline. It uses activity-level labels
and fixed matrix summary features, so it supports protocol development but
does not establish the final raw-trace counterfactual claim.
