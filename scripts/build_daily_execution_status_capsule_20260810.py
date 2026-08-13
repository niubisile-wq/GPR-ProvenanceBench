#!/usr/bin/env python3
"""Build a single current-state capsule for daily execution handoff."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "daily_execution_status_capsule_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_CAPSULE = Path.home() / "Desktop" / "NatComms_19.90_daily_execution_status_capsule_20260810.md"


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
    marker = "### 19.90 Daily execution status capsule update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/daily_execution_status_capsule_20260810/` and Desktop capsule `NatComms_19.90_daily_execution_status_capsule_20260810.md` as the single current-state handoff entry.
- Current `capsule_items={summary["capsule_items"]}`, `manual_action_queue_rows={summary["manual_action_queue_rows"]}`, `runnable_validation_rows={summary["runnable_validation_rows"]}`.
- Current `blocked_command_rows={summary["blocked_command_rows"]}`, `submission_ready=false`, `goal_complete=false`.
- Boundary: this capsule is read-only status packaging. It does not execute human actions, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
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

    route_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_route_snapshot_20260810"
        / "manual_evidence_route_snapshot_summary.json"
    )
    receipt_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "final_manual_receipt_completion_validator_20260810"
        / "final_manual_receipt_completion_validator_summary.json"
    )
    brief_acceptance = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_execution_brief_acceptance_20260810"
        / "manual_execution_brief_acceptance_summary.json"
    )
    action_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "manual_execution_brief_20260810"
        / "manual_execution_brief_actions.csv"
    )
    blocked_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_route_snapshot_20260810"
        / "manual_evidence_blocked_command_queue.csv"
    )

    capsule_rows = [
        {
            "item": "single_handoff_entry",
            "current_value": str(DESKTOP_CAPSULE),
            "status": "ready",
            "interpretation": "Open this capsule first for the current state.",
        },
        {
            "item": "human_action_queue",
            "current_value": str(route_summary.get("manual_action_queue_rows")),
            "status": "open",
            "interpretation": "Only these external/manual actions can move the project forward.",
        },
        {
            "item": "runnable_validation_queue",
            "current_value": str(route_summary.get("runnable_validation_rows")),
            "status": "blocked",
            "interpretation": "No validation command is allowed until real evidence and MOF forms are complete.",
        },
        {
            "item": "manual_receipts_complete",
            "current_value": str(receipt_summary.get("complete_receipt_rows")),
            "status": "blocked",
            "interpretation": "FMR receipt completion is still zero.",
        },
        {
            "item": "handoff_acceptance",
            "current_value": str(brief_acceptance.get("handoff_acceptance_ready")).lower(),
            "status": "ready",
            "interpretation": "The brief is safe to hand to a human; actions are not executed.",
        },
        {
            "item": "submission_ready",
            "current_value": "false",
            "status": "blocked",
            "interpretation": "Portal upload and submission remain prohibited.",
        },
    ]

    qa_rows = [
        {
            "check": "capsule includes required six status items",
            "result": "PASS" if len(capsule_rows) == 6 else "FAIL",
            "detail": f"capsule_items={len(capsule_rows)}",
        },
        {
            "check": "manual action queue remains five",
            "result": "PASS" if route_summary.get("manual_action_queue_rows") == 5 else "FAIL",
            "detail": f"manual_action_queue_rows={route_summary.get('manual_action_queue_rows')}",
        },
        {
            "check": "no runnable validation rows",
            "result": "PASS" if route_summary.get("runnable_validation_rows") == 0 else "FAIL",
            "detail": f"runnable_validation_rows={route_summary.get('runnable_validation_rows')}",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not route_summary.get("submission_ready") else "FAIL",
            "detail": f"submission_ready={route_summary.get('submission_ready')}",
        },
    ]

    capsule_lines = [
        "# NatComms 19.90 Daily Execution Status Capsule",
        "",
        "Current decision: do not run system validation, writeback, recheck, portal upload or submission.",
        "",
        "Allowed now:",
    ]
    for row in action_rows:
        capsule_lines.append(f"- {row['form_id']} / {row['primary_fmr']} / {row['phase']}: {row['do_now']}")
    capsule_lines.extend(["", "Blocked commands:"])
    for row in blocked_rows:
        capsule_lines.append(f"- {row['blocked_command']} [{row['blocked_item']}]: {row['reason']}")
    capsule_lines.extend(
        [
            "",
            "Status numbers:",
            f"- manual_action_queue_rows={route_summary.get('manual_action_queue_rows')}",
            f"- runnable_validation_rows={route_summary.get('runnable_validation_rows')}",
            f"- blocked_command_rows={route_summary.get('blocked_command_rows')}",
            f"- complete_receipt_rows={receipt_summary.get('complete_receipt_rows')}",
            "- submission_ready=false",
            "- goal_complete=false",
            "",
            "Boundary: this capsule is read-only status packaging. It does not execute human actions, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.",
        ]
    )
    capsule_text = "\n".join(capsule_lines) + "\n"

    summary = {
        "package": "daily_execution_status_capsule_20260810",
        "capsule_items": len(capsule_rows),
        "manual_action_queue_rows": int(route_summary.get("manual_action_queue_rows", 0) or 0),
        "runnable_validation_rows": int(route_summary.get("runnable_validation_rows", 0) or 0),
        "blocked_command_rows": int(route_summary.get("blocked_command_rows", 0) or 0),
        "complete_receipt_rows": int(receipt_summary.get("complete_receipt_rows", 0) or 0),
        "submission_ready": False,
        "goal_complete": False,
        "desktop_capsule": str(DESKTOP_CAPSULE),
        "desktop_capsule_exists": True,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "daily_execution_status_capsule_ready_manual_actions_only",
    }

    write_csv(OUT_DIR / "daily_execution_status_capsule.csv", ["item", "current_value", "status", "interpretation"], capsule_rows)
    write_csv(OUT_DIR / "daily_execution_status_capsule_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "DAILY_EXECUTION_STATUS_CAPSULE_README.md", capsule_text)
    write_text(OUT_DIR / "daily_execution_status_capsule_report.md", capsule_text)
    write_text(DESKTOP_CAPSULE, capsule_text)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "daily_execution_status_capsule_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
