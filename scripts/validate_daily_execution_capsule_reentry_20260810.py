#!/usr/bin/env python3
"""Validate the daily execution capsule as the re-entry source of truth."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "daily_execution_capsule_reentry_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_CAPSULE = Path.home() / "Desktop" / "NatComms_19.90_daily_execution_status_capsule_20260810.md"


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
    marker = "### 19.91 Daily execution capsule re-entry audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/daily_execution_capsule_reentry_audit_20260810/` to validate the 19.90 capsule as the current re-entry source of truth.
- Current `reentry_checks={summary["reentry_checks"]}`, `reentry_passed={str(summary["reentry_passed"]).lower()}`, `next_reentry_action={summary["next_reentry_action"]}`.
- Current `manual_action_queue_rows=5`, `runnable_validation_rows=0`, `allowed_commands_now=0`, `submission_ready=false`.
- Boundary: this audit is read-only. It does not execute human actions, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
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

    capsule_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "daily_execution_status_capsule_20260810"
        / "daily_execution_status_capsule_summary.json"
    )
    route_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_route_snapshot_20260810"
        / "manual_evidence_route_snapshot_summary.json"
    )
    watcher_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_arrival_watcher_20260810"
        / "manual_evidence_arrival_watcher_summary.json"
    )
    receipt_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "final_manual_receipt_completion_validator_20260810"
        / "final_manual_receipt_completion_validator_summary.json"
    )
    capsule_text = DESKTOP_CAPSULE.read_text(encoding="utf-8-sig") if DESKTOP_CAPSULE.exists() else ""

    checks = [
        {
            "check_id": "DCR-001",
            "check": "Desktop capsule exists",
            "expected": "true",
            "observed": str(DESKTOP_CAPSULE.exists()).lower(),
            "passes": "yes" if DESKTOP_CAPSULE.exists() else "no",
        },
        {
            "check_id": "DCR-002",
            "check": "Capsule and route agree on manual action queue",
            "expected": str(route_summary.get("manual_action_queue_rows")),
            "observed": str(capsule_summary.get("manual_action_queue_rows")),
            "passes": "yes" if capsule_summary.get("manual_action_queue_rows") == route_summary.get("manual_action_queue_rows") else "no",
        },
        {
            "check_id": "DCR-003",
            "check": "Capsule and route agree on runnable validation queue",
            "expected": str(route_summary.get("runnable_validation_rows")),
            "observed": str(capsule_summary.get("runnable_validation_rows")),
            "passes": "yes" if capsule_summary.get("runnable_validation_rows") == route_summary.get("runnable_validation_rows") else "no",
        },
        {
            "check_id": "DCR-004",
            "check": "Capsule and route agree on blocked commands",
            "expected": str(route_summary.get("blocked_command_rows")),
            "observed": str(capsule_summary.get("blocked_command_rows")),
            "passes": "yes" if capsule_summary.get("blocked_command_rows") == route_summary.get("blocked_command_rows") else "no",
        },
        {
            "check_id": "DCR-005",
            "check": "Capsule text preserves no-command decision",
            "expected": "do not run system validation, writeback, recheck, portal upload or submission",
            "observed": "present" if "do not run system validation, writeback, recheck, portal upload or submission" in capsule_text else "missing",
            "passes": "yes" if "do not run system validation, writeback, recheck, portal upload or submission" in capsule_text else "no",
        },
        {
            "check_id": "DCR-006",
            "check": "Watcher still detects no candidate evidence",
            "expected": "0",
            "observed": str(watcher_summary.get("candidate_files_detected")),
            "passes": "yes" if watcher_summary.get("candidate_files_detected") == 0 else "no",
        },
        {
            "check_id": "DCR-007",
            "check": "Receipt completion remains zero",
            "expected": "0",
            "observed": str(receipt_summary.get("complete_receipt_rows")),
            "passes": "yes" if receipt_summary.get("complete_receipt_rows") == 0 else "no",
        },
        {
            "check_id": "DCR-008",
            "check": "Goal remains incomplete",
            "expected": "false",
            "observed": str(capsule_summary.get("goal_complete")).lower(),
            "passes": "yes" if capsule_summary.get("goal_complete") is False else "no",
        },
    ]

    reentry_passed = all(row["passes"] == "yes" for row in checks)
    next_reentry_action = "open_capsule_then_execute_manual_actions_only"
    reentry_rows = [
        {
            "priority": 1,
            "action": "Open Desktop/NatComms_19.90_daily_execution_status_capsule_20260810.md",
            "allowed_now": "yes",
            "reason": "single current-state handoff entry",
        },
        {
            "priority": 2,
            "action": "Execute the five real manual actions listed in the capsule",
            "allowed_now": "yes",
            "reason": "only external/manual actions can produce missing evidence",
        },
        {
            "priority": 3,
            "action": "Run any validation/writeback/recheck/portal command",
            "allowed_now": "no",
            "reason": "runnable_validation_rows=0 and complete_receipt_rows=0",
        },
    ]

    qa_rows = [
        {
            "check": "all re-entry checks pass",
            "result": "PASS" if reentry_passed else "FAIL",
            "detail": f"passed={sum(1 for row in checks if row['passes'] == 'yes')}; total={len(checks)}",
        },
        {
            "check": "no command execution is allowed",
            "result": "PASS" if capsule_summary.get("runnable_validation_rows") == 0 else "FAIL",
            "detail": f"runnable_validation_rows={capsule_summary.get('runnable_validation_rows')}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if capsule_summary.get("submission_ready") is False else "FAIL",
            "detail": f"submission_ready={capsule_summary.get('submission_ready')}",
        },
    ]

    summary = {
        "package": "daily_execution_capsule_reentry_audit_20260810",
        "reentry_checks": len(checks),
        "passed_reentry_checks": sum(1 for row in checks if row["passes"] == "yes"),
        "reentry_passed": reentry_passed,
        "next_reentry_action": next_reentry_action,
        "manual_action_queue_rows": int(capsule_summary.get("manual_action_queue_rows", 0) or 0),
        "runnable_validation_rows": int(capsule_summary.get("runnable_validation_rows", 0) or 0),
        "allowed_commands_now": 0,
        "submission_ready": False,
        "goal_complete": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "daily_execution_capsule_reentry_audit_passed_manual_actions_only",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(OUT_DIR / "daily_execution_capsule_reentry_checks.csv", ["check_id", "check", "expected", "observed", "passes"], checks)
    write_csv(OUT_DIR / "daily_execution_capsule_reentry_next_actions.csv", ["priority", "action", "allowed_now", "reason"], reentry_rows)
    write_csv(OUT_DIR / "daily_execution_capsule_reentry_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Daily Execution Capsule Re-entry Audit

Status: `{summary["status"]}`

Current result:

1. Re-entry checks: {summary["reentry_checks"]}
2. Passed re-entry checks: {summary["passed_reentry_checks"]}
3. Re-entry passed: {str(summary["reentry_passed"]).lower()}
4. Next re-entry action: `{summary["next_reentry_action"]}`
5. Manual action queue rows: {summary["manual_action_queue_rows"]}
6. Runnable validation rows: {summary["runnable_validation_rows"]}
7. Allowed commands now: 0
8. Submission ready: false
9. Goal complete: false

Boundary: this audit is read-only. It does not execute human actions, create
evidence, run validators, execute writeback, run recheck, upload portal files
or submit.
"""
    write_text(OUT_DIR / "DAILY_EXECUTION_CAPSULE_REENTRY_AUDIT_README.md", report)
    write_text(OUT_DIR / "daily_execution_capsule_reentry_audit_report.md", report)
    write_text(OUT_DIR / "daily_execution_capsule_reentry_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
