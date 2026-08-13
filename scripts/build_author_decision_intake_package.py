#!/usr/bin/env python3
"""Build author/external decision intake package for remaining submission gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "author_decision_intake_package_20260810"
DASHBOARD_GATES = BENCH_ROOT / "reports" / "submission_readiness_dashboard_20260810" / "open_gate_priority_queue.csv"


DECISION_ROWS = [
    {
        "decision_id": "D001",
        "decision": "Figure rendering backend",
        "owner": "author",
        "required_choice": "Python or R",
        "recommended_default": "Python",
        "reason": "Current environment and scripts are Python-based; figure source data are CSV/JSON; using Python minimizes translation risk.",
        "blocks": "Formal figure rendering, visual QA, panel-level Source Data mapping.",
        "status": "needs_author_confirmation",
    },
    {
        "decision_id": "D002",
        "decision": "External blind asset route",
        "owner": "author/advisor/data_holder",
        "required_choice": "Track B third-party blind asset, TIGPR restoration, 4TU-like raw-trace asset, or no external result yet",
        "recommended_default": "Track B third-party blind asset",
        "reason": "Current Res-SAM is already used and TIGPR is local NO-GO; a separate held-label asset is the cleanest external validation route.",
        "blocks": "Blind external validation, final main claim strength, Reporting Summary blinding/external validation fields.",
        "status": "external_input_required",
    },
    {
        "decision_id": "D003",
        "decision": "Code licence",
        "owner": "author/institution",
        "required_choice": "MIT, BSD-3-Clause, Apache-2.0, institutional licence, or restricted",
        "recommended_default": "MIT or BSD-3-Clause after institutional approval",
        "reason": "A software licence is required before public code reuse and archive DOI.",
        "blocks": "Code Availability final wording, public code release, code DOI.",
        "status": "needs_author_confirmation",
    },
    {
        "decision_id": "D004",
        "decision": "Derived data licence",
        "owner": "author/institution/data providers",
        "required_choice": "CC BY 4.0, CC0, restricted derived metrics only, or no public derived data",
        "recommended_default": "CC BY 4.0 for derived non-raw artifacts after third-party rights review",
        "reason": "Derived manifests and source-data tables may contain third-party-derived metadata and need redistribution clearance.",
        "blocks": "Data Availability final wording, source-data deposit, release package.",
        "status": "rights_review_required",
    },
    {
        "decision_id": "D005",
        "decision": "Repository route",
        "owner": "author",
        "required_choice": "Zenodo, OSF, institutional repository, GitHub+Zenodo, or other DOI-capable repository",
        "recommended_default": "GitHub+Zenodo for code and Zenodo/OSF for derived data if rights permit",
        "reason": "Persistent DOI/accession is required for Nature-style Data/Code Availability.",
        "blocks": "Repository identifiers, Data Availability, Code Availability, FAIR metadata.",
        "status": "needs_author_confirmation",
    },
    {
        "decision_id": "D006",
        "decision": "Manuscript framing if external validation remains open",
        "owner": "author",
        "required_choice": "Finding-led Nature Communications article, benchmark/resource framing, or hold submission until external validation",
        "recommended_default": "Benchmark/resource framing unless real blind external validation is acquired",
        "reason": "The current strongest evidence is internal/environment-transfer; blind external validation remains NO-GO.",
        "blocks": "Title, abstract, cover letter, Table 3 placement, claim strength.",
        "status": "needs_author_confirmation",
    },
    {
        "decision_id": "D007",
        "decision": "Final reference style conversion timing",
        "owner": "author",
        "required_choice": "Convert after final prose lock or convert now as temporary numbered references",
        "recommended_default": "Convert after final prose lock",
        "reason": "Candidate [P#] markers are still safer while figures, tables and prose continue changing.",
        "blocks": "Final bibliography and citation numbering.",
        "status": "defer_until_prose_lock",
    },
]


DEPENDENCY_ROWS = [
    {
        "blocked_output": "Rendered main figures",
        "required_decision_or_input": "D001 Figure rendering backend",
        "next_script_after_decision": "future build_rendered_figures_<backend>.py",
        "current_status": "blocked_by_backend_choice",
    },
    {
        "blocked_output": "Blind external validation result",
        "required_decision_or_input": "D002 External blind asset route plus real data holder input",
        "next_script_after_decision": "validate_external_blind_intake.py --strict-sha; evaluate_external_blind_submission.py --main-claim",
        "current_status": "blocked_by_missing_external_asset",
    },
    {
        "blocked_output": "Public code release DOI",
        "required_decision_or_input": "D003 Code licence and D005 repository route",
        "next_script_after_decision": "release archive creation and DOI registration",
        "current_status": "blocked_by_licence_and_repository",
    },
    {
        "blocked_output": "Public source-data DOI",
        "required_decision_or_input": "D004 Derived data licence and D005 repository route",
        "next_script_after_decision": "repository deposit using repository_metadata_package_20260810",
        "current_status": "blocked_by_rights_and_repository",
    },
    {
        "blocked_output": "Final Reporting Summary",
        "required_decision_or_input": "D001-D005 plus final figure/source-data mapping",
        "next_script_after_decision": "future build_reporting_summary_final.py",
        "current_status": "blocked_by_multiple_open_gates",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gate_rows = read_csv(DASHBOARD_GATES)

    write_csv(
        OUT_DIR / "author_decision_register.csv",
        DECISION_ROWS,
        ["decision_id", "decision", "owner", "required_choice", "recommended_default", "reason", "blocks", "status"],
    )
    write_csv(
        OUT_DIR / "decision_dependency_map.csv",
        DEPENDENCY_ROWS,
        ["blocked_output", "required_decision_or_input", "next_script_after_decision", "current_status"],
    )

    action_rows = [
        {
            "priority": "1",
            "action": "Choose figure backend",
            "exact_author_response_needed": "Python or R",
            "why_now": "This unlocks formal figure rendering from the existing figure_rendering_spec.",
        },
        {
            "priority": "2",
            "action": "Send external blind asset request package",
            "exact_author_response_needed": "Name the data holder/advisor/collaborator or confirm no contact yet",
            "why_now": "External validation is the highest hard gate and requires external lead time.",
        },
        {
            "priority": "3",
            "action": "Choose tentative code/data licence direction",
            "exact_author_response_needed": "MIT/BSD/Apache for code; CC BY/CC0/restricted for derived data, pending institutional approval",
            "why_now": "Repository metadata and Data/Code Availability cannot become final without this.",
        },
        {
            "priority": "4",
            "action": "Choose repository route",
            "exact_author_response_needed": "GitHub+Zenodo, Zenodo only, OSF, institutional repository, or other",
            "why_now": "DOI/accession creation depends on repository route.",
        },
    ]
    write_csv(
        OUT_DIR / "next_author_actions.csv",
        action_rows,
        ["priority", "action", "exact_author_response_needed", "why_now"],
    )

    md_lines = [
        "# Author decision intake package 2026-08-10",
        "",
        "This package collects decisions that cannot be closed by local scripting alone.",
        "",
        "## Immediate decisions",
        "",
        "| ID | Decision | Recommended default | Blocks |",
        "| --- | --- | --- | --- |",
    ]
    for row in DECISION_ROWS:
        md_lines.append(f"| {row['decision_id']} | {row['decision']} | {row['recommended_default']} | {row['blocks']} |")
    md_lines.extend(
        [
            "",
            "## Current open gates from dashboard",
            "",
            "| Priority | Gate | Status | Current best action |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in gate_rows:
        md_lines.append(f"| {row['priority']} | {row['gate']} | {row['status']} | {row['current_best_action']} |")
    md_lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This intake package does not close any gate. It defines the exact choices required before figure rendering, repository deposit, external validation and final Reporting Summary can proceed.",
            "",
        ]
    )
    (OUT_DIR / "author_decision_intake.md").write_text("\n".join(md_lines), encoding="utf-8")

    summary = {
        "run_id": "20260810_author_decision_intake_package",
        "decisions": len(DECISION_ROWS),
        "dependencies": len(DEPENDENCY_ROWS),
        "next_author_actions": len(action_rows),
        "open_gates_imported": len(gate_rows),
        "local_work_can_continue_without_author_decisions": False,
        "status": "author_decisions_required",
        "boundary": "Decision intake package is ready, but figure rendering, DOI creation, external validation and final Reporting Summary remain blocked until decisions or external inputs arrive.",
    }
    (OUT_DIR / "author_decision_intake_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Author decision intake report 2026-08-10",
        "",
        f"- Decisions required: {summary['decisions']}",
        f"- Dependency rows: {summary['dependencies']}",
        f"- Next author actions: {summary['next_author_actions']}",
        f"- Open gates imported: {summary['open_gates_imported']}",
        "",
        "Immediate required response: choose `Python` or `R` for figure rendering, and identify whether a real blind external data holder exists.",
        "",
    ]
    (OUT_DIR / "author_decision_intake_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
