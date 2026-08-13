# TinyCNN Lightweight Model Matrix 2026-08-10

This is the third model family after HOG+RBF-SVM and LBP+LinearSVM.

## Model

- Input: 64 x 64 grayscale pixels.
- Architecture: three small convolution blocks with batch normalization and adaptive pooling.
- Epochs: 8 fixed epochs, no validation-based epoch selection.
- Batch size: 64.
- Seeds: 20260810 to 20260814.

## Aggregate Results

| dataset | protocol | n_seeds | BA_mean | BA_std | BA_min | BA_max | macro_f1_mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mojahid | grouped_fold_0_test_fold_1_val | 5 | 0.9769 | 0.0077 | 0.9631 | 0.9861 | 0.9776 |
| mojahid | random_stratified_80_20 | 5 | 0.9867 | 0.0066 | 0.9798 | 0.9974 | 0.9877 |
| res_sam | transfer_real_world_to_synthetic | 5 | 0.3204 | 0.0234 | 0.2800 | 0.3444 | 0.2015 |
| res_sam | transfer_synthetic_to_real_world | 5 | 0.4187 | 0.1240 | 0.2900 | 0.5900 | 0.3182 |
| res_sam | within_real_world_random_80_20 | 5 | 0.4083 | 0.1242 | 0.1667 | 0.5083 | 0.3635 |
| res_sam | within_synthetic_random_80_20 | 5 | 0.6111 | 0.1324 | 0.3667 | 0.7667 | 0.5414 |

## Key Contrasts

| dataset | contrast | delta_mean |
| --- | --- | ---: |
| mojahid | random_minus_grouped_balanced_accuracy | 0.0098 |
| res_sam | within_minus_transfer_synthetic_to_real_world | -0.0103 |
| res_sam | within_minus_transfer_real_world_to_synthetic | 0.2907 |

## Interpretation Boundary

This is a CPU-scale deep baseline. It expands model-family coverage but is intentionally not tuned; use it as directional evidence only until the full frozen model matrix is complete.
