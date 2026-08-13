#!/usr/bin/env python3
"""Build a guarded post-return execution runner that refuses unsafe commands."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

SCANNER_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json"
WRITEBACK_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json"
TRANSITION_SUMMARY = BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_gate_transition_validator_summary.json"
TRANSITION_MATRIX = BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_route_transition_matrix.csv"
FINAL_SEQUENCE = BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_final_sequence.csv"


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
    marker = "### 19.19 Post-return guarded execution runner update"
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

    scanner_summary = read_json(SCANNER_SUMMARY)
    writeback_summary = read_json(WRITEBACK_SUMMARY)
    transition_summary = read_json(TRANSITION_SUMMARY)
    transition_rows = read_csv(TRANSITION_MATRIX)
    final_sequence_rows = read_csv(FINAL_SEQUENCE)

    guarded_rows: list[dict[str, object]] = []
    for row in transition_rows:
        currently_allowed = (
            row.get("command_currently_allowed") == "yes"
            and row.get("transition_allowed_now") == "yes"
            and writeback_summary.get("writeback_allowed_rows", 0) > 0
        )
        guarded_rows.append(
            {
                "guard_id": f"GUARD-{len(guarded_rows) + 1:03d}",
                "route_id": row.get("route_id", ""),
                "worksheet_id": row.get("worksheet_id", ""),
                "mapped_gate_id": row.get("mapped_gate_id", ""),
                "command": row.get("command", ""),
                "guard_decision": "allow" if currently_allowed else "block",
                "would_execute_now": "yes" if currently_allowed else "no",
                "blocking_reason": "Blocked by guard: protected writeback and gate transition are not both allowed.",
            }
        )

    global_guard_rows = [
        {
            "guard": "candidate_return_files_present",
            "required": "candidate_return_files > 0",
            "current": f"candidate_return_files={scanner_summary.get('candidate_return_files')}",
            "passes": "yes" if scanner_summary.get("candidate_return_files", 0) > 0 else "no",
        },
        {
            "guard": "writeback_allowed",
            "required": "writeback_allowed_rows > 0",
            "current": f"writeback_allowed_rows={writeback_summary.get('writeback_allowed_rows')}",
            "passes": "yes" if writeback_summary.get("writeback_allowed_rows", 0) > 0 else "no",
        },
        {
            "guard": "transition_allowed",
            "required": "transition_allowed_rows > 0",
            "current": f"transition_allowed_rows={transition_summary.get('transition_allowed_rows')}",
            "passes": "yes" if transition_summary.get("transition_allowed_rows", 0) > 0 else "no",
        },
        {
            "guard": "gate_closure_allowed",
            "required": "gate_closure_allowed = true",
            "current": f"gate_closure_allowed={transition_summary.get('gate_closure_allowed')}",
            "passes": "yes" if transition_summary.get("gate_closure_allowed") is True else "no",
        },
        {
            "guard": "submission_ready",
            "required": "submission_ready = true",
            "current": f"submission_ready={transition_summary.get('submission_ready')}",
            "passes": "yes" if transition_summary.get("submission_ready") is True else "no",
        },
    ]

    blocked_rows = [row for row in guarded_rows if row["guard_decision"] == "block"]
    allowed_rows = [row for row in guarded_rows if row["guard_decision"] == "allow"]
    global_passes = [row for row in global_guard_rows if row["passes"] == "yes"]

    runner_ps1 = OUT_DIR / "run_post_return_guarded_execution.ps1"
    runner_text = """$ErrorActionPreference = "Stop"
Write-Host "POST-RETURN GUARDED EXECUTION REFUSED"
Write-Host "No commands are allowed because real returned evidence/writeback/gate transitions are not ready."
Write-Host "Run build_post_return_guarded_execution_runner.py after real evidence writeback to regenerate guard state."
exit 2
"""
    write_text(runner_ps1, runner_text)

    qa_rows = [
        {
            "check": "all_transition_commands_guarded",
            "result": "PASS" if len(guarded_rows) == transition_summary.get("route_transition_rows") == 7 else "FAIL",
            "detail": f"guarded_rows={len(guarded_rows)}; route_transition_rows={transition_summary.get('route_transition_rows')}",
        },
        {
            "check": "all_commands_currently_blocked",
            "result": "PASS" if len(blocked_rows) == 7 and len(allowed_rows) == 0 else "FAIL",
            "detail": f"blocked={len(blocked_rows)}; allowed={len(allowed_rows)}",
        },
        {
            "check": "global_guards_refuse_execution",
            "result": "PASS" if len(global_passes) == 0 else "FAIL",
            "detail": f"passing_global_guards={len(global_passes)}",
        },
        {
            "check": "runner_script_created",
            "result": "PASS" if runner_ps1.exists() else "FAIL",
            "detail": str(runner_ps1),
        },
        {
            "check": "submission_still_blocked",
            "result": "PASS" if transition_summary.get("submission_ready") is False else "FAIL",
            "detail": f"submission_ready={transition_summary.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "post_return_guarded_command_plan.csv", guarded_rows, ["guard_id", "route_id", "worksheet_id", "mapped_gate_id", "command", "guard_decision", "would_execute_now", "blocking_reason"])
    write_csv(OUT_DIR / "post_return_global_guard_state.csv", global_guard_rows, ["guard", "required", "current", "passes"])
    write_csv(OUT_DIR / "post_return_guarded_final_sequence.csv", final_sequence_rows, ["sequence", "stage", "required_status", "current_status", "allowed_now"])
    write_csv(OUT_DIR / "post_return_guarded_execution_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Post-return guarded execution runner 2026-08-10",
        "",
        "Status: `post_return_guarded_execution_runner_ready_refusing_all_commands`",
        "",
        f"1. Guarded commands: {len(guarded_rows)}",
        f"2. Commands allowed now: {len(allowed_rows)}",
        f"3. Commands blocked now: {len(blocked_rows)}",
        f"4. Global guards passing: {len(global_passes)}",
        f"5. Runner script: `{runner_ps1}`",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this runner is a guarded refusal layer. It does not execute validators, write back evidence, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "POST_RETURN_GUARDED_EXECUTION_RUNNER_README.md", "\n".join(report))
    write_text(OUT_DIR / "post_return_guarded_execution_runner_report.md", "\n".join(report))

    summary = {
        "package": "post_return_guarded_execution_runner_20260810",
        "guarded_commands": len(guarded_rows),
        "commands_allowed_now": len(allowed_rows),
        "commands_blocked_now": len(blocked_rows),
        "global_guards": len(global_guard_rows),
        "global_guards_passing": len(global_passes),
        "runner_script": str(runner_ps1),
        "runner_script_exists": runner_ps1.exists(),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": scanner_summary.get("candidate_return_files"),
        "writeback_allowed_rows": writeback_summary.get("writeback_allowed_rows"),
        "transition_allowed_rows": transition_summary.get("transition_allowed_rows"),
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "post_return_guarded_execution_runner_ready_refusing_all_commands",
    }

    section = f"""### 19.19 Post-return guarded execution runner update

Added a guarded runner layer for post-return command execution.

New directory: `{OUT_DIR}`

New files:
1. `post_return_guarded_command_plan.csv`
2. `post_return_global_guard_state.csv`
3. `post_return_guarded_final_sequence.csv`
4. `post_return_guarded_execution_qa.csv`
5. `run_post_return_guarded_execution.ps1`
6. `POST_RETURN_GUARDED_EXECUTION_RUNNER_README.md`
7. `post_return_guarded_execution_runner_report.md`
8. `post_return_guarded_execution_runner_summary.json`

Current result:
1. guarded_commands = {summary['guarded_commands']}
2. commands_allowed_now = {summary['commands_allowed_now']}
3. commands_blocked_now = {summary['commands_blocked_now']}
4. global_guards_passing = {summary['global_guards_passing']}
5. candidate_return_files = {summary['candidate_return_files']}
6. writeback_allowed_rows = {summary['writeback_allowed_rows']}
7. transition_allowed_rows = {summary['transition_allowed_rows']}
8. gate_closure_allowed = false
9. submission_ready = false

Boundary:
1. This runner is a guarded refusal layer for post-return commands.
2. It does not execute validators or write back evidence.
3. It does not close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "post_return_guarded_execution_runner_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("Post-return guarded execution runner QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
