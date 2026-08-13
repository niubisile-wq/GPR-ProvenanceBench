#!/usr/bin/env python3
"""Build a closure packet for the remaining final blockers.

The packet converts the residual blockers into evidence requirements,
validation commands, dependencies and stop rules. It does not write evidence or
close any gate.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_residual_blocker_closure_packet_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_PACKET = Path.home() / "Desktop" / "NatComms_final_residual_blocker_closure_packet_20260810.md"

SUMMARY_PATHS = {
    "residual_audit": BENCH_ROOT / "reports" / "final_completion_residual_blocker_audit_20260810" / "final_completion_residual_blocker_audit_summary.json",
    "manual_intake": BENCH_ROOT / "reports" / "manual_evidence_final_intake_validator_20260810" / "manual_evidence_final_intake_validator_summary.json",
    "scanner": BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json",
    "writeback": BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json",
    "transition": BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_gate_transition_validator_summary.json",
    "guarded_runner": BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "post_return_guarded_execution_runner_summary.json",
    "submission": BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810" / "natcomms_submission_final_lock_validator_summary.json",
}

RESIDUAL_BLOCKERS_CSV = BENCH_ROOT / "reports" / "final_completion_residual_blocker_audit_20260810" / "final_completion_residual_blockers.csv"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.23 Final residual blocker closure packet update"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n"
        else:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n\n" + text[next_start:].lstrip("\n")
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = {name: read_json(path) for name, path in SUMMARY_PATHS.items()}
    residual_rows = read_csv(RESIDUAL_BLOCKERS_CSV)

    closure_rows = [
        {
            "blocker_id": "RB-001",
            "closure_item": "Collect real returned evidence",
            "owner": "author_or_data_holder",
            "required_input": "Returned files in canonical inbox folders with source identity and SHA256 provenance.",
            "target_artifact": "final_return_evidence_inbox_20260810/",
            "acceptance_test": "candidate_return_files > 0 and route scan has no invalid file rows.",
            "first_validation_command": "py scripts/build_final_return_evidence_intake_scanner.py",
            "unlocks": "RB-002",
            "ready_to_close_now": "no",
            "current_blocker": f"candidate_return_files={summaries['scanner'].get('candidate_return_files')}",
        },
        {
            "blocker_id": "RB-002",
            "closure_item": "Perform protected evidence writeback",
            "owner": "operator_after_manual_inspection",
            "required_input": "Accepted returned evidence plus route-specific safe-edit target approval.",
            "target_artifact": "manual evidence target files listed by final_return_writeback_route_matrix.csv",
            "acceptance_test": "writeback_allowed_rows > 0 after scanner acceptance; evidence_writeback_performed recorded only after manual writeback.",
            "first_validation_command": "py scripts/build_final_return_evidence_writeback_preflight.py",
            "unlocks": "RB-003; RB-004; RB-005; RB-006; RB-007",
            "ready_to_close_now": "no",
            "current_blocker": f"writeback_allowed_rows={summaries['writeback'].get('writeback_allowed_rows')}",
        },
        {
            "blocker_id": "RB-003",
            "closure_item": "Fill and validate author replies",
            "owner": "corresponding_author",
            "required_input": "All required author response fields filled with allowed values and evidence links.",
            "target_artifact": "author decision and final manual evidence target files",
            "acceptance_test": "blank_author_reply_fields = 0 and evidence_rows_passed equals required evidence rows.",
            "first_validation_command": "py scripts/build_manual_evidence_final_intake_validator.py",
            "unlocks": "RB-006; RB-008",
            "ready_to_close_now": "no",
            "current_blocker": f"blank_author_reply_fields={summaries['manual_intake'].get('blank_author_reply_fields')}",
        },
        {
            "blocker_id": "RB-004",
            "closure_item": "Ingest final figure approvals",
            "owner": "author_team",
            "required_input": "Figure 1-Figure 6 accept/revise/drop decisions and final source-file approvals.",
            "target_artifact": "reports/python_figure_author_review_intake_validator_20260810/",
            "acceptance_test": "approved_rows covers all required final figure rows and final_figures_ready=true.",
            "first_validation_command": "py scripts/build_python_figure_author_review_intake_validator.py",
            "unlocks": "RB-006; RB-008",
            "ready_to_close_now": "no",
            "current_blocker": "final_figures_ready=false",
        },
        {
            "blocker_id": "RB-005",
            "closure_item": "Finalize repository DOI, licence and third-party rights",
            "owner": "corresponding_author_or_repo_owner",
            "required_input": "Repository DOI, code/data licence, third-party rights and restricted-data wording.",
            "target_artifact": "reports/availability_repository_finalization_validator_20260810/",
            "acceptance_test": "final_availability_ready=true with DOI/licence/rights all accepted.",
            "first_validation_command": "py scripts/build_availability_repository_finalization_validator.py",
            "unlocks": "RB-006; RB-008",
            "ready_to_close_now": "no",
            "current_blocker": "final_availability_ready=false",
        },
        {
            "blocker_id": "RB-006",
            "closure_item": "Lock the final Reporting Summary",
            "owner": "corresponding_author",
            "required_input": "Completed Reporting Summary dependencies, figure status, data/code availability and methodological declarations.",
            "target_artifact": "reports/reporting_summary_final_lock_validator_20260810/",
            "acceptance_test": "final_reporting_summary_ready=true and no dependency row is open.",
            "first_validation_command": "py scripts/build_reporting_summary_final_lock_validator.py",
            "unlocks": "RB-008",
            "ready_to_close_now": "no",
            "current_blocker": "final_reporting_summary_ready=false",
        },
        {
            "blocker_id": "RB-007",
            "closure_item": "Verify and lock final references",
            "owner": "manuscript_operator",
            "required_input": "Manual reference verification, placeholder replacement authorization and final citation export.",
            "target_artifact": "reports/reference_final_lock_validator_20260810/",
            "acceptance_test": "final_references_ready=true and no placeholder/candidate reference markers remain.",
            "first_validation_command": "py scripts/build_reference_final_lock_validator.py",
            "unlocks": "RB-008",
            "ready_to_close_now": "no",
            "current_blocker": "final_references_ready=false",
        },
        {
            "blocker_id": "RB-008",
            "closure_item": "Run final submission gate and portal upload readiness",
            "owner": "submitting_author",
            "required_input": "All master gates closed, final manuscript files locked and portal metadata completed.",
            "target_artifact": "reports/natcomms_submission_final_lock_validator_20260810/",
            "acceptance_test": "open_master_gates = 0, portal_upload_ready_rows > 0 and submission_ready=true.",
            "first_validation_command": "py scripts/build_natcomms_submission_final_lock_validator.py",
            "unlocks": "portal_upload",
            "ready_to_close_now": "no",
            "current_blocker": f"open_master_gates={summaries['submission'].get('open_master_gates')}; submission_ready={summaries['submission'].get('submission_ready')}",
        },
    ]

    dependency_rows = [
        {"order": 1, "blocker_id": "RB-001", "dependency": "none", "can_start_without_external_return": "yes_manual_collection_only", "stop_rule": "Do not write evidence into protected targets before scanner acceptance."},
        {"order": 2, "blocker_id": "RB-002", "dependency": "RB-001 accepted", "can_start_without_external_return": "no", "stop_rule": "Do not write back when writeback_allowed_rows=0."},
        {"order": 3, "blocker_id": "RB-003", "dependency": "RB-002 writeback evidence", "can_start_without_external_return": "no", "stop_rule": "Do not rerun author-dependent branches while blank_author_reply_fields>0."},
        {"order": 4, "blocker_id": "RB-004", "dependency": "RB-002 writeback evidence", "can_start_without_external_return": "no", "stop_rule": "Do not call figures final while author approvals are absent."},
        {"order": 5, "blocker_id": "RB-005", "dependency": "RB-002 writeback evidence", "can_start_without_external_return": "no", "stop_rule": "Do not claim DOI/rights/licence readiness before accepted repository evidence."},
        {"order": 6, "blocker_id": "RB-007", "dependency": "RB-002 writeback evidence", "can_start_without_external_return": "no", "stop_rule": "Do not remove reference placeholders without manual verification."},
        {"order": 7, "blocker_id": "RB-006", "dependency": "RB-003/RB-004/RB-005", "can_start_without_external_return": "no", "stop_rule": "Do not lock Reporting Summary while any dependency remains open."},
        {"order": 8, "blocker_id": "RB-008", "dependency": "RB-003/RB-004/RB-005/RB-006/RB-007 all closed", "can_start_without_external_return": "no", "stop_rule": "Do not upload or submit while open_master_gates>0."},
    ]

    command_rows = [
        {
            "sequence": row["order"],
            "blocker_id": row["blocker_id"],
            "command": next(item["first_validation_command"] for item in closure_rows if item["blocker_id"] == row["blocker_id"]),
            "allowed_now": "diagnostic_only" if row["blocker_id"] == "RB-001" else "no",
            "reason": row["stop_rule"],
        }
        for row in dependency_rows
    ]

    qa_rows = [
        {"check": "all_residual_blockers_mapped", "result": "PASS" if len(closure_rows) == summaries["residual_audit"].get("residual_blockers") == 8 else "FAIL", "detail": f"closure_rows={len(closure_rows)}; residual_blockers={summaries['residual_audit'].get('residual_blockers')}"},
        {"check": "all_rows_have_validation_commands", "result": "PASS" if all(row["first_validation_command"] for row in closure_rows) else "FAIL", "detail": "one command per blocker"},
        {"check": "no_false_closure", "result": "PASS" if all(row["ready_to_close_now"] == "no" for row in closure_rows) else "FAIL", "detail": "ready_to_close_now remains no for every blocker"},
        {"check": "manual_evidence_absence_preserved", "result": "PASS" if summaries["scanner"].get("candidate_return_files") == 0 and summaries["writeback"].get("writeback_allowed_rows") == 0 else "FAIL", "detail": f"candidate_return_files={summaries['scanner'].get('candidate_return_files')}; writeback_allowed_rows={summaries['writeback'].get('writeback_allowed_rows')}"},
        {"check": "submission_guard_preserved", "result": "PASS" if summaries["submission"].get("submission_ready") is False and summaries["transition"].get("open_master_gates") == 8 else "FAIL", "detail": f"submission_ready={summaries['submission'].get('submission_ready')}; open_master_gates={summaries['transition'].get('open_master_gates')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "final_residual_blocker_closure_packet.csv",
        closure_rows,
        ["blocker_id", "closure_item", "owner", "required_input", "target_artifact", "acceptance_test", "first_validation_command", "unlocks", "ready_to_close_now", "current_blocker"],
    )
    write_csv(
        OUT_DIR / "final_residual_blocker_dependency_order.csv",
        dependency_rows,
        ["order", "blocker_id", "dependency", "can_start_without_external_return", "stop_rule"],
    )
    write_csv(
        OUT_DIR / "final_residual_blocker_validation_commands.csv",
        command_rows,
        ["sequence", "blocker_id", "command", "allowed_now", "reason"],
    )
    write_csv(OUT_DIR / "final_residual_blocker_closure_packet_qa.csv", qa_rows, ["check", "result", "detail"])

    report_lines = [
        "# Final residual blocker closure packet 2026-08-10",
        "",
        "Status: `final_residual_blocker_closure_packet_ready_waiting_for_external_evidence`",
        "",
        "This packet converts the eight residual blockers into closure items. It does not provide the missing evidence, write protected targets, close gates, upload files or submit the manuscript.",
        "",
        "## Closure Order",
        "",
    ]
    for row in dependency_rows:
        item = next(item for item in closure_rows if item["blocker_id"] == row["blocker_id"])
        report_lines.append(f"{row['order']}. `{row['blocker_id']}` {item['closure_item']}: {item['acceptance_test']}")
    report_lines.extend(
        [
            "",
            "## Current Hard Stops",
            "",
            f"1. candidate_return_files={summaries['scanner'].get('candidate_return_files')}",
            f"2. writeback_allowed_rows={summaries['writeback'].get('writeback_allowed_rows')}",
            f"3. blank_author_reply_fields={summaries['manual_intake'].get('blank_author_reply_fields')}",
            f"4. commands_allowed_now={summaries['guarded_runner'].get('commands_allowed_now')}",
            f"5. open_master_gates={summaries['transition'].get('open_master_gates')}",
            f"6. submission_ready={summaries['submission'].get('submission_ready')}",
            "",
            "Boundary: only RB-001 manual collection can start without returned evidence. All downstream closure rows remain blocked until accepted evidence exists.",
            "",
        ]
    )
    report = "\n".join(report_lines)
    write_text(OUT_DIR / "FINAL_RESIDUAL_BLOCKER_CLOSURE_PACKET_README.md", report)
    write_text(OUT_DIR / "final_residual_blocker_closure_packet_report.md", report)
    shutil.copy2(OUT_DIR / "final_residual_blocker_closure_packet_report.md", DESKTOP_PACKET)

    summary = {
        "package": "final_residual_blocker_closure_packet_20260810",
        "closure_rows": len(closure_rows),
        "dependency_rows": len(dependency_rows),
        "validation_command_rows": len(command_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "ready_to_close_rows": sum(1 for row in closure_rows if row["ready_to_close_now"] == "yes"),
        "diagnostic_commands_allowed_now": sum(1 for row in command_rows if row["allowed_now"] == "diagnostic_only"),
        "blocked_validation_commands": sum(1 for row in command_rows if row["allowed_now"] == "no"),
        "candidate_return_files": summaries["scanner"].get("candidate_return_files"),
        "writeback_allowed_rows": summaries["writeback"].get("writeback_allowed_rows"),
        "blank_author_reply_fields": summaries["manual_intake"].get("blank_author_reply_fields"),
        "commands_allowed_now": summaries["guarded_runner"].get("commands_allowed_now"),
        "open_master_gates": summaries["transition"].get("open_master_gates"),
        "submission_ready": False,
        "desktop_packet": str(DESKTOP_PACKET),
        "status": "final_residual_blocker_closure_packet_ready_waiting_for_external_evidence",
    }

    section = f"""### 19.23 Final residual blocker closure packet update

Added a closure packet that converts the eight residual blockers into exact evidence requirements, target artifacts, acceptance tests, validation commands, dependencies and stop rules.

New directory: `{OUT_DIR}`

Desktop packet: `{DESKTOP_PACKET}`

Current result:
1. closure_rows = {summary['closure_rows']}
2. dependency_rows = {summary['dependency_rows']}
3. validation_command_rows = {summary['validation_command_rows']}
4. ready_to_close_rows = {summary['ready_to_close_rows']}
5. diagnostic_commands_allowed_now = {summary['diagnostic_commands_allowed_now']}
6. blocked_validation_commands = {summary['blocked_validation_commands']}
7. candidate_return_files = {summary['candidate_return_files']}
8. writeback_allowed_rows = {summary['writeback_allowed_rows']}
9. blank_author_reply_fields = {summary['blank_author_reply_fields']}
10. open_master_gates = {summary['open_master_gates']}
11. submission_ready = false

Boundary:
1. This packet is a closure map, not closure evidence.
2. Only RB-001 manual evidence collection can start without returned evidence.
3. No downstream validation command is allowed to close a gate while candidate_return_files=0 and writeback_allowed_rows=0."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_residual_blocker_closure_packet_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("Final residual blocker closure packet QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
