# 4TU Task Baseline: Land use

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
| High density residental - land-high rise, town and city centre with high population | 53 |
| Commercial and industrial | 12 |
| Residential - quiet suburbia | 14 |
| Public institutions and service | 10 |
| Rural residential - small farm allotments, increased population | 4 |

## Split Label Coverage

Viable smoke target: `False`
Reason: `one_or_more_splits_have_fewer_than_two_classes`

| split | class_count | label_counts |
| --- | ---: | --- |
| train | 3 | `{'High density residental - land-high rise, town and city centre with high population': 38, 'Commercial and industrial': 12, 'Rural residential - small farm allotments, increased population': 4}` |
| val | 1 | `{'High density residental - land-high rise, town and city centre with high population': 15}` |
| test | 2 | `{'Residential - quiet suburbia': 14, 'Public institutions and service': 10}` |

## Model Comparison

| model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |
| --- | ---: | ---: | ---: | ---: |
| dummy_majority | 1.000 | 0.000 | 1.000 | 0.000 |
| extra_trees | 0.133 | 0.000 | 0.078 | 0.000 |
| rbf_svm | 0.133 | 0.000 | 0.078 | 0.000 |

## Boundary

This is a 4TU task-metadata smoke baseline. It uses activity-level labels
and fixed matrix summary features, so it supports protocol development but
does not establish the final raw-trace counterfactual claim.
