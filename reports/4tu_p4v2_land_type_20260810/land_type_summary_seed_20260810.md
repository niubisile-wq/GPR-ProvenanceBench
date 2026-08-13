# 4TU Task Baseline: Land type

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
| Greenery | 24 |
| Sidewalk | 44 |
| Street/Cycling road | 14 |
| Pedestrian/parking area | 11 |

## Model Comparison

| model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |
| --- | ---: | ---: | ---: | ---: |
| dummy_majority | 0.250 | 0.333 | 0.125 | 0.246 |
| extra_trees | 0.250 | 0.357 | 0.111 | 0.163 |
| rbf_svm | 0.350 | 0.386 | 0.258 | 0.279 |

## Boundary

This is a 4TU task-metadata smoke baseline. It uses activity-level labels
and fixed matrix summary features, so it supports protocol development but
does not establish the final raw-trace counterfactual claim.
