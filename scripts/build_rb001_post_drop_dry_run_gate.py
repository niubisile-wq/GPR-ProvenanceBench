#!/usr/bin/env python3
"""Build the RB-001 post-drop dry-run gate.

This records the safe command sequence after real returned evidence is placed in
the canonical inbox. It is deliberately read-only in the current empty state and
must not close gates or perform writeback.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_post_drop_dry_run_gate_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"

SUMMARY_PATHS = {
    "scanner": BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json",
    "hash_reconciliation": BENCH_ROOT / "reports" / "rb001_return_evidence_hash_reconciliation_20260810" / "rb001_return_evidence_hash_reconciliation_summary.json",
    "writeback": BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json",
    "transition": BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_gate_transition_validator_summary.json",
    "guarded_runner": BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "post_return_guarded_execution_runner_summary.json",
    "submission": BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810" / "natcomms_submission_final_lock_validator_summary.json",
}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
    marker = "### 19.26 RB-001 post-drop dry-run gate update"
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
    s = {name: read_json(path) for name, path in SUMMARY_PATHS.items()}

    candidate_files = int(s["scanner"].get("candidate_return_files", 0))
    missing_register_rows = int(s["hash_reconciliation"].get("missing_source_register_rows", 0))
    hash_mismatch_rows = int(s["hash_reconciliation"].get("hash_mismatch_rows", 0))
    reconciled_rows = int(s["hash_reconciliation"].get("reconciled_rows", 0))
    writeback_allowed_rows = int(s["writeback"].get("writeback_allowed_rows", 0))
    transition_allowed_rows = int(s["transition"].get("transition_allowed_rows", 0))
    commands_allowed_now = int(s["guarded_runner"].get("commands_allowed_now", 0))
    open_master_gates = int(s["submission"].get("open_master_gates", 0))
    submission_ready = bool(s["submission"].get("submission_ready"))

    scanner_can_run = True
    reconciliation_can_run = candidate_files >= 0
    writeback_preflight_for_closure = (
        candidate_files > 0
        and missing_register_rows == 0
        and hash_mismatch_rows == 0
        and reconciled_rows == candidate_files
    )
    transition_for_closure = writeback_allowed_rows > 0
    guarded_runner_for_closure = commands_allowed_now > 0
    submission_for_closure = open_master_gates == 0 and submission_ready

    sequence_rows = [
        {
            "sequence": 1,
            "stage": "scan_canonical_inbox",
            "command": "py scripts/build_final_return_evidence_intake_scanner.py",
            "allowed_now": "yes_diagnostic",
            "closure_allowed_now": "no",
            "entry_condition": "canonical inbox folders exist",
            "stop_rule": "Do not write protected targets from scanner output alone.",
        },
        {
            "sequence": 2,
            "stage": "reconcile_hash_and_source_register",
            "command": "py scripts/build_rb001_return_evidence_hash_reconciliation.py",
            "allowed_now": "yes_diagnostic" if reconciliation_can_run else "no",
            "closure_allowed_now": "no",
            "entry_condition": "scanner manifest exists",
            "stop_rule": "Stop if missing_source_register_rows>0 or hash_mismatch_rows>0.",
        },
        {
            "sequence": 3,
            "stage": "writeback_preflight",
            "command": "py scripts/build_final_return_evidence_writeback_preflight.py",
            "allowed_now": "no",
            "closure_allowed_now": "yes" if writeback_preflight_for_closure else "no",
            "entry_condition": "candidate_return_files>0 and all scanner rows have matching source/hash registers",
            "stop_rule": "Do not write back while candidate_return_files=0 or reconciled_rows!=candidate_return_files.",
        },
        {
            "sequence": 4,
            "stage": "gate_transition_validation",
            "command": "py scripts/build_post_writeback_gate_transition_validator.py",
            "allowed_now": "no",
            "closure_allowed_now": "yes" if transition_for_closure else "no",
            "entry_condition": "protected writeback completed and writeback_allowed_rows>0",
            "stop_rule": "Do not transition gates while writeback_allowed_rows=0.",
        },
        {
            "sequence": 5,
            "stage": "guarded_runner",
            "command": "powershell -ExecutionPolicy Bypass -File reports/post_return_guarded_execution_runner_20260810/run_post_return_guarded_execution.ps1",
            "allowed_now": "no",
            "closure_allowed_now": "yes" if guarded_runner_for_closure else "no",
            "entry_condition": "transition validator allows at least one command",
            "stop_rule": "Do not execute guarded commands while commands_allowed_now=0.",
        },
        {
            "sequence": 6,
            "stage": "submission_final_lock",
            "command": "py scripts/build_natcomms_submission_final_lock_validator.py",
            "allowed_now": "no",
            "closure_allowed_now": "yes" if submission_for_closure else "no",
            "entry_condition": "all master gates closed",
            "stop_rule": "Do not upload or submit while open_master_gates>0.",
        },
    ]

    guard_rows = [
        {"guard": "candidate_files_present", "current_value": candidate_files, "required_for_closure": ">0", "passes_now": "yes" if candidate_files > 0 else "no"},
        {"guard": "all_files_registered", "current_value": missing_register_rows, "required_for_closure": "0", "passes_now": "yes" if candidate_files > 0 and missing_register_rows == 0 else "no"},
        {"guard": "no_hash_mismatch", "current_value": hash_mismatch_rows, "required_for_closure": "0", "passes_now": "yes" if candidate_files > 0 and hash_mismatch_rows == 0 else "no"},
        {"guard": "all_files_reconciled", "current_value": reconciled_rows, "required_for_closure": "candidate_return_files", "passes_now": "yes" if candidate_files > 0 and reconciled_rows == candidate_files else "no"},
        {"guard": "writeback_allowed", "current_value": writeback_allowed_rows, "required_for_closure": ">0", "passes_now": "yes" if writeback_allowed_rows > 0 else "no"},
        {"guard": "transitions_allowed", "current_value": transition_allowed_rows, "required_for_closure": ">0", "passes_now": "yes" if transition_allowed_rows > 0 else "no"},
        {"guard": "guarded_commands_allowed", "current_value": commands_allowed_now, "required_for_closure": ">0", "passes_now": "yes" if commands_allowed_now > 0 else "no"},
        {"guard": "master_gates_closed", "current_value": open_master_gates, "required_for_closure": "0", "passes_now": "yes" if open_master_gates == 0 else "no"},
    ]

    dry_run_rows = [
        {"check": "diagnostic_scanner_available", "result": "PASS" if scanner_can_run else "FAIL", "detail": "scanner command is always diagnostic-only"},
        {"check": "diagnostic_reconciliation_available", "result": "PASS" if reconciliation_can_run else "FAIL", "detail": "hash reconciliation can run without writeback"},
        {"check": "writeback_refused_empty_state", "result": "PASS" if not writeback_preflight_for_closure and writeback_allowed_rows == 0 else "FAIL", "detail": f"candidate_files={candidate_files}; writeback_allowed_rows={writeback_allowed_rows}"},
        {"check": "guarded_runner_refused_empty_state", "result": "PASS" if commands_allowed_now == 0 else "FAIL", "detail": f"commands_allowed_now={commands_allowed_now}"},
        {"check": "submission_guard_preserved", "result": "PASS" if open_master_gates > 0 and not submission_ready else "FAIL", "detail": f"open_master_gates={open_master_gates}; submission_ready={submission_ready}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in dry_run_rows)

    write_csv(OUT_DIR / "rb001_post_drop_command_sequence.csv", sequence_rows, ["sequence", "stage", "command", "allowed_now", "closure_allowed_now", "entry_condition", "stop_rule"])
    write_csv(OUT_DIR / "rb001_post_drop_guard_matrix.csv", guard_rows, ["guard", "current_value", "required_for_closure", "passes_now"])
    write_csv(OUT_DIR / "rb001_post_drop_dry_run_qa.csv", dry_run_rows, ["check", "result", "detail"])

    report = [
        "# RB-001 post-drop dry-run gate 2026-08-10",
        "",
        "Status: `rb001_post_drop_dry_run_gate_ready_empty_state_refuses_writeback`",
        "",
        f"1. Candidate returned files: {candidate_files}",
        f"2. Missing source-register rows: {missing_register_rows}",
        f"3. Hash mismatch rows: {hash_mismatch_rows}",
        f"4. Reconciled rows: {reconciled_rows}",
        f"5. Writeback allowed rows: {writeback_allowed_rows}",
        f"6. Guarded commands allowed now: {commands_allowed_now}",
        f"7. Open master gates: {open_master_gates}",
        f"8. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this is a dry-run gate. It defines the post-drop command order and refusal conditions only. It does not create evidence, write protected targets, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "RB001_POST_DROP_DRY_RUN_GATE_README.md", "\n".join(report))
    write_text(OUT_DIR / "rb001_post_drop_dry_run_gate_report.md", "\n".join(report))

    summary = {
        "package": "rb001_post_drop_dry_run_gate_20260810",
        "sequence_rows": len(sequence_rows),
        "guard_rows": len(guard_rows),
        "qa_rows": len(dry_run_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": candidate_files,
        "missing_source_register_rows": missing_register_rows,
        "hash_mismatch_rows": hash_mismatch_rows,
        "reconciled_rows": reconciled_rows,
        "writeback_allowed_rows": writeback_allowed_rows,
        "transition_allowed_rows": transition_allowed_rows,
        "commands_allowed_now": commands_allowed_now,
        "open_master_gates": open_master_gates,
        "submission_ready": False,
        "status": "rb001_post_drop_dry_run_gate_ready_empty_state_refuses_writeback",
    }

    section = f"""### 19.26 RB-001 post-drop dry-run gate update

Added a dry-run gate for the safe command order after real returned evidence is placed in `final_return_evidence_inbox_20260810`.

New directory: `{OUT_DIR}`

Current result:
1. sequence_rows = {summary['sequence_rows']}
2. guard_rows = {summary['guard_rows']}
3. candidate_return_files = {summary['candidate_return_files']}
4. missing_source_register_rows = {summary['missing_source_register_rows']}
5. hash_mismatch_rows = {summary['hash_mismatch_rows']}
6. reconciled_rows = {summary['reconciled_rows']}
7. writeback_allowed_rows = {summary['writeback_allowed_rows']}
8. transition_allowed_rows = {summary['transition_allowed_rows']}
9. commands_allowed_now = {summary['commands_allowed_now']}
10. open_master_gates = {summary['open_master_gates']}
11. submission_ready = false

Boundary:
1. This is a dry-run gate and command-order guard only.
2. It does not create evidence or source authorization.
3. It does not write protected targets, close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb001_post_drop_dry_run_gate_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-001 post-drop dry-run gate QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
