# 4TU Group-Aware Feasibility Audit 2026-08-10

Purpose: determine whether the current 4TU metadata labels can support stronger project-level validation, or whether effort should move to external validation.

## Target Summary

| target | status | samples | projects | labels | test2/val2 feasible | rare project labels |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Land type | usable_with_caution | 93 | 9 | 4 | 708/756 | none |
| Land use | not_viable_for_group_holdout | 93 | 9 | 5 | 0/756 | Commercial and industrial, Public institutions and service, Residential - quiet suburbia, Rural residential - small farm allotments, increased population |
| Land cover | weak_due_to_single_project_labels | 93 | 9 | 4 | 420/756 | Asphalt |
| Utility crossing | usable_with_caution | 84 | 9 | 2 | 360/756 | none |
| Construction workers | not_viable_for_group_holdout | 69 | 8 | 3 | 0/420 | Replacement and new installation of utilities, Replacement of utilities |
| Relative groundwater level | weak_due_to_single_project_labels | 93 | 9 | 3 | 60/756 | Within utility range |

## Land Type Project Coverage

| project | n | labels |
| --- | ---: | --- |
| 010 | 24 | Greenery: 11, Pedestrian/parking area: 3, Sidewalk: 6, Street/Cycling road: 4 |
| 011 | 17 | Pedestrian/parking area: 1, Sidewalk: 13, Street/Cycling road: 3 |
| 02 | 7 | Greenery: 3, Sidewalk: 2, Street/Cycling road: 2 |
| 04 | 8 | Sidewalk: 8 |
| 05 | 10 | Greenery: 5, Pedestrian/parking area: 5 |
| 06 | 6 | Sidewalk: 6 |
| 07 | 4 | Greenery: 4 |
| 08 | 8 | Greenery: 1, Pedestrian/parking area: 2, Sidewalk: 3, Street/Cycling road: 2 |
| 09 | 9 | Sidewalk: 6, Street/Cycling road: 3 |

## Existing Group-Split Result

- Existing target: `Land type`.
- Metric rows: `120`.
- Selected models by split: `rbf_svm, dummy_majority, extra_trees, extra_trees, rbf_svm`.

| model | n_splits | log_clip BA_mean | log_clip delta_mean | flip_mean |
| --- | ---: | ---: | ---: | ---: |
| dummy_majority | 1 | 0.3333 | 0.0000 | 0.0000 |
| extra_trees | 2 | 0.2456 | -0.0422 | 0.4693 |
| rbf_svm | 2 | 0.2917 | 0.0000 | 0.0000 |

## Decision

The current 4TU labels can produce some project-level holdouts, but they are not strong enough to serve as the main cross-model confirmation layer. Land type has feasible test2/val2 project splits, but model selection collapses to weak classifiers in several splits and the selected ExtraTrees signal appears in only 2/5 repeated splits.

## Protocol Consequence

1. Keep 4TU as raw-trace counterfactual and stress-test evidence.
2. Do not force a full five-model 4TU matrix as the next priority unless a stronger grouped split design or more balanced labels are added.
3. Prioritize external or 4TU-like validation data for the next confirmation layer.
