# ResNet18 Embedding + LinearSVM Model Matrix 2026-08-10

This is the fourth model family after HOG+RBF-SVM, LBP+LinearSVM and TinyCNN.

## Model

- ResNet18 weight status: `imagenet_default`.
- Weight source: `https://download.pytorch.org/models/resnet18-f37072fd.pth`.
- Image size: 128 x 128 RGB.
- Feature: frozen 512-dimensional ResNet18 penultimate embedding.
- Classifier: `LinearSVC(C=1.0, class_weight='balanced')`.
- Seeds: 20260810 to 20260814.

## Aggregate Results

| dataset | protocol | n_seeds | BA_mean | BA_std | BA_min | BA_max | macro_f1_mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mojahid | grouped_fold_0_test_fold_1_val | 5 | 0.9635 | 0.0000 | 0.9635 | 0.9635 | 0.9660 |
| mojahid | random_stratified_80_20 | 5 | 0.9885 | 0.0041 | 0.9814 | 0.9929 | 0.9898 |
| res_sam | transfer_real_world_to_synthetic | 5 | 0.5556 | 0.0000 | 0.5556 | 0.5556 | 0.5446 |
| res_sam | transfer_synthetic_to_real_world | 5 | 0.3367 | 0.0000 | 0.3367 | 0.3367 | 0.1737 |
| res_sam | within_real_world_random_80_20 | 5 | 0.9150 | 0.0207 | 0.8917 | 0.9500 | 0.9145 |
| res_sam | within_synthetic_random_80_20 | 5 | 0.9844 | 0.0089 | 0.9778 | 1.0000 | 0.9844 |

## Key Contrasts

| dataset | contrast | delta_mean |
| --- | --- | ---: |
| mojahid | random_minus_grouped_balanced_accuracy | 0.0250 |
| res_sam | within_minus_transfer_synthetic_to_real_world | 0.5783 |
| res_sam | within_minus_transfer_real_world_to_synthetic | 0.4289 |

## Interpretation Boundary

This run uses frozen image embeddings and a linear classifier. It tests whether split and environment effects persist under a generic convolutional representation, but it is not a fine-tuned GPR model.
