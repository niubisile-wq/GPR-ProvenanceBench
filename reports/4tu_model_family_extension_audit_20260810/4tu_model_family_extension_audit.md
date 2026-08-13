# 4TU Model-Family Extension Audit

Status: `4tu_model_family_extension_audit_ready_stress_test_only`

This audit asks whether current 4TU evidence can be upgraded into the same kind of five-model confirmation matrix used for Mojahid and Res-SAM. The answer is no. The current value of 4TU is stress-test and feasibility-boundary evidence.

## Evidence Layers

| layer | model family | aggregate rows | strongest target | strongest variant | strongest delta | allowed use |
| --- | --- | ---: | --- | --- | ---: | --- |
| summary_feature_fixed_split | summary_feature_classifiers | 7 | Land type | log_clip | -0.3857 | stress_test_only |
| raw_pixel_fixed_split | rawtrace_pixel_classifiers | 14 | Land cover | amplitude_jitter | 0.0000 | stress_test_only |
| hog_seed_sweep_fixed_split | hog_image_classifiers | 21 | Land type | log_clip | -0.3393 | stress_test_only |
| small_cnn_seed_sweep_fixed_split | small_cnn | 7 | Land type | log_clip | -0.1419 | stress_test_only |
| hog_group_aware_repeated_split | hog_group_aware_classifiers | 14 | Land type | remove_top_band | -0.0625 | feasibility_boundary |

## Strongest Counterfactual Drops

| layer | target | model | variant | delta_mean | flip_mean | material_drop |
| --- | --- | --- | --- | ---: | ---: | --- |
| summary_feature_fixed_split | Land type | rbf_svm | log_clip | -0.3857 | 0.8333 | True |
| summary_feature_fixed_split | Land type | rbf_svm | zscore_clip | -0.3857 | 0.8750 | True |
| hog_seed_sweep_fixed_split | Land type | extra_trees | log_clip | -0.3393 | 0.8646 | True |
| summary_feature_fixed_split | Land type | rbf_svm | remove_border | -0.2429 | 0.4167 | True |
| hog_seed_sweep_fixed_split | Land type | rbf_svm | log_clip | -0.2143 | 0.5833 | True |
| hog_seed_sweep_fixed_split | Land type | rbf_svm | time_reverse | -0.2143 | 0.5833 | True |
| small_cnn_seed_sweep_fixed_split | Land type | small_cnn | log_clip | -0.1419 | 0.8583 | True |
| hog_seed_sweep_fixed_split | Land type | extra_trees | time_reverse | -0.0952 | 0.7917 | True |
| hog_seed_sweep_fixed_split | Land cover | rbf_svm | log_clip | -0.0720 | 0.9583 | True |
| hog_seed_sweep_fixed_split | Land cover | rbf_svm | time_reverse | -0.0720 | 0.9583 | True |

## Boundary

4TU should remain a counterfactual stress-test and failure-mode/feasibility-boundary layer. It must not be used as a main five-model confirmation layer or as blind external validation evidence until label structure, grouped split coverage and external held-label status are resolved.
