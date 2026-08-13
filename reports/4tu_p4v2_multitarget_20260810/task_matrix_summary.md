# 4TU P4 v2 Multi-Target Baseline Matrix 2026-08-10

This table summarizes task-metadata smoke baselines from the same P4 v2
package and activity-level metadata join.

| target | records | selected_model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Construction workers | 93 | dummy_majority | 0.500 | 0.500 | 0.318 | 0.368 |
| Land cover | 93 | dummy_majority | 0.333 | 0.333 | 0.212 | 0.167 |
| Land type | 93 | rbf_svm | 0.350 | 0.386 | 0.258 | 0.279 |
| Land use | 93 | dummy_majority | 1.000 | 0.000 | 1.000 | 0.000 |
| Relative groundwater level | 93 | dummy_majority | 0.500 | 1.000 | 0.375 | 1.000 |
| Utility crossing | 84 | dummy_majority | 0.500 | 0.500 | 0.483 | 0.488 |

## Target Viability

| target | viable | train_classes | val_classes | test_classes | reason |
| --- | --- | ---: | ---: | ---: | --- |
| Construction workers | True | 2 | 2 | 2 | ok |
| Land cover | True | 4 | 3 | 3 | ok |
| Land type | True | 4 | 4 | 3 | ok |
| Land use | False | 3 | 1 | 2 | one_or_more_splits_have_fewer_than_two_classes |
| Relative groundwater level | False | 3 | 2 | 1 | one_or_more_splits_have_fewer_than_two_classes |
| Utility crossing | True | 2 | 2 | 2 | ok |

## Boundary

These are task-metadata smoke baselines. They are useful for selecting
which 4TU target fields are viable for controlled experiments, but they
do not complete the strict raw-trace counterfactual requirement.
