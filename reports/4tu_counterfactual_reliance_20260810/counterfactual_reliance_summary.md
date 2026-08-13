# 4TU Classifier-Level Counterfactual Reliance 2026-08-10

Training protocol: train each model on original train matrices, select by original validation balanced accuracy, then evaluate original and variant test matrices.

## Target Status

| target | records | viable | selected_model |
| --- | ---: | --- | --- |
| Land type | 93 | True | rbf_svm |
| Land cover | 93 | True | dummy_majority |
| Utility crossing | 84 | True | dummy_majority |
| Construction workers | 93 | True | dummy_majority |
| Land use | 93 | False | not_run |
| Relative groundwater level | 93 | False | not_run |

## Largest Drops For Validation-Selected Models

| target | model | variant | test_BA | delta_BA | flip_rate | unseen_pred_classes |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Land type | rbf_svm | zscore_clip | 0.0000 | -0.3857 | 0.8750 | 1 |
| Land type | rbf_svm | log_clip | 0.0000 | -0.3857 | 0.8333 | 1 |
| Land type | rbf_svm | remove_border | 0.1429 | -0.2429 | 0.4167 | 1 |
| Land type | rbf_svm | amplitude_jitter | 0.3143 | -0.0714 | 0.1250 | 0 |
| Land type | rbf_svm | remove_top_band | 0.3333 | -0.0524 | 0.5833 | 0 |
| Land type | rbf_svm | time_reverse | 0.3333 | -0.0524 | 0.5833 | 0 |
| Land cover | dummy_majority | log_clip | 0.3333 | 0.0000 | 0.0000 | 0 |
| Land cover | dummy_majority | zscore_clip | 0.3333 | 0.0000 | 0.0000 | 0 |
| Land cover | dummy_majority | amplitude_jitter | 0.3333 | 0.0000 | 0.0000 | 0 |
| Land cover | dummy_majority | remove_top_band | 0.3333 | 0.0000 | 0.0000 | 0 |
| Land cover | dummy_majority | remove_bottom_band | 0.3333 | 0.0000 | 0.0000 | 0 |
| Land cover | dummy_majority | remove_border | 0.3333 | 0.0000 | 0.0000 | 0 |

## Largest Drops For Non-Dummy Models

| target | model | variant | test_BA | delta_BA | flip_rate | unseen_pred_classes |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Utility crossing | rbf_svm | amplitude_jitter | 0.3250 | -0.5250 | 0.0952 | 0 |
| Utility crossing | rbf_svm | remove_border | 0.3750 | -0.4750 | 0.1905 | 0 |
| Land type | rbf_svm | zscore_clip | 0.0000 | -0.3857 | 0.8750 | 1 |
| Land type | rbf_svm | log_clip | 0.0000 | -0.3857 | 0.8333 | 1 |
| Utility crossing | rbf_svm | log_clip | 0.5000 | -0.3500 | 0.3333 | 0 |
| Utility crossing | rbf_svm | zscore_clip | 0.5000 | -0.3500 | 0.3333 | 0 |
| Utility crossing | rbf_svm | remove_top_band | 0.5000 | -0.3500 | 0.3333 | 0 |
| Utility crossing | rbf_svm | time_reverse | 0.5000 | -0.3500 | 0.3333 | 0 |
| Land type | rbf_svm | remove_border | 0.1429 | -0.2429 | 0.4167 | 1 |
| Land cover | rbf_svm | log_clip | 0.3333 | -0.1091 | 1.0000 | 0 |
| Land cover | rbf_svm | zscore_clip | 0.3333 | -0.1091 | 1.0000 | 0 |
| Land cover | rbf_svm | remove_top_band | 0.3333 | -0.1091 | 0.5000 | 0 |

## Boundary

This is a classifier-level stress test on matrix summary features. It is stronger than the generation-only audit, but it is not yet final raw-trace causal evidence because the models are lightweight feature classifiers and the target labels are task metadata.

`unseen_pred_classes` records when a variant makes the classifier predict labels absent from the test split. Treat this as an instability warning, not as a separate success criterion.
