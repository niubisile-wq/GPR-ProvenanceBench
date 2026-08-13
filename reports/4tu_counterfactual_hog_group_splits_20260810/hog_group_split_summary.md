# 4TU HOG Group-Repeated Split Counterfactual Reliance 2026-08-10

Target: Land type
Split seeds: 20260810, 20260811, 20260812, 20260813, 20260814
Image size: 64
Metric rows: 120

## Original Baseline By Selected Model

| model | n_splits | BA_mean | BA_std |
| --- | ---: | ---: | ---: |
| dummy_majority | 1 | 0.3333 | 0.0000 |
| extra_trees | 2 | 0.2878 | 0.0199 |
| rbf_svm | 2 | 0.2917 | 0.0417 |

## Counterfactual Drops For Split-Selected Models

| model | variant | n_splits | BA_mean | delta_mean | delta_std | flip_mean | all_delta_nonpositive |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| extra_trees | remove_top_band | 2 | 0.2253 | -0.0625 | 0.0625 | 0.0799 | True |
| extra_trees | zscore_clip | 2 | 0.2308 | -0.0570 | 0.0391 | 0.3971 | True |
| extra_trees | log_clip | 2 | 0.2456 | -0.0422 | 0.0347 | 0.4693 | True |
| extra_trees | time_reverse | 2 | 0.2500 | -0.0378 | 0.0199 | 0.3971 | True |
| extra_trees | remove_border | 2 | 0.2878 | 0.0000 | 0.0000 | 0.0722 | True |
| dummy_majority | amplitude_jitter | 1 | 0.3333 | 0.0000 | 0.0000 | 0.0000 | True |
| dummy_majority | log_clip | 1 | 0.3333 | 0.0000 | 0.0000 | 0.0000 | True |
| dummy_majority | remove_border | 1 | 0.3333 | 0.0000 | 0.0000 | 0.0000 | True |
| dummy_majority | remove_bottom_band | 1 | 0.3333 | 0.0000 | 0.0000 | 0.0000 | True |
| dummy_majority | remove_top_band | 1 | 0.3333 | 0.0000 | 0.0000 | 0.0000 | True |
| dummy_majority | time_reverse | 1 | 0.3333 | 0.0000 | 0.0000 | 0.0000 | True |
| dummy_majority | zscore_clip | 1 | 0.3333 | 0.0000 | 0.0000 | 0.0000 | True |
| extra_trees | amplitude_jitter | 2 | 0.2878 | 0.0000 | 0.0000 | 0.0000 | True |
| extra_trees | remove_bottom_band | 2 | 0.2878 | 0.0000 | 0.0000 | 0.0000 | True |
| rbf_svm | amplitude_jitter | 2 | 0.2917 | 0.0000 | 0.0000 | 0.0000 | True |
| rbf_svm | log_clip | 2 | 0.2917 | 0.0000 | 0.0000 | 0.0000 | True |
| rbf_svm | remove_border | 2 | 0.2917 | 0.0000 | 0.0000 | 0.0000 | True |
| rbf_svm | remove_bottom_band | 2 | 0.2917 | 0.0000 | 0.0000 | 0.0000 | True |
| rbf_svm | remove_top_band | 2 | 0.2917 | 0.0000 | 0.0000 | 0.0000 | True |
| rbf_svm | time_reverse | 2 | 0.2917 | 0.0000 | 0.0000 | 0.0000 | True |
| rbf_svm | zscore_clip | 2 | 0.2917 | 0.0000 | 0.0000 | 0.0000 | True |

## Split Audit

| split_seed | train_projects | val_projects | test_projects | selected_model |
| ---: | --- | --- | --- | --- |
| 20260810 | `010;011;04;06;08` | `05;09` | `02;07` | rbf_svm |
| 20260811 | `010;011;02;07;08` | `06;09` | `04;05` | dummy_majority |
| 20260812 | `011;04;05;06;09` | `07;08` | `010;02` | extra_trees |
| 20260813 | `02;04;05;08;09` | `010;06` | `011;07` | extra_trees |
| 20260814 | `011;02;06;07;09` | `010;05` | `04;08` | rbf_svm |

## Boundary

This is group-aware repeated split replication across 4TU projects. The small number of projects and uneven labels make it a stress test rather than a final external validation protocol.
