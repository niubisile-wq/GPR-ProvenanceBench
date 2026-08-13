#!/usr/bin/env python3
"""Build a closeout dashboard for RB-001 real returned evidence intake."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dashboard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_DASHBOARD = Path.home() / "Desktop" / "RB001_closeout_dashboard_20260810.md"

SUMMARY_PATHS = {
    "drop_kit": BENCH_ROOT / "reports" / "rb001_return_evidence_drop_kit_20260810" / "rb001_return_evidence_drop_kit_summary.json",
    "hash_reconciliation": BENCH_ROOT / "reports" / "rb001_return_evidence_hash_reconciliation_20260810" / "rb001_return_evidence_hash_reconciliation_summary.json",
    "dry_run_gate": BENCH_ROOT / "reports" / "rb001_post_drop_dry_run_gate_20260810" / "rb001_post_drop_dry_run_gate_summary.json",
    "diagnostic_runner": BENCH_ROOT / "reports" / "rb001_diagnostic_only_runner_20260810" / "rb001_diagnostic_only_runner_summary.json",
    "manual_receipt": BENCH_ROOT / "reports" / "rb001_manual_execution_receipt_20260810" / "rb001_manual_execution_receipt_summary.json",
    "receipt_validator": BENCH_ROOT / "reports" / "rb001_receipt_completion_validator_20260810" / "rb001_receipt_completion_validator_summary.json",
    "writeback": BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810" / "final_return_evidence_writeback_preflight_summary.json",
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
    marker = "### 19.30 RB-001 closeout dashboard update"
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

    prepared_rows = [
        {"item": "canonical_drop_locations", "status": "ready", "evidence": f"route_rows={s['drop_kit'].get('route_rows')}"},
        {"item": "hash_source_register_template", "status": "ready", "evidence": f"register_template_rows={s['hash_reconciliation'].get('register_template_rows')}"},
        {"item": "post_drop_dry_run_gate", "status": "ready", "evidence": f"sequence_rows={s['dry_run_gate'].get('sequence_rows')}; guard_rows={s['dry_run_gate'].get('guard_rows')}"},
        {"item": "diagnostic_only_runner", "status": "ready", "evidence": f"runner_returncode={s['diagnostic_runner'].get('runner_returncode')}; forbidden_commands_excluded={s['diagnostic_runner'].get('forbidden_commands_excluded')}"},
        {"item": "manual_execution_receipt_template", "status": "ready_template_only", "evidence": f"receipt_template_rows={s['manual_receipt'].get('receipt_template_rows')}"},
        {"item": "receipt_completion_validator", "status": "ready_blocking_empty_state", "evidence": f"receipt_rows_validated={s['receipt_validator'].get('receipt_rows_validated')}"},
    ]

    blocker_rows = [
        {"blocker": "real_returned_files_absent", "current": s["drop_kit"].get("candidate_return_files"), "required": ">0", "next_action": "Copy real returned files into final_return_evidence_inbox_20260810 route folders."},
        {"blocker": "source_hash_register_unfilled", "current": s["hash_reconciliation"].get("filled_register_rows"), "required": ">0 and one row per scanner file", "next_action": "Fill source/hash register after real files exist."},
        {"blocker": "manual_receipt_unfilled", "current": s["manual_receipt"].get("completed_receipt_rows"), "required": ">0 and matching scanner rows", "next_action": "Fill RB001_manual_execution_receipt_20260810.csv after file copy and diagnostic runner."},
        {"blocker": "receipt_not_complete", "current": s["receipt_validator"].get("receipt_complete"), "required": "true", "next_action": "Rerun receipt completion validator after scanner, hash reconciliation and receipt are populated."},
        {"blocker": "writeback_preflight_not_allowed", "current": s["receipt_validator"].get("writeback_preflight_entry_allowed"), "required": "true", "next_action": "Do not run writeback for closure until receipt completion validator allows entry."},
        {"blocker": "submission_not_ready", "current": s["submission"].get("submission_ready"), "required": "true", "next_action": "Keep submission blocked until all master gates close."},
    ]

    next_action_rows = [
        {"order": 1, "action": "Place real returned files in the correct route folders under final_return_evidence_inbox_20260810.", "owner": "operator_or_author", "allowed_now": "manual_only"},
        {"order": 2, "action": "Run reports/rb001_diagnostic_only_runner_20260810/run_rb001_diagnostic_only.ps1.", "owner": "operator", "allowed_now": "yes_diagnostic"},
        {"order": 3, "action": "Fill source/hash register and RB001_manual_execution_receipt_20260810.csv with real file names, SHA256 values, source identity and runner return code.", "owner": "operator", "allowed_now": "after_real_files_exist"},
        {"order": 4, "action": "Run py scripts/build_rb001_receipt_completion_validator.py.", "owner": "operator", "allowed_now": "yes_diagnostic"},
        {"order": 5, "action": "Only if receipt_complete=true and writeback_preflight_entry_allowed=true, consider writeback preflight.", "owner": "operator", "allowed_now": "no_currently_blocked"},
    ]

    rb001_ready_for_writeback_preflight = bool(s["receipt_validator"].get("writeback_preflight_entry_allowed"))
    rb001_closed = (
        bool(s["receipt_validator"].get("receipt_complete"))
        and rb001_ready_for_writeback_preflight
        and int(s["writeback"].get("writeback_allowed_rows", 0)) > 0
    )

    qa_rows = [
        {"check": "all_preparation_layers_summarized", "result": "PASS" if len(prepared_rows) == 6 else "FAIL", "detail": f"prepared_rows={len(prepared_rows)}"},
        {"check": "blockers_preserved", "result": "PASS" if len(blocker_rows) >= 6 and not rb001_closed else "FAIL", "detail": f"blockers={len(blocker_rows)}; rb001_closed={rb001_closed}"},
        {"check": "no_false_writeback_entry", "result": "PASS" if not rb001_ready_for_writeback_preflight else "FAIL", "detail": f"writeback_preflight_entry_allowed={rb001_ready_for_writeback_preflight}"},
        {"check": "manual_next_action_present", "result": "PASS" if next_action_rows[0]["allowed_now"] == "manual_only" else "FAIL", "detail": next_action_rows[0]["action"]},
        {"check": "submission_guard_preserved", "result": "PASS" if s["submission"].get("submission_ready") is False else "FAIL", "detail": f"submission_ready={s['submission'].get('submission_ready')}"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "rb001_closeout_prepared_layers.csv", prepared_rows, ["item", "status", "evidence"])
    write_csv(OUT_DIR / "rb001_closeout_blockers.csv", blocker_rows, ["blocker", "current", "required", "next_action"])
    write_csv(OUT_DIR / "rb001_closeout_next_actions.csv", next_action_rows, ["order", "action", "owner", "allowed_now"])
    write_csv(OUT_DIR / "rb001_closeout_dashboard_qa.csv", qa_rows, ["check", "result", "detail"])

    report_lines = [
        "# RB-001 closeout dashboard 2026-08-10",
        "",
        "Status: `rb001_closeout_dashboard_ready_not_closed_waiting_for_real_returned_files`",
        "",
        "## Current State",
        "",
        f"1. candidate_return_files = {s['drop_kit'].get('candidate_return_files')}",
        f"2. completed_receipt_rows = {s['manual_receipt'].get('completed_receipt_rows')}",
        f"3. receipt_complete = {s['receipt_validator'].get('receipt_complete')}",
        f"4. writeback_preflight_entry_allowed = {s['receipt_validator'].get('writeback_preflight_entry_allowed')}",
        f"5. writeback_allowed_rows = {s['writeback'].get('writeback_allowed_rows')}",
        f"6. submission_ready = {s['submission'].get('submission_ready')}",
        "",
        "## Next Manual Action",
        "",
        "Copy real returned files into `final_return_evidence_inbox_20260810`, run the diagnostic-only runner, then fill the source/hash register and manual execution receipt.",
        "",
        "Boundary: RB-001 is not closed. This dashboard does not create evidence, grant writeback permission, close gates, upload files or submit the manuscript.",
        "",
    ]
    report = "\n".join(report_lines)
    write_text(OUT_DIR / "RB001_CLOSEOUT_DASHBOARD_README.md", report)
    write_text(OUT_DIR / "rb001_closeout_dashboard_report.md", report)
    write_text(DESKTOP_DASHBOARD, report)

    summary = {
        "package": "rb001_closeout_dashboard_20260810",
        "prepared_layers": len(prepared_rows),
        "blockers": len(blocker_rows),
        "next_actions": len(next_action_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": s["drop_kit"].get("candidate_return_files"),
        "completed_receipt_rows": s["manual_receipt"].get("completed_receipt_rows"),
        "receipt_complete": s["receipt_validator"].get("receipt_complete"),
        "writeback_preflight_entry_allowed": rb001_ready_for_writeback_preflight,
        "writeback_allowed_rows": s["writeback"].get("writeback_allowed_rows"),
        "rb001_closed": rb001_closed,
        "submission_ready": False,
        "desktop_dashboard": str(DESKTOP_DASHBOARD),
        "status": "rb001_closeout_dashboard_ready_not_closed_waiting_for_real_returned_files",
    }

    section = f"""### 19.30 RB-001 closeout dashboard update

Added a RB-001 closeout dashboard that separates prepared control layers from remaining real-evidence blockers and identifies the next manual action.

New directory: `{OUT_DIR}`

Desktop dashboard: `{DESKTOP_DASHBOARD}`

Current result:
1. prepared_layers = {summary['prepared_layers']}
2. blockers = {summary['blockers']}
3. next_actions = {summary['next_actions']}
4. candidate_return_files = {summary['candidate_return_files']}
5. completed_receipt_rows = {summary['completed_receipt_rows']}
6. receipt_complete = false
7. writeback_preflight_entry_allowed = false
8. rb001_closed = false
9. submission_ready = false

Boundary:
1. This dashboard is a closeout status view only.
2. It does not create returned evidence or fill manual receipts.
3. It does not grant writeback permission, close gates, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb001_closeout_dashboard_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-001 closeout dashboard QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
