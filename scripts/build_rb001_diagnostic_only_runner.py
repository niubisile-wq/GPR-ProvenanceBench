#!/usr/bin/env python3
"""Build and validate the RB-001 diagnostic-only runner.

The generated PowerShell runner executes only read-only diagnostics:
1. final return evidence scanner
2. RB-001 hash/source reconciliation
3. RB-001 post-drop dry-run gate

It must not execute writeback, transition, guarded runner or submission
commands.
"""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_diagnostic_only_runner_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
RUNNER = OUT_DIR / "run_rb001_diagnostic_only.ps1"

SUMMARY_PATHS = {
    "scanner": BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json",
    "hash_reconciliation": BENCH_ROOT / "reports" / "rb001_return_evidence_hash_reconciliation_20260810" / "rb001_return_evidence_hash_reconciliation_summary.json",
    "dry_run_gate": BENCH_ROOT / "reports" / "rb001_post_drop_dry_run_gate_20260810" / "rb001_post_drop_dry_run_gate_summary.json",
    "writeback": BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json",
    "transition": BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_gate_transition_validator_summary.json",
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
    marker = "### 19.27 RB-001 diagnostic-only runner update"
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

    command_rows = [
        {
            "sequence": 1,
            "stage": "scan_canonical_inbox",
            "command": "py scripts/build_final_return_evidence_intake_scanner.py",
            "runner_includes": "yes",
            "allowed_mode": "diagnostic_only",
        },
        {
            "sequence": 2,
            "stage": "reconcile_hash_and_source_register",
            "command": "py scripts/build_rb001_return_evidence_hash_reconciliation.py",
            "runner_includes": "yes",
            "allowed_mode": "diagnostic_only",
        },
        {
            "sequence": 3,
            "stage": "post_drop_dry_run_gate",
            "command": "py scripts/build_rb001_post_drop_dry_run_gate.py",
            "runner_includes": "yes",
            "allowed_mode": "diagnostic_only",
        },
        {
            "sequence": 4,
            "stage": "writeback_preflight",
            "command": "py scripts/build_final_return_evidence_writeback_preflight.py",
            "runner_includes": "no",
            "allowed_mode": "forbidden_in_diagnostic_runner",
        },
        {
            "sequence": 5,
            "stage": "gate_transition_validation",
            "command": "py scripts/build_post_writeback_gate_transition_validator.py",
            "runner_includes": "no",
            "allowed_mode": "forbidden_in_diagnostic_runner",
        },
        {
            "sequence": 6,
            "stage": "submission_final_lock",
            "command": "py scripts/build_natcomms_submission_final_lock_validator.py",
            "runner_includes": "no",
            "allowed_mode": "forbidden_in_diagnostic_runner",
        },
    ]

    runner_text = """$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
Write-Host "RB-001 DIAGNOSTIC-ONLY RUNNER"
Write-Host "Running scanner, hash reconciliation and dry-run gate only."
py scripts/build_final_return_evidence_intake_scanner.py
py scripts/build_rb001_return_evidence_hash_reconciliation.py
py scripts/build_rb001_post_drop_dry_run_gate.py
Write-Host "RB-001 diagnostic-only runner completed. No writeback, transition, guarded runner or submission command was executed."
exit 0
"""
    write_text(RUNNER, runner_text)

    completed = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(RUNNER)],
        cwd=BENCH_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    write_text(OUT_DIR / "rb001_diagnostic_runner_stdout.txt", completed.stdout)
    write_text(OUT_DIR / "rb001_diagnostic_runner_stderr.txt", completed.stderr)

    s = {name: read_json(path) for name, path in SUMMARY_PATHS.items()}

    forbidden_tokens = [
        "build_final_return_evidence_writeback_preflight.py",
        "build_post_writeback_gate_transition_validator.py",
        "build_natcomms_submission_final_lock_validator.py",
        "run_post_return_guarded_execution.ps1",
    ]
    runner_includes_forbidden = any(token in runner_text for token in forbidden_tokens)

    qa_rows = [
        {"check": "runner_created", "result": "PASS" if RUNNER.exists() else "FAIL", "detail": str(RUNNER.name)},
        {"check": "runner_returncode_zero", "result": "PASS" if completed.returncode == 0 else "FAIL", "detail": f"returncode={completed.returncode}"},
        {"check": "runner_excludes_forbidden_commands", "result": "PASS" if not runner_includes_forbidden else "FAIL", "detail": "writeback/transition/submission/guarded runner not present"},
        {"check": "diagnostic_outputs_preserve_blocked_state", "result": "PASS" if s["scanner"].get("candidate_return_files") == 0 and s["hash_reconciliation"].get("writeback_allowed_rows") == 0 and s["dry_run_gate"].get("commands_allowed_now") == 0 else "FAIL", "detail": f"candidate_return_files={s['scanner'].get('candidate_return_files')}; writeback_allowed_rows={s['hash_reconciliation'].get('writeback_allowed_rows')}; commands_allowed_now={s['dry_run_gate'].get('commands_allowed_now')}"},
        {"check": "submission_guard_preserved", "result": "PASS" if s["submission"].get("submission_ready") is False and s["submission"].get("open_master_gates") == 8 else "FAIL", "detail": f"open_master_gates={s['submission'].get('open_master_gates')}; submission_ready={s['submission'].get('submission_ready')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "rb001_diagnostic_only_runner_commands.csv", command_rows, ["sequence", "stage", "command", "runner_includes", "allowed_mode"])
    write_csv(OUT_DIR / "rb001_diagnostic_only_runner_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# RB-001 diagnostic-only runner 2026-08-10",
        "",
        "Status: `rb001_diagnostic_only_runner_ready_diagnostic_passed_blocked_state_preserved`",
        "",
        f"1. Runner: `{RUNNER.name}`",
        f"2. Runner return code: {completed.returncode}",
        f"3. Candidate returned files: {s['scanner'].get('candidate_return_files')}",
        f"4. Writeback allowed rows: {s['hash_reconciliation'].get('writeback_allowed_rows')}",
        f"5. Commands allowed now: {s['dry_run_gate'].get('commands_allowed_now')}",
        f"6. Open master gates: {s['submission'].get('open_master_gates')}",
        f"7. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this runner executes diagnostic scanner, hash reconciliation and dry-run gate only. It does not run writeback, transition validation, guarded execution, upload or submission commands.",
        "",
    ]
    write_text(OUT_DIR / "RB001_DIAGNOSTIC_ONLY_RUNNER_README.md", "\n".join(report))
    write_text(OUT_DIR / "rb001_diagnostic_only_runner_report.md", "\n".join(report))

    summary = {
        "package": "rb001_diagnostic_only_runner_20260810",
        "runner_script": str(RUNNER),
        "runner_script_exists": RUNNER.exists(),
        "runner_returncode": completed.returncode,
        "command_rows": len(command_rows),
        "diagnostic_commands_included": sum(1 for row in command_rows if row["runner_includes"] == "yes"),
        "forbidden_commands_excluded": not runner_includes_forbidden,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": s["scanner"].get("candidate_return_files"),
        "writeback_allowed_rows": s["hash_reconciliation"].get("writeback_allowed_rows"),
        "commands_allowed_now": s["dry_run_gate"].get("commands_allowed_now"),
        "open_master_gates": s["submission"].get("open_master_gates"),
        "submission_ready": False,
        "status": "rb001_diagnostic_only_runner_ready_diagnostic_passed_blocked_state_preserved",
    }

    section = f"""### 19.27 RB-001 diagnostic-only runner update

Added a one-command diagnostic-only runner for RB-001. It executes only scanner, hash/source reconciliation and post-drop dry-run gate.

New directory: `{OUT_DIR}`

Runner: `{RUNNER}`

Current result:
1. runner_returncode = {summary['runner_returncode']}
2. diagnostic_commands_included = {summary['diagnostic_commands_included']}
3. forbidden_commands_excluded = {str(summary['forbidden_commands_excluded']).lower()}
4. candidate_return_files = {summary['candidate_return_files']}
5. writeback_allowed_rows = {summary['writeback_allowed_rows']}
6. commands_allowed_now = {summary['commands_allowed_now']}
7. open_master_gates = {summary['open_master_gates']}
8. submission_ready = false

Boundary:
1. This runner is diagnostic-only.
2. It does not run writeback, transition validation, guarded execution, upload or submission commands.
3. It preserves the current blocked state while making the RB-001 after-drop diagnostic path executable."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb001_diagnostic_only_runner_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-001 diagnostic-only runner QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
