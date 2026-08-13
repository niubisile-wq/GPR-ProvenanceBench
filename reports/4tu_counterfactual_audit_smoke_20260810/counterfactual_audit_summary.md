# 4TU Counterfactual Variant Audit 2026-08-10

Samples: 9
Variants: original, log_clip, zscore_clip, amplitude_jitter, remove_top_band, remove_bottom_band, remove_border, time_reverse

## Aggregate Metrics

| variant | pearson_r_mean | mae_mean | rmse_mean | border_mae_mean | center_mae_mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| original | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| log_clip | 0.5658 | 0.2094 | 0.2271 | 0.1860 | 0.2147 |
| zscore_clip | 0.9561 | 0.0430 | 0.0672 | 0.0373 | 0.0443 |
| amplitude_jitter | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| remove_top_band | 0.9798 | 0.0023 | 0.0118 | 0.0122 | 0.0001 |
| remove_bottom_band | 1.0000 | 0.0000 | 0.0002 | 0.0001 | 0.0000 |
| remove_border | 0.9326 | 0.0035 | 0.0249 | 0.0157 | 0.0000 |
| time_reverse | -0.0008 | 0.0461 | 0.0976 | 0.0308 | 0.0494 |

## Boundary

This audit verifies deterministic counterfactual generation and
measurable variant deltas on the selected frozen package rows. It is
not yet a classifier-level causal reliance test.
