# 4TU Task Baseline: Utility crossing

Rows: 84
Seed: 20260810

## Split Counts

| split | count |
| --- | ---: |
| train | 48 |
| val | 15 |
| test | 21 |

## Label Counts

| label | count |
| --- | ---: |
| No | 78 |
| Yes | 6 |

## Split Label Coverage

Viable smoke target: `True`
Reason: `ok`

| split | class_count | label_counts |
| --- | ---: | --- |
| train | 2 | `{'No': 44, 'Yes': 4}` |
| val | 2 | `{'No': 14, 'Yes': 1}` |
| test | 2 | `{'No': 20, 'Yes': 1}` |

## Model Comparison

| model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |
| --- | ---: | ---: | ---: | ---: |
| dummy_majority | 0.500 | 0.500 | 0.483 | 0.488 |
| extra_trees | 0.500 | 0.425 | 0.483 | 0.447 |
| rbf_svm | 0.464 | 0.850 | 0.464 | 0.537 |

## Boundary

This is a 4TU task-metadata smoke baseline. It uses activity-level labels
and fixed matrix summary features, so it supports protocol development but
does not establish the final raw-trace counterfactual claim.
