# 4TU Task Baseline: Relative groundwater level

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
| Below utility range | 71 |
| Within utility range | 4 |
| Partially within utility range | 18 |

## Split Label Coverage

Viable smoke target: `False`
Reason: `one_or_more_splits_have_fewer_than_two_classes`

| split | class_count | label_counts |
| --- | ---: | --- |
| train | 3 | `{'Below utility range': 38, 'Within utility range': 4, 'Partially within utility range': 12}` |
| val | 2 | `{'Below utility range': 9, 'Partially within utility range': 6}` |
| test | 1 | `{'Below utility range': 24}` |

## Model Comparison

| model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |
| --- | ---: | ---: | ---: | ---: |
| dummy_majority | 0.500 | 1.000 | 0.375 | 1.000 |
| extra_trees | 0.444 | 0.667 | 0.281 | 0.400 |
| rbf_svm | 0.444 | 0.667 | 0.254 | 0.400 |

## Boundary

This is a 4TU task-metadata smoke baseline. It uses activity-level labels
and fixed matrix summary features, so it supports protocol development but
does not establish the final raw-trace counterfactual claim.
