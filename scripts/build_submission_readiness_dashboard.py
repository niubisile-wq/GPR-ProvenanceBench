#!/usr/bin/env python3
"""Build a single submission-readiness dashboard from current checkpoint artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "submission_readiness_dashboard_20260810"


INPUTS = {
    "manuscript_assembly": BENCH_ROOT / "reports" / "manuscript_assembly_skeleton_20260810" / "manuscript_assembly_summary.json",
    "external_validation": BENCH_ROOT / "reports" / "external_validation_readiness_20260810" / "external_validation_readiness_summary.json",
    "companion": BENCH_ROOT / "reports" / "companion_artifacts_skeleton_20260810" / "companion_artifacts_summary.json",
    "source_data": BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "source_data_deposit_summary.json",
    "release": BENCH_ROOT / "reports" / "release_readiness_audit_20260810" / "release_readiness_summary.json",
    "staging": BENCH_ROOT / "reports" / "sanitized_release_staging_20260810" / "sanitized_release_summary.json",
    "citation_pass": BENCH_ROOT / "reports" / "narrative_citation_pass_20260810" / "citation_pass_summary.json",
    "cited_drafts": BENCH_ROOT / "reports" / "narrative_cited_drafts_20260810" / "narrative_cited_drafts_summary.json",
    "anchor_lock": BENCH_ROOT / "reports" / "figure_table_anchor_lock_20260810" / "figure_table_anchor_lock_summary.json",
    "table_drafts": BENCH_ROOT / "reports" / "manuscript_table_drafts_20260810" / "manuscript_table_drafts_summary.json",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bool_status(value: bool, true_label: str = "ready", false_label: str = "not_ready") -> str:
    return true_label if value else false_label


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = {name: read_json(path) for name, path in INPUTS.items()}

    readiness_rows = [
        {
            "area": "Manuscript assembly",
            "current_status": bool_status(data["manuscript_assembly"].get("manuscript_ready", False), "ready", "not_ready"),
            "evidence": "reports/manuscript_assembly_skeleton_20260810/manuscript_assembly_summary.json",
            "blocking_or_next_action": "; ".join(data["manuscript_assembly"].get("reason_not_ready", [])),
            "submission_impact": "Controls whether the package can be treated as manuscript-ready.",
        },
        {
            "area": "Blind external validation",
            "current_status": data["external_validation"]["gate"]["status"],
            "evidence": "reports/external_validation_readiness_20260810/external_validation_readiness_summary.json",
            "blocking_or_next_action": data["external_validation"]["gate"]["decision"],
            "submission_impact": "Main generalization claim cannot be final without a real blind external asset.",
        },
        {
            "area": "Figures",
            "current_status": data["anchor_lock"]["status"],
            "evidence": "reports/figure_table_anchor_lock_20260810/figure_table_anchor_lock_summary.json",
            "blocking_or_next_action": "Render figures, run visual QA, lock panel labels and Source Data.",
            "submission_impact": "Main figures are planned but not submission-ready.",
        },
        {
            "area": "Tables",
            "current_status": data["table_drafts"]["status"],
            "evidence": "reports/manuscript_table_drafts_20260810/manuscript_table_drafts_summary.json",
            "blocking_or_next_action": "Final journal formatting and consistency check after figure order is locked.",
            "submission_impact": "Table source layer is ready; final typesetting remains open.",
        },
        {
            "area": "Narrative citations",
            "current_status": data["cited_drafts"]["status"],
            "evidence": "reports/narrative_cited_drafts_20260810/narrative_cited_drafts_summary.json",
            "blocking_or_next_action": "Convert candidate markers to final numbered references after final prose locks.",
            "submission_impact": "Citation placeholders are resolved, but final reference placement is not locked.",
        },
        {
            "area": "Companion artifacts",
            "current_status": bool_status(data["companion"].get("submission_ready", False), "ready", "not_ready"),
            "evidence": "reports/companion_artifacts_skeleton_20260810/companion_artifacts_summary.json",
            "blocking_or_next_action": "; ".join(data["companion"].get("blocking_items", [])),
            "submission_impact": "Data Availability, Code Availability and Reporting Summary cannot be finalized.",
        },
        {
            "area": "Source-data deposit",
            "current_status": bool_status(data["source_data"].get("submission_ready", False), "ready", "not_ready"),
            "evidence": "reports/source_data_deposit_package_20260810/source_data_deposit_summary.json",
            "blocking_or_next_action": "Final rendered figures, DOI/accession and licence are missing.",
            "submission_impact": "Source-data skeleton is auditable but not final deposit.",
        },
        {
            "area": "Public release",
            "current_status": bool_status(data["release"].get("release_ready", False), "ready", "not_ready"),
            "evidence": "reports/release_readiness_audit_20260810/release_readiness_summary.json",
            "blocking_or_next_action": "Resolve local-path markers, placeholders, licence, DOI and third-party rights.",
            "submission_impact": "Code/data release cannot be claimed as completed.",
        },
        {
            "area": "Sanitized staging",
            "current_status": data["staging"].get("public_release_ready", False) and "public_ready" or "internal_preview_only",
            "evidence": "reports/sanitized_release_staging_20260810/sanitized_release_summary.json",
            "blocking_or_next_action": "Use only as internal preview until licence and DOI decisions close.",
            "submission_impact": "Cannot be cited as a public repository.",
        },
    ]

    open_gate_rows = [
        {
            "priority": "1",
            "gate": "Real blind external validation",
            "status": "NO-GO",
            "required_evidence_to_close": "Strict-SHA manifest, labels held outside analyst workflow, frozen prediction submission, one locked evaluation after label unlock.",
            "current_best_action": "Acquire or restore a separate advisor-held/third-party GPR asset.",
        },
        {
            "priority": "2",
            "gate": "Main figure rendering",
            "status": "not_started",
            "required_evidence_to_close": "Rendered Fig. 1-Fig. 6 or reduced final figure set, visual QA outputs, source-data panel mapping.",
            "current_best_action": "Choose Python or R before running the Nature figure workflow.",
        },
        {
            "priority": "3",
            "gate": "Repository identifiers",
            "status": "missing",
            "required_evidence_to_close": "Data repository DOI/accession and code release DOI.",
            "current_best_action": "Resolve release rights and create archive only after final source-data scope is locked.",
        },
        {
            "priority": "4",
            "gate": "Reporting Summary",
            "status": "incomplete",
            "required_evidence_to_close": "Final answers for study design, sample handling, blinding, statistics, software, data and code.",
            "current_best_action": "Fill from frozen Methods and final figure/table set.",
        },
        {
            "priority": "5",
            "gate": "Third-party rights",
            "status": "not_cleared",
            "required_evidence_to_close": "Licence decisions for derived artifacts and raw/third-party GPR data redistribution boundaries.",
            "current_best_action": "Review release readiness audit and exclude non-redistributable files from public package.",
        },
        {
            "priority": "6",
            "gate": "Final reference numbering",
            "status": "not_locked",
            "required_evidence_to_close": "Final prose, final reference order and manual verification of every cited candidate.",
            "current_best_action": "Keep `[P#]` markers until prose and figure/table references stop moving.",
        },
    ]

    milestone_rows = [
        {
            "milestone": "Evidence package",
            "status": "partially_ready",
            "completed_assets": "Mojahid, 4TU, Res-SAM local manifests; five-model Mojahid/Res-SAM synthesis; 4TU stress-test source packages.",
            "not_completed": "TIGPR restoration; real blind external asset; full Res-SAM SAM checkpoint/runtime replication.",
        },
        {
            "milestone": "Writing package",
            "status": "draft_ready_not_final",
            "completed_assets": "Results/Methods skeletons, submission skeleton, narrative v1 cited/anchored drafts.",
            "not_completed": "Final prose, final numbered references, figure/table final callouts.",
        },
        {
            "milestone": "Figure/table package",
            "status": "tables_ready_figures_not_rendered",
            "completed_assets": "Figure/table anchor lock and Table 1-3 drafts.",
            "not_completed": "Figure rendering, visual QA, panel-level source-data mapping.",
        },
        {
            "milestone": "Companion/release package",
            "status": "skeleton_ready_not_submission_ready",
            "completed_assets": "Data/code availability skeletons, source-data deposit skeleton, release audit, sanitized staging preview.",
            "not_completed": "Data DOI, code DOI, licence, third-party rights and final Reporting Summary.",
        },
    ]

    write_csv(
        OUT_DIR / "submission_readiness_dashboard.csv",
        readiness_rows,
        ["area", "current_status", "evidence", "blocking_or_next_action", "submission_impact"],
    )
    write_csv(
        OUT_DIR / "open_gate_priority_queue.csv",
        open_gate_rows,
        ["priority", "gate", "status", "required_evidence_to_close", "current_best_action"],
    )
    write_csv(
        OUT_DIR / "milestone_completion_matrix.csv",
        milestone_rows,
        ["milestone", "status", "completed_assets", "not_completed"],
    )

    hard_no_go = [row for row in readiness_rows if row["current_status"] in {"NO-GO", "not_ready", "internal_preview_only"}]
    summary = {
        "run_id": "20260810_submission_readiness_dashboard",
        "areas": len(readiness_rows),
        "open_gates": len(open_gate_rows),
        "milestones": len(milestone_rows),
        "hard_no_go_or_not_ready_areas": len(hard_no_go),
        "submission_ready": False,
        "next_required_decision": "Choose Python or R to start formal figure rendering, while separately acquiring a real blind external validation asset.",
        "status": "dashboard_ready_submission_not_ready",
        "boundary": "Dashboard summarizes current evidence; it does not close blind external validation, figure rendering, repository DOI, Reporting Summary or rights gates.",
    }
    (OUT_DIR / "submission_readiness_dashboard_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md_lines = [
        "# Submission readiness dashboard 2026-08-10",
        "",
        "This dashboard consolidates manuscript, figure/table, citation, companion-artifact and release gates into one current-state view.",
        "",
        "## Current Decision",
        "",
        "The package is not submission-ready. The strongest current evidence remains Res-SAM environment-transfer fragility, with Mojahid directional support and 4TU stress-test/feasibility evidence. Blind external validation is still NO-GO.",
        "",
        "## Readiness Areas",
        "",
        "| Area | Status | Submission impact |",
        "| --- | --- | --- |",
    ]
    for row in readiness_rows:
        md_lines.append(f"| {row['area']} | {row['current_status']} | {row['submission_impact']} |")
    md_lines.extend(
        [
            "",
            "## Priority Queue",
            "",
            "| Priority | Gate | Status | Current best action |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in open_gate_rows:
        md_lines.append(f"| {row['priority']} | {row['gate']} | {row['status']} | {row['current_best_action']} |")
    md_lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a dashboard only. It does not convert planned figures into rendered figures, does not create repository identifiers and does not satisfy blind external validation.",
            "",
        ]
    )
    (OUT_DIR / "submission_readiness_dashboard.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
