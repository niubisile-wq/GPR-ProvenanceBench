#!/usr/bin/env python3
"""Build a dashboard for the manual-evidence lifecycle from dispatch to gate closure."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manual_evidence_lifecycle_dashboard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

SUMMARIES = {
    "manual_action": REPORTS / "today_manual_action_minipack_20260810" / "today_manual_action_minipack_summary.json",
    "inbox_scaffold": REPORTS / "manual_evidence_inbox_scaffold_20260810" / "manual_evidence_inbox_scaffold_summary.json",
    "inbox_audit": REPORTS / "manual_evidence_inbox_audit_20260810" / "manual_evidence_inbox_audit_summary.json",
    "writeback_queue": REPORTS / "inbox_to_tracker_writeback_queue_20260810" / "inbox_to_tracker_writeback_queue_summary.json",
    "post_dispatch_intake": REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json",
    "safe_rerun": REPORTS / "post_evidence_safe_rerun_guard_20260810" / "post_evidence_safe_rerun_guard_summary.json",
    "gate_closure": REPORTS / "gate_closure_execution_board_20260810" / "gate_closure_execution_board_summary.json",
}


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
    marker = "### 18.93 Manual evidence lifecycle dashboard update"
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
    summaries = {name: read_json(path) for name, path in SUMMARIES.items()}

    stage_rows = [
        {
            "stage_order": 1,
            "stage": "manual dispatch action",
            "current_status": summaries["manual_action"].get("status"),
            "ready_artifacts": f"action_rows={summaries['manual_action'].get('action_rows')}; desktop_guide_exists={summaries['manual_action'].get('desktop_guide_exists')}",
            "pass_metric": "manual_actions_executed=true",
            "current_pass": summaries["manual_action"].get("manual_actions_executed"),
            "next_required_action": "Execute real manual send/request actions and capture evidence.",
        },
        {
            "stage_order": 2,
            "stage": "inbox receiving",
            "current_status": summaries["inbox_scaffold"].get("status"),
            "ready_artifacts": f"inbox_folders={summaries['inbox_scaffold'].get('inbox_folders')}",
            "pass_metric": "candidate_evidence_files>0 after real returns",
            "current_pass": summaries["inbox_audit"].get("candidate_evidence_files", 0) > 0,
            "next_required_action": "Drop real returned files into the matching MD inbox folders.",
        },
        {
            "stage_order": 3,
            "stage": "inbox audit",
            "current_status": summaries["inbox_audit"].get("status"),
            "ready_artifacts": f"candidate_evidence_files={summaries['inbox_audit'].get('candidate_evidence_files')}; sensitive_name_rows={summaries['inbox_audit'].get('sensitive_name_rows')}",
            "pass_metric": "candidate files audited and no blocking sensitive-name issues",
            "current_pass": summaries["inbox_audit"].get("candidate_evidence_files", 0) > 0 and summaries["inbox_audit"].get("sensitive_name_rows") == 0,
            "next_required_action": "Rerun inbox audit after files arrive; inspect any label/answer markers.",
        },
        {
            "stage_order": 4,
            "stage": "tracker writeback queue",
            "current_status": summaries["writeback_queue"].get("status"),
            "ready_artifacts": f"writeback_rows={summaries['writeback_queue'].get('writeback_rows')}; writeback_allowed_rows={summaries['writeback_queue'].get('writeback_allowed_rows')}",
            "pass_metric": "manual tracker writeback completed and documented",
            "current_pass": summaries["writeback_queue"].get("tracker_write_performed"),
            "next_required_action": "Fill only mapped tracker fields after candidate files pass audit.",
        },
        {
            "stage_order": 5,
            "stage": "post-dispatch evidence intake",
            "current_status": summaries["post_dispatch_intake"].get("status"),
            "ready_artifacts": f"evidence_rows_passed={summaries['post_dispatch_intake'].get('evidence_rows_passed')}; missing={summaries['post_dispatch_intake'].get('evidence_rows_missing')}",
            "pass_metric": "all required evidence rows pass",
            "current_pass": summaries["post_dispatch_intake"].get("evidence_rows_passed") == summaries["post_dispatch_intake"].get("evidence_rows"),
            "next_required_action": "Run post-dispatch validator after tracker writeback.",
        },
        {
            "stage_order": 6,
            "stage": "safe branch rerun",
            "current_status": summaries["safe_rerun"].get("status"),
            "ready_artifacts": f"branch_commands_safe_to_run_now={summaries['safe_rerun'].get('branch_commands_safe_to_run_now')}",
            "pass_metric": "needed branch commands become safe and execute",
            "current_pass": summaries["safe_rerun"].get("commands_executed"),
            "next_required_action": "Run only branch validators marked safe after intake passes.",
        },
        {
            "stage_order": 7,
            "stage": "gate closure",
            "current_status": summaries["gate_closure"].get("status"),
            "ready_artifacts": f"gate_rows={summaries['gate_closure'].get('gate_rows')}; gate_closure_allowed={summaries['gate_closure'].get('gate_closure_allowed')}",
            "pass_metric": "gate_closure_allowed=true and portal_upload_ready=true",
            "current_pass": summaries["gate_closure"].get("gate_closure_allowed"),
            "next_required_action": "Close gates only after evidence binder and final verification pass.",
        },
    ]

    blocker_rows = [
        {
            "blocker_order": 1,
            "blocking_stage": "manual dispatch action",
            "blocking_fact": "manual_actions_executed=false",
            "effect": "No inbox evidence can legitimately exist yet.",
        },
        {
            "blocker_order": 2,
            "blocking_stage": "inbox audit",
            "blocking_fact": f"candidate_evidence_files={summaries['inbox_audit'].get('candidate_evidence_files')}",
            "effect": "tracker writeback remains disallowed.",
        },
        {
            "blocker_order": 3,
            "blocking_stage": "post-dispatch evidence intake",
            "blocking_fact": f"evidence_rows_passed={summaries['post_dispatch_intake'].get('evidence_rows_passed')}",
            "effect": "branch validators remain blocked.",
        },
        {
            "blocker_order": 4,
            "blocking_stage": "gate closure",
            "blocking_fact": f"gate_closure_allowed={summaries['gate_closure'].get('gate_closure_allowed')}",
            "effect": "portal upload and submission remain disallowed.",
        },
    ]

    next_action_rows = [
        {
            "priority": 1,
            "action": "Use the Desktop manual action minipack to send/request real materials.",
            "proof_required": "send evidence, returned files, backend/scope choice, external asset, rights/replies",
        },
        {
            "priority": 2,
            "action": "Place returned files into manual_evidence_inbox_20260810.",
            "proof_required": "candidate_evidence_files > 0 in inbox audit",
        },
        {
            "priority": 3,
            "action": "Rerun inbox audit and inspect sensitive-name rows.",
            "proof_required": "checksums recorded and sensitive_name_rows=0 or manually resolved",
        },
        {
            "priority": 4,
            "action": "Use writeback queue to fill only allowed tracker fields.",
            "proof_required": "post-dispatch evidence intake rows pass",
        },
        {
            "priority": 5,
            "action": "Run safe branch validators and then full M0-M2.",
            "proof_required": "gate_closure_allowed and submission dashboard updates",
        },
    ]

    qa_rows = [
        {
            "check": "seven_lifecycle_stages_indexed",
            "result": "PASS" if len(stage_rows) == 7 else "FAIL",
            "detail": f"stage_rows={len(stage_rows)}",
        },
        {
            "check": "current_blocking_chain_preserved",
            "result": "PASS" if summaries["manual_action"].get("manual_actions_executed") is False and summaries["post_dispatch_intake"].get("evidence_rows_passed") == 0 else "FAIL",
            "detail": "manual_actions_executed=false; evidence_rows_passed=0",
        },
        {
            "check": "no_downstream_execution_claim",
            "result": "PASS" if summaries["safe_rerun"].get("commands_executed") is False and summaries["gate_closure"].get("gate_closure_allowed") is False else "FAIL",
            "detail": f"commands_executed={summaries['safe_rerun'].get('commands_executed')}; gate_closure_allowed={summaries['gate_closure'].get('gate_closure_allowed')}",
        },
        {
            "check": "all_source_summaries_pass_qa",
            "result": "PASS" if all(summary.get("qa_pass") is True for summary in summaries.values()) else "FAIL",
            "detail": "; ".join(f"{name}={summary.get('qa_pass')}" for name, summary in summaries.items()),
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "manual_evidence_lifecycle_dashboard.csv",
        stage_rows,
        ["stage_order", "stage", "current_status", "ready_artifacts", "pass_metric", "current_pass", "next_required_action"],
    )
    write_csv(OUT_DIR / "manual_evidence_lifecycle_blockers.csv", blocker_rows, ["blocker_order", "blocking_stage", "blocking_fact", "effect"])
    write_csv(OUT_DIR / "manual_evidence_lifecycle_next_actions.csv", next_action_rows, ["priority", "action", "proof_required"])
    write_csv(OUT_DIR / "manual_evidence_lifecycle_dashboard_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Manual evidence lifecycle dashboard report 2026-08-10",
        "",
        "Status: `manual_evidence_lifecycle_dashboard_ready_waiting_manual_execution`",
        "",
        f"1. Lifecycle stages: {len(stage_rows)}",
        f"2. Blockers: {len(blocker_rows)}",
        f"3. Next actions: {len(next_action_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: the manual-evidence lifecycle is indexed end-to-end, but it is blocked at manual execution and empty inbox stages.",
        "",
    ]
    write_text(OUT_DIR / "MANUAL_EVIDENCE_LIFECYCLE_DASHBOARD_README.md", "\n".join(report))
    write_text(OUT_DIR / "manual_evidence_lifecycle_dashboard_report.md", "\n".join(report))

    summary = {
        "package": "manual_evidence_lifecycle_dashboard_20260810",
        "lifecycle_stages": len(stage_rows),
        "blocker_rows": len(blocker_rows),
        "next_action_rows": len(next_action_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_actions_executed": summaries["manual_action"].get("manual_actions_executed"),
        "candidate_evidence_files": summaries["inbox_audit"].get("candidate_evidence_files"),
        "writeback_allowed_rows": summaries["writeback_queue"].get("writeback_allowed_rows"),
        "evidence_rows_passed": summaries["post_dispatch_intake"].get("evidence_rows_passed"),
        "branch_commands_safe_to_run_now": summaries["safe_rerun"].get("branch_commands_safe_to_run_now"),
        "gate_closure_allowed": summaries["gate_closure"].get("gate_closure_allowed"),
        "submission_ready": False,
        "status": "manual_evidence_lifecycle_dashboard_ready_waiting_manual_execution",
    }

    section = f"""### 18.93 Manual evidence lifecycle dashboard update

Added a manual evidence lifecycle dashboard linking dispatch action, inbox receiving, inbox audit, tracker writeback, post-dispatch intake, safe rerun and gate closure.

New directory: `{OUT_DIR}`

New files:
1. `manual_evidence_lifecycle_dashboard.csv`
2. `manual_evidence_lifecycle_blockers.csv`
3. `manual_evidence_lifecycle_next_actions.csv`
4. `manual_evidence_lifecycle_dashboard_qa.csv`
5. `MANUAL_EVIDENCE_LIFECYCLE_DASHBOARD_README.md`
6. `manual_evidence_lifecycle_dashboard_report.md`
7. `manual_evidence_lifecycle_dashboard_summary.json`

Current result:
1. lifecycle_stages = {summary['lifecycle_stages']}
2. candidate_evidence_files = {summary['candidate_evidence_files']}
3. writeback_allowed_rows = {summary['writeback_allowed_rows']}
4. evidence_rows_passed = {summary['evidence_rows_passed']}
5. branch_commands_safe_to_run_now = {summary['branch_commands_safe_to_run_now']}
6. gate_closure_allowed = false
7. submission_ready = false

Boundary:
1. This step is a dashboard only.
2. This step does not write evidence or run branch validators.
3. This step does not close gates or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_evidence_lifecycle_dashboard_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual evidence lifecycle dashboard QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
