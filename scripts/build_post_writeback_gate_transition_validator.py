#!/usr/bin/env python3
"""Validate gate-transition readiness after protected evidence writeback."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

WRITEBACK_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json"
WRITEBACK_COMMANDS = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_writeback_validation_commands.csv"
GATE_BINDER_SUMMARY = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810" / "gate_closure_evidence_binder_summary.json"
GATE_BINDER = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810" / "gate_closure_evidence_binder.csv"
SUBMISSION_SUMMARY = BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810" / "natcomms_submission_final_lock_validator_summary.json"
COMMAND_DASHBOARD_SUMMARY = BENCH_ROOT / "reports" / "natcomms_finalization_command_dashboard_v3_20260810" / "finalization_command_dashboard_v3_summary.json"

ROUTE_TO_GATE = {
    "RTE-001": "FM-001",
    "RTE-002": "FM-001",
    "RTE-003": "FM-003",
    "RTE-004": "FM-004",
    "RTE-005": "FM-005",
    "RTE-006": "FM-006",
    "RTE-007": "FM-008",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.18 Post-writeback gate transition validator update"
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

    writeback_summary = read_json(WRITEBACK_SUMMARY)
    gate_summary = read_json(GATE_BINDER_SUMMARY)
    submission_summary = read_json(SUBMISSION_SUMMARY)
    dashboard_summary = read_json(COMMAND_DASHBOARD_SUMMARY)
    command_rows_in = read_csv(WRITEBACK_COMMANDS)
    gate_rows_in = {row["gate_id"]: row for row in read_csv(GATE_BINDER)}

    transition_rows: list[dict[str, object]] = []
    for row in command_rows_in:
        route_id = row["route_id"]
        gate_id = ROUTE_TO_GATE.get(route_id, "")
        gate_row = gate_rows_in.get(gate_id, {})
        command_allowed = row.get("currently_allowed") == "yes"
        gate_currently_closed = gate_row.get("master_closed_status") == "yes"
        transition_allowed = command_allowed and gate_currently_closed
        transition_rows.append(
            {
                "route_id": route_id,
                "worksheet_id": row.get("worksheet_id", ""),
                "command": row.get("command", ""),
                "mapped_gate_id": gate_id,
                "mapped_gate": gate_row.get("gate", ""),
                "command_currently_allowed": row.get("currently_allowed", "no"),
                "gate_master_closed_status": gate_row.get("master_closed_status", "no"),
                "open_artifact_requirements": gate_row.get("open_artifact_requirements", ""),
                "transition_allowed_now": "yes" if transition_allowed else "no",
                "reason": "Transition blocked until protected writeback is allowed and the mapped gate evidence binder reports closed.",
            }
        )

    gate_transition_rows: list[dict[str, object]] = []
    for gate_id, gate_row in gate_rows_in.items():
        mapped_routes = [row["route_id"] for row in transition_rows if row["mapped_gate_id"] == gate_id]
        gate_transition_rows.append(
            {
                "gate_id": gate_id,
                "gate": gate_row.get("gate", ""),
                "mapped_routes": "; ".join(mapped_routes) if mapped_routes else "none",
                "master_closed_status": gate_row.get("master_closed_status", "no"),
                "closure_recommendation": gate_row.get("closure_recommendation", "keep_open"),
                "open_artifact_requirements": gate_row.get("open_artifact_requirements", ""),
                "gate_transition_status": "closed" if gate_row.get("master_closed_status") == "yes" else "blocked_open",
                "next_evidence_needed": gate_row.get("next_evidence_needed", ""),
            }
        )

    final_sequence_rows = [
        {
            "sequence": 1,
            "stage": "scan_return_inbox",
            "required_status": "candidate_return_files>0 only after real evidence arrives",
            "current_status": f"candidate_return_files={writeback_summary.get('candidate_return_files')}",
            "allowed_now": "no",
        },
        {
            "sequence": 2,
            "stage": "protected_manual_writeback",
            "required_status": "writeback_allowed_rows>0 after manual inspection",
            "current_status": f"writeback_allowed_rows={writeback_summary.get('writeback_allowed_rows')}",
            "allowed_now": "no",
        },
        {
            "sequence": 3,
            "stage": "route_specific_validators",
            "required_status": "all currently_allowed commands pass after writeback",
            "current_status": f"validation_command_rows={writeback_summary.get('validation_command_rows')}",
            "allowed_now": "no",
        },
        {
            "sequence": 4,
            "stage": "gate_closure_binder",
            "required_status": "open_evidence_requirements=0",
            "current_status": f"open_evidence_requirements={gate_summary.get('open_evidence_requirements')}",
            "allowed_now": "no",
        },
        {
            "sequence": 5,
            "stage": "submission_final_lock",
            "required_status": "open_master_gates=0 and portal_upload_ready=true",
            "current_status": f"open_master_gates={submission_summary.get('open_master_gates')}; portal_upload_ready={submission_summary.get('portal_upload_ready')}",
            "allowed_now": "no",
        },
        {
            "sequence": 6,
            "stage": "portal_upload_or_submission",
            "required_status": "submission_ready=true",
            "current_status": f"submission_ready={submission_summary.get('submission_ready')}",
            "allowed_now": "no",
        },
    ]

    no_go_rows = [
        {
            "rule_id": "GT-NG-001",
            "rule": "Do not execute route-specific validators as gate-closing commands before protected writeback is allowed.",
            "evidence": f"writeback_allowed_rows={writeback_summary.get('writeback_allowed_rows')}",
        },
        {
            "rule_id": "GT-NG-002",
            "rule": "Do not close any finalization gate while artifact evidence requirements remain open.",
            "evidence": f"open_evidence_requirements={gate_summary.get('open_evidence_requirements')}",
        },
        {
            "rule_id": "GT-NG-003",
            "rule": "Do not treat dashboard commands as executable while they remain blocked.",
            "evidence": f"blocked_commands={dashboard_summary.get('blocked_commands')}",
        },
        {
            "rule_id": "GT-NG-004",
            "rule": "Do not perform portal upload or submission while portal upload rows are not ready.",
            "evidence": f"portal_upload_ready_rows={submission_summary.get('portal_upload_ready_rows')}",
        },
    ]

    transition_allowed_rows = [row for row in transition_rows if row["transition_allowed_now"] == "yes"]
    open_gate_rows = [row for row in gate_transition_rows if row["master_closed_status"] != "yes"]

    qa_rows = [
        {
            "check": "all_writeback_commands_mapped",
            "result": "PASS" if len(transition_rows) == writeback_summary.get("validation_command_rows") == 7 else "FAIL",
            "detail": f"transition_rows={len(transition_rows)}; validation_command_rows={writeback_summary.get('validation_command_rows')}",
        },
        {
            "check": "no_transition_allowed_without_writeback",
            "result": "PASS" if writeback_summary.get("writeback_allowed_rows") == 0 and not transition_allowed_rows else "FAIL",
            "detail": f"writeback_allowed_rows={writeback_summary.get('writeback_allowed_rows')}; transition_allowed_rows={len(transition_allowed_rows)}",
        },
        {
            "check": "all_master_gates_still_open",
            "result": "PASS" if len(open_gate_rows) == gate_summary.get("master_gates_bound") == 8 else "FAIL",
            "detail": f"open_gate_rows={len(open_gate_rows)}; master_gates={gate_summary.get('master_gates_bound')}",
        },
        {
            "check": "dashboard_commands_still_blocked",
            "result": "PASS" if dashboard_summary.get("blocked_commands") == 8 else "FAIL",
            "detail": f"blocked_commands={dashboard_summary.get('blocked_commands')}",
        },
        {
            "check": "submission_still_blocked",
            "result": "PASS" if submission_summary.get("submission_ready") is False and submission_summary.get("open_master_gates") == 8 else "FAIL",
            "detail": f"submission_ready={submission_summary.get('submission_ready')}; open_master_gates={submission_summary.get('open_master_gates')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "post_writeback_route_transition_matrix.csv", transition_rows, ["route_id", "worksheet_id", "command", "mapped_gate_id", "mapped_gate", "command_currently_allowed", "gate_master_closed_status", "open_artifact_requirements", "transition_allowed_now", "reason"])
    write_csv(OUT_DIR / "post_writeback_gate_transition_status.csv", gate_transition_rows, ["gate_id", "gate", "mapped_routes", "master_closed_status", "closure_recommendation", "open_artifact_requirements", "gate_transition_status", "next_evidence_needed"])
    write_csv(OUT_DIR / "post_writeback_final_sequence.csv", final_sequence_rows, ["sequence", "stage", "required_status", "current_status", "allowed_now"])
    write_csv(OUT_DIR / "post_writeback_transition_no_go_rules.csv", no_go_rows, ["rule_id", "rule", "evidence"])
    write_csv(OUT_DIR / "post_writeback_gate_transition_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Post-writeback gate transition validator 2026-08-10",
        "",
        "Status: `post_writeback_gate_transition_validator_ready_all_transitions_blocked`",
        "",
        f"1. Route transitions: {len(transition_rows)}",
        f"2. Transition allowed rows: {len(transition_allowed_rows)}",
        f"3. Gate rows: {len(gate_transition_rows)}",
        f"4. Open gate rows: {len(open_gate_rows)}",
        f"5. No-go rules: {len(no_go_rows)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator checks post-writeback transition readiness only. It does not execute validators, write back evidence, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "POST_WRITEBACK_GATE_TRANSITION_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "post_writeback_gate_transition_validator_report.md", "\n".join(report))

    summary = {
        "package": "post_writeback_gate_transition_validator_20260810",
        "route_transition_rows": len(transition_rows),
        "transition_allowed_rows": len(transition_allowed_rows),
        "gate_rows": len(gate_transition_rows),
        "open_gate_rows": len(open_gate_rows),
        "final_sequence_rows": len(final_sequence_rows),
        "no_go_rules": len(no_go_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "writeback_allowed_rows": writeback_summary.get("writeback_allowed_rows"),
        "open_evidence_requirements": gate_summary.get("open_evidence_requirements"),
        "blocked_dashboard_commands": dashboard_summary.get("blocked_commands"),
        "open_master_gates": submission_summary.get("open_master_gates"),
        "portal_upload_ready_rows": submission_summary.get("portal_upload_ready_rows"),
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "post_writeback_gate_transition_validator_ready_all_transitions_blocked",
    }

    section = f"""### 19.18 Post-writeback gate transition validator update

Added a validator for the command and gate transition sequence after protected evidence writeback.

New directory: `{OUT_DIR}`

New files:
1. `post_writeback_route_transition_matrix.csv`
2. `post_writeback_gate_transition_status.csv`
3. `post_writeback_final_sequence.csv`
4. `post_writeback_transition_no_go_rules.csv`
5. `post_writeback_gate_transition_qa.csv`
6. `POST_WRITEBACK_GATE_TRANSITION_VALIDATOR_README.md`
7. `post_writeback_gate_transition_validator_report.md`
8. `post_writeback_gate_transition_validator_summary.json`

Current result:
1. route_transition_rows = {summary['route_transition_rows']}
2. transition_allowed_rows = {summary['transition_allowed_rows']}
3. gate_rows = {summary['gate_rows']}
4. open_gate_rows = {summary['open_gate_rows']}
5. writeback_allowed_rows = {summary['writeback_allowed_rows']}
6. open_evidence_requirements = {summary['open_evidence_requirements']}
7. blocked_dashboard_commands = {summary['blocked_dashboard_commands']}
8. open_master_gates = {summary['open_master_gates']}
9. portal_upload_ready_rows = {summary['portal_upload_ready_rows']}
10. gate_closure_allowed = false
11. submission_ready = false

Boundary:
1. This validator checks post-writeback transition readiness only.
2. It does not execute validators or write back evidence.
3. It does not close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "post_writeback_gate_transition_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Post-writeback gate transition validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
