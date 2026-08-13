# IOAI 2025 Radar public benchmark probe

- Route: `public_benchmark_evaluation`
- Blind external validation: `False`
- Training samples: `4`
- Validation samples: `2`
- Test samples: `2`
- Epochs: `1`
- Batch size: `2`

## Training history

| epoch | train_loss |
| ---: | ---: |
| 1 | 1.6186 |

## Evaluation

- Validation weighted score: `0.0779`
- Test weighted score: `0.0880`

### Validation preview

- `1.mat.pt`: score `0.0874`, pred_len `9050`, gt_len `9050`
- `2.mat.pt`: score `0.0684`, pred_len `9050`, gt_len `9050`

### Test preview

- `1.mat.pt`: score `0.1152`, pred_len `9050`, gt_len `9050`
- `2.mat.pt`: score `0.0607`, pred_len `9050`, gt_len `9050`

## Boundary

This is a public benchmark evaluation route with public scoring assets. It can strengthen experiment closure, but it is not blind external validation.