# Mojahid Lineage Leakage-Dose Sweep

Runs: `25`
Test fold: `0`
Val fold excluded: `1`

| dose | leaked groups mean | leaked train samples mean | test samples mean | balanced accuracy | delta vs 0 | macro-F1 | mean confidence | ECE | worst recall | recall spread | pred entropy |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.00 | 0.0 | 0.0 | 586.0 | 0.8566 | +0.0000 | 0.8579 | 0.9015 | 0.0365 | 0.6905 | 0.2996 | 0.9743 |
| 0.05 | 3.0 | 17.0 | 569.0 | 0.8696 | +0.0129 | 0.8709 | 0.9014 | 0.0280 | 0.7332 | 0.2534 | 0.9794 |
| 0.10 | 5.0 | 23.0 | 563.0 | 0.8641 | +0.0075 | 0.8656 | 0.9035 | 0.0399 | 0.7126 | 0.2729 | 0.9771 |
| 0.20 | 9.0 | 36.0 | 550.0 | 0.8777 | +0.0211 | 0.8799 | 0.9073 | 0.0325 | 0.7309 | 0.2568 | 0.9765 |
| 0.40 | 20.0 | 86.0 | 500.0 | 0.8983 | +0.0417 | 0.9018 | 0.9155 | 0.0230 | 0.7666 | 0.2181 | 0.9766 |

Boundary: this intentionally injects augmentation-lineage leakage into
the training set. It quantifies leakage sensitivity and is not a valid
generalization protocol.
