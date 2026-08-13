#!/usr/bin/env python3
"""Build RB-002 writeback readiness dashboard.

RB-002 is protected evidence writeback. This dashboard separates editable
targets from actual writeback permission and preserves the blocked state while
RB-001 is not closed.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb002_writeback_readiness_dashboard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_DASHBOARD = Path.home() / "Desktop" / "RB002_writeback_readiness_dashboard_20260810.md"

RB001_SUMMARY = BENCH_ROOT / "reports" / "rb001_closeout_dashboard_20260810" / "rb001_closeout_dashboard_summary.json"
WRITEBACK_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json"
WRITEBACK_MATRIX = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_writeback_route_matrix.csv"
TRANSITION_SUMMARY = BENCH_ROOT / "reports" / "post_writeback_gate_transition_validator_20260810" / "post_writeback_gate_transition_validator_summary.json"
RUNNER_SUMMARY = BENCH_ROOT / "reports" / "post_return_guarded_execution_runner_20260810" / "post_return_guarded_execution_runner_summary.json"
SUBMISSION_SUMMARY = BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810" / "natcomms_submission_final_lock_validator_summary.json"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
    marker = "### 19.31 RB-002 writeback readiness dashboard update"
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
    rb001 = read_json(RB001_SUMMARY)
    writeback = read_json(WRITEBACK_SUMMARY)
    transition = read_json(TRANSITION_SUMMARY)
    runner = read_json(RUNNER_SUMMARY)
    submission = read_json(SUBMISSION_SUMMARY)
    matrix = read_csv(WRITEBACK_MATRIX)

    readiness_rows = []
    for row in matrix:
        editable_target = row["safe_to_edit_now"] == "yes"
        candidate_files = int(row["candidate_files"])
        writeback_allowed = row["writeback_allowed_now"] == "yes"
        hard_blocker = (
            "rb001_not_closed"
            if not rb001.get("rb001_closed")
            else "candidate_files_absent"
            if candidate_files == 0
            else "route_not_writeback_allowed"
            if not writeback_allowed
            else ""
        )
        readiness_rows.append(
            {
                "route_id": row["route_id"],
                "evidence_type": row["evidence_type"],
                "target_status": row["target_status"],
                "candidate_files": candidate_files,
                "safe_to_edit_now": row["safe_to_edit_now"],
                "writeback_allowed_now": row["writeback_allowed_now"],
                "editable_target_ready": "yes" if editable_target else "no",
                "rb002_ready_now": "yes" if writeback_allowed and rb001.get("rb001_closed") else "no",
                "hard_blocker": hard_blocker,
            }
        )

    editable_targets = sum(1 for row in readiness_rows if row["editable_target_ready"] == "yes")
    schema_or_portal_blocked = sum(1 for row in readiness_rows if row["editable_target_ready"] == "no")
    rb002_ready_rows = sum(1 for row in readiness_rows if row["rb002_ready_now"] == "yes")

    blocker_rows = [
        {"blocker": "RB001_not_closed", "current": rb001.get("rb001_closed"), "required": "true", "effect": "No RB-002 writeback can proceed."},
        {"blocker": "candidate_files_absent", "current": writeback.get("candidate_return_files"), "required": ">0", "effect": "No route has real evidence for protected writeback."},
        {"blocker": "writeback_allowed_rows_zero", "current": writeback.get("writeback_allowed_rows"), "required": ">0", "effect": "No protected target can be written."},
        {"blocker": "transition_allowed_rows_zero", "current": transition.get("transition_allowed_rows"), "required": ">0 after writeback", "effect": "No gate transition can be triggered."},
        {"blocker": "guarded_commands_zero", "current": runner.get("commands_allowed_now"), "required": ">0 after transitions", "effect": "Guarded execution runner remains refusing commands."},
        {"blocker": "submission_not_ready", "current": submission.get("submission_ready"), "required": "true after all gates close", "effect": "No upload or submission."},
    ]

    next_action_rows = [
        {"order": 1, "action": "Finish RB-001 by placing real returned files, registering hashes and completing receipt validation.", "allowed_now": "manual_only"},
        {"order": 2, "action": "Rerun RB-001 closeout dashboard and receipt completion validator.", "allowed_now": "diagnostic_only"},
        {"order": 3, "action": "Only after RB-001 closes, rerun final_return_evidence_writeback_preflight.", "allowed_now": "blocked_now"},
        {"order": 4, "action": "Only if writeback_allowed_rows>0, perform protected manual writeback into listed target fields.", "allowed_now": "blocked_now"},
        {"order": 5, "action": "After protected writeback, rerun transition validator and guarded runner.", "allowed_now": "blocked_now"},
    ]

    rb002_ready = bool(rb001.get("rb001_closed")) and int(writeback.get("writeback_allowed_rows", 0)) > 0

    qa_rows = [
        {"check": "all_writeback_routes_summarized", "result": "PASS" if len(readiness_rows) == writeback.get("writeback_route_rows") == 7 else "FAIL", "detail": f"routes={len(readiness_rows)}"},
        {"check": "editable_targets_not_confused_with_writeback_permission", "result": "PASS" if editable_targets == writeback.get("safe_edit_rows") and rb002_ready_rows == 0 else "FAIL", "detail": f"editable_targets={editable_targets}; rb002_ready_rows={rb002_ready_rows}"},
        {"check": "rb001_blocker_preserved", "result": "PASS" if not rb001.get("rb001_closed") else "FAIL", "detail": f"rb001_closed={rb001.get('rb001_closed')}"},
        {"check": "writeback_still_blocked", "result": "PASS" if not rb002_ready and writeback.get("writeback_allowed_rows") == 0 else "FAIL", "detail": f"rb002_ready={rb002_ready}; writeback_allowed_rows={writeback.get('writeback_allowed_rows')}"},
        {"check": "submission_guard_preserved", "result": "PASS" if submission.get("submission_ready") is False else "FAIL", "detail": f"submission_ready={submission.get('submission_ready')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "rb002_writeback_route_readiness.csv", readiness_rows, ["route_id", "evidence_type", "target_status", "candidate_files", "safe_to_edit_now", "writeback_allowed_now", "editable_target_ready", "rb002_ready_now", "hard_blocker"])
    write_csv(OUT_DIR / "rb002_writeback_blockers.csv", blocker_rows, ["blocker", "current", "required", "effect"])
    write_csv(OUT_DIR / "rb002_writeback_next_actions.csv", next_action_rows, ["order", "action", "allowed_now"])
    write_csv(OUT_DIR / "rb002_writeback_readiness_dashboard_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# RB-002 writeback readiness dashboard 2026-08-10",
        "",
        "Status: `rb002_writeback_readiness_dashboard_ready_blocked_by_rb001`",
        "",
        f"1. Writeback routes: {len(readiness_rows)}",
        f"2. Editable targets: {editable_targets}",
        f"3. Schema/portal blocked targets: {schema_or_portal_blocked}",
        f"4. RB-002 ready rows: {rb002_ready_rows}",
        f"5. RB-001 closed: {rb001.get('rb001_closed')}",
        f"6. Writeback allowed rows: {writeback.get('writeback_allowed_rows')}",
        f"7. Submission ready: {submission.get('submission_ready')}",
        "",
        "Next action: finish RB-001 first. Editable target readiness is not writeback permission.",
        "",
        "Boundary: this dashboard does not write evidence, edit protected files, close gates, run transition commands, upload files or submit the manuscript.",
        "",
    ]
    report_text = "\n".join(report)
    write_text(OUT_DIR / "RB002_WRITEBACK_READINESS_DASHBOARD_README.md", report_text)
    write_text(OUT_DIR / "rb002_writeback_readiness_dashboard_report.md", report_text)
    write_text(DESKTOP_DASHBOARD, report_text)

    summary = {
        "package": "rb002_writeback_readiness_dashboard_20260810",
        "writeback_routes": len(readiness_rows),
        "editable_targets": editable_targets,
        "schema_or_portal_blocked_targets": schema_or_portal_blocked,
        "rb002_ready_rows": rb002_ready_rows,
        "blockers": len(blocker_rows),
        "next_actions": len(next_action_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "rb001_closed": rb001.get("rb001_closed"),
        "candidate_return_files": writeback.get("candidate_return_files"),
        "writeback_allowed_rows": writeback.get("writeback_allowed_rows"),
        "transition_allowed_rows": transition.get("transition_allowed_rows"),
        "commands_allowed_now": runner.get("commands_allowed_now"),
        "rb002_ready": rb002_ready,
        "submission_ready": False,
        "desktop_dashboard": str(DESKTOP_DASHBOARD),
        "status": "rb002_writeback_readiness_dashboard_ready_blocked_by_rb001",
    }

    section = f"""### 19.31 RB-002 writeback readiness dashboard update

Added a RB-002 writeback readiness dashboard that separates editable target readiness from protected writeback permission.

New directory: `{OUT_DIR}`

Desktop dashboard: `{DESKTOP_DASHBOARD}`

Current result:
1. writeback_routes = {summary['writeback_routes']}
2. editable_targets = {summary['editable_targets']}
3. schema_or_portal_blocked_targets = {summary['schema_or_portal_blocked_targets']}
4. rb002_ready_rows = {summary['rb002_ready_rows']}
5. rb001_closed = false
6. candidate_return_files = {summary['candidate_return_files']}
7. writeback_allowed_rows = {summary['writeback_allowed_rows']}
8. transition_allowed_rows = {summary['transition_allowed_rows']}
9. commands_allowed_now = {summary['commands_allowed_now']}
10. rb002_ready = false
11. submission_ready = false

Boundary:
1. This dashboard is a readiness view only.
2. Editable target readiness is not writeback permission.
3. It does not write protected targets, close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb002_writeback_readiness_dashboard_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-002 writeback readiness dashboard QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
