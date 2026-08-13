# Zenodo MCG GPR Non-Blind Baseline

Annotated rows: 966
Train/val/test: {'test': 168, 'train': 630, 'val': 168}

| task | model | metric | value |
| --- | --- | --- | ---: |
| regression | ridge_pixel32 | MAE | 0.146622 |
| regression | ridge_pixel32 | R2 | -11.641354 |
| regression | extra_trees_pixel32 | MAE | 0.045372 |
| regression | extra_trees_pixel32 | R2 | -0.151186 |
| tertile classification | extra_trees_pixel32 | balanced accuracy | 0.530482 |

## Boundary

This is a public, non-blind segmentation-derived stress baseline. It
cannot close the hard blind external validation gate.
