# IOAI 2025 Radar public benchmark probe

- Route: `public_benchmark_evaluation`
- Blind external validation: `False`
- Training samples: `1800`
- Validation samples: `500`
- Test samples: `500`
- Epochs: `1`
- Batch size: `4`

## Training history

| epoch | train_loss |
| ---: | ---: |
| 1 | 0.1662 |

## Evaluation

- Validation weighted score: `0.0318`
- Test weighted score: `0.0318`

### Validation preview

- `1.mat.pt`: score `0.0092`, pred_len `9050`, gt_len `9050`
- `2.mat.pt`: score `0.0383`, pred_len `9050`, gt_len `9050`
- `3.mat.pt`: score `0.0191`, pred_len `9050`, gt_len `9050`

### Test preview

- `1.mat.pt`: score `0.0092`, pred_len `9050`, gt_len `9050`
- `2.mat.pt`: score `0.0166`, pred_len `9050`, gt_len `9050`
- `3.mat.pt`: score `0.0306`, pred_len `9050`, gt_len `9050`

## Boundary

This is a public benchmark evaluation route with public scoring assets. It can strengthen experiment closure, but it is not blind external validation.