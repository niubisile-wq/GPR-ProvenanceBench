# Zenodo Raw-GPR Track C Metadata Baseline

Scope: non-blind public raw-GPR stress test on Zenodo record 14637589.
Features are file-level metadata plus head/tail byte signatures, not semantic GPR interpretation.

## Dataset

- Samples: 914
- Labels: {'pipe': 553, 'rebar': 217, 'tunnel': 144}
- Project groups: 20

## Split Contrast

| model | random BA | group BA | random - group BA | group shared groups |
| --- | ---: | ---: | ---: | ---: |
| sgd_logistic | 0.9022 | 0.7846 | +0.1177 | 0.0 |
| extra_trees | 0.9677 | 0.8399 | +0.1278 | 0.0 |

## Interpretation

The public Zenodo raw-GPR asset is now executable as a Track C non-blind stress test. Any high accuracy from metadata/byte-signature features should be interpreted as source or format separability, not as proof that semantic GPR defect reasoning generalizes. The hard blind-external gate remains open.
