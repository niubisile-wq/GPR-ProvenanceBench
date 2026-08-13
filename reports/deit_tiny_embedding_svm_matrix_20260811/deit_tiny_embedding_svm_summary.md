# DeiT-Tiny Embedding + LinearSVM Model Matrix 2026-08-11

This adds the DeiT-Tiny family explicitly named in the frozen 18-month plan.

## Model

- Architecture: `deit_tiny_patch16_224.fb_in1k`.
- Weight status: `imagenet_default`.
- Weight source: `timm:deit_tiny_patch16_224.fb_in1k:pretrained=True`.
- Image size: 224 x 224 RGB.
- Feature: frozen 192-dimensional DeiT-Tiny embedding.
- Classifier: `LinearSVC(C=1.0, class_weight='balanced')`.
- Seeds: 20260810 to 20260814.

## Aggregate Results

| dataset | protocol | n_seeds | BA_mean | BA_std | BA_min | BA_max | macro_f1_mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mojahid | grouped_fold_0_test_fold_1_val | 5 | 0.9681 | 0.0000 | 0.9681 | 0.9681 | 0.9701 |
| mojahid | random_stratified_80_20 | 5 | 0.9872 | 0.0029 | 0.9813 | 0.9893 | 0.9885 |
| res_sam | transfer_real_world_to_synthetic | 5 | 0.4400 | 0.0000 | 0.4400 | 0.4400 | 0.3730 |
| res_sam | transfer_synthetic_to_real_world | 5 | 0.4300 | 0.0000 | 0.4300 | 0.4300 | 0.3325 |
| res_sam | within_real_world_random_80_20 | 5 | 0.9367 | 0.0125 | 0.9167 | 0.9500 | 0.9358 |
| res_sam | within_synthetic_random_80_20 | 5 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |

## Key Contrasts

| dataset | contrast | delta_mean |
| --- | --- | ---: |
| mojahid | random_minus_grouped_balanced_accuracy | 0.0191 |
| res_sam | within_minus_transfer_synthetic_to_real_world | 0.5067 |
| res_sam | within_minus_transfer_real_world_to_synthetic | 0.5600 |

## Interpretation Boundary

This is a frozen ImageNet representation plus a train-fold classifier. It closes the missing DeiT-Tiny architecture slot for directional split/transfer evidence, but it is not end-to-end GPR fine-tuning or blind external validation.
