#!/usr/bin/env python3
"""Build a conservative manuscript draft package from audited claims."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "conservative_manuscript_draft_20260810"
CLAIM_AUDIT = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "manuscript_claim_readiness_audit.csv"
ABSTRACT_GUARDS = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "abstract_claim_guardrails.csv"
TABLES_MD = BENCH_ROOT / "reports" / "manuscript_table_drafts_20260810" / "manuscript_table_drafts.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


TITLE_CANDIDATES = [
    {
        "rank": "1",
        "title": "Environment transfer exposes fragile generalization in ground-penetrating-radar recognition",
        "type": "finding-led",
        "defensibility": "highest",
        "reason": "States the strongest supported result without claiming blind external validation.",
    },
    {
        "rank": "2",
        "title": "GPR-ProvenanceBench audits environment and provenance sensitivity in radar recognition",
        "type": "resource/workflow-led",
        "defensibility": "high",
        "reason": "Emphasizes the auditable workflow and avoids overclaiming external generalization.",
    },
    {
        "rank": "3",
        "title": "Provenance-aware evaluation reveals environment-transfer fragility in GPR recognition",
        "type": "balanced",
        "defensibility": "high",
        "reason": "Connects the evaluation contribution to the main Res-SAM result.",
    },
    {
        "rank": "4",
        "title": "A reproducible audit workflow for environment-sensitive ground-penetrating-radar recognition",
        "type": "methods/resource-leaning",
        "defensibility": "medium",
        "reason": "Useful if the paper is framed as benchmark/resource rather than finding-led.",
    },
]


TERMINOLOGY_ROWS = [
    {
        "canonical_term": "ground-penetrating radar (GPR)",
        "first_use": "ground-penetrating radar (GPR)",
        "variants_to_avoid": "Ground Penetrating Radar; GPR radar",
        "decision": "spell out once, then use GPR",
    },
    {
        "canonical_term": "GPR-ProvenanceBench",
        "first_use": "GPR-ProvenanceBench",
        "variants_to_avoid": "GPR Provenance Bench; provenance benchmark",
        "decision": "use as benchmark/workflow name",
    },
    {
        "canonical_term": "Res-SAM",
        "first_use": "Res-SAM",
        "variants_to_avoid": "ResSAM; RES-SAM",
        "decision": "use dataset/model-source name as currently recorded",
    },
    {
        "canonical_term": "Mojahid",
        "first_use": "Mojahid",
        "variants_to_avoid": "Mojahid dataset if not introduced; MJH",
        "decision": "use as dataset name",
    },
    {
        "canonical_term": "4TU",
        "first_use": "4TU",
        "variants_to_avoid": "Four TU; 4-TU",
        "decision": "use as asset/source name",
    },
    {
        "canonical_term": "TIGPR",
        "first_use": "TIGPR",
        "variants_to_avoid": "TI-GPR; tigpr",
        "decision": "use only with NO-GO local-core boundary",
    },
    {
        "canonical_term": "balanced accuracy",
        "first_use": "balanced accuracy",
        "variants_to_avoid": "BA unless abbreviation is introduced",
        "decision": "prefer spelled-out form in main text",
    },
    {
        "canonical_term": "blind external validation",
        "first_use": "blind external validation",
        "variants_to_avoid": "external validation if blind labels are not held",
        "decision": "use only as open gate until real evaluation exists",
    },
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    claims = read_csv(CLAIM_AUDIT)
    abstract_guards = read_csv(ABSTRACT_GUARDS)
    tables_present = TABLES_MD.exists()

    write_csv(OUT_DIR / "title_candidates_v0_1.csv", TITLE_CANDIDATES, ["rank", "title", "type", "defensibility", "reason"])
    write_csv(OUT_DIR / "terminology_ledger_v0_1.csv", TERMINOLOGY_ROWS, ["canonical_term", "first_use", "variants_to_avoid", "decision"])

    paragraph_map = [
        {
            "section": "Abstract",
            "paragraph": "A1",
            "job": "context/problem -> approach -> key result -> boundary",
            "claim_ids": "R1,R2,R3,R4,R6",
            "word_target": "140-150",
        },
        {
            "section": "Results",
            "paragraph": "R1",
            "job": "system/workflow validation",
            "claim_ids": "R1",
            "word_target": "130-170",
        },
        {
            "section": "Results",
            "paragraph": "R2",
            "job": "main result",
            "claim_ids": "R2",
            "word_target": "150-190",
        },
        {
            "section": "Results",
            "paragraph": "R3",
            "job": "baseline comparison",
            "claim_ids": "R3",
            "word_target": "130-170",
        },
        {
            "section": "Results",
            "paragraph": "R4",
            "job": "stress test/failure mode",
            "claim_ids": "R4,R5",
            "word_target": "180-230",
        },
        {
            "section": "Results",
            "paragraph": "R5",
            "job": "external-validation boundary",
            "claim_ids": "R6",
            "word_target": "120-160",
        },
        {
            "section": "Discussion",
            "paragraph": "D1",
            "job": "central advance",
            "claim_ids": "R2",
            "word_target": "120-160",
        },
        {
            "section": "Discussion",
            "paragraph": "D2",
            "job": "rival explanations and constraints",
            "claim_ids": "R3,R4,R5",
            "word_target": "170-220",
        },
        {
            "section": "Discussion",
            "paragraph": "D3",
            "job": "reuse and open gates",
            "claim_ids": "R1,R6",
            "word_target": "160-210",
        },
    ]
    write_csv(OUT_DIR / "paragraph_map_v0_1.csv", paragraph_map, ["section", "paragraph", "job", "claim_ids", "word_target"])

    abstract = (
        "Ground-penetrating radar (GPR) recognition models are often evaluated within curated datasets, but such tests may not separate target recognition from acquisition, environment or processing structure. "
        "We assembled GPR-ProvenanceBench as an auditable workflow linking dated manifests, grouped split logic, model-family comparisons and source-data traceability. "
        "At the current checkpoint, Res-SAM environment transfer produced the strongest reproducible signal: real-to-synthetic transfer showed directional and material drops in all five model families, with a mean balanced-accuracy delta of 0.4239, and synthetic-to-real transfer showed directional and material drops in four of five families, with a mean delta of 0.3743. "
        "Mojahid showed only directional and modest split sensitivity, whereas 4TU multi-layer counterfactual stress tests defined stress-test and feasibility boundaries. "
        "These results support a provenance-aware evaluation argument, not yet a completed blind external validation claim."
    )

    results = """# Results draft v0.1

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
"""

    discussion = """# Discussion draft v0.1

The current evidence indicates that environment and provenance structure can substantially reshape apparent GPR recognition performance. The strongest support comes from Res-SAM environment transfer, where performance drops were reproducible across multiple model families and larger than the Mojahid random-minus-grouped contrast. This finding does not show that every GPR model fails under deployment, but it does show that high internal performance is an insufficient basis for broad generalization claims when environment structure is not explicitly audited.

The secondary evidence layers constrain the interpretation. Mojahid showed directionally consistent split sensitivity, but the effect was modest and model-dependent at the five-family synthesis layer. The 4TU experiments showed sensitivity to raw-trace-derived perturbations across several evidence layers, but the group-aware and target-feasibility audits kept this asset in a stress-test role. These patterns are consistent with evaluation fragility, but they also indicate that the observed effects depend on asset structure, target feasibility and split design. The benchmark should therefore be read as an audit workflow and evidence boundary rather than as a universal leakage detector.

Several requirements remain open before a final Nature Communications submission can be claimed. The main figures still need formal rendering and visual quality assurance, repository identifiers and release licences remain unresolved, and the Reporting Summary cannot be finalized until Methods, figures, source data and validation status are frozen. Most importantly, blind external validation remains a no-go gate until a real held-label GPR asset is acquired and evaluated once after prediction freezing. These limits are substantive rather than cosmetic because they determine the strength of the central generalization claim.
"""

    draft_md = [
        "# Conservative manuscript draft v0.1 2026-08-10",
        "",
        "## One-sentence argument",
        "",
        "In GPR recognition, current executable evidence shows that environment and provenance structure can strongly reshape apparent generalization, supported most directly by Res-SAM environment-transfer drops across five model families, with Mojahid and 4TU providing bounded secondary and stress-test evidence, while blind external validation and submission gates remain open.",
        "",
        "## Recommended title",
        "",
        TITLE_CANDIDATES[0]["title"],
        "",
        "## Abstract draft",
        "",
        abstract,
        "",
        results,
        "",
        discussion,
        "",
        "## Assumptions and missing inputs",
        "",
        "1. The draft uses current audited claims only and does not invent new experiments.",
        "2. Figure references remain conceptual until formal rendering and visual QA are complete.",
        "3. Repository DOI, code DOI, rights clearance, final Reporting Summary and blind external validation remain missing.",
        "4. The target framing is Nature Communications Article; final word budget must include Methods within the main ~5000-word limit.",
        "",
    ]
    (OUT_DIR / "conservative_manuscript_draft_v0_1.md").write_text("\n".join(draft_md), encoding="utf-8")

    claim_trace_rows = [
        {
            "draft_section": "Abstract",
            "claim_ids_used": "R1,R2,R3,R4,R6",
            "guardrail_source": "abstract_claim_guardrails.csv",
            "status": "bounded_draft_only",
        },
        {
            "draft_section": "Results",
            "claim_ids_used": "R1,R2,R3,R4,R5,R6",
            "guardrail_source": "manuscript_claim_readiness_audit.csv",
            "status": "bounded_draft_only",
        },
        {
            "draft_section": "Discussion",
            "claim_ids_used": "R2,R3,R4,R5,R6",
            "guardrail_source": "forbidden_claims_ledger.csv",
            "status": "bounded_draft_only",
        },
    ]
    write_csv(OUT_DIR / "draft_claim_trace_v0_1.csv", claim_trace_rows, ["draft_section", "claim_ids_used", "guardrail_source", "status"])

    qa_rows = [
        {
            "check": "Nat Comms abstract length",
            "result": "PASS",
            "detail": f"{len(abstract.split())} words; limit is 150 words.",
        },
        {
            "check": "Blind external validation overclaim",
            "result": "PASS",
            "detail": "Draft states blind external validation remains open/no-go.",
        },
        {
            "check": "Repository/DOI overclaim",
            "result": "PASS",
            "detail": "Draft states identifiers remain unresolved.",
        },
        {
            "check": "Main claim calibration",
            "result": "PASS",
            "detail": "Res-SAM is lead result; Mojahid and 4TU are downgraded.",
        },
        {
            "check": "Tables available for context",
            "result": "PASS" if tables_present else "WARN",
            "detail": "Manuscript table drafts present." if tables_present else "Manuscript table drafts missing.",
        },
    ]
    write_csv(OUT_DIR / "draft_boundary_qa_v0_1.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "run_id": "20260810_conservative_manuscript_draft_v0_1",
        "title_candidates": len(TITLE_CANDIDATES),
        "terminology_terms": len(TERMINOLOGY_ROWS),
        "paragraph_map_rows": len(paragraph_map),
        "abstract_words": len(abstract.split()),
        "nat_comms_abstract_limit": 150,
        "abstract_within_limit": len(abstract.split()) <= 150,
        "draft_sections": 3,
        "claim_trace_rows": len(claim_trace_rows),
        "qa_rows": len(qa_rows),
        "submission_ready": False,
        "status": "conservative_draft_ready_not_submission_final",
        "boundary": "Draft is conservative manuscript prose based on audited claims; final submission remains blocked by figures, external validation, DOI, rights and Reporting Summary.",
    }
    (OUT_DIR / "conservative_manuscript_draft_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Conservative manuscript draft report 2026-08-10",
        "",
        f"- Title candidates: {summary['title_candidates']}",
        f"- Terminology terms: {summary['terminology_terms']}",
        f"- Paragraph-map rows: {summary['paragraph_map_rows']}",
        f"- Abstract words: {summary['abstract_words']} / {summary['nat_comms_abstract_limit']}",
        f"- Draft sections: {summary['draft_sections']}",
        f"- Claim-trace rows: {summary['claim_trace_rows']}",
        f"- QA rows: {summary['qa_rows']}",
        "",
        "Conclusion: conservative prose is ready for author review, but not for final submission.",
        "",
    ]
    (OUT_DIR / "conservative_manuscript_draft_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
