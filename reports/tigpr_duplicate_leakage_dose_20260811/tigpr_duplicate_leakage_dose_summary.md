# TIGPR Duplicate Leakage Dose

A hash-group split is contaminated by moving one same-label duplicate
from selected test duplicate groups into training while leaving at least
one same-group test sample held out.

| dose | leaked groups | shared test samples | BA | delta vs 0 | macro F1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.00 | 0.0 | 0.0 | 0.6777 | +0.0000 | 0.6851 |
| 0.05 | 2.2 | 2.2 | 0.6805 | +0.0028 | 0.6888 |
| 0.10 | 4.4 | 4.4 | 0.6809 | +0.0032 | 0.6877 |
| 0.20 | 9.2 | 9.2 | 0.6898 | +0.0121 | 0.6967 |
| 0.40 | 18.4 | 18.4 | 0.6868 | +0.0091 | 0.6935 |

## Boundary

This is a restored-local duplicate leakage dose experiment. It strengthens
cross-asset dose-response evidence, but does not create blind external
validation because TIGPR labels and media are visible locally.
