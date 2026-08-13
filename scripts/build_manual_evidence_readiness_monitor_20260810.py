#!/usr/bin/env python3
"""Build a cross-source readiness monitor for manual evidence intake."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_evidence_readiness_monitor_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.85 Manual evidence readiness monitor update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_evidence_readiness_monitor_20260810/` to combine the 19.82 board, 19.83 forms, 19.84 validation and FMR inbox/operator states into one readiness monitor.
- Current `monitor_rows={summary["monitor_rows"]}`, `ready_for_downstream_validator_rows={summary["ready_for_downstream_validator_rows"]}`, `ready_for_writeback_rows={summary["ready_for_writeback_rows"]}`.
- Current `human_only_next_action_rows={summary["human_only_next_action_rows"]}`, `blocked_command_rows={summary["blocked_command_rows"]}`, `submission_ready=false`.
- Boundary: this monitor is read-only. It does not send messages, fill forms, create evidence, run downstream validators, execute writeback, run recheck, upload portal files or submit.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
        else:
            text = text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    board_rows = read_csv(BENCH_ROOT / "reports" / "final_execution_board_20260810" / "final_execution_board.csv")
    forms_index = read_csv(BENCH_ROOT / "reports" / "manual_only_execution_forms_20260810" / "manual_only_execution_forms_index.csv")
    validation_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "manual_only_execution_forms_validation_20260810"
        / "manual_only_execution_form_validation_status.csv"
    )
    route_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "manual_only_execution_forms_validation_20260810"
        / "manual_only_execution_form_to_validator_routes.csv"
    )
    operator_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "fmr_manual_evidence_operator_packet_20260810"
        / "fmr_manual_evidence_operator_packet.csv"
    )
    inbox_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "fmr_manual_evidence_inbox_integrity_audit_20260810"
        / "fmr_manual_evidence_inbox_integrity_matrix.csv"
    )
    validation_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_only_execution_forms_validation_20260810"
        / "manual_only_execution_forms_validation_summary.json"
    )
    receipt_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "final_manual_receipt_completion_validator_20260810"
        / "final_manual_receipt_completion_validator_summary.json"
    )

    board_by_step = {row["step_id"]: row for row in board_rows}
    validation_by_form = {row["form_id"]: row for row in validation_rows}
    route_by_form = {row["form_id"]: row for row in route_rows}
    inbox_by_fmr = {row["receipt_id"]: row for row in inbox_rows}
    operator_count_by_fmr: dict[str, int] = {}
    for row in operator_rows:
        operator_count_by_fmr[row["receipt_id"]] = operator_count_by_fmr.get(row["receipt_id"], 0) + 1

    monitor_rows = []
    for form in forms_index:
        validation = validation_by_form.get(form["form_id"], {})
        route = route_by_form.get(form["form_id"], {})
        board = board_by_step.get(form["step_id"], {})
        fmr = form["primary_fmr"]
        ready_for_downstream = validation.get("downstream_validator_allowed_now") == "yes"
        ready_for_writeback = False
        if ready_for_downstream:
            next_action = f"Run downstream validator: {form['next_validator']}"
            monitor_status = "ready_for_downstream_validator_only"
        else:
            next_action = "Complete the real manual action, place real evidence, fill form fields, record SHA256 and pass sensitive-content check."
            monitor_status = "waiting_real_manual_evidence"
        monitor_rows.append(
            {
                "form_id": form["form_id"],
                "step_id": form["step_id"],
                "phase": form["phase"],
                "primary_fmr": fmr,
                "board_allowed_now": board.get("allowed_now", ""),
                "form_complete_now": validation.get("form_complete_now", "no"),
                "evidence_path_exists": validation.get("evidence_path_exists", "no"),
                "sha256_format_valid": validation.get("sha256_format_valid", "no"),
                "validator_passed": validation.get("validator_passed", "no"),
                "inbox_present": "yes" if inbox_by_fmr.get(fmr, {}).get("primary_inbox_present") == "yes" else "no",
                "operator_rows_linked": operator_count_by_fmr.get(fmr, 0),
                "ready_for_downstream_validator": "yes" if ready_for_downstream else "no",
                "ready_for_writeback": "yes" if ready_for_writeback else "no",
                "next_action": next_action,
                "monitor_status": monitor_status,
                "blocked_commands": form.get("next_validator", "") if not ready_for_downstream else "FMR guarded writeback still blocked until preflight candidate is allowed",
                "submission_ready": "no",
            }
        )

    command_rows = []
    for row in monitor_rows:
        command_rows.append(
            {
                "form_id": row["form_id"],
                "primary_fmr": row["primary_fmr"],
                "command_or_action": row["next_action"],
                "allowed_now": "yes" if row["ready_for_downstream_validator"] == "yes" else "manual_only",
                "why_not_command": "" if row["ready_for_downstream_validator"] == "yes" else "form is incomplete or evidence is missing",
                "writeback_allowed_now": "no",
            }
        )
    command_rows.extend(
        [
            {
                "form_id": "GLOBAL",
                "primary_fmr": "FMR-001..FMR-006",
                "command_or_action": "any --execute-writeback",
                "allowed_now": "no",
                "why_not_command": "no preflight-approved FMR candidate exists",
                "writeback_allowed_now": "no",
            },
            {
                "form_id": "GLOBAL",
                "primary_fmr": "all",
                "command_or_action": "portal upload or submission",
                "allowed_now": "no",
                "why_not_command": "submission_ready=false",
                "writeback_allowed_now": "no",
            },
        ]
    )

    qa_rows = [
        {
            "check": "monitor covers all five manual-only forms",
            "result": "PASS" if len(monitor_rows) == 5 else "FAIL",
            "detail": f"monitor_rows={len(monitor_rows)}",
        },
        {
            "check": "current state allows no downstream validators",
            "result": "PASS" if all(row["ready_for_downstream_validator"] == "no" for row in monitor_rows) else "FAIL",
            "detail": f"ready_for_downstream_validator_rows={sum(1 for row in monitor_rows if row['ready_for_downstream_validator'] == 'yes')}",
        },
        {
            "check": "current state allows no writeback",
            "result": "PASS" if all(row["ready_for_writeback"] == "no" for row in monitor_rows) else "FAIL",
            "detail": "ready_for_writeback_rows=0",
        },
        {
            "check": "receipt completion remains false",
            "result": "PASS" if receipt_summary.get("complete_receipt_rows") == 0 else "FAIL",
            "detail": f"complete_receipt_rows={receipt_summary.get('complete_receipt_rows')}",
        },
        {
            "check": "validation summary agrees with no complete forms",
            "result": "PASS" if validation_summary.get("validated_form_rows") == 0 else "FAIL",
            "detail": f"validated_form_rows={validation_summary.get('validated_form_rows')}",
        },
    ]

    ready_for_downstream = sum(1 for row in monitor_rows if row["ready_for_downstream_validator"] == "yes")
    ready_for_writeback = sum(1 for row in monitor_rows if row["ready_for_writeback"] == "yes")
    human_only_next_actions = sum(1 for row in command_rows if row["allowed_now"] == "manual_only")
    blocked_command_rows = sum(1 for row in command_rows if row["allowed_now"] == "no")

    summary = {
        "package": "manual_evidence_readiness_monitor_20260810",
        "monitor_rows": len(monitor_rows),
        "ready_for_downstream_validator_rows": ready_for_downstream,
        "ready_for_writeback_rows": ready_for_writeback,
        "human_only_next_action_rows": human_only_next_actions,
        "blocked_command_rows": blocked_command_rows,
        "validated_form_rows": int(validation_summary.get("validated_form_rows", 0) or 0),
        "complete_receipt_rows": int(receipt_summary.get("complete_receipt_rows", 0) or 0),
        "allowed_commands_now": 0,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_evidence_readiness_monitor_ready_waiting_real_manual_evidence",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_evidence_readiness_monitor.csv",
        [
            "form_id",
            "step_id",
            "phase",
            "primary_fmr",
            "board_allowed_now",
            "form_complete_now",
            "evidence_path_exists",
            "sha256_format_valid",
            "validator_passed",
            "inbox_present",
            "operator_rows_linked",
            "ready_for_downstream_validator",
            "ready_for_writeback",
            "next_action",
            "monitor_status",
            "blocked_commands",
            "submission_ready",
        ],
        monitor_rows,
    )
    write_csv(
        OUT_DIR / "manual_evidence_next_allowed_actions.csv",
        ["form_id", "primary_fmr", "command_or_action", "allowed_now", "why_not_command", "writeback_allowed_now"],
        command_rows,
    )
    write_csv(OUT_DIR / "manual_evidence_readiness_monitor_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual Evidence Readiness Monitor

Status: `{summary["status"]}`

Current result:

1. Monitor rows: {summary["monitor_rows"]}
2. Ready for downstream validator rows: {summary["ready_for_downstream_validator_rows"]}
3. Ready for writeback rows: {summary["ready_for_writeback_rows"]}
4. Human-only next action rows: {summary["human_only_next_action_rows"]}
5. Blocked command rows: {summary["blocked_command_rows"]}
6. Validated form rows: {summary["validated_form_rows"]}
7. Complete receipt rows: {summary["complete_receipt_rows"]}
8. Allowed commands now: 0
9. Portal upload allowed: false
10. Submission ready: false

Boundary: this monitor is read-only. It does not send messages, fill forms,
create evidence, run downstream validators, execute writeback, run recheck,
upload portal files or submit.
"""
    write_text(OUT_DIR / "MANUAL_EVIDENCE_READINESS_MONITOR_README.md", report)
    write_text(OUT_DIR / "manual_evidence_readiness_monitor_report.md", report)
    write_text(OUT_DIR / "manual_evidence_readiness_monitor_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
