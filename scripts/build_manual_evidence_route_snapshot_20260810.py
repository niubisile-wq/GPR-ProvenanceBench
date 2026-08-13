#!/usr/bin/env python3
"""Build a read-only route snapshot from manual evidence watcher results."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_evidence_route_snapshot_20260810"
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
    marker = "### 19.89 Manual evidence route snapshot update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_evidence_route_snapshot_20260810/` to convert the 19.88 watcher results into explicit run/do-not-run queues.
- Current `route_rows={summary["route_rows"]}`, `manual_action_queue_rows={summary["manual_action_queue_rows"]}`, `runnable_validation_rows={summary["runnable_validation_rows"]}`.
- Current `blocked_command_rows={summary["blocked_command_rows"]}`, `allowed_commands_now=0`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this snapshot is read-only routing. It does not move files, fill forms, run validators, execute writeback, run recheck, upload portal files or submit.
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

    watcher_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_arrival_watcher_20260810"
        / "manual_evidence_arrival_watcher_summary.json"
    )
    routes = read_csv(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_arrival_watcher_20260810"
        / "manual_evidence_arrival_next_routes.csv"
    )
    form_index = {
        row["form_id"]: row
        for row in read_csv(
            BENCH_ROOT
            / "reports"
            / "manual_only_execution_forms_20260810"
            / "manual_only_execution_forms_index.csv"
        )
    }

    route_rows = []
    run_queue_rows = []
    blocked_rows = []
    for row in routes:
        form = form_index.get(row["form_id"], {})
        ready_for_validation = row["ready_for_19_84_validation"] == "yes"
        state = "run_19_84_validation" if ready_for_validation else "manual_action_required"
        route_rows.append(
            {
                "form_id": row["form_id"],
                "primary_fmr": row["primary_fmr"],
                "phase": form.get("phase", ""),
                "candidate_files": row["candidate_files"],
                "filled_cells": row["filled_cells"],
                "tracked_cells": row["tracked_cells"],
                "route_state": state,
                "next_allowed_action": (
                    "py scripts/validate_manual_only_execution_forms_20260810.py"
                    if ready_for_validation
                    else "Complete real manual evidence capture and fill the matching MOF form."
                ),
                "system_command_allowed_now": "yes" if ready_for_validation else "no",
                "writeback_allowed_now": "no",
                "portal_upload_allowed_now": "no",
            }
        )
        if ready_for_validation:
            run_queue_rows.append(
                {
                    "queue_id": f"RUN-{row['form_id']}",
                    "form_id": row["form_id"],
                    "primary_fmr": row["primary_fmr"],
                    "command": "py scripts/validate_manual_only_execution_forms_20260810.py",
                    "allowed_now": "yes",
                    "boundary": "validation only; no writeback",
                }
            )
        else:
            blocked_rows.append(
                {
                    "blocked_item": row["form_id"],
                    "primary_fmr": row["primary_fmr"],
                    "blocked_command": "py scripts/validate_manual_only_execution_forms_20260810.py",
                    "reason": f"candidate_files={row['candidate_files']}; filled_cells={row['filled_cells']}/{row['tracked_cells']}",
                }
            )

    blocked_rows.extend(
        [
            {
                "blocked_item": "GLOBAL",
                "primary_fmr": "FMR-001..FMR-006",
                "blocked_command": "any --execute-writeback",
                "reason": "no downstream validation/preflight candidate is allowed",
            },
            {
                "blocked_item": "GLOBAL",
                "primary_fmr": "all",
                "blocked_command": "guarded recheck, portal upload or submission",
                "reason": "manual evidence incomplete and submission_ready=false",
            },
        ]
    )

    manual_action_queue_rows = sum(1 for row in route_rows if row["route_state"] == "manual_action_required")
    runnable_validation_rows = len(run_queue_rows)
    qa_rows = [
        {
            "check": "route snapshot covers all watcher route rows",
            "result": "PASS" if len(route_rows) == 5 else "FAIL",
            "detail": f"route_rows={len(route_rows)}",
        },
        {
            "check": "current state has no runnable validation rows",
            "result": "PASS" if runnable_validation_rows == 0 else "FAIL",
            "detail": f"runnable_validation_rows={runnable_validation_rows}",
        },
        {
            "check": "current state has five manual action rows",
            "result": "PASS" if manual_action_queue_rows == 5 else "FAIL",
            "detail": f"manual_action_queue_rows={manual_action_queue_rows}",
        },
        {
            "check": "watcher agrees no candidate files are present",
            "result": "PASS" if watcher_summary.get("candidate_files_detected") == 0 else "FAIL",
            "detail": f"candidate_files_detected={watcher_summary.get('candidate_files_detected')}",
        },
        {
            "check": "submission remains blocked",
            "result": "PASS" if not watcher_summary.get("submission_ready") else "FAIL",
            "detail": f"submission_ready={watcher_summary.get('submission_ready')}",
        },
    ]

    summary = {
        "package": "manual_evidence_route_snapshot_20260810",
        "route_rows": len(route_rows),
        "manual_action_queue_rows": manual_action_queue_rows,
        "runnable_validation_rows": runnable_validation_rows,
        "blocked_command_rows": len(blocked_rows),
        "candidate_files_detected": int(watcher_summary.get("candidate_files_detected", 0) or 0),
        "forms_with_any_fill": int(watcher_summary.get("forms_with_any_fill", 0) or 0),
        "allowed_commands_now": 0,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_evidence_route_snapshot_ready_manual_actions_only",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_evidence_route_snapshot.csv",
        [
            "form_id",
            "primary_fmr",
            "phase",
            "candidate_files",
            "filled_cells",
            "tracked_cells",
            "route_state",
            "next_allowed_action",
            "system_command_allowed_now",
            "writeback_allowed_now",
            "portal_upload_allowed_now",
        ],
        route_rows,
    )
    write_csv(
        OUT_DIR / "manual_evidence_runnable_validation_queue.csv",
        ["queue_id", "form_id", "primary_fmr", "command", "allowed_now", "boundary"],
        run_queue_rows,
    )
    write_csv(
        OUT_DIR / "manual_evidence_blocked_command_queue.csv",
        ["blocked_item", "primary_fmr", "blocked_command", "reason"],
        blocked_rows,
    )
    write_csv(OUT_DIR / "manual_evidence_route_snapshot_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual Evidence Route Snapshot

Status: `{summary["status"]}`

Current result:

1. Route rows: {summary["route_rows"]}
2. Manual action queue rows: {summary["manual_action_queue_rows"]}
3. Runnable validation rows: {summary["runnable_validation_rows"]}
4. Blocked command rows: {summary["blocked_command_rows"]}
5. Candidate files detected: {summary["candidate_files_detected"]}
6. Forms with any fill: {summary["forms_with_any_fill"]}
7. Allowed commands now: 0
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this snapshot is read-only routing. It does not move files, fill
forms, run validators, execute writeback, run recheck, upload portal files or
submit.
"""
    write_text(OUT_DIR / "MANUAL_EVIDENCE_ROUTE_SNAPSHOT_README.md", report)
    write_text(OUT_DIR / "manual_evidence_route_snapshot_report.md", report)
    write_text(OUT_DIR / "manual_evidence_route_snapshot_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
