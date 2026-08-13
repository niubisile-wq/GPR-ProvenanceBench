# Target journal GPR benchmark scan

Scope: recent same-venue / same-domain papers around GPR, civil infrastructure NDT, and radar-based assessment in `Nondestructive Testing and Evaluation`.

This is a focused comparison scan, not a systematic review. The goal is to understand the publication bar and the dominant evidence style in the target venue.

## Sample set

| # | Paper | Year | Venue / DOI | Main focus | What it shows |
|---|---|---:|---|---|---|
| 1 | `Non-destructive compaction quality evaluation of runway construction based on GPR data` | 2023 | Nondestructive Testing and Evaluation, `10.1080/10589759.2023.2255363` | Runway compaction / rockfill assessment | One applied civil-infrastructure problem, with GPR used as a thickness/permittivity proxy. |
| 2 | `Crack depth measurement and key points of accurate identification in concrete structures: a review` | 2024 | Nondestructive Testing and Evaluation, `10.1080/10589759.2024.2340645` | Concrete crack depth review | Review-style synthesis of a narrow concrete-defect question, not a benchmark paper. |
| 3 | `Assessing concrete strength loss at elevated temperatures as a function of dielectric variation measured by GPR: an empirical study` | 2022 | Nondestructive Testing and Evaluation, `10.1080/10589759.2022.2140155` | Fire / thermal damage in concrete | Single-application empirical validation with dielectric variation as the measured signal. |
| 4 | `Automatic recognition for tunnel lining voids in GPR images based on SC-PGGAN and bidirectional ...` | 2025 | Nondestructive Testing and Evaluation, `10.1080/10589759.2025.2595524` | Tunnel void recognition | Modern learning-based recognition for one defect type in one imaging domain. |
| 5 | `Pavement thickness and stabilised foundation layer assessment using ground-coupled GPR` | 2016 | Nondestructive Testing and Evaluation, `10.1080/10589759.2015.1111890` | Pavement layer thickness | Field-oriented thickness estimation with core comparison. |
| 6 | `Using ground-penetrating radar for assessing the structural needs of ...` | 2012 | Nondestructive Testing and Evaluation, `10.1080/10589759.2012.695784` | Pavement / structure assessment | Structural-needs assessment in a pavement context; one task, one validation setting. |
| 7 | `Novel perspectives in bridges inspection using GPR` | 2012 | Nondestructive Testing and Evaluation, `10.1080/10589759.2012.694883` | Bridge inspection | Inspection-focused bridge application, framed as perspective plus practice. |
| 8 | `Time-varying deconvolution of GPR data in civil engineering` | 2012 | Nondestructive Testing and Evaluation, `10.1080/10589759.2012.695787` | Signal processing | Methodological GPR processing, not transfer/generalization auditing. |
| 9 | `Significance of GPR polarisation for improving target detection and characterisation` | 2014 | Nondestructive Testing and Evaluation, `10.1080/10589759.2014.949708` | Polarization diversity | Imaging / target-characterization study with controlled GPR acquisition. |
| 10 | `Performance evaluation of the neural networks for moisture detection using GPR` | 2014 | Nondestructive Testing and Evaluation, `10.1080/10589759.2014.941839` | Moisture detection | Model comparison for one defect type, with performance evaluation rather than benchmark governance. |

## Pattern summary

- The venue's GPR papers are mostly problem-specific rather than benchmark-specific.
- The common evidence unit is a single application setting: pavement, bridge deck, tunnel lining, concrete crack, moisture, or burial/void detection.
- Many papers evaluate one signal-processing method or one detector against one local task.
- Review papers exist, but they are usually narrow topic reviews rather than protocol audits or provenance-aware benchmark papers.
- In this sample, none of the papers is organized around cross-environment transfer, split-protocol governance, duplicate/leakage auditing, or blind external validation as the main claim.

## Relevance to our manuscript

This comparison supports the current framing of `GPR-ProvenanceBench` as an audit and evidence-boundary paper rather than as a single detector paper.

- Our strongest lead result is cross-environment transfer fragility.
- The supporting claims are provenance predictability, grouped-split sensitivity, and repair/calibration boundary effects.
- The paper is therefore aiming at a different evidence level than most same-venue GPR studies: not just `does it work on this dataset?`, but `what structure in the dataset is driving the apparent performance?`

## Source links

- https://www.tandfonline.com/doi/abs/10.1080/10589759.2023.2255363
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2024.2340645
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2022.2140155
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2025.2595524
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2015.1111890
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2012.695784
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2012.694883
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2012.695787
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2014.949708
- https://www.tandfonline.com/doi/abs/10.1080/10589759.2014.941839
