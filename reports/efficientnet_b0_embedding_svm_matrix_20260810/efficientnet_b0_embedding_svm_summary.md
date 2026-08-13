# EfficientNetB0 Embedding + LinearSVM Model Matrix 2026-08-10

This is the fifth model family after HOG+RBF-SVM, LBP+LinearSVM, TinyCNN and ResNet18 embeddings.

## Model

- EfficientNetB0 weight status: `imagenet_default`.
- Weight source: `https://download.pytorch.org/models/efficientnet_b0_rwightman-7f5810bc.pth`.
- Image size: 128 x 128 RGB.
- Feature: frozen 1280-dimensional EfficientNetB0 embedding.
- Classifier: `LinearSVC(C=1.0, class_weight='balanced')`.
- Seeds: 20260810 to 20260814.

## Aggregate Results

| dataset | protocol | n_seeds | BA_mean | BA_std | BA_min | BA_max | macro_f1_mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mojahid | grouped_fold_0_test_fold_1_val | 5 | 0.9591 | 0.0000 | 0.9591 | 0.9591 | 0.9622 |
| mojahid | random_stratified_80_20 | 5 | 0.9931 | 0.0028 | 0.9884 | 0.9974 | 0.9939 |
| res_sam | transfer_real_world_to_synthetic | 5 | 0.3889 | 0.0000 | 0.3889 | 0.3889 | 0.2953 |
| res_sam | transfer_synthetic_to_real_world | 5 | 0.3600 | 0.0000 | 0.3600 | 0.3600 | 0.2256 |
| res_sam | within_real_world_random_80_20 | 5 | 0.9433 | 0.0162 | 0.9250 | 0.9667 | 0.9433 |
| res_sam | within_synthetic_random_80_20 | 5 | 0.9978 | 0.0044 | 0.9889 | 1.0000 | 0.9978 |

## Key Contrasts

| dataset | contrast | delta_mean |
| --- | --- | ---: |
| mojahid | random_minus_grouped_balanced_accuracy | 0.0340 |
| res_sam | within_minus_transfer_synthetic_to_real_world | 0.5833 |
| res_sam | within_minus_transfer_real_world_to_synthetic | 0.6089 |

## Interpretation Boundary

This run uses frozen EfficientNetB0 image embeddings and a linear classifier. It completes the first five-model matrix, but it remains a feature-transfer baseline rather than a fine-tuned GPR model.
