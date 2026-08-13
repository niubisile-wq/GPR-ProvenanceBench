#!/usr/bin/env python3
"""Build a consolidated command dashboard for current submission gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "submission_command_dashboard_v2_20260810"

SUMMARY_PATHS = {
    "gap_matrix": BENCH_ROOT / "reports" / "submission_gap_closure_matrix_20260810" / "submission_gap_closure_summary.json",
    "author_review_manuscript": BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_summary.json",
    "broad_interest": BENCH_ROOT / "reports" / "broad_interest_framing_revision_20260810" / "broad_interest_framing_revision_summary.json",
    "external_contingency": BENCH_ROOT / "reports" / "external_validation_contingency_framing_20260810" / "external_validation_contingency_framing_summary.json",
    "availability": BENCH_ROOT / "reports" / "availability_statement_prelock_20260810" / "availability_statement_prelock_summary.json",
    "reporting_summary": BENCH_ROOT / "reports" / "reporting_summary_finalization_prelock_20260810" / "reporting_summary_finalization_prelock_summary.json",
    "references": BENCH_ROOT / "reports" / "reference_numbering_prelock_20260810" / "reference_numbering_prelock_summary.json",
}
ACCEPTANCE_TESTS = BENCH_ROOT / "reports" / "reviewer_risk_revision_action_packet_20260810" / "evidence_closure_acceptance_tests.csv"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    summaries = {key: read_json(path) for key, path in SUMMARY_PATHS.items()}
    acceptance_rows = read_csv(ACCEPTANCE_TESTS)

    gate_rows = [
        {
            "gate": "blind_external_validation",
            "current_state": "NO-GO",
            "current_owner": "author/advisor/data holder",
            "current_control_artifact": "external_validation_contingency_framing_20260810",
            "next_decision_or_action": "Use Track B unless a real held-label external asset passes strict intake and locked evaluation.",
            "minimum_evidence_to_close": "Strict-SHA manifest, label holdout, frozen prediction file, label unlock record and one locked metrics table.",
            "forbidden_until_closed": "Completed blind validation; external generalization; deployment robustness.",
            "can_close_locally": "no",
        },
        {
            "gate": "formal_figures",
            "current_state": "open_backend_choice_needed",
            "current_owner": "author/analyst",
            "current_control_artifact": "figure_rendering_spec_20260810",
            "next_decision_or_action": "Choose exactly one backend, Python or R, then render final figure set with visual QA.",
            "minimum_evidence_to_close": "Final exports, panel labels, source-data panel map and visual QA pass record.",
            "forbidden_until_closed": "Final figure claims; final figure legends; final source-data claims.",
            "can_close_locally": "after_backend_choice",
        },
        {
            "gate": "repository_rights_doi",
            "current_state": "open",
            "current_owner": "author/institution/repository lead",
            "current_control_artifact": "availability_statement_prelock_20260810",
            "next_decision_or_action": "Resolve licence, rights and repository route; then create data DOI/accession and code archive DOI.",
            "minimum_evidence_to_close": "Repository landing page, data DOI/accession, code DOI, licence and rights checklist.",
            "forbidden_until_closed": "Data deposited; code archived; public release ready.",
            "can_close_locally": "no",
        },
        {
            "gate": "reporting_summary",
            "current_state": "prelock_not_final",
            "current_owner": "author/analyst",
            "current_control_artifact": "reporting_summary_finalization_prelock_20260810",
            "next_decision_or_action": "Lock only after figures, external validation status, availability statements and methods are final.",
            "minimum_evidence_to_close": "Every Reporting Summary item has final answer and evidence trigger satisfied.",
            "forbidden_until_closed": "Final Reporting Summary ready.",
            "can_close_locally": "after_other_gates",
        },
        {
            "gate": "references",
            "current_state": "prelock_not_final",
            "current_owner": "author/reference lead",
            "current_control_artifact": "reference_numbering_prelock_20260810",
            "next_decision_or_action": "Verify DOI/publisher pages and claim support after final prose and figure calls lock.",
            "minimum_evidence_to_close": "No [P#] markers remain; numbered references support local claims; bibliography verified.",
            "forbidden_until_closed": "Final numbered references.",
            "can_close_locally": "after_prose_lock",
        },
        {
            "gate": "broad_interest_framing",
            "current_state": "draft_only",
            "current_owner": "writing lead",
            "current_control_artifact": "broad_interest_framing_revision_20260810",
            "next_decision_or_action": "Use benchmark-trust framing, then align title/abstract/Introduction with final branch and figure schematic.",
            "minimum_evidence_to_close": "Title, abstract, Introduction opening and schematic caption remain cross-field but bounded.",
            "forbidden_until_closed": "Overbroad field-wide robustness or universal leakage claims.",
            "can_close_locally": "partially",
        },
    ]
    write_csv(
        OUT_DIR / "submission_command_dashboard_v2.csv",
        gate_rows,
        [
            "gate",
            "current_state",
            "current_owner",
            "current_control_artifact",
            "next_decision_or_action",
            "minimum_evidence_to_close",
            "forbidden_until_closed",
            "can_close_locally",
        ],
    )

    branch_rows = [
        {
            "decision": "current_manuscript_branch",
            "selected_value": summaries["external_contingency"]["current_applicable_branch"],
            "meaning": "Track B: benchmark/resource plus evidence-boundary framing; external validation remains open.",
            "change_trigger": "Switch to Track A only after real blind external validation is completed.",
        },
        {
            "decision": "current_submission_state",
            "selected_value": "not_submission_ready",
            "meaning": "Author-review manuscript and prelock packages are usable for internal review only.",
            "change_trigger": "All hard gates close and final checks pass.",
        },
        {
            "decision": "current_figure_backend",
            "selected_value": "Python",
            "meaning": "Formal figure rendering follows the current Python-based evidence pipeline and source-data tooling.",
            "change_trigger": "Switch only if the author explicitly re-routes the full figure pipeline to R.",
        },
    ]
    write_csv(OUT_DIR / "current_branch_and_decision_register.csv", branch_rows, ["decision", "selected_value", "meaning", "change_trigger"])

    forbidden_rows = [
        {"category": "external_validation", "forbidden_claim": "Completed blind external validation", "safe_current_wording": "Blind external validation remains open/NO-GO."},
        {"category": "repository", "forbidden_claim": "Data/code are deposited under DOI", "safe_current_wording": "Availability wording and repository metadata are prelocked; DOI/accession remain missing."},
        {"category": "figures", "forbidden_claim": "Final figures and Source Data are ready", "safe_current_wording": "Figure specifications and source-data plans are ready; final rendered figures remain open."},
        {"category": "reporting_summary", "forbidden_claim": "Final Reporting Summary is ready", "safe_current_wording": "Reporting Summary finalization prelock is ready; final lock remains blocked."},
        {"category": "references", "forbidden_claim": "Final numbered references are complete", "safe_current_wording": "Reference numbering prelock is ready; candidate markers remain non-final."},
    ]
    write_csv(OUT_DIR / "global_forbidden_claims_dashboard.csv", forbidden_rows, ["category", "forbidden_claim", "safe_current_wording"])

    artifact_rows = [
        {"artifact": key, "status": value.get("status", ""), "submission_ready": str(value.get("submission_ready", False)), "boundary": value.get("boundary", "")}
        for key, value in summaries.items()
    ]
    write_csv(OUT_DIR / "prelock_artifact_status_register.csv", artifact_rows, ["artifact", "status", "submission_ready", "boundary"])

    markdown = [
        "# Submission command dashboard v2 2026-08-10",
        "",
        "Current decision: submission is not ready.",
        "",
        "Current manuscript branch: Track B. The paper should be positioned as a benchmark/resource and evidence-boundary manuscript unless real blind external validation is completed.",
        "",
        "## Hard gates",
        "",
    ]
    for row in gate_rows:
        markdown.extend(
            [
                f"### {row['gate']}",
                f"- State: {row['current_state']}",
                f"- Owner: {row['current_owner']}",
                f"- Next action: {row['next_decision_or_action']}",
                f"- Minimum evidence: {row['minimum_evidence_to_close']}",
                f"- Forbidden until closed: {row['forbidden_until_closed']}",
                "",
            ]
        )
    markdown.extend(
        [
            "## Current acceptance tests",
            "",
        ]
    )
    for row in acceptance_rows:
        markdown.append(f"- {row['gate']}: {row['current_state']} | {row['minimum_acceptance_test']}")
    markdown.append("")
    (OUT_DIR / "submission_command_dashboard_v2.md").write_text("\n".join(markdown), encoding="utf-8")

    qa_rows = [
        {"check": "all_source_summaries_loaded", "result": "PASS", "detail": str(len(summaries))},
        {"check": "submission_not_ready_preserved", "result": "PASS" if not any(v.get("submission_ready", False) for v in summaries.values()) else "FAIL", "detail": "All source summaries report not submission-ready or no ready flag."},
        {"check": "track_b_current", "result": "PASS" if summaries["external_contingency"]["current_applicable_branch"] == "TRACK-B" else "FAIL", "detail": summaries["external_contingency"]["current_applicable_branch"]},
        {"check": "hard_gates_recorded", "result": "PASS" if len(gate_rows) == 6 else "FAIL", "detail": str(len(gate_rows))},
        {"check": "acceptance_tests_imported", "result": "PASS" if len(acceptance_rows) >= 5 else "FAIL", "detail": str(len(acceptance_rows))},
    ]
    write_csv(OUT_DIR / "submission_command_dashboard_v2_qa.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "run_id": "20260810_submission_command_dashboard_v2",
        "hard_gates": len(gate_rows),
        "branch_decisions": len(branch_rows),
        "forbidden_claim_rows": len(forbidden_rows),
        "artifact_status_rows": len(artifact_rows),
        "acceptance_tests": len(acceptance_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "current_applicable_branch": summaries["external_contingency"]["current_applicable_branch"],
        "submission_ready": False,
        "status": "submission_command_dashboard_v2_ready_submission_not_ready",
        "boundary": "This dashboard consolidates current gates and decisions; it does not close external validation, figures, DOI, rights, Reporting Summary or references.",
    }
    (OUT_DIR / "submission_command_dashboard_v2_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Submission command dashboard v2 report 2026-08-10",
        "",
        f"- Hard gates: {summary['hard_gates']}",
        f"- Branch decisions: {summary['branch_decisions']}",
        f"- Forbidden claim rows: {summary['forbidden_claim_rows']}",
        f"- Artifact status rows: {summary['artifact_status_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Current branch: {summary['current_applicable_branch']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: the command dashboard is ready; submission remains not ready.",
        "",
    ]
    (OUT_DIR / "submission_command_dashboard_v2_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
