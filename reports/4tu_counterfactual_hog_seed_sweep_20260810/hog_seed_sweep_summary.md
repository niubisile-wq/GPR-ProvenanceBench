# 4TU HOG Counterfactual Reliance Seed Sweep 2026-08-10

Seeds: 20260810, 20260811, 20260812, 20260813, 20260814
Image size: 64
Metric rows: 480

## Largest Mean Drops For Seed-Selected Models

| target | model | variant | selected_count | BA_mean | delta_mean | delta_std | flip_mean |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Land type | extra_trees | log_clip | 4 | 0.0905 | -0.3429 | 0.0243 | 0.8583 |
| Land type | rbf_svm | log_clip | 1 | 0.3333 | -0.2143 | 0.0000 | 0.5833 |
| Land type | rbf_svm | time_reverse | 1 | 0.3333 | -0.2143 | 0.0000 | 0.5833 |
| Land type | extra_trees | time_reverse | 4 | 0.3333 | -0.1000 | 0.0278 | 0.7833 |
| Land cover | rbf_svm | log_clip | 5 | 0.3333 | -0.0720 | 0.0000 | 0.9583 |
| Land cover | rbf_svm | time_reverse | 5 | 0.3333 | -0.0720 | 0.0000 | 0.9583 |
| Land type | extra_trees | remove_top_band | 4 | 0.4143 | -0.0190 | 0.0278 | 0.0333 |
| Land cover | rbf_svm | remove_top_band | 5 | 0.4053 | 0.0000 | 0.0000 | 0.0417 |
| Construction workers | dummy_majority | amplitude_jitter | 5 | 0.5000 | 0.0000 | 0.0000 | 0.0000 |
| Construction workers | dummy_majority | log_clip | 5 | 0.5000 | 0.0000 | 0.0000 | 0.0000 |
| Construction workers | dummy_majority | remove_border | 5 | 0.5000 | 0.0000 | 0.0000 | 0.0000 |
| Construction workers | dummy_majority | remove_bottom_band | 5 | 0.5000 | 0.0000 | 0.0000 | 0.0000 |

## Largest Mean Drops For Non-Dummy Models

| target | model | variant | BA_mean | delta_mean | delta_std | flip_mean | all_delta_nonpositive |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Land type | extra_trees | log_clip | 0.0905 | -0.3429 | 0.0243 | 0.8583 | True |
| Land type | rbf_svm | log_clip | 0.3333 | -0.2143 | 0.0000 | 0.5833 | True |
| Land type | rbf_svm | time_reverse | 0.3333 | -0.2143 | 0.0000 | 0.5833 | True |
| Land type | extra_trees | time_reverse | 0.3333 | -0.1000 | 0.0278 | 0.7833 | True |
| Land cover | rbf_svm | log_clip | 0.3333 | -0.0720 | 0.0000 | 0.9583 | True |
| Land cover | rbf_svm | time_reverse | 0.3333 | -0.0720 | 0.0000 | 0.9583 | True |
| Land cover | extra_trees | time_reverse | 0.3333 | -0.0333 | 0.0312 | 0.9333 | True |
| Land cover | extra_trees | log_clip | 0.3333 | -0.0333 | 0.0312 | 0.8917 | True |
| Land type | extra_trees | remove_top_band | 0.4143 | -0.0190 | 0.0278 | 0.0333 | True |
| Land cover | rbf_svm | remove_top_band | 0.4053 | 0.0000 | 0.0000 | 0.0417 | True |
| Construction workers | extra_trees | amplitude_jitter | 0.0571 | 0.0000 | 0.0000 | 0.0000 | True |
| Construction workers | extra_trees | remove_bottom_band | 0.0571 | 0.0000 | 0.0000 | 0.0000 | True |

## Boundary

This sweep tests model-randomness stability for the HOG image-feature counterfactual result. The split itself is still fixed, so it does not replace future protocol-level split replication or external blind validation.
