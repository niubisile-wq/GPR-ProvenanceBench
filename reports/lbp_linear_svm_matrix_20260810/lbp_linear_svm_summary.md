# LBP + LinearSVM Lightweight Model Matrix 2026-08-10

This is the second lightweight model family after HOG+RBF-SVM.

## Model

- Feature: uniform local binary pattern histogram, P=16, R=2.
- Classifier: `LinearSVC(C=1.0, class_weight='balanced')`.
- Image size: 64 x 64 grayscale.
- Seeds: 20260810 to 20260814.

## Aggregate Results

| dataset | protocol | n_seeds | BA_mean | BA_std | BA_min | BA_max | macro_f1_mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mojahid | grouped_fold_0_test_fold_1_val | 5 | 0.8010 | 0.0000 | 0.8010 | 0.8010 | 0.7999 |
| mojahid | random_stratified_80_20 | 5 | 0.8375 | 0.0214 | 0.8141 | 0.8634 | 0.8369 |
| res_sam | transfer_real_world_to_synthetic | 5 | 0.3067 | 0.0000 | 0.3067 | 0.3067 | 0.2732 |
| res_sam | transfer_synthetic_to_real_world | 5 | 0.3433 | 0.0000 | 0.3433 | 0.3433 | 0.3481 |
| res_sam | within_real_world_random_80_20 | 5 | 0.6517 | 0.0420 | 0.5833 | 0.7000 | 0.6447 |
| res_sam | within_synthetic_random_80_20 | 5 | 0.5422 | 0.0257 | 0.5000 | 0.5778 | 0.5390 |

## Key Contrasts

| dataset | contrast | delta_mean |
| --- | --- | ---: |
| mojahid | random_minus_grouped_balanced_accuracy | 0.0365 |
| res_sam | within_minus_transfer_synthetic_to_real_world | 0.3083 |
| res_sam | within_minus_transfer_real_world_to_synthetic | 0.2356 |

## Interpretation Boundary

These runs expand the model matrix but remain CPU-only lightweight baselines. They should be used to test whether split and environment effects persist outside HOG+RBF-SVM, not as final deep-learning evidence.
