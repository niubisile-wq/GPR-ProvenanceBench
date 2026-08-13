# Conservative manuscript draft v0.1 2026-08-10

## One-sentence argument

In GPR recognition, current executable evidence shows that environment and provenance structure can strongly reshape apparent generalization, supported most directly by Res-SAM environment-transfer drops across five model families, with Mojahid and 4TU providing bounded secondary and stress-test evidence, while blind external validation and submission gates remain open.

## Recommended title

Environment transfer exposes fragile generalization in ground-penetrating-radar recognition

## Abstract draft

Ground-penetrating radar (GPR) recognition models are often evaluated within curated datasets, but such tests may not separate target recognition from acquisition, environment or processing structure. We assembled GPR-ProvenanceBench as an auditable workflow linking dated manifests, grouped split logic, model-family comparisons and source-data traceability. At the current checkpoint, Res-SAM environment transfer produced the strongest reproducible signal: real-to-synthetic transfer showed directional and material drops in all five model families, with a mean balanced-accuracy delta of 0.4239, and synthetic-to-real transfer showed directional and material drops in four of five families, with a mean delta of 0.3743. Mojahid showed only directional and modest split sensitivity, whereas 4TU multi-layer counterfactual stress tests defined stress-test and feasibility boundaries. These results support a provenance-aware evaluation argument, not yet a completed blind external validation claim.

# Results draft v0.1

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


# Discussion draft v0.1

The current evidence indicates that environment and provenance structure can substantially reshape apparent GPR recognition performance. The strongest support comes from Res-SAM environment transfer, where performance drops were reproducible across multiple model families and larger than the Mojahid random-minus-grouped contrast. This finding does not show that every GPR model fails under deployment, but it does show that high internal performance is an insufficient basis for broad generalization claims when environment structure is not explicitly audited.

The secondary evidence layers constrain the interpretation. Mojahid showed directionally consistent split sensitivity, but the effect was modest and model-dependent at the five-family synthesis layer. The 4TU experiments showed sensitivity to raw-trace-derived perturbations across several evidence layers, but the group-aware and target-feasibility audits kept this asset in a stress-test role. These patterns are consistent with evaluation fragility, but they also indicate that the observed effects depend on asset structure, target feasibility and split design. The benchmark should therefore be read as an audit workflow and evidence boundary rather than as a universal leakage detector.

Several requirements remain open before a final Nature Communications submission can be claimed. The main figures still need formal rendering and visual quality assurance, repository identifiers and release licences remain unresolved, and the Reporting Summary cannot be finalized until Methods, figures, source data and validation status are frozen. Most importantly, blind external validation remains a no-go gate until a real held-label GPR asset is acquired and evaluated once after prediction freezing. These limits are substantive rather than cosmetic because they determine the strength of the central generalization claim.


## Assumptions and missing inputs

1. The draft uses current audited claims only and does not invent new experiments.
2. Figure references remain conceptual until formal rendering and visual QA are complete.
3. Repository DOI, code DOI, rights clearance, final Reporting Summary and blind external validation remain missing.
4. The target framing is Nature Communications Article; final word budget must include Methods within the main ~5000-word limit.
