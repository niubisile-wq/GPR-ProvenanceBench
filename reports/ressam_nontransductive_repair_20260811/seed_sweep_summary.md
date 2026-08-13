# Res-SAM Non-Transductive Repair Sweep

Runs: `30`
Seeds: `20260811, 20260812, 20260813, 20260814, 20260815`

| transfer | raw bal acc | zscore bal acc | equalized bal acc | best delta |
| --- | ---: | ---: | ---: | ---: |
| synthetic_to_real_world | 0.4367 | 0.4400 | 0.4267 | +0.0033 |
| real_world_to_synthetic | 0.3511 | 0.3489 | 0.3400 | -0.0022 |

Boundary: these repairs are per-image preprocessing variants. They do not
use target-domain batch statistics or labels, but this is still not a
formal blind external submission because the Res-SAM asset is already part
of local model development.
