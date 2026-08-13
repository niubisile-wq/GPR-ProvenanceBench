# Narrative Section Drafts v1 with Candidate Citation Markers 2026-08-10

## Drafting Boundary

These sections use candidate citation markers such as `[P1]` and internal source-data markers. They are not final Nature Communications numbered references, and they do not close blind external validation, repository DOI, Reporting Summary, figure numbering or public-release gates.

# Introduction Draft v1 cited

Ground-penetrating radar (GPR) is increasingly used to support non-destructive inspection, subsurface mapping and infrastructure assessment, where recognition models are expected to work beyond a single curated image collection [P1]. For such models, high internal test performance is useful only if it reflects transferable subsurface information rather than acquisition-, environment- or processing-specific regularities. This distinction is especially important for GPR B-scan recognition, because nominally similar images can be shaped by site conditions, instrument settings, rendering choices and dataset construction [P1].

A central evaluation bottleneck is that common random or weakly structured splits can mix samples that share provenance structure across training and test partitions [P4,P5]. When acquisition setting, environment, project identity or processing chain is correlated with the target label, a model may appear to generalize while partly exploiting these non-target cues. The problem is not that every GPR model is invalid, but that conventional split protocols can make it difficult to separate target recognition from provenance sensitivity. A benchmark intended to support generalization claims therefore needs to audit executable assets, split construction and environment transfer explicitly [P2,P4,P5].

Existing GPR recognition studies often report model performance within individual datasets, but fewer workflows make the evidence boundary executable: which assets can be regenerated, which labels support grouped evaluation, which model families agree, and which results survive environment or project-level stress tests. This leaves an unresolved gap between model comparison and provenance-aware validation. In particular, a claim that a model generalizes across GPR settings should be supported by dated manifests, reproducible split logic, model-family-level checks and, ultimately, blind external validation with labels withheld until predictions are frozen.

Here we assemble GPR-ProvenanceBench as an auditable workflow for testing how provenance and environment structure affect GPR recognition. At the current checkpoint, the executable local evidence includes Mojahid, Res-SAM and 4TU assets, five lightweight model-family comparisons for Mojahid and Res-SAM, and raw-trace-derived 4TU stress tests. The strongest current result is the Res-SAM environment transfer drop across model families; Mojahid provides directional but modest split-sensitivity evidence, and 4TU provides stress-test and feasibility boundaries. Blind external validation remains an open gate rather than a completed result. [planned Fig. 1, planned Fig. 2, Table 1 and Table 2; final numbering pending rendering].


# Discussion Draft v1 cited

The central observation from the current executable evidence is that environment and provenance structure can substantially reshape apparent GPR recognition performance. The Res-SAM real-world/synthetic environment-transfer contrasts show the strongest support for this point: the transfer drop is present across multiple model families and is larger than the Mojahid random-minus-grouped contrast. This result shows a reproducible performance collapse under a specific environment shift and suggests that internal accuracy alone is an incomplete proxy for field-facing generalization [planned Fig. 2 and Table 2 source data; P1 for GPR context only].

The secondary evidence layers sharpen rather than replace this main conclusion. Mojahid shows a directionally consistent random-minus-grouped split gap, but only one of five model families reaches the predeclared material-support threshold, so it should be interpreted as modest and model-dependent split sensitivity. The 4TU experiments show that raw-trace-derived counterfactual variants can strongly disrupt fixed-split predictions, but the same signal weakens under project-level repeated splits. Together, these results support a benchmark argument about evaluation fragility, not a universal claim that all GPR recognition results are driven by leakage.

Several rival explanations constrain the interpretation. First, the TinyCNN results indicate that provenance effects can depend on model family, so a single architecture cannot define the claim. Second, the 4TU group-aware weakening may reflect limited project counts and imbalanced metadata labels rather than the absence of processing sensitivity. Third, the current 4TU target audit shows that only some labels can support grouped holdouts with useful coverage. These constraints are not incidental limitations; they are part of the evidence for why provenance-aware GPR evaluation must report asset feasibility alongside performance [P2,P3,P5].

A practical contribution of the current package is the separation of executable evidence from nominal dataset availability. Dated manifests, source-data packages, Results and Methods skeletons, manuscript assembly files and the M0-M2 check script create a reproducible audit path for the current checkpoint. The source-data deposit and sanitized release staging previews also make the future public-release work explicit [source-data deposit and release-readiness artifacts; not a public repository]. However, these previews are internal release candidates; they are not a public repository, do not provide persistent identifiers and do not resolve third-party redistribution rights.

The manuscript is therefore not submission-ready. The most important missing evidence is a real blind external validation asset that is unused during development, hash-frozen, label-held and evaluated once after prediction freezing. In addition, the main figures have not been rendered, the Data Availability and Code Availability statements lack repository identifiers, the Reporting Summary still requires final answers, and third-party data rights are not cleared for public release. These are blocking items rather than cosmetic production tasks, because they determine whether the central generalization claim can be evaluated independently.


# Conclusion Draft v1 cited

GPR-ProvenanceBench turns provenance-aware GPR evaluation into an auditable workflow by linking asset status, split construction, model-family comparisons, stress tests, source-data mapping and dated regeneration checks.

At this checkpoint, Res-SAM environment transfer provides the strongest cross-model evidence that apparent GPR generalization can be brittle, whereas Mojahid and 4TU provide bounded directional and stress-test support.

The narrow implication is that provenance-aware evaluation should precede broad claims of GPR model generalization [P1,P4,P5]; the final submission case still depends on blind external validation, rendered figures, repository identifiers and public-release rights being closed.

