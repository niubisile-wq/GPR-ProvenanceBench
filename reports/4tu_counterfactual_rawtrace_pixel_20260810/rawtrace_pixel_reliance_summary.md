# 4TU Raw-Trace Pixel Counterfactual Reliance 2026-08-10

Feature protocol: normalize each raw matrix, resize to 64x64 grayscale pixels, flatten, train on original train matrices, then evaluate original and variant test matrices.

## Target Status

| target | records | viable | selected_model |
| --- | ---: | --- | --- |
| Land type | 93 | True | rbf_svm |
| Land cover | 93 | True | rbf_svm |
| Utility crossing | 84 | True | dummy_majority |
| Construction workers | 93 | True | dummy_majority |
| Land use | 93 | False | not_run |
| Relative groundwater level | 93 | False | not_run |

## Largest Drops For Validation-Selected Models

| target | model | variant | test_BA | delta_BA | flip_rate |
| --- | --- | --- | ---: | ---: | ---: |
| Land type | rbf_svm | log_clip | 0.3333 | 0.0000 | 1.0000 |
| Land type | rbf_svm | time_reverse | 0.3333 | 0.0000 | 1.0000 |
| Land cover | rbf_svm | log_clip | 0.3333 | 0.0000 | 1.0000 |
| Land cover | rbf_svm | time_reverse | 0.3333 | 0.0000 | 1.0000 |
| Land type | rbf_svm | remove_border | 0.3333 | 0.0000 | 0.0833 |
| Land type | rbf_svm | remove_top_band | 0.3333 | 0.0000 | 0.0417 |
| Land type | rbf_svm | zscore_clip | 0.3333 | 0.0000 | 0.0000 |
| Land type | rbf_svm | amplitude_jitter | 0.3333 | 0.0000 | 0.0000 |
| Land type | rbf_svm | remove_bottom_band | 0.3333 | 0.0000 | 0.0000 |
| Land cover | rbf_svm | zscore_clip | 0.3333 | 0.0000 | 0.0000 |
| Land cover | rbf_svm | amplitude_jitter | 0.3333 | 0.0000 | 0.0000 |
| Land cover | rbf_svm | remove_bottom_band | 0.3333 | 0.0000 | 0.0000 |

## Largest Drops For Non-Dummy Models

| target | model | variant | test_BA | delta_BA | flip_rate |
| --- | --- | --- | ---: | ---: | ---: |
| Utility crossing | rbf_svm | remove_top_band | 0.3000 | -0.4500 | 0.1429 |
| Utility crossing | rbf_svm | log_clip | 0.5000 | -0.2500 | 0.5238 |
| Utility crossing | rbf_svm | time_reverse | 0.5000 | -0.2500 | 0.5238 |
| Construction workers | extra_trees | remove_border | 0.1429 | -0.0357 | 0.0833 |
| Land type | rbf_svm | log_clip | 0.3333 | 0.0000 | 1.0000 |
| Land type | rbf_svm | time_reverse | 0.3333 | 0.0000 | 1.0000 |
| Land cover | rbf_svm | log_clip | 0.3333 | 0.0000 | 1.0000 |
| Land cover | rbf_svm | time_reverse | 0.3333 | 0.0000 | 1.0000 |
| Land type | rbf_svm | remove_border | 0.3333 | 0.0000 | 0.0833 |
| Land cover | extra_trees | remove_top_band | 0.3333 | 0.0000 | 0.0833 |
| Land cover | extra_trees | time_reverse | 0.3333 | 0.0000 | 0.0833 |
| Land type | rbf_svm | remove_top_band | 0.3333 | 0.0000 | 0.0417 |

## Boundary

This is a direct raw-trace pixel baseline, but it is still lightweight. It strengthens the counterfactual evidence chain relative to summary features, while final claims still require frozen multi-model replication and external validation.
