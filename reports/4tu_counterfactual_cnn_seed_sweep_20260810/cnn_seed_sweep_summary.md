# 4TU Small-CNN Counterfactual Reliance Seed Sweep 2026-08-10

Target(s): Land type
Seeds: 20260810, 20260811, 20260812, 20260813, 20260814
Image size: 64
Epochs per seed: 40
Metric rows: 40

## Original Baseline

| target | model | BA_mean | BA_std | val_BA_mean |
| --- | --- | ---: | ---: | ---: |
| Land type | small_cnn | 0.2229 | 0.1419 | 0.4125 |

## Counterfactual Drops

| target | variant | BA_mean | delta_mean | delta_std | flip_mean | all_delta_nonpositive |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Land type | log_clip | 0.0810 | -0.1419 | 0.2504 | 0.8583 | False |
| Land type | amplitude_jitter | 0.2229 | 0.0000 | 0.0000 | 0.0000 | True |
| Land type | remove_bottom_band | 0.2229 | 0.0000 | 0.0000 | 0.0000 | True |
| Land type | remove_border | 0.2648 | 0.0419 | 0.0374 | 0.2000 | False |
| Land type | time_reverse | 0.2667 | 0.0438 | 0.1067 | 0.6083 | False |
| Land type | zscore_clip | 0.2933 | 0.0705 | 0.1819 | 0.5000 | False |
| Land type | remove_top_band | 0.3390 | 0.1162 | 0.1413 | 0.2500 | False |

## Boundary

This sweep tests CNN model-randomness stability for the key Land type counterfactual result. It remains fixed-split and CPU-scale, so it does not replace split/package replication or a tuned deep-learning benchmark.
