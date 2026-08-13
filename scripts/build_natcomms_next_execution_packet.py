#!/usr/bin/env python3
"""Build the next execution packet from the Nat Comms command dashboard v3."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_next_execution_packet_20260810"

DASHBOARD = BENCH_ROOT / "reports" / "natcomms_finalization_command_dashboard_v3_20260810" / "finalization_command_dashboard_v3.csv"
CRITICAL_PATH = BENCH_ROOT / "reports" / "natcomms_finalization_command_dashboard_v3_20260810" / "critical_path_command_queue.csv"
NO_GO = BENCH_ROOT / "reports" / "natcomms_finalization_command_dashboard_v3_20260810" / "finalization_no_go_register_v3.csv"
AUTHOR_FORM = BENCH_ROOT / "reports" / "natcomms_author_finalization_reply_packet_20260810" / "author_finalization_reply_form_cn.csv"


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

    dashboard_rows = read_csv(DASHBOARD)
    critical_rows = read_csv(CRITICAL_PATH)
    no_go_rows = read_csv(NO_GO)
    author_rows = read_csv(AUTHOR_FORM)

    execution_rows = [
        {
            "task_id": "NEXT-001",
            "priority": "1",
            "owner": "corresponding_author",
            "task": "Fill author/admin identity, order, affiliation, contribution, competing-interest, funding, acknowledgement, ethics and reviewer/policy replies.",
            "input_artifacts": "reports/natcomms_author_finalization_reply_packet_20260810/author_finalization_reply_form_cn.csv; reports/natcomms_author_finalization_reply_packet_20260810/corresponding_author_metadata_form.csv; reports/natcomms_author_finalization_reply_packet_20260810/reviewer_and_policy_reply_sheet.csv",
            "completion_evidence": "All required author_reply cells for AFR-001, AFR-002, AFR-003, AFR-004, AFR-005, AFR-006 and AFR-010 are filled and manually reviewed.",
            "validation_command": "py GPR-ProvenanceBench\\scripts\\build_natcomms_author_reply_ingestion_validator.py",
            "current_status": "blocked_blank_replies",
        },
        {
            "task_id": "NEXT-002",
            "priority": "2",
            "owner": "author_advisor",
            "task": "Confirm Track B route or provide a real held-label external blind GPR asset path for Track A.",
            "input_artifacts": "reports/natcomms_author_finalization_reply_packet_20260810/track_branch_and_external_validation_reply.csv",
            "completion_evidence": "AFR-007 is filled; Track A only if strict blind intake and locked evaluation evidence exist.",
            "validation_command": "py GPR-ProvenanceBench\\scripts\\build_natcomms_author_reply_ingestion_validator.py",
            "current_status": "blocked_blank_branch_reply",
        },
        {
            "task_id": "NEXT-003",
            "priority": "3",
            "owner": "author_analysis",
            "task": "Select one formal figure backend, then start the journal figure workflow only after the selected backend is explicit.",
            "input_artifacts": "reports/natcomms_author_finalization_reply_packet_20260810/figure_backend_decision_ticket.csv; reports/figure_rendering_preflight_20260810/figure_rendering_kickoff_queue.csv",
            "completion_evidence": "Backend field is explicitly filled as Python or R; rendered figure exports and visual QA are still a later step.",
            "validation_command": "py GPR-ProvenanceBench\\scripts\\build_natcomms_author_reply_ingestion_validator.py",
            "current_status": "blocked_backend_undecided",
        },
        {
            "task_id": "NEXT-004",
            "priority": "4",
            "owner": "author_institution_repository_lead",
            "task": "Confirm licence, rights and repository release route for code, derived source data and any restricted third-party materials.",
            "input_artifacts": "reports/natcomms_author_finalization_reply_packet_20260810/licence_rights_reply_sheet.csv; reports/repository_release_manifest_lock_20260810/rights_and_licence_release_blockers.csv",
            "completion_evidence": "AFR-009 and licence/rights reply rows are filled; DOI creation remains separate and cannot be inferred.",
            "validation_command": "py GPR-ProvenanceBench\\scripts\\build_natcomms_gate_closure_evidence_binder.py",
            "current_status": "blocked_licence_rights_replies_missing",
        },
        {
            "task_id": "NEXT-005",
            "priority": "5",
            "owner": "analysis_reference_lead",
            "task": "Prepare post-author-choice work order for Reporting Summary and final references, without locking them before figures and final prose.",
            "input_artifacts": "reports/reporting_summary_finalization_prelock_20260810/reporting_summary_final_lock_matrix.csv; reports/sentence_citation_support_lock_20260810/citation_marker_replacement_plan.csv",
            "completion_evidence": "Ready-to-run checklist exists, but final Reporting Summary and final numbered references remain locked only after upstream evidence.",
            "validation_command": "py GPR-ProvenanceBench\\scripts\\build_natcomms_gate_closure_evidence_binder.py",
            "current_status": "waiting_for_figures_availability_final_prose",
        },
        {
            "task_id": "NEXT-006",
            "priority": "6",
            "owner": "writing_lead_corresponding_author",
            "task": "Hold final manuscript/SI and portal upload until every upstream finalization gate has evidence and manual review.",
            "input_artifacts": "reports/natcomms_initial_submission_text_preassembly_20260810/natcomms_initial_submission_text_preassembly.md; reports/natcomms_supplementary_info_preassembly_20260810/supplementary_information_preassembly.md; reports/natcomms_portal_upload_manifest_prelock_20260810/portal_upload_item_manifest.csv",
            "completion_evidence": "No final assembly is allowed at this checkpoint; use this row as a stop condition.",
            "validation_command": "py GPR-ProvenanceBench\\scripts\\build_natcomms_finalization_command_dashboard_v3.py",
            "current_status": "blocked_all_prior_gates_open",
        },
    ]
    write_csv(
        OUT_DIR / "next_execution_task_queue.csv",
        execution_rows,
        ["task_id", "priority", "owner", "task", "input_artifacts", "completion_evidence", "validation_command", "current_status"],
    )

    owner_packet_rows = [
        {"owner": "corresponding_author", "packet_items": "author_finalization_reply_form_cn.csv; corresponding_author_metadata_form.csv; reviewer_and_policy_reply_sheet.csv", "reply_due_event": "before any final declarations or portal metadata lock", "status": "not_sent_or_not_collected"},
        {"owner": "author_advisor", "packet_items": "track_branch_and_external_validation_reply.csv", "reply_due_event": "before title/abstract/cover-letter final route lock", "status": "not_collected"},
        {"owner": "author_analysis", "packet_items": "figure_backend_decision_ticket.csv", "reply_due_event": "before formal figure rendering", "status": "not_collected"},
        {"owner": "repository_lead", "packet_items": "licence_rights_reply_sheet.csv; rights_and_licence_release_blockers.csv", "reply_due_event": "before DOI, Data Availability or Code Availability lock", "status": "not_collected"},
        {"owner": "analysis_reference_lead", "packet_items": "reporting_summary_author_reply_sheet.csv; citation_marker_replacement_plan.csv", "reply_due_event": "after figures/source-data/final prose lock", "status": "waiting"},
    ]
    write_csv(OUT_DIR / "owner_packet_distribution_matrix.csv", owner_packet_rows, ["owner", "packet_items", "reply_due_event", "status"])

    acceptance_rows = [
        {"acceptance_id": "ACC-NEXT-001", "test": "Author reply validator reruns after replies are filled.", "must_pass_before": "FM-001/FM-002/FM-003/FM-004/FM-005/FM-008 closure review", "current_result": "not_applicable_blank_replies"},
        {"acceptance_id": "ACC-NEXT-002", "test": "Gate evidence binder reruns and still requires concrete artifacts after replies.", "must_pass_before": "any gate closure", "current_result": "passes_keep_open"},
        {"acceptance_id": "ACC-NEXT-003", "test": "Figure rendering starts only after backend is explicit.", "must_pass_before": "FM-003 closure review", "current_result": "blocked_backend_undecided"},
        {"acceptance_id": "ACC-NEXT-004", "test": "Repository DOI/code DOI are externally verified before availability lock.", "must_pass_before": "FM-004/FM-005/FM-008 closure review", "current_result": "blocked_no_doi"},
        {"acceptance_id": "ACC-NEXT-005", "test": "Final manuscript/SI assembly starts only after upstream gates are reviewed.", "must_pass_before": "FM-007/FM-008 closure review", "current_result": "blocked_all_prior_gates_open"},
    ]
    write_csv(OUT_DIR / "next_execution_acceptance_tests.csv", acceptance_rows, ["acceptance_id", "test", "must_pass_before", "current_result"])

    handoff = [
        "# Nat Comms next execution handoff",
        "",
        "Current state: all finalization commands remain blocked. This package turns the command dashboard into assignable work items only.",
        "",
        "## First work item",
        "",
        "Send or manually fill the author/corresponding-author reply tables. Do not proceed to final figure rendering or final manuscript assembly until the reply validator has been rerun on filled replies.",
        "",
        "## Required reruns after author replies",
        "",
        "1. `py GPR-ProvenanceBench\\scripts\\build_natcomms_author_reply_ingestion_validator.py`",
        "2. `py GPR-ProvenanceBench\\scripts\\build_natcomms_gate_closure_evidence_binder.py`",
        "3. `py GPR-ProvenanceBench\\scripts\\build_natcomms_finalization_command_dashboard_v3.py`",
        "4. `py GPR-ProvenanceBench\\scripts\\run_m0_m2_checks.ps1`",
        "",
        "Boundary: this handoff does not collect author replies, choose Python/R, render figures, create DOI records, finalize references, generate final files or submit the manuscript.",
        "",
    ]
    (OUT_DIR / "next_execution_handoff.md").write_text("\n".join(handoff), encoding="utf-8")

    stop_rows = [
        {"stop_id": "STOP-NEXT-001", "rule": "Stop if any required author reply is blank.", "current_status": "active"},
        {"stop_id": "STOP-NEXT-002", "rule": "Stop before figure rendering unless backend is explicitly chosen.", "current_status": "active"},
        {"stop_id": "STOP-NEXT-003", "rule": "Stop before availability finalization unless DOI/rights evidence exists.", "current_status": "active"},
        {"stop_id": "STOP-NEXT-004", "rule": "Stop before final references unless final prose and display-item order are locked.", "current_status": "active"},
        {"stop_id": "STOP-NEXT-005", "rule": "Stop before portal upload unless every portal item is upload-ready.", "current_status": "active"},
    ]
    write_csv(OUT_DIR / "next_execution_stop_rules.csv", stop_rows, ["stop_id", "rule", "current_status"])

    blank_author_reply_count = sum(1 for row in author_rows if row.get("author_reply", "").strip() == "")
    blocked_dashboard_count = sum(1 for row in dashboard_rows if row.get("command_status") == "blocked_keep_open")
    active_no_go_count = sum(1 for row in no_go_rows if row.get("current_status") == "active")
    qa_rows = [
        {"check": "Execution tasks exist", "result": "PASS" if len(execution_rows) == 6 else "FAIL", "detail": f"{len(execution_rows)} tasks."},
        {"check": "Dashboard remains blocked", "result": "PASS" if blocked_dashboard_count == 8 else "FAIL", "detail": f"{blocked_dashboard_count} blocked dashboard rows."},
        {"check": "Author replies still blank", "result": "PASS" if blank_author_reply_count == 12 else "FAIL", "detail": f"{blank_author_reply_count} blank reply fields."},
        {"check": "Active no-go rows imported", "result": "PASS" if active_no_go_count == 5 else "FAIL", "detail": f"{active_no_go_count} active no-go rows."},
        {"check": "Stop rules active", "result": "PASS" if len(stop_rows) == 5 else "FAIL", "detail": f"{len(stop_rows)} stop rules."},
    ]
    write_csv(OUT_DIR / "next_execution_packet_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = [
        "# Nat Comms next execution packet",
        "",
        "Purpose: convert the blocked finalization command dashboard into assignable next actions, owner packets, acceptance tests and stop rules.",
        "",
        "Boundary: this is an execution handoff only. It does not complete author replies, select a backend, render figures, create DOI records or make the submission ready.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_NEXT_EXECUTION_PACKET_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Next execution packet report",
        "",
        f"- Execution tasks: {len(execution_rows)}",
        f"- Owner packet rows: {len(owner_packet_rows)}",
        f"- Acceptance tests: {len(acceptance_rows)}",
        f"- Stop rules: {len(stop_rows)}",
        f"- Blank author reply fields: {blank_author_reply_count}",
        f"- Blocked dashboard rows: {blocked_dashboard_count}",
        f"- Critical path rows imported: {len(critical_rows)}",
        f"- Active no-go rows: {active_no_go_count}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_next_execution_packet_ready_waiting_author_inputs",
        "",
    ]
    (OUT_DIR / "next_execution_packet_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_next_execution_packet",
        "execution_tasks": len(execution_rows),
        "owner_packet_rows": len(owner_packet_rows),
        "acceptance_tests": len(acceptance_rows),
        "stop_rules": len(stop_rows),
        "blank_author_reply_fields": blank_author_reply_count,
        "blocked_dashboard_rows": blocked_dashboard_count,
        "critical_path_rows_imported": len(critical_rows),
        "active_no_go_rows": active_no_go_count,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "author_inputs_collected": False,
        "backend_selected": False,
        "submission_ready": False,
        "status": "natcomms_next_execution_packet_ready_waiting_author_inputs",
        "boundary": "Execution packet defines next actions only; it does not execute author replies, figure rendering, DOI creation, final assembly or submission.",
    }
    (OUT_DIR / "next_execution_packet_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
