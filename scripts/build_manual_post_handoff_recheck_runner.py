#!/usr/bin/env python3
"""Build a safe recheck runner for after human handoff actions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manual_post_handoff_recheck_runner_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8\u670810\u65e5cns.md"

HANDOFF_SUMMARY = REPORTS / "human_execution_handoff_acceptance_checklist_20260810" / "human_execution_handoff_acceptance_summary.json"
INBOX_SUMMARY = REPORTS / "manual_evidence_inbox_audit_20260810" / "manual_evidence_inbox_audit_summary.json"
VALIDATOR_SUMMARY = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"
LIFECYCLE_SUMMARY = REPORTS / "manual_evidence_lifecycle_dashboard_20260810" / "manual_evidence_lifecycle_dashboard_summary.json"
GATE_SUMMARY = REPORTS / "gate_closure_execution_board_20260810" / "gate_closure_execution_board_summary.json"


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
    marker = "### 18.96 Manual post-handoff recheck runner update"
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

    handoff = read_json(HANDOFF_SUMMARY)
    inbox = read_json(INBOX_SUMMARY)
    validator = read_json(VALIDATOR_SUMMARY)
    lifecycle = read_json(LIFECYCLE_SUMMARY)
    gate = read_json(GATE_SUMMARY)

    command_rows = [
        {
            "order": 1,
            "command": "py scripts\\build_manual_evidence_inbox_audit.py",
            "purpose": "Re-scan manual evidence inbox folders and checksums after returned files are placed.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 2,
            "command": "py scripts\\build_inbox_to_tracker_writeback_queue.py",
            "purpose": "Refresh writeback eligibility from audited inbox status.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 3,
            "command": "py scripts\\build_post_dispatch_evidence_intake_validator.py",
            "purpose": "Validate whether any returned manual evidence row is complete enough to unlock a branch.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 4,
            "command": "py scripts\\build_manual_evidence_entry_preflight.py",
            "purpose": "Check manual-entry targets, editable fields and blockers before any writeback.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 5,
            "command": "py scripts\\build_manual_evidence_lifecycle_dashboard.py",
            "purpose": "Refresh lifecycle status after inbox and validator updates.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 6,
            "command": "py scripts\\build_gate_closure_execution_board.py",
            "purpose": "Refresh gate prerequisites and stop rules without closing gates.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 7,
            "command": "py scripts\\build_submission_completion_ledger.py",
            "purpose": "Refresh top-level completion ledger after status-only packages change.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 8,
            "command": "py scripts\\build_portal_submission_file_preflight.py",
            "purpose": "Refresh upload blockers after gate ledger changes.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 9,
            "command": "py scripts\\check_manuscript_text_encoding.py",
            "purpose": "Check generated text artifacts for mojibake markers.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
        {
            "order": 10,
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\run_m0_m2_checks.ps1",
            "purpose": "Optional full-chain verification after evidence-dependent status packages are refreshed.",
            "writes_manual_evidence": "no",
            "can_close_gate": "no",
        },
    ]

    input_rows = [
        {"input_id": "INPUT-001", "source": str(HANDOFF_SUMMARY), "current_signal": f"manual_actions_executed={handoff.get('manual_actions_executed')}"},
        {"input_id": "INPUT-002", "source": str(INBOX_SUMMARY), "current_signal": f"candidate_evidence_files={inbox.get('candidate_evidence_files')}"},
        {"input_id": "INPUT-003", "source": str(VALIDATOR_SUMMARY), "current_signal": f"evidence_rows_passed={validator.get('evidence_rows_passed')}"},
        {"input_id": "INPUT-004", "source": str(LIFECYCLE_SUMMARY), "current_signal": f"submission_ready={lifecycle.get('submission_ready')}"},
        {"input_id": "INPUT-005", "source": str(GATE_SUMMARY), "current_signal": f"gate_closure_allowed={gate.get('gate_closure_allowed')}"},
    ]

    stop_rows = [
        {"rule_id": "RECHECK-STOP-001", "rule": "Do not run this as proof that manual emails were sent; send evidence must be entered separately."},
        {"rule_id": "RECHECK-STOP-002", "rule": "Do not write returned evidence into tracker files from this runner."},
        {"rule_id": "RECHECK-STOP-003", "rule": "Do not run branch validators unless the intake validator explicitly unlocks the branch."},
        {"rule_id": "RECHECK-STOP-004", "rule": "Do not close gates unless the evidence binder and finalization dashboard both allow closure."},
        {"rule_id": "RECHECK-STOP-005", "rule": "Do not upload while portal_upload_ready=false or submission_ready=false."},
    ]

    referenced_scripts = [
        "build_manual_evidence_inbox_audit.py",
        "build_inbox_to_tracker_writeback_queue.py",
        "build_post_dispatch_evidence_intake_validator.py",
        "build_manual_evidence_entry_preflight.py",
        "build_manual_evidence_lifecycle_dashboard.py",
        "build_gate_closure_execution_board.py",
        "build_submission_completion_ledger.py",
        "build_portal_submission_file_preflight.py",
        "check_manuscript_text_encoding.py",
    ]
    missing_scripts = [name for name in referenced_scripts if not (BENCH_ROOT / "scripts" / name).exists()]

    runner = r"""param(
    [switch]$FullM0M2
)

$ErrorActionPreference = "Stop"
$Bench = (Get-Item $PSScriptRoot).Parent.Parent.FullName
Set-Location $Bench

function Invoke-SafeStep {
    param([string]$Label, [string[]]$Command)
    Write-Host "SAFE RECHECK: $Label"
    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label"
    }
}

Invoke-SafeStep "audit manual evidence inbox" @("py", "scripts\build_manual_evidence_inbox_audit.py")
Invoke-SafeStep "refresh inbox-to-tracker writeback queue" @("py", "scripts\build_inbox_to_tracker_writeback_queue.py")
Invoke-SafeStep "validate post-dispatch evidence intake" @("py", "scripts\build_post_dispatch_evidence_intake_validator.py")
Invoke-SafeStep "preflight manual evidence entry" @("py", "scripts\build_manual_evidence_entry_preflight.py")
Invoke-SafeStep "refresh manual evidence lifecycle dashboard" @("py", "scripts\build_manual_evidence_lifecycle_dashboard.py")
Invoke-SafeStep "refresh gate closure execution board" @("py", "scripts\build_gate_closure_execution_board.py")
Invoke-SafeStep "refresh submission completion ledger" @("py", "scripts\build_submission_completion_ledger.py")
Invoke-SafeStep "refresh portal submission file preflight" @("py", "scripts\build_portal_submission_file_preflight.py")
Invoke-SafeStep "check text encoding" @("py", "scripts\check_manuscript_text_encoding.py")

if ($FullM0M2) {
    powershell -ExecutionPolicy Bypass -File scripts\run_m0_m2_checks.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Full M0-M2 check failed"
    }
}

Write-Host "SAFE RECHECK COMPLETE. This runner did not write manual evidence, close gates, or upload files."
"""
    write_text(OUT_DIR / "run_after_manual_evidence_recheck.ps1", runner)

    qa_rows = [
        {
            "check": "all_current_state_summaries_exist",
            "result": "PASS" if all(path.exists() for path in [HANDOFF_SUMMARY, INBOX_SUMMARY, VALIDATOR_SUMMARY, LIFECYCLE_SUMMARY, GATE_SUMMARY]) else "FAIL",
            "detail": "five status summaries checked",
        },
        {
            "check": "referenced_scripts_exist",
            "result": "PASS" if not missing_scripts else "FAIL",
            "detail": ";".join(missing_scripts) if missing_scripts else "all referenced scripts present",
        },
        {
            "check": "runner_is_status_only",
            "result": "PASS" if all(row["writes_manual_evidence"] == "no" and row["can_close_gate"] == "no" for row in command_rows) else "FAIL",
            "detail": f"command_rows={len(command_rows)}",
        },
        {
            "check": "blocked_state_preserved",
            "result": "PASS" if validator.get("evidence_rows_passed") == 0 and lifecycle.get("submission_ready") is False and gate.get("gate_closure_allowed") is False else "FAIL",
            "detail": f"evidence_rows_passed={validator.get('evidence_rows_passed')}; submission_ready={lifecycle.get('submission_ready')}; gate_closure_allowed={gate.get('gate_closure_allowed')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "safe_recheck_command_sequence.csv", command_rows, ["order", "command", "purpose", "writes_manual_evidence", "can_close_gate"])
    write_csv(OUT_DIR / "safe_recheck_inputs.csv", input_rows, ["input_id", "source", "current_signal"])
    write_csv(OUT_DIR / "safe_recheck_stop_rules.csv", stop_rows, ["rule_id", "rule"])
    write_csv(OUT_DIR / "manual_post_handoff_recheck_runner_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Manual post-handoff recheck runner report 2026-08-10",
        "",
        "Status: `manual_post_handoff_recheck_runner_ready_status_only`",
        "",
        f"1. Safe command rows: {len(command_rows)}",
        f"2. Current-state input rows: {len(input_rows)}",
        f"3. Stop rules: {len(stop_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: a status-only PowerShell recheck runner is ready for use after real manual evidence is placed in the inbox/tracker workflow.",
        "",
        "Boundary: this package does not send messages, write manual evidence, close gates, render final figures, create DOI records or upload submission files.",
        "",
    ]
    write_text(OUT_DIR / "MANUAL_POST_HANDOFF_RECHECK_RUNNER_README.md", "\n".join(report))
    write_text(OUT_DIR / "manual_post_handoff_recheck_runner_report.md", "\n".join(report))

    output_summary = {
        "package": "manual_post_handoff_recheck_runner_20260810",
        "safe_command_rows": len(command_rows),
        "input_rows": len(input_rows),
        "stop_rules": len(stop_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "runner_script": "reports/manual_post_handoff_recheck_runner_20260810/run_after_manual_evidence_recheck.ps1",
        "commands_executed_by_builder": False,
        "writes_manual_evidence": False,
        "can_close_gate": False,
        "evidence_rows_passed": validator.get("evidence_rows_passed"),
        "gate_closure_allowed": gate.get("gate_closure_allowed"),
        "submission_ready": lifecycle.get("submission_ready"),
        "status": "manual_post_handoff_recheck_runner_ready_status_only",
    }

    section = f"""### 18.96 Manual post-handoff recheck runner update

Added a status-only PowerShell recheck runner for use after real human handoff actions and returned evidence are placed in the manual evidence workflow.

New directory: `{OUT_DIR}`

New files:
1. `safe_recheck_command_sequence.csv`
2. `safe_recheck_inputs.csv`
3. `safe_recheck_stop_rules.csv`
4. `run_after_manual_evidence_recheck.ps1`
5. `manual_post_handoff_recheck_runner_qa.csv`
6. `MANUAL_POST_HANDOFF_RECHECK_RUNNER_README.md`
7. `manual_post_handoff_recheck_runner_report.md`
8. `manual_post_handoff_recheck_runner_summary.json`

Current result:
1. safe_command_rows = {output_summary['safe_command_rows']}
2. input_rows = {output_summary['input_rows']}
3. stop_rules = {output_summary['stop_rules']}
4. qa_pass = {str(qa_pass).lower()}
5. evidence_rows_passed = {output_summary['evidence_rows_passed']}
6. gate_closure_allowed = false
7. submission_ready = false

Boundary:
1. This runner is status-only unless the operator explicitly runs it.
2. It does not write manual evidence or close gates.
3. It does not render final figures, create DOI records or upload submission files."""
    output_summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_post_handoff_recheck_runner_summary.json", json.dumps(output_summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual post-handoff recheck runner QA failed")
    print(json.dumps(output_summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
