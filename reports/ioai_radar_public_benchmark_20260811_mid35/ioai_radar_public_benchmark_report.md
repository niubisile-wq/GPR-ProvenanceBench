# IOAI 2025 Radar public benchmark probe

- Route: `public_benchmark_evaluation`
- Blind external validation: `False`
- Training samples: `35`
- Validation samples: `2`
- Test samples: `2`
- Epochs: `2`
- Batch size: `5`

## Training history

| epoch | train_loss |
| ---: | ---: |
| 1 | 1.5615 |
| 2 | 1.2925 |

## Evaluation

- Validation weighted score: `0.0238`
- Test weighted score: `0.0129`

### Validation preview

- `1.mat.pt`: score `0.0092`, pred_len `9050`, gt_len `9050`
- `2.mat.pt`: score `0.0383`, pred_len `9050`, gt_len `9050`

### Test preview

- `1.mat.pt`: score `0.0092`, pred_len `9050`, gt_len `9050`
- `2.mat.pt`: score `0.0166`, pred_len `9050`, gt_len `9050`

## Boundary

This is a public benchmark evaluation route with public scoring assets. It can strengthen experiment closure, but it is not blind external validation.