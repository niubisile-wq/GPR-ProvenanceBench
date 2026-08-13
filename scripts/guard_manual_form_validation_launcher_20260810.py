#!/usr/bin/env python3
"""Guard whether manual-only form validation may be launched after backfill."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_form_validation_launcher_guard_20260810"
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
    marker = "### 19.93 Manual form validation launcher guard update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_form_validation_launcher_guard_20260810/` to guard whether 19.84 manual form validation may be launched after MOF backfill.
- Current `guard_rows={summary["guard_rows"]}`, `launch_allowed_rows={summary["launch_allowed_rows"]}`, `global_launch_allowed={str(summary["global_launch_allowed"]).lower()}`.
- Current `missing_required_cells={summary["missing_required_cells"]}`, `candidate_files_detected={summary["candidate_files_detected"]}`, `submission_ready=false`.
- Boundary: this guard is read-only. It does not launch validation, fill forms, create evidence, execute writeback, run recheck, upload portal files or submit.
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
    backfill_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_action_backfill_template_audit_20260810"
        / "manual_action_backfill_template_audit_summary.json"
    )
    watcher_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "manual_evidence_arrival_watcher_20260810"
        / "manual_evidence_arrival_watcher_summary.json"
    )
    backfill_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "manual_action_backfill_template_audit_20260810"
        / "manual_action_backfill_form_audit.csv"
    )
    route_rows = {
        row["form_id"]: row
        for row in read_csv(
            BENCH_ROOT
            / "reports"
            / "manual_evidence_arrival_watcher_20260810"
            / "manual_evidence_arrival_next_routes.csv"
        )
    }

    guard_rows = []
    for row in backfill_rows:
        route = route_rows.get(row["form_id"], {})
        candidate_files = int(route.get("candidate_files", "0") or 0)
        complete = row["form_backfill_complete"] == "yes"
        launch_allowed = complete and candidate_files > 0
        guard_rows.append(
            {
                "form_id": row["form_id"],
                "primary_fmr": row["primary_fmr"],
                "form_backfill_complete": row["form_backfill_complete"],
                "missing_required_cells": row["missing_required_cells"],
                "candidate_files": candidate_files,
                "ready_for_19_84_validation": route.get("ready_for_19_84_validation", "no"),
                "launch_19_84_allowed_now": "yes" if launch_allowed else "no",
                "blocked_reason": "" if launch_allowed else "missing backfill cells or no candidate evidence files",
            }
        )

    launch_allowed_rows = sum(1 for row in guard_rows if row["launch_19_84_allowed_now"] == "yes")
    global_launch_allowed = launch_allowed_rows == len(guard_rows) and len(guard_rows) == 5
    blocked_rows = [
        {
            "blocked_item": row["form_id"],
            "blocked_command": "py scripts/validate_manual_only_execution_forms_20260810.py",
            "reason": row["blocked_reason"],
        }
        for row in guard_rows
        if row["launch_19_84_allowed_now"] == "no"
    ]
    if not global_launch_allowed:
        blocked_rows.append(
            {
                "blocked_item": "GLOBAL",
                "blocked_command": "py scripts/validate_manual_only_execution_forms_20260810.py",
                "reason": "not all five MOF forms are complete with candidate evidence",
            }
        )

    qa_rows = [
        {
            "check": "guard covers all five MOF forms",
            "result": "PASS" if len(guard_rows) == 5 else "FAIL",
            "detail": f"guard_rows={len(guard_rows)}",
        },
        {
            "check": "current state refuses launch",
            "result": "PASS" if not global_launch_allowed else "FAIL",
            "detail": f"global_launch_allowed={global_launch_allowed}",
        },
        {
            "check": "backfill audit agrees forms incomplete",
            "result": "PASS" if backfill_summary.get("currently_complete_forms") == 0 else "FAIL",
            "detail": f"currently_complete_forms={backfill_summary.get('currently_complete_forms')}",
        },
        {
            "check": "watcher agrees no candidate files",
            "result": "PASS" if watcher_summary.get("candidate_files_detected") == 0 else "FAIL",
            "detail": f"candidate_files_detected={watcher_summary.get('candidate_files_detected')}",
        },
    ]

    summary = {
        "package": "manual_form_validation_launcher_guard_20260810",
        "guard_rows": len(guard_rows),
        "launch_allowed_rows": launch_allowed_rows,
        "global_launch_allowed": global_launch_allowed,
        "blocked_rows": len(blocked_rows),
        "missing_required_cells": int(backfill_summary.get("missing_required_cells", 0) or 0),
        "candidate_files_detected": int(watcher_summary.get("candidate_files_detected", 0) or 0),
        "allowed_commands_now": 0,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_form_validation_launcher_guard_refusing_current_state",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_form_validation_launcher_guard.csv",
        [
            "form_id",
            "primary_fmr",
            "form_backfill_complete",
            "missing_required_cells",
            "candidate_files",
            "ready_for_19_84_validation",
            "launch_19_84_allowed_now",
            "blocked_reason",
        ],
        guard_rows,
    )
    write_csv(OUT_DIR / "manual_form_validation_launcher_blockers.csv", ["blocked_item", "blocked_command", "reason"], blocked_rows)
    write_csv(OUT_DIR / "manual_form_validation_launcher_guard_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual Form Validation Launcher Guard

Status: `{summary["status"]}`

Current result:

1. Guard rows: {summary["guard_rows"]}
2. Launch allowed rows: {summary["launch_allowed_rows"]}
3. Global launch allowed: {str(summary["global_launch_allowed"]).lower()}
4. Blocked rows: {summary["blocked_rows"]}
5. Missing required cells: {summary["missing_required_cells"]}
6. Candidate files detected: {summary["candidate_files_detected"]}
7. Allowed commands now: 0
8. Submission ready: false

Boundary: this guard is read-only. It does not launch validation, fill forms,
create evidence, execute writeback, run recheck, upload portal files or submit.
"""
    write_text(OUT_DIR / "MANUAL_FORM_VALIDATION_LAUNCHER_GUARD_README.md", report)
    write_text(OUT_DIR / "manual_form_validation_launcher_guard_report.md", report)
    write_text(OUT_DIR / "manual_form_validation_launcher_guard_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
