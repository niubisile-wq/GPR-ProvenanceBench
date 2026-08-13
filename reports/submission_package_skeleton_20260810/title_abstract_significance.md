# Submission Package Skeleton 2026-08-10

Purpose: provide a bounded Nature Communications-facing title, abstract and cover-letter scaffold from frozen evidence only.

## One-Sentence Argument

In GPR recognition, we show that source and environment structure can materially change apparent model generalization using dated manifests, five model families, split/environment-transfer contrasts and counterfactual stress tests, with blind external validation still open.

## Recommended Title

Environment transfer exposes brittle generalization in ground-penetrating radar recognition

## Title Alternatives

| rank | title | type | status | boundary |
| --- | --- | --- | --- | --- |
| 1 | Environment transfer exposes brittle generalization in ground-penetrating radar recognition | finding-led | most_defensible_current_title | Lead claim is Res-SAM environment transfer; external blind validation is not complete. |
| 2 | A provenance-aware benchmark for evaluating ground-penetrating radar recognition | resource/method-led | fallback_if_framed_as_benchmark | Use if external validation remains open and the paper is downgraded to benchmark/resource framing. |
| 3 | Source and environment structure reshape performance estimates in GPR image recognition | mechanism/phenomenon-led | balanced_scope | Avoids claiming completed mitigation or blind validation. |
| 4 | Provenance-aware evaluation of GPR recognition under split and environment shifts | methods-led | conservative | Best if the manuscript emphasizes evaluation protocol rather than a standalone discovery. |

## Abstract Draft

Ground-penetrating radar (GPR) recognition models are commonly assessed with internal splits that may preserve source and processing structure. Here we assemble a provenance-aware evaluation skeleton across locally executable Mojahid, 4TU and Res-SAM assets, while keeping TIGPR and blind external validation as open gates. Across five model families, Res-SAM real-world/synthetic environment transfer produced the strongest current signal, with material support in 5/5 model families for real-to-synthetic transfer and 4/5 for synthetic-to-real transfer. Mojahid split inflation was directionally consistent but modest, and 4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result. These results indicate that GPR recognition claims should report source-aware splits, environment-transfer contrasts and explicit validation gates before being interpreted as robust generalization.

Word count: 121 / 150.

## Significance Paragraph Draft

GPR-based subsurface recognition is increasingly evaluated with machine-learning benchmarks, but internal splits can leave source, acquisition or processing cues shared between training and test data. The current evidence shows that this issue is not a cosmetic reporting detail: in Res-SAM, environment transfer produced the strongest cross-model performance drop, whereas Mojahid and 4TU provided more bounded split-sensitivity, stress-test and feasibility-boundary evidence. A provenance-aware evaluation workflow can therefore make GPR recognition studies more reusable by separating executable local evidence from unresolved confirmation gates, especially blind external validation.

## Cover Letter Skeleton

1. What the finding is: We show that source and environment structure can substantially reshape apparent generalization in GPR recognition, with the strongest current evidence from Res-SAM real-world/synthetic transfer across five model families.
2. What makes it new: The manuscript frames GPR recognition around provenance-aware evaluation, combining dated asset manifests, split/transfer contrasts, counterfactual 4TU stress tests and explicit validation gates rather than relying on random split performance.
3. Why it matters across disciplines: The work is relevant to geophysics, infrastructure sensing and machine-learning evaluation because it provides a reproducible way to distinguish robust subsurface recognition from dataset-source or processing-chain shortcuts.

## Section Budget For Nature Communications Article

| section | target words | current status |
| --- | ---: | --- |
| Introduction | 700 | outline not yet drafted |
| Results | 1800 | skeleton ready |
| Discussion | 700 | skeleton not yet drafted |
| Methods | 1800 | module skeleton ready |
| Abstract | 150 | draft ready |

## Required Companion Artifacts

1. Data Availability statement with public repository identifiers remains missing.
2. Code Availability statement with repository URL and archival DOI remains missing.
3. Reporting Summary remains missing.
4. Final figure files are not rendered yet.
5. Blind external validation remains an open gate, not a completed result.

## Evidence Backbone

Methods modules covered: M1, M2, M3, M4, M5, M6, M7.

Planned display items covered: Figure 1, Figure 2, Figure 3, Figure 4, Figure 5, Figure 6, Table 1, Table 2, Table 3.

| claim | status | figure/table | boundary |
| --- | --- | --- | --- |
| We first froze the executable evidence boundary rather than treating all nominal datasets as equivalent validation assets. | supported_for_checkpoint | Figure 1; Table 1 | This establishes asset/protocol status, not model performance. |
| Across five model families, Res-SAM environment transfer produced the strongest and most reproducible performance drop. | supported_current_main | Figure 2; Table 2 | Scope is Mojahid and Res-SAM only; not blind external validation. |
| Mojahid random-minus-grouped inflation was directionally consistent but too modest to serve as the lead claim. | directional_only | Figure 3; Table 2 | Do not frame as universal leakage; only 1/5 model families reaches material support. |
| 4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result. | stress_test_supported | Figure 4 | Stress-test and feasibility-boundary evidence only; not final causal proof, main 4TU confirmation or blind external validation. |
| A target-level feasibility audit explained why 4TU should not yet be expanded into the main cross-model confirmation matrix. | gate_supported | Figure 5 | Feasibility/gate result, not model superiority. |
| The blind external validation gate remains open despite having protocol templates and dry-run evaluators. | not_yet_supported | Figure 6 | No completed blind external validation; protocol readiness is not a positive result. |

## Drafting Guardrails

1. Do not state or imply that blind external validation is complete.
2. Do not describe 4TU as a full five-model confirmation layer.
3. Do not lead the abstract with Mojahid split inflation because it is directional_only.
4. Keep the main title and abstract anchored to Res-SAM environment-transfer fragility until stronger external evidence is added.
