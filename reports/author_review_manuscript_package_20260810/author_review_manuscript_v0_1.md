# Author-review manuscript package v0.1 2026-08-10

Boundary: this is an author-review manuscript draft assembled from audited local evidence. It is not final submission text. Formal figures, blind external validation, repository identifiers, rights clearance and final Reporting Summary remain open.

## Title

Environment transfer exposes fragile generalization in ground-penetrating-radar recognition

## Abstract

Ground-penetrating radar (GPR) recognition models are often evaluated within curated datasets, but such tests may not separate target recognition from acquisition, environment or processing structure. We assembled GPR-ProvenanceBench as an auditable workflow linking dated manifests, grouped split logic, model-family comparisons and source-data traceability. At the current checkpoint, Res-SAM environment transfer produced the strongest reproducible signal: real-to-synthetic transfer showed directional and material drops in all five model families, with a mean balanced-accuracy delta of 0.4239, and synthetic-to-real transfer showed directional and material drops in four of five families, with a mean delta of 0.3743. Mojahid showed only directional and modest split sensitivity, whereas 4TU multi-layer counterfactual stress tests defined stress-test and feasibility boundaries. These results support a provenance-aware evaluation argument, not yet a completed blind external validation claim.

## Introduction

Ground-penetrating radar (GPR) is increasingly used to support non-destructive inspection, subsurface mapping and infrastructure assessment, where recognition models are expected to work beyond a single curated image collection [P1]. For such models, high internal test performance is useful only if it reflects transferable subsurface information rather than acquisition-, environment- or processing-specific regularities. This distinction is especially important for GPR B-scan recognition, because nominally similar images can be shaped by site conditions, instrument settings, rendering choices and dataset construction [P1].

A central evaluation bottleneck is that common random or weakly structured splits can mix samples that share provenance structure across training and test partitions [P4,P5]. When acquisition setting, environment, project identity or processing chain is correlated with the target label, a model may appear to generalize while partly exploiting these non-target cues. The problem is not that every GPR model is invalid, but that conventional split protocols can make it difficult to separate target recognition from provenance sensitivity. A benchmark intended to support generalization claims therefore needs to audit executable assets, split construction and environment transfer explicitly [P2,P4,P5].

Existing GPR recognition studies often report model performance within individual datasets, but fewer workflows make the evidence boundary executable: which assets can be regenerated, which labels support grouped evaluation, which model families agree, and which results survive environment or project-level stress tests. This leaves an unresolved gap between model comparison and provenance-aware validation. In particular, a claim that a model generalizes across GPR settings should be supported by dated manifests, reproducible split logic, model-family-level checks and, ultimately, blind external validation with labels withheld until predictions are frozen.

Here we assemble GPR-ProvenanceBench as an auditable workflow for testing how provenance and environment structure affect GPR recognition. At the current checkpoint, the executable local evidence includes Mojahid, Res-SAM and 4TU assets, five lightweight model-family comparisons for Mojahid and Res-SAM, and raw-trace-derived 4TU stress tests. The strongest current result is the Res-SAM environment transfer drop across model families; Mojahid provides directional but modest split-sensitivity evidence, and 4TU provides stress-test and feasibility boundaries. Blind external validation remains an open gate rather than a completed result. The current evidence is summarized in Figures 1-6 and Tables 1-2.

## Results

## Freezing the executable evidence boundary

We first defined the executable evidence boundary before comparing model performance. The current local manifests contain 2524 Mojahid samples, 99 4TU samples and 1050 Res-SAM samples, whereas TIGPR has no executable local sample rows at this checkpoint. This boundary is important because nominal dataset availability does not by itself establish whether an asset can support a reproducible model matrix, grouped evaluation or external validation. We therefore treat TIGPR as a supporting gate item rather than as a current core validation asset, and we use the remaining assets according to their documented executable status.

## Res-SAM environment transfer is the current main signal

Across five model families, Res-SAM environment transfer produced the strongest and most reproducible performance drop. In the real-to-synthetic direction, all five model families showed directional and material support, with a mean balanced-accuracy delta of 0.4239. In the synthetic-to-real direction, four of five model families showed directional and material support, with a mean delta of 0.3743. This pattern makes Res-SAM environment transfer the lead result in the current evidence package. The claim remains bounded to the tested Mojahid and Res-SAM model-family matrix and does not constitute blind external validation.

## Mojahid provides directional but modest secondary support

Mojahid random-minus-grouped inflation was directionally consistent but too modest to serve as the lead claim. The HOG plus RBF-SVM five-seed experiment showed a random-split balanced-accuracy mean of 0.9543, a grouped-split mean of 0.8566 and a delta of 0.0976. However, at the five-model-family synthesis layer, the Mojahid contrast reached directional support in five of five families but material support in only one of five, with a mean delta of 0.0406. We therefore interpret Mojahid as secondary split-sensitivity evidence rather than as proof of universal leakage.

## 4TU defines multi-layer stress-test and feasibility boundaries

The 4TU raw-trace-derived counterfactual experiments identified a stress-test signal that weakened under project-level repeated splits and did not upgrade to main confirmation. For the Land type ExtraTrees fixed-split sweep, log-clip perturbation reduced mean balanced accuracy by 0.3429 and produced a mean flip rate of 0.8583. Under group-aware repeated splits, the corresponding mean delta decreased to 0.0422 in magnitude and the mean flip rate decreased to 0.4693. A five-layer 4TU extension audit then consolidated summary-feature, raw-pixel, HOG, small-CNN and group-aware HOG evidence as stress-test or feasibility-boundary layers. These findings support 4TU as stress-test and feasibility evidence, not as causal proof, blind external validation or a main confirmation matrix.

## Blind external validation remains an open gate

The project has blind-intake templates, prediction-submission templates and a locked-evaluation dry run, but no current track satisfies the requirements for blind external validation. A valid external result still requires a real asset unused during model development, strict file hashes, labels held outside the analyst workflow, a frozen prediction submission and one locked evaluation after label release. Until that evidence exists, external validation must be reported as an open gate rather than as a positive result.

## Discussion

The current evidence indicates that environment and provenance structure can substantially reshape apparent GPR recognition performance. The strongest support comes from Res-SAM environment transfer, where performance drops were reproducible across multiple model families and larger than the Mojahid random-minus-grouped contrast. This finding does not show that every GPR model fails under deployment, but it does show that high internal performance is an insufficient basis for broad generalization claims when environment structure is not explicitly audited.

The secondary evidence layers constrain the interpretation. Mojahid showed directionally consistent split sensitivity, but the effect was modest and model-dependent at the five-family synthesis layer. The 4TU experiments showed sensitivity to raw-trace-derived perturbations across several evidence layers, but the group-aware and target-feasibility audits kept this asset in a stress-test role. These patterns are consistent with evaluation fragility, but they also indicate that the observed effects depend on asset structure, target feasibility and split design. The benchmark should therefore be read as an audit workflow and evidence boundary rather than as a universal leakage detector.

Several requirements remain open before a final Nature Communications submission can be claimed. The main figures still need formal rendering and visual quality assurance, repository identifiers and release licences remain unresolved, and the Reporting Summary cannot be finalized until Methods, figures, source data and validation status are frozen. Most importantly, blind external validation remains a no-go gate until a real held-label GPR asset is acquired and evaluated once after prediction freezing. These limits are substantive rather than cosmetic because they determine the strength of the central generalization claim.

## Methods

## Study design and evidence boundary

This study was designed as an auditable evaluation of how provenance and environment structure affect ground-penetrating radar (GPR) recognition. The workflow did not treat every nominally available dataset as an equivalent validation asset. Instead, each asset was assigned a dated executable status before it was used for model comparison, stress testing or gate reporting. At the 2026-08-10 checkpoint, Mojahid, 4TU and Res-SAM contributed executable local samples, whereas TIGPR remained a supporting-only asset because its local executable sample index was empty. This distinction was used to prevent non-executable assets from being promoted into the core evidence matrix.

## Unified sample manifests

Local assets were represented using unified sample manifests generated for the 2026-08-10 checkpoint. Each manifest recorded the asset name, sample identifiers, available paths, task-relevant fields and asset status needed for downstream audit. The manifest layer was used to count executable rows and to separate current analysis assets from assets that required restoration or additional permission. The asset-boundary outputs were then summarized for Figure 1 and Table 1 source data. This module defines the provenance and execution boundary; it does not measure recognition performance.

## Split and environment-transfer construction

Mojahid and Res-SAM were used for split and environment-transfer contrasts. Mojahid was evaluated under random stratified splits and grouped splits to test whether apparent performance changed when provenance-related grouping was respected. Res-SAM was evaluated under within-environment and cross-environment transfer settings between real-world and synthetic subsets. These contrasts were designed to separate ordinary within-source performance from sensitivity to environment transfer. They do not constitute blind external validation because the assets were already part of the current development and analysis matrix.

## Five-model family matrix

To reduce dependence on a single model family, the current Mojahid and Res-SAM comparisons were summarized across five model families: HOG plus RBF-SVM, LBP plus LinearSVM, TinyCNN, ResNet18 frozen embeddings plus LinearSVM and EfficientNetB0 frozen embeddings plus LinearSVM. For each contrast, the primary effect direction was defined using the difference in balanced accuracy between the compared settings. Directional support recorded whether a model family changed in the predeclared direction, whereas material support required an absolute balanced-accuracy delta of at least 0.05. The first five-model matrix excluded 4TU and did not include a real blind external asset.

## 4TU multi-layer counterfactual stress tests

The 4TU asset was used to examine whether raw-trace rendering and processing choices could alter model predictions. Raw traces were rendered into image-feature inputs and evaluated through summary-feature, raw-pixel, HOG image-feature and small-CNN stress-test layers. Deterministic counterfactual variants included log clipping, z-score clipping, time reversal and nuisance-band or border-related modifications. Fixed-split seed sweeps were compared with project-level repeated splits, and a five-layer extension audit was used to keep the 4TU evidence in a stress-test and feasibility-boundary role. These analyses were not treated as causal proof, main confirmation or blind external validation.

## 4TU grouped feasibility audit

Before expanding 4TU into any main confirmation matrix, each metadata target was audited for grouped-holdout feasibility. The audit recorded sample count, project count, label count, singleton labels, rare project support and the number of feasible test-project and validation-project combinations. This gate was used to identify targets that could support grouped evaluation and targets that should remain feasibility or failure-mode examples. Land type was retained as usable with caution, whereas several other targets were limited by non-viable grouped holdouts or single-project label structure. The target-feasibility gate and the five-layer extension audit therefore jointly prevent 4TU from being promoted beyond stress-test support at the current checkpoint.

## Blind external validation protocol

A blind external validation protocol was defined but not completed. The protocol requires an external asset that was not used during model development, a manifest with strict file hashes, labels held outside the analyst workflow, a frozen prediction submission and one locked evaluation after labels are released. Analyst-facing manifest, label-holdout and prediction-submission templates were created, and a locked-evaluation dry run was executed on template files. These outputs verify the protocol entry point only. They are not evidence of completed blind external validation.

## Reproducibility and checkpoint regeneration

All current artifacts were regenerated through the dated M0-M2 check script. The script validates the Python launcher and core imports, checks manifest consistency, audits asset readiness, builds source-data packages, regenerates Results and Methods skeletons, produces submission-readiness artifacts and verifies required outputs. The checkpoint also runs a manuscript-facing text-encoding check to detect common mojibake markers in generated prose and tabular files. Passing this script demonstrates that the current checkpoint can be regenerated, but it does not close future scientific gates such as rendered figures, repository identifiers, rights clearance, final Reporting Summary or blind external validation.

## Conclusion

GPR-ProvenanceBench turns provenance-aware GPR evaluation into an auditable workflow by linking asset status, split construction, model-family comparisons, stress tests, source-data mapping and dated regeneration checks.

At this checkpoint, Res-SAM environment transfer provides the strongest cross-model evidence that apparent GPR generalization can be brittle, whereas Mojahid and 4TU provide bounded directional and stress-test support.

The narrow implication is that provenance-aware evaluation should precede broad claims of GPR model generalization [P1,P4,P5]; the final submission case still depends on blind external validation, rendered figures, repository identifiers and public-release rights being closed.

## Non-final companion statements

Data Availability and Code Availability are captured in the repository metadata prelock drafts for this checkpoint, but they remain unfinalized until repository identifiers, rights review, figure-source locking and licence decisions are complete. Reporting Summary, figure legends, source-data deposit identifiers and final reference numbering are likewise not finalized in this draft.
