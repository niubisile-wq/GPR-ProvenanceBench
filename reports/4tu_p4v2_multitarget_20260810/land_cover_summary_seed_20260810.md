# 4TU Task Baseline: Land cover

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
| Grass / vegetation | 24 |
| Brick road concrete | 32 |
| Asphalt | 3 |
| Concrete surfacing | 34 |

## Split Label Coverage

Viable smoke target: `True`
Reason: `ok`

| split | class_count | label_counts |
| --- | ---: | --- |
| train | 4 | `{'Grass / vegetation': 15, 'Brick road concrete': 17, 'Asphalt': 3, 'Concrete surfacing': 19}` |
| val | 3 | `{'Concrete surfacing': 7, 'Grass / vegetation': 4, 'Brick road concrete': 4}` |
| test | 3 | `{'Concrete surfacing': 8, 'Brick road concrete': 11, 'Grass / vegetation': 5}` |

## Model Comparison

| model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |
| --- | ---: | ---: | ---: | ---: |
| dummy_majority | 0.333 | 0.333 | 0.212 | 0.167 |
| extra_trees | 0.333 | 0.333 | 0.148 | 0.123 |
| rbf_svm | 0.333 | 0.442 | 0.178 | 0.350 |

## Boundary

This is a 4TU task-metadata smoke baseline. It uses activity-level labels
and fixed matrix summary features, so it supports protocol development but
does not establish the final raw-trace counterfactual claim.
