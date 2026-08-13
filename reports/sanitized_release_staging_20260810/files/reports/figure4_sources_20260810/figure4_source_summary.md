# Figure 4 Source Data 2026-08-10

Purpose: freeze the 4TU HOG counterfactual stress-test source data before plotting.

Main claim: fixed-split 4TU HOG counterfactuals show strong rendering sensitivity, but project-level repeated splits weaken the evidence.

Boundary: Figure 4 is stress-test evidence. It is not final causal proof, not a full 4TU five-model matrix and not blind external validation.

## Fixed-Split Seed Sweep

| variant | n | BA mean | delta BA mean | flip mean | interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| log_clip | 4 | 0.0905 | -0.3429 | 0.8583 | Strong fixed-split sensitivity signal. |
| zscore_clip | 4 | 0.5752 | 0.1419 | 0.3750 | Prediction instability without a large BA drop. |
| time_reverse | 4 | 0.3333 | -0.1000 | 0.7833 | Material drop under this stress variant. |
| remove_top_band | 4 | 0.4143 | -0.0190 | 0.0333 | Limited or no BA drop. |
| remove_bottom_band | 4 | 0.4333 | 0.0000 | 0.0000 | Limited or no BA drop. |
| remove_border | 4 | 0.4762 | 0.0429 | 0.1167 | Limited or no BA drop. |
| amplitude_jitter | 4 | 0.4333 | 0.0000 | 0.0000 | Limited or no BA drop. |

## Group-Aware Repeated Split

| variant | n | BA mean | delta BA mean | flip mean | interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| log_clip | 2 | 0.2456 | -0.0422 | 0.4693 | Signal weakens under project-level repeated splits. |
| zscore_clip | 2 | 0.2308 | -0.0570 | 0.3971 | Material drop under this stress variant. |
| time_reverse | 2 | 0.2500 | -0.0378 | 0.3971 | Prediction instability without a large BA drop. |
| remove_top_band | 2 | 0.2253 | -0.0625 | 0.0799 | Material drop under this stress variant. |
| remove_bottom_band | 2 | 0.2878 | 0.0000 | 0.0000 | Limited or no BA drop. |
| remove_border | 2 | 0.2878 | 0.0000 | 0.0722 | Limited or no BA drop. |
| amplitude_jitter | 2 | 0.2878 | 0.0000 | 0.0000 | Limited or no BA drop. |

## Plotting Notes

1. Show fixed-split and group-aware bars side by side for the same variants.
2. Use delta balanced accuracy as the primary axis and flip rate as a secondary annotation, not a second y-axis.
3. Highlight `log_clip` because it is the strongest fixed-split signal and the clearest weakened group-aware comparison.
4. Avoid claiming robust 4TU confirmation; the group-aware layer is explicitly weaker.

## 4TU Evidence-Layer Extension Audit

The updated Figure 4 source package also imports the 4TU model-family extension audit. These rows are boundary metadata for plotting or captioning, not a new main confirmation layer.

| evidence layer | model family | aggregate rows | strongest target | strongest variant | strongest delta | allowed role |
| --- | --- | ---: | --- | --- | ---: | --- |
| summary_feature_fixed_split | summary_feature_classifiers | 7 | Land type | log_clip | -0.3857 | stress-test boundary layer |
| raw_pixel_fixed_split | rawtrace_pixel_classifiers | 14 | Land cover | amplitude_jitter | 0.0000 | stress-test boundary layer |
| hog_seed_sweep_fixed_split | hog_image_classifiers | 21 | Land type | log_clip | -0.3393 | stress-test boundary layer |
| small_cnn_seed_sweep_fixed_split | small_cnn | 7 | Land type | log_clip | -0.1419 | stress-test boundary layer |
| hog_group_aware_repeated_split | hog_group_aware_classifiers | 14 | Land type | remove_top_band | -0.0625 | stress-test boundary layer |

Caption boundary: 4TU can be described as a multi-layer counterfactual stress test, but not as a main five-model confirmation layer and not as blind external validation.
