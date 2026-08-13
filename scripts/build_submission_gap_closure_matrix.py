#!/usr/bin/env python3
"""Build submission gap-closure matrix from current readiness evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "submission_gap_closure_matrix_20260810"
DASHBOARD = BENCH_ROOT / "reports" / "submission_readiness_dashboard_20260810" / "submission_readiness_dashboard.csv"
OPEN_GATES = BENCH_ROOT / "reports" / "submission_readiness_dashboard_20260810" / "open_gate_priority_queue.csv"
DEPENDENCIES = BENCH_ROOT / "reports" / "author_decision_intake_package_20260810" / "decision_dependency_map.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


CLOSURE_DETAILS = {
    "Real blind external validation": {
        "owner": "author/advisor/data_holder",
        "proof_type": "external_asset_plus_locked_evaluation",
        "minimum_evidence": "Real manifest with strict SHA256 checksums, label-holder confirmation, frozen prediction submission, timestamped one-shot evaluation and signed boundary note for any reruns.",
        "local_next_step": "Use the external blind request email and label-holder SOP to contact a real data holder.",
        "blocked_claim": "Do not claim blind external validation or external generalization.",
        "can_close_locally": "no",
    },
    "Main figure rendering": {
        "owner": "author/analyst",
        "proof_type": "rendered_figures_plus_visual_QA",
        "minimum_evidence": "Final Fig. 1-Fig. 6 files, panel labels, source-data panel map, visual QA checklist and exported publication formats.",
        "local_next_step": "Wait for Python/R decision, then run the formal figure workflow from the rendering spec.",
        "blocked_claim": "Do not submit, cite or circulate planned figures as final manuscript figures.",
        "can_close_locally": "after_backend_choice",
    },
    "Repository identifiers": {
        "owner": "author/institution",
        "proof_type": "persistent_identifier",
        "minimum_evidence": "Data repository DOI/accession, code release DOI, repository metadata, archived release files and public landing pages.",
        "local_next_step": "Resolve licence/rights and final source-data scope before deposit.",
        "blocked_claim": "Do not state that code or data are deposited.",
        "can_close_locally": "no",
    },
    "Reporting Summary": {
        "owner": "author/analyst",
        "proof_type": "final_form_answers",
        "minimum_evidence": "Final answers linked to frozen Methods, figure/table set, blinding/external-validation status, software versions and repository identifiers.",
        "local_next_step": "Keep draft only until figures, external validation, repositories and rights are frozen.",
        "blocked_claim": "Do not label the Reporting Summary as final.",
        "can_close_locally": "after_other_gates",
    },
    "Third-party rights": {
        "owner": "author/institution/data_providers",
        "proof_type": "rights_clearance",
        "minimum_evidence": "Licence decisions for code, derived data and raw/third-party material, plus exclusion list for non-redistributable files.",
        "local_next_step": "Use release readiness audit and repository metadata package to identify files requiring approval or exclusion.",
        "blocked_claim": "Do not release raw or third-party-derived material publicly.",
        "can_close_locally": "no",
    },
    "Final reference numbering": {
        "owner": "author",
        "proof_type": "manual_reference_lock",
        "minimum_evidence": "Final prose, final figure/table references, verified bibliographic records and numbered reference list.",
        "local_next_step": "Keep candidate [P#] markers until prose and figure/table numbering stop changing.",
        "blocked_claim": "Do not treat candidate citation markers as final references.",
        "can_close_locally": "after_prose_lock",
    },
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dashboard_rows = read_csv(DASHBOARD)
    gate_rows = read_csv(OPEN_GATES)
    dependency_rows = read_csv(DEPENDENCIES)

    closure_rows: list[dict[str, str]] = []
    for gate in gate_rows:
        details = CLOSURE_DETAILS[gate["gate"]]
        closure_rows.append(
            {
                "priority": gate["priority"],
                "gate": gate["gate"],
                "current_status": gate["status"],
                "owner": details["owner"],
                "proof_type": details["proof_type"],
                "minimum_evidence_to_close": details["minimum_evidence"],
                "current_best_action": gate["current_best_action"],
                "local_next_step": details["local_next_step"],
                "blocked_claim_until_closed": details["blocked_claim"],
                "can_close_locally": details["can_close_locally"],
            }
        )

    write_csv(
        OUT_DIR / "submission_gap_closure_matrix.csv",
        closure_rows,
        [
            "priority",
            "gate",
            "current_status",
            "owner",
            "proof_type",
            "minimum_evidence_to_close",
            "current_best_action",
            "local_next_step",
            "blocked_claim_until_closed",
            "can_close_locally",
        ],
    )

    evidence_rows = [
        {
            "evidence_id": f"E{i + 1:02d}",
            "gate": row["gate"],
            "required_artifact": row["minimum_evidence_to_close"],
            "acceptable_current_substitute": "none" if row["can_close_locally"] == "no" else "planning/specification artifacts only",
            "why_current_evidence_is_not_enough": row["blocked_claim_until_closed"],
        }
        for i, row in enumerate(closure_rows)
    ]
    write_csv(
        OUT_DIR / "minimum_evidence_requirements.csv",
        evidence_rows,
        ["evidence_id", "gate", "required_artifact", "acceptable_current_substitute", "why_current_evidence_is_not_enough"],
    )

    dependency_lookup = {row["blocked_output"]: row for row in dependency_rows}
    execution_rows = [
        {
            "order": "1",
            "workstream": "Decision collection",
            "start_condition": "Author opens action packet",
            "stop_condition": "D001-D006 decisions recorded",
            "main_output": "Resolved author_decision_form_cn.csv",
        },
        {
            "order": "2",
            "workstream": "Figure rendering",
            "start_condition": "D001 backend confirmed",
            "stop_condition": "Fig. 1-Fig. 6 rendered and QAed",
            "main_output": dependency_lookup.get("Rendered main figures", {}).get("blocked_output", "Rendered main figures"),
        },
        {
            "order": "3",
            "workstream": "External validation",
            "start_condition": "Named real blind asset holder confirms feasibility",
            "stop_condition": "One-shot locked evaluation complete",
            "main_output": dependency_lookup.get("Blind external validation result", {}).get("blocked_output", "Blind external validation result"),
        },
        {
            "order": "4",
            "workstream": "Repository and rights",
            "start_condition": "Licences and repository route confirmed",
            "stop_condition": "DOI/accession and exclusion list verified",
            "main_output": "Public code/data identifiers or explicit restricted-access wording",
        },
        {
            "order": "5",
            "workstream": "Final manuscript lock",
            "start_condition": "Figures, tables, repositories and validation status frozen",
            "stop_condition": "Final Reporting Summary and numbered references locked",
            "main_output": "Submission-ready manuscript package",
        },
    ]
    write_csv(
        OUT_DIR / "next_execution_order.csv",
        execution_rows,
        ["order", "workstream", "start_condition", "stop_condition", "main_output"],
    )

    no_go_lines = [
        "# Submission no-go statement 2026-08-10",
        "",
        "Current status: **not submission-ready**.",
        "",
        "The package is not ready for Nature Communications/CNS-family submission because these gates remain open:",
        "",
    ]
    for row in closure_rows:
        no_go_lines.append(f"{row['priority']}. {row['gate']}: {row['current_status']}. Required evidence: {row['minimum_evidence_to_close']}")
    no_go_lines.extend(
        [
            "",
            "Allowed current framing:",
            "",
            "1. Res-SAM environment-transfer fragility is the strongest current evidence.",
            "2. Mojahid provides directional secondary support.",
            "3. 4TU provides stress-test/failure-mode context.",
            "4. TIGPR remains a NO-GO local core asset.",
            "5. External blind validation remains a NO-GO until a real held-label asset is acquired and evaluated.",
            "",
            "Forbidden final claims:",
            "",
        ]
    )
    for row in closure_rows:
        no_go_lines.append(f"- {row['blocked_claim_until_closed']}")
    no_go_lines.append("")
    (OUT_DIR / "submission_no_go_statement.md").write_text("\n".join(no_go_lines), encoding="utf-8")

    md_lines = [
        "# Submission gap-closure matrix 2026-08-10",
        "",
        "| Priority | Gate | Status | Minimum evidence to close | Can close locally |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in closure_rows:
        md_lines.append(
            f"| {row['priority']} | {row['gate']} | {row['current_status']} | {row['minimum_evidence_to_close']} | {row['can_close_locally']} |"
        )
    md_lines.extend(
        [
            "",
            "## Next execution order",
            "",
            "| Order | Workstream | Start condition | Stop condition |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in execution_rows:
        md_lines.append(f"| {row['order']} | {row['workstream']} | {row['start_condition']} | {row['stop_condition']} |")
    md_lines.extend(
        [
            "",
            "Boundary: this matrix is a control artifact. It does not close any scientific gate by itself.",
            "",
        ]
    )
    (OUT_DIR / "submission_gap_closure_matrix.md").write_text("\n".join(md_lines), encoding="utf-8")

    summary = {
        "run_id": "20260810_submission_gap_closure_matrix",
        "dashboard_areas": len(dashboard_rows),
        "open_gates": len(gate_rows),
        "closure_rows": len(closure_rows),
        "minimum_evidence_rows": len(evidence_rows),
        "execution_steps": len(execution_rows),
        "externally_blocked_gates": sum(1 for row in closure_rows if row["can_close_locally"] == "no"),
        "submission_ready": False,
        "status": "gap_closure_matrix_ready_submission_not_ready",
        "boundary": "Gap matrix defines closure evidence and forbidden claims; it does not create external validation, rendered figures, DOI, rights clearance or final Reporting Summary.",
    }
    (OUT_DIR / "submission_gap_closure_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Submission gap-closure report 2026-08-10",
        "",
        f"- Dashboard areas imported: {summary['dashboard_areas']}",
        f"- Open gates imported: {summary['open_gates']}",
        f"- Closure rows generated: {summary['closure_rows']}",
        f"- Minimum evidence rows generated: {summary['minimum_evidence_rows']}",
        f"- Execution steps generated: {summary['execution_steps']}",
        f"- Externally blocked gates: {summary['externally_blocked_gates']}",
        f"- Submission ready: {summary['submission_ready']}",
        "",
        "Immediate next requirement: record author decisions and obtain real external inputs before claiming final readiness.",
        "",
    ]
    (OUT_DIR / "submission_gap_closure_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
