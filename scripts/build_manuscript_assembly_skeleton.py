#!/usr/bin/env python3
"""Build a manuscript assembly skeleton from frozen 2026-08-10 artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manuscript_assembly_skeleton_20260810"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results_summary = read_json(
        BENCH_ROOT / "reports" / "results_section_skeleton_20260810" / "results_section_skeleton.json"
    )
    methods_summary = read_json(
        BENCH_ROOT / "reports" / "methods_section_skeleton_20260810" / "methods_section_skeleton.json"
    )
    submission_summary = read_json(
        BENCH_ROOT / "reports" / "submission_package_skeleton_20260810" / "submission_package_summary.json"
    )
    companion_summary = read_json(
        BENCH_ROOT / "reports" / "companion_artifacts_skeleton_20260810" / "companion_artifacts_summary.json"
    )
    source_data_summary = read_json(
        BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "source_data_deposit_summary.json"
    )
    release_summary = read_json(
        BENCH_ROOT / "reports" / "release_readiness_audit_20260810" / "release_readiness_summary.json"
    )
    sanitized_summary = read_json(
        BENCH_ROOT / "reports" / "sanitized_release_staging_20260810" / "sanitized_release_summary.json"
    )

    section_rows = [
        {
            "section": "Title",
            "role": "Searchable finding-led title",
            "target_words": 15,
            "current_asset": "submission_package_skeleton/title_candidates.csv",
            "status": "draft_ready",
            "boundary": "Retain environment-transfer framing unless future blind validation changes the hierarchy.",
        },
        {
            "section": "Abstract",
            "role": "150-word unstructured Nat Commun abstract",
            "target_words": 150,
            "current_asset": "submission_package_skeleton/title_abstract_significance.md",
            "status": "draft_ready_bounded",
            "boundary": "Current 115-word draft must not imply completed blind external validation.",
        },
        {
            "section": "Introduction",
            "role": "Field stake, evaluation bottleneck, provenance-aware gap, present study",
            "target_words": 700,
            "current_asset": "not yet drafted",
            "status": "outline_needed",
            "boundary": "Do not overstate novelty before external validation closes.",
        },
        {
            "section": "Results",
            "role": "Six claim-first paragraphs led by Res-SAM environment transfer",
            "target_words": 1800,
            "current_asset": "results_section_skeleton_20260810",
            "status": "skeleton_ready",
            "boundary": "Mojahid is directional-only; 4TU is stress-test evidence; external validation is open.",
        },
        {
            "section": "Methods",
            "role": "Seven reproducibility modules tied to Results claims",
            "target_words": 1800,
            "current_asset": "methods_section_skeleton_20260810",
            "status": "skeleton_ready",
            "boundary": "No full Res-SAM model replication and no TIGPR executable asset yet.",
        },
        {
            "section": "Discussion",
            "role": "Interpret central advance, rival explanations, limits and next validation",
            "target_words": 700,
            "current_asset": "not yet drafted",
            "status": "outline_needed",
            "boundary": "Limitations must name external blind NO-GO, 4TU group weakening and third-party rights.",
        },
        {
            "section": "Data Availability",
            "role": "Repository and accession statement",
            "target_words": 120,
            "current_asset": "companion_artifacts_skeleton/data_availability_skeleton.md",
            "status": "blocked",
            "boundary": "Cannot be ready-to-paste until repository DOI/accession exists.",
        },
        {
            "section": "Code Availability",
            "role": "Public code release statement",
            "target_words": 100,
            "current_asset": "companion_artifacts_skeleton/code_availability_skeleton.md",
            "status": "blocked",
            "boundary": "Cannot be complete until public repository URL, release tag, licence and DOI exist.",
        },
        {
            "section": "Reporting Summary",
            "role": "Study design, statistics, blinding, software and data checklist",
            "target_words": 0,
            "current_asset": "companion_artifacts_skeleton/reporting_summary_checklist.csv",
            "status": "blocked",
            "boundary": "Checklist rows exist but final answers are incomplete.",
        },
        {
            "section": "Figures and Source Data",
            "role": "Six figures, three tables and source-data deposit mapping",
            "target_words": 0,
            "current_asset": "figure/table source packages and source_data_deposit_package",
            "status": "source_ready_not_rendered",
            "boundary": "Actual figure rendering is not done and requires a selected plotting backend.",
        },
        {
            "section": "Cover Letter",
            "role": "Finding, novelty and cross-disciplinary relevance",
            "target_words": 180,
            "current_asset": "submission_package_skeleton/cover_letter_skeleton.md",
            "status": "draft_ready_bounded",
            "boundary": "Must be revised if external validation or main figure hierarchy changes.",
        },
    ]

    traceability_rows = [
        {
            "claim_id": "R1",
            "manuscript_location": "Results paragraph 1; Methods M1/M7; Figure 1; Table 1",
            "claim": "The executable local evidence set is bounded and auditable.",
            "evidence_status": "supported",
            "prose_rule": "Use as study-design context, not performance evidence.",
        },
        {
            "claim_id": "R2",
            "manuscript_location": "Results paragraph 2; Methods M2/M3/M7; Figure 2; Table 2",
            "claim": "Res-SAM environment transfer exposes the strongest current cross-model generalization fragility.",
            "evidence_status": "supported",
            "prose_rule": "Lead the Results with this claim and include quantitative transfer drops.",
        },
        {
            "claim_id": "R3",
            "manuscript_location": "Results paragraph 3; Methods M2/M3/M7; Figure 3; Table 2",
            "claim": "Mojahid random-minus-grouped split inflation is directionally consistent but modest.",
            "evidence_status": "directional_only",
            "prose_rule": "Frame as secondary support; do not call it decisive leakage proof.",
        },
        {
            "claim_id": "R4",
            "manuscript_location": "Results paragraph 4; Methods M4/M7; Figure 4",
            "claim": "4TU fixed-split counterfactual sensitivity weakens under group-aware repeated splits.",
            "evidence_status": "stress_test",
            "prose_rule": "Use as failure-mode and boundary evidence, not main confirmation.",
        },
        {
            "claim_id": "R5",
            "manuscript_location": "Results paragraph 5; Methods M5/M7; Figure 5",
            "claim": "4TU label and project structure constrain which tasks can support grouped evaluation.",
            "evidence_status": "supported_boundary",
            "prose_rule": "Report feasibility limits before any 4TU generalization claim.",
        },
        {
            "claim_id": "R6",
            "manuscript_location": "Results paragraph 6; Methods M6/M7; Figure 6",
            "claim": "External blind validation is protocol-ready but not complete.",
            "evidence_status": "open_gate",
            "prose_rule": "Write as a remaining gate only; no main-claim language.",
        },
    ]

    blocker_rows = [
        {
            "blocker": "Real blind external validation",
            "severity": "critical",
            "current_status": "NO-GO",
            "required_action": "Acquire an unused external GPR asset, strict-SHA validate intake, freeze predictions and run one locked evaluation after label unlock.",
        },
        {
            "blocker": "Rendered main figures",
            "severity": "critical",
            "current_status": "source data only",
            "required_action": "Select Python or R backend, render Figure 2/Table 2 first, then Figures 3-6 with panel-level source mapping.",
        },
        {
            "blocker": "Data repository DOI/accession",
            "severity": "critical",
            "current_status": "missing",
            "required_action": "Create a public or controlled-access repository record and replace placeholders in Data Availability.",
        },
        {
            "blocker": "Code release DOI and licence",
            "severity": "critical",
            "current_status": "missing",
            "required_action": "Prepare repository, release tag, licence file and archival DOI.",
        },
        {
            "blocker": "Reporting Summary final answers",
            "severity": "major",
            "current_status": "checklist only",
            "required_action": "Complete final study-design, blinding, exclusion, statistics and software answers.",
        },
        {
            "blocker": "Third-party data rights",
            "severity": "major",
            "current_status": "not cleared",
            "required_action": "Verify redistribution rights for reused public/third-party data and keep raw data out of public release if rights are unclear.",
        },
        {
            "blocker": "Full Res-SAM model replication",
            "severity": "major",
            "current_status": "NO-GO",
            "required_action": "Restore SAM ViT-L checkpoint and compatible runtime before claiming full method replication.",
        },
        {
            "blocker": "TIGPR executable asset",
            "severity": "major",
            "current_status": "NO-GO",
            "required_action": "Restore authorized five-class image tree and rebuild the 7169-row index before counting TIGPR as a core executable asset.",
        },
    ]

    write_csv(OUT_DIR / "manuscript_section_plan.csv", section_rows)
    write_csv(OUT_DIR / "claim_section_traceability.csv", traceability_rows)
    write_csv(OUT_DIR / "manuscript_blocker_checklist.csv", blocker_rows)

    summary = {
        "status_date": "2026-08-10",
        "one_sentence_argument": (
            "In ground-penetrating radar recognition, current executable evidence shows that "
            "environment and provenance structure can strongly reshape apparent generalization, "
            "with Res-SAM environment transfer providing the strongest cross-model support and "
            "Mojahid/4TU providing bounded secondary and stress-test evidence."
        ),
        "target_journal": "Nature Communications",
        "article_type": "Article",
        "word_budget": {
            "abstract": 150,
            "introduction": 700,
            "results": 1800,
            "discussion": 700,
            "methods": 1800,
            "body_total_target": 5000,
        },
        "source_inputs": {
            "results_paragraphs": results_summary.get("paragraphs", "unknown"),
            "methods_modules": methods_summary.get("modules", "unknown"),
            "submission_ready": submission_summary.get("submission_ready", False),
            "companion_submission_ready": companion_summary.get("submission_ready", False),
            "source_data_submission_ready": source_data_summary.get("submission_ready", False),
            "release_ready": release_summary.get("release_ready", False),
            "sanitized_public_release_ready": sanitized_summary.get("public_release_ready", False),
        },
        "section_rows": len(section_rows),
        "traceability_rows": len(traceability_rows),
        "blocker_rows": len(blocker_rows),
        "manuscript_ready": False,
        "reason_not_ready": [
            "blind external validation remains NO-GO",
            "main figures are not rendered",
            "data/code repository identifiers are missing",
            "Reporting Summary is incomplete",
            "public release rights are not cleared",
        ],
        "official_policy_notes": [
            "Nature Portfolio original research requires a Data Availability statement.",
            "Nature Communications expects a Code Availability statement when custom code is used.",
            "Nature Communications submission uses the online submission system.",
        ],
    }

    (OUT_DIR / "manuscript_assembly_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    markdown = f"""# Manuscript Assembly Skeleton 2026-08-10

## One-sentence argument

{summary["one_sentence_argument"]}

## Target format

- Target journal: Nature Communications.
- Article type: Article.
- Working body budget: Introduction 700 words, Results 1800 words, Discussion 700 words and Methods 1800 words, for an approximately 5000-word body including Methods.
- Abstract budget: 150 words, unstructured.

## Manuscript section status

| Section | Status | Current asset | Boundary |
| --- | --- | --- | --- |
"""
    for row in section_rows:
        markdown += (
            f"| {row['section']} | {row['status']} | {row['current_asset']} | "
            f"{row['boundary']} |\n"
        )

    markdown += """
## Claim-to-section traceability

| Claim ID | Manuscript location | Evidence status | Prose rule |
| --- | --- | --- | --- |
"""
    for row in traceability_rows:
        markdown += (
            f"| {row['claim_id']} | {row['manuscript_location']} | "
            f"{row['evidence_status']} | {row['prose_rule']} |\n"
        )

    markdown += """
## Current main narrative

1. Start with the problem of apparent generalization in GPR recognition.
2. State the unresolved gap: conventional random or weakly grouped evaluation can hide environment and provenance dependence.
3. Lead the Results with Res-SAM environment transfer because it has the strongest current cross-model support.
4. Use Mojahid only as secondary directional split-inflation evidence.
5. Use 4TU as raw-trace-derived stress-test and feasibility evidence, not as a full confirmation layer.
6. Treat blind external validation as an explicit open gate until a real unused asset is evaluated under the locked protocol.

## Blocking checklist

| Blocker | Severity | Current status | Required action |
| --- | --- | --- | --- |
"""
    for row in blocker_rows:
        markdown += (
            f"| {row['blocker']} | {row['severity']} | {row['current_status']} | "
            f"{row['required_action']} |\n"
        )

    markdown += """
## Submission boundary

This package is a manuscript assembly skeleton, not a finished manuscript. It does not close the external validation gate, does not render figures, does not create repository identifiers and does not complete the Reporting Summary.

## Official policy notes to verify at final submission

1. Nature Portfolio requires Data Availability statements for original research.
2. Nature Communications requires a Code Availability statement when custom code is used.
3. Nature Communications files are submitted through the online submission system.
"""

    (OUT_DIR / "manuscript_assembly_skeleton.md").write_text(markdown, encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
