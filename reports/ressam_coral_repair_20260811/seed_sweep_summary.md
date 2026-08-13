# Res-SAM Alignment Mitigation Seed Sweep

Runs: `5`
Seeds: `20260811, 20260812, 20260813, 20260814, 20260815`

## Balanced Accuracy

| transfer | baseline mean | mean/std mean | CORAL mean | mean/std delta | CORAL delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| synthetic_to_real_world | 0.4367 | 0.4633 | 0.4267 | +0.0267 | -0.0100 | 
| real_world_to_synthetic | 0.3511 | 0.4778 | 0.4333 | +0.1267 | +0.0822 | 

## Macro-F1

| transfer | baseline mean | mean/std mean | CORAL mean | mean/std delta | CORAL delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| synthetic_to_real_world | 0.3423 | 0.4506 | 0.4104 | +0.1082 | +0.0680 | 
| real_world_to_synthetic | 0.2034 | 0.4742 | 0.4223 | +0.2708 | +0.2190 | 

## Interpretation Boundary

This run tests whether a simple unsupervised covariance alignment can reduce
Res-SAM environment-transfer fragility on published image exports. It is
internal repair evidence only. It does not satisfy the blind external
validation or external-repair gate because the target images are available
during alignment and no one-shot locked external submission is involved.
