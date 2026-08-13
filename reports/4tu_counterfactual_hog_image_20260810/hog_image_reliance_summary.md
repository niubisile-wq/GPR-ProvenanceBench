# 4TU HOG Image Counterfactual Reliance 2026-08-10

Feature protocol: normalize each raw matrix, resize to 64x64 grayscale, extract HOG features, train on original train matrices, then evaluate original and variant test matrices.

## Target Status

| target | records | viable | selected_model | hog_dimension |
| --- | ---: | --- | --- | ---: |
| Land type | 93 | True | extra_trees | 1764 |
| Land cover | 93 | True | rbf_svm | 1764 |
| Utility crossing | 84 | True | dummy_majority | 1764 |
| Construction workers | 93 | True | dummy_majority | 1764 |
| Land use | 93 | False | not_run | 0 |
| Relative groundwater level | 93 | False | not_run | 0 |

## Largest Drops For Validation-Selected Models

| target | model | variant | test_BA | delta_BA | flip_rate |
| --- | --- | --- | ---: | ---: | ---: |
| Land type | extra_trees | log_clip | 0.0952 | -0.3810 | 0.8333 |
| Land type | extra_trees | time_reverse | 0.3333 | -0.1429 | 0.7083 |
| Land cover | rbf_svm | log_clip | 0.3333 | -0.0720 | 0.9583 |
| Land cover | rbf_svm | time_reverse | 0.3333 | -0.0720 | 0.9583 |
| Land type | extra_trees | remove_top_band | 0.4048 | -0.0714 | 0.1250 |
| Land cover | rbf_svm | remove_top_band | 0.4053 | 0.0000 | 0.0417 |
| Land type | extra_trees | amplitude_jitter | 0.4762 | 0.0000 | 0.0000 |
| Land type | extra_trees | remove_bottom_band | 0.4762 | 0.0000 | 0.0000 |
| Land cover | rbf_svm | amplitude_jitter | 0.4053 | 0.0000 | 0.0000 |
| Land cover | rbf_svm | remove_bottom_band | 0.4053 | 0.0000 | 0.0000 |
| Utility crossing | dummy_majority | log_clip | 0.5000 | 0.0000 | 0.0000 |
| Utility crossing | dummy_majority | zscore_clip | 0.5000 | 0.0000 | 0.0000 |

## Largest Drops For Non-Dummy Models

| target | model | variant | test_BA | delta_BA | flip_rate |
| --- | --- | --- | ---: | ---: | ---: |
| Land type | extra_trees | log_clip | 0.0952 | -0.3810 | 0.8333 |
| Land type | rbf_svm | log_clip | 0.3333 | -0.2143 | 0.5833 |
| Land type | rbf_svm | time_reverse | 0.3333 | -0.2143 | 0.5833 |
| Land type | extra_trees | time_reverse | 0.3333 | -0.1429 | 0.7083 |
| Land cover | rbf_svm | log_clip | 0.3333 | -0.0720 | 0.9583 |
| Land cover | rbf_svm | time_reverse | 0.3333 | -0.0720 | 0.9583 |
| Land type | extra_trees | remove_top_band | 0.4048 | -0.0714 | 0.1250 |
| Land cover | extra_trees | log_clip | 0.3333 | -0.0417 | 0.9167 |
| Land cover | extra_trees | time_reverse | 0.3333 | -0.0417 | 0.9167 |
| Land cover | rbf_svm | remove_top_band | 0.4053 | 0.0000 | 0.0417 |
| Construction workers | extra_trees | remove_top_band | 0.0714 | 0.0000 | 0.0417 |
| Land type | extra_trees | amplitude_jitter | 0.4762 | 0.0000 | 0.0000 |

## Boundary

This is an image-feature classifier test on raw-trace-derived HOG vectors. It is stronger than the 16-feature summary test and more structured than the raw pixel baseline, but it is still not a deep raw-trace model or external blind validation.
