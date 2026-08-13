#!/usr/bin/env python3
"""Build a safe rerun guard for after manual evidence is entered."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "post_evidence_safe_rerun_guard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

WORKSHEET = REPORTS / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet.csv"
VALIDATOR_SUMMARY = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"
VALIDATOR_COMMANDS = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_next_validation_commands.csv"
MANUAL_FIELD_RERUN = REPORTS / "manual_field_preservation_audit_20260810" / "manual_field_safe_rerun_order.csv"
POST_SEND_QUEUE = REPORTS / "natcomms_manual_sendout_execution_guard_20260810" / "post_send_validation_command_queue.csv"


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
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.83 Post-evidence safe rerun guard update"
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

    worksheet_rows = read_csv(WORKSHEET)
    validator_summary = read_json(VALIDATOR_SUMMARY)
    validator_command_rows = read_csv(VALIDATOR_COMMANDS)
    manual_rerun_rows = read_csv(MANUAL_FIELD_RERUN)
    post_send_rows = read_csv(POST_SEND_QUEUE)

    stage_rows = [
        {
            "stage": "S0",
            "stage_name": "before_manual_evidence_entry",
            "allowed_action": "Read worksheets and dispatch packets only.",
            "blocked_action": "Do not run downstream ingestion/rendering/release finalization.",
            "current_state": "active",
        },
        {
            "stage": "S1",
            "stage_name": "after_partial_manual_evidence_entry",
            "allowed_action": "Run post-dispatch evidence intake validator to identify which branch is unlocked.",
            "blocked_action": "Do not run full finalization commands for branches whose evidence is still missing.",
            "current_state": "waiting",
        },
        {
            "stage": "S2",
            "stage_name": "after_branch_evidence_passes",
            "allowed_action": "Run only the branch validator listed for the passed evidence row.",
            "blocked_action": "Do not close gates until evidence binder and finalization dashboard pass.",
            "current_state": "waiting",
        },
        {
            "stage": "S3",
            "stage_name": "after_all_branch_validators_pass",
            "allowed_action": "Run gate binder, finalization dashboard, completion ledger and full M0-M2.",
            "blocked_action": "Do not portal-upload until portal_upload_ready=true and submission_ready=true.",
            "current_state": "waiting",
        },
    ]

    branch_rows = []
    for row in worksheet_rows:
        matching_command = next(
            (cmd for cmd in validator_command_rows if row["evidence_type"].replace("_", " ") in cmd["condition"].replace("_", " ")),
            None,
        )
        branch_rows.append(
            {
                "worksheet_id": row["worksheet_id"],
                "evidence_type": row["evidence_type"],
                "target_file": row["target_file"],
                "after_fill_validation": row["after_fill_validation"],
                "post_dispatch_command": matching_command["next_command"] if matching_command else row["after_fill_validation"],
                "blocked_now": matching_command["blocked_now"] if matching_command else "yes",
                "safe_to_run_now": "no",
            }
        )

    global_rerun_rows = [
        {"order": 1, "command": "py scripts\\build_post_dispatch_evidence_intake_validator.py", "purpose": "Re-evaluate real manual evidence after any worksheet target file is filled.", "run_now": "yes"},
        {"order": 2, "command": "Run only branch validators whose blocked_now becomes no", "purpose": "Avoid running downstream commands on missing evidence.", "run_now": "no"},
        {"order": 3, "command": "py scripts\\build_natcomms_gate_closure_evidence_binder.py", "purpose": "Bind candidate closure to explicit evidence after branch validators pass.", "run_now": "no"},
        {"order": 4, "command": "py scripts\\build_natcomms_finalization_command_dashboard_v3.py", "purpose": "Refresh finalization status after evidence binder changes.", "run_now": "no"},
        {"order": 5, "command": "py scripts\\build_submission_completion_ledger.py", "purpose": "Refresh the top-level gate ledger.", "run_now": "no"},
        {"order": 6, "command": "py scripts\\build_post_evidence_safe_rerun_guard.py", "purpose": "Refresh this rerun guard after branch status changes.", "run_now": "yes"},
        {"order": 7, "command": "powershell -ExecutionPolicy Bypass -File scripts\\run_m0_m2_checks.ps1", "purpose": "Final full-chain verification after evidence-dependent packages are updated.", "run_now": "no"},
    ]

    qa_rows = [
        {
            "check": "worksheet_and_validator_commands_imported",
            "result": "PASS" if len(worksheet_rows) == len(branch_rows) == 7 and len(validator_command_rows) == 7 else "FAIL",
            "detail": f"worksheet_rows={len(worksheet_rows)}; validator_commands={len(validator_command_rows)}",
        },
        {
            "check": "all_branch_commands_blocked_now",
            "result": "PASS" if all(row["blocked_now"] == "yes" for row in branch_rows) and validator_summary.get("evidence_rows_passed") == 0 else "FAIL",
            "detail": f"evidence_rows_passed={validator_summary.get('evidence_rows_passed')}",
        },
        {
            "check": "manual_preservation_rerun_order_imported",
            "result": "PASS" if len(manual_rerun_rows) >= 5 else "FAIL",
            "detail": f"manual_rerun_rows={len(manual_rerun_rows)}",
        },
        {
            "check": "post_send_queue_imported",
            "result": "PASS" if len(post_send_rows) >= 6 else "FAIL",
            "detail": f"post_send_rows={len(post_send_rows)}",
        },
        {
            "check": "no_downstream_gate_claimed",
            "result": "PASS",
            "detail": "This guard outputs order only; it does not execute commands or close gates.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "post_evidence_stage_gate_matrix.csv", stage_rows, ["stage", "stage_name", "allowed_action", "blocked_action", "current_state"])
    write_csv(
        OUT_DIR / "post_evidence_branch_rerun_matrix.csv",
        branch_rows,
        ["worksheet_id", "evidence_type", "target_file", "after_fill_validation", "post_dispatch_command", "blocked_now", "safe_to_run_now"],
    )
    write_csv(OUT_DIR / "post_evidence_global_rerun_order.csv", global_rerun_rows, ["order", "command", "purpose", "run_now"])
    write_csv(OUT_DIR / "post_evidence_safe_rerun_guard_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Post-evidence Safe Rerun Guard 2026-08-10

This package defines the safe command order after real manual evidence is entered.

Boundary: it does not execute the commands, modify manual evidence, close gates or submit the manuscript.
"""
    write_text(OUT_DIR / "POST_EVIDENCE_SAFE_RERUN_GUARD_README.md", readme)

    report = [
        "# Post-evidence safe rerun guard report 2026-08-10",
        "",
        "Status: `post_evidence_safe_rerun_guard_ready_waiting_manual_evidence`",
        "",
        f"- Stage rows: {len(stage_rows)}",
        f"- Branch rerun rows: {len(branch_rows)}",
        f"- Global rerun rows: {len(global_rerun_rows)}",
        f"- QA pass: {qa_pass}",
        "",
        "Conclusion: safe rerun order is defined. Branch validators remain blocked until real evidence appears.",
        "",
    ]
    write_text(OUT_DIR / "post_evidence_safe_rerun_guard_report.md", "\n".join(report))

    summary = {
        "package": "post_evidence_safe_rerun_guard_20260810",
        "stage_rows": len(stage_rows),
        "branch_rerun_rows": len(branch_rows),
        "branch_commands_safe_to_run_now": 0,
        "global_rerun_rows": len(global_rerun_rows),
        "manual_rerun_rows_imported": len(manual_rerun_rows),
        "post_send_rows_imported": len(post_send_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "commands_executed": False,
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "post_evidence_safe_rerun_guard_ready_waiting_manual_evidence",
    }

    section = f"""### 18.83 Post-evidence safe rerun guard update

Added a post-evidence safe rerun guard. This defines the safe command order after real manual evidence is entered.

New directory: `{OUT_DIR}`

New files:
1. `post_evidence_stage_gate_matrix.csv`
2. `post_evidence_branch_rerun_matrix.csv`
3. `post_evidence_global_rerun_order.csv`
4. `post_evidence_safe_rerun_guard_qa.csv`
5. `POST_EVIDENCE_SAFE_RERUN_GUARD_README.md`
6. `post_evidence_safe_rerun_guard_report.md`
7. `post_evidence_safe_rerun_guard_summary.json`

Current result:
1. stage_rows = {summary['stage_rows']}
2. branch_rerun_rows = {summary['branch_rerun_rows']}
3. branch_commands_safe_to_run_now = 0
4. global_rerun_rows = {summary['global_rerun_rows']}
5. manual_rerun_rows_imported = {summary['manual_rerun_rows_imported']}
6. post_send_rows_imported = {summary['post_send_rows_imported']}
7. qa_pass = {str(qa_pass).lower()}
8. commands_executed = false
9. gate_closure_allowed = false
10. submission_ready = false
11. status = `post_evidence_safe_rerun_guard_ready_waiting_manual_evidence`

Boundary:
1. This step does not execute commands.
2. This step does not modify manual evidence.
3. This step does not close gates or make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "post_evidence_safe_rerun_guard_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Post-evidence safe rerun guard QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
