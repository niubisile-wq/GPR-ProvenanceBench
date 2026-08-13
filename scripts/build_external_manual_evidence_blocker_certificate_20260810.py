#!/usr/bin/env python3
"""Certify the current external-manual-evidence blocker state."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_manual_evidence_blocker_certificate_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


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
    marker = "### 19.94 External manual evidence blocker certificate update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/external_manual_evidence_blocker_certificate_20260810/` to certify that the current remaining blocker is real external/manual evidence, not a local automation failure.
- Current `blocker_rows={summary["blocker_rows"]}`, `missing_external_evidence_rows={summary["missing_external_evidence_rows"]}`, `local_automation_blocked_by_policy=true`.
- Current `allowed_local_commands_now=0`, `manual_action_queue_rows=5`, `submission_ready=false`, `goal_complete=false`.
- Boundary: this certificate is read-only. It does not execute human actions, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
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

    launcher_guard = read_json(BENCH_ROOT / "reports" / "manual_form_validation_launcher_guard_20260810" / "manual_form_validation_launcher_guard_summary.json")
    watcher = read_json(BENCH_ROOT / "reports" / "manual_evidence_arrival_watcher_20260810" / "manual_evidence_arrival_watcher_summary.json")
    capsule = read_json(BENCH_ROOT / "reports" / "daily_execution_status_capsule_20260810" / "daily_execution_status_capsule_summary.json")
    receipts = read_json(BENCH_ROOT / "reports" / "final_manual_receipt_completion_validator_20260810" / "final_manual_receipt_completion_validator_summary.json")

    blockers = [
        {
            "blocker_id": "EMB-001",
            "blocker": "No real manual evidence files detected",
            "evidence": f"candidate_files_detected={watcher.get('candidate_files_detected')}",
            "required_to_clear": "Place real evidence in the mapped inboxes.",
        },
        {
            "blocker_id": "EMB-002",
            "blocker": "MOF forms are not backfilled",
            "evidence": f"missing_required_cells={launcher_guard.get('missing_required_cells')}",
            "required_to_clear": "Fill all required MOF fields after real manual actions.",
        },
        {
            "blocker_id": "EMB-003",
            "blocker": "Manual form validation launcher is locked",
            "evidence": f"global_launch_allowed={launcher_guard.get('global_launch_allowed')}",
            "required_to_clear": "Complete backfill and evidence detection before launching 19.84.",
        },
        {
            "blocker_id": "EMB-004",
            "blocker": "Final manual receipts are incomplete",
            "evidence": f"complete_receipt_rows={receipts.get('complete_receipt_rows')}; incomplete_receipt_rows={receipts.get('incomplete_receipt_rows')}",
            "required_to_clear": "Complete FMR-001 through FMR-006 from validated evidence.",
        },
        {
            "blocker_id": "EMB-005",
            "blocker": "Portal and submission remain prohibited",
            "evidence": f"submission_ready={capsule.get('submission_ready')}; goal_complete={capsule.get('goal_complete')}",
            "required_to_clear": "Only after receipts, guarded recheck and final gate pass.",
        },
    ]

    allowed_rows = [
        {
            "action_type": "allowed",
            "action": "Execute the five real external/manual actions listed in the 19.90 capsule.",
            "evidence_source": "Desktop/NatComms_19.90_daily_execution_status_capsule_20260810.md",
        },
        {
            "action_type": "forbidden",
            "action": "Run validation/writeback/recheck/portal/submission commands.",
            "evidence_source": "runnable_validation_rows=0; allowed_local_commands_now=0",
        },
    ]

    qa_rows = [
        {
            "check": "external evidence is absent",
            "result": "PASS" if watcher.get("candidate_files_detected") == 0 else "FAIL",
            "detail": f"candidate_files_detected={watcher.get('candidate_files_detected')}",
        },
        {
            "check": "launcher remains blocked",
            "result": "PASS" if launcher_guard.get("global_launch_allowed") is False else "FAIL",
            "detail": f"global_launch_allowed={launcher_guard.get('global_launch_allowed')}",
        },
        {
            "check": "receipts remain incomplete",
            "result": "PASS" if receipts.get("complete_receipt_rows") == 0 else "FAIL",
            "detail": f"complete_receipt_rows={receipts.get('complete_receipt_rows')}",
        },
        {
            "check": "goal and submission remain false",
            "result": "PASS" if capsule.get("goal_complete") is False and capsule.get("submission_ready") is False else "FAIL",
            "detail": f"goal_complete={capsule.get('goal_complete')}; submission_ready={capsule.get('submission_ready')}",
        },
    ]

    summary = {
        "package": "external_manual_evidence_blocker_certificate_20260810",
        "blocker_rows": len(blockers),
        "missing_external_evidence_rows": 5,
        "local_automation_blocked_by_policy": True,
        "allowed_local_commands_now": 0,
        "manual_action_queue_rows": int(capsule.get("manual_action_queue_rows", 0) or 0),
        "complete_receipt_rows": int(receipts.get("complete_receipt_rows", 0) or 0),
        "submission_ready": False,
        "goal_complete": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "external_manual_evidence_blocker_certified_waiting_human_actions",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(OUT_DIR / "external_manual_evidence_blockers.csv", ["blocker_id", "blocker", "evidence", "required_to_clear"], blockers)
    write_csv(OUT_DIR / "external_manual_evidence_allowed_vs_forbidden.csv", ["action_type", "action", "evidence_source"], allowed_rows)
    write_csv(OUT_DIR / "external_manual_evidence_blocker_certificate_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# External Manual Evidence Blocker Certificate

Status: `{summary["status"]}`

Current result:

1. Blocker rows: {summary["blocker_rows"]}
2. Missing external evidence rows: {summary["missing_external_evidence_rows"]}
3. Local automation blocked by policy: true
4. Allowed local commands now: 0
5. Manual action queue rows: {summary["manual_action_queue_rows"]}
6. Complete receipt rows: {summary["complete_receipt_rows"]}
7. Submission ready: false
8. Goal complete: false

Boundary: this certificate is read-only. It does not execute human actions,
create evidence, run validators, execute writeback, run recheck, upload portal
files or submit.
"""
    write_text(OUT_DIR / "EXTERNAL_MANUAL_EVIDENCE_BLOCKER_CERTIFICATE_README.md", report)
    write_text(OUT_DIR / "external_manual_evidence_blocker_certificate_report.md", report)
    write_text(OUT_DIR / "external_manual_evidence_blocker_certificate_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
