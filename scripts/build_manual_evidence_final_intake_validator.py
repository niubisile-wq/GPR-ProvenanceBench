#!/usr/bin/env python3
"""Validate whether manual/author evidence can be ingested into final gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_evidence_final_intake_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

AUTHOR_REPLY_DIR = BENCH_ROOT / "reports" / "natcomms_author_reply_ingestion_validator_20260810"
POST_DISPATCH_DIR = BENCH_ROOT / "reports" / "post_dispatch_evidence_intake_validator_20260810"
MANUAL_ENTRY_DIR = BENCH_ROOT / "reports" / "manual_evidence_entry_preflight_20260810"
GATE_BINDER_DIR = BENCH_ROOT / "reports" / "natcomms_gate_closure_evidence_binder_20260810"
SUBMISSION_LOCK_DIR = BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810"

AUTHOR_REPLY_SUMMARY = AUTHOR_REPLY_DIR / "author_reply_ingestion_validator_summary.json"
POST_DISPATCH_SUMMARY = POST_DISPATCH_DIR / "post_dispatch_evidence_intake_validator_summary.json"
MANUAL_ENTRY_SUMMARY = MANUAL_ENTRY_DIR / "manual_evidence_entry_preflight_summary.json"
GATE_BINDER_SUMMARY = GATE_BINDER_DIR / "gate_closure_evidence_binder_summary.json"
SUBMISSION_LOCK_SUMMARY = SUBMISSION_LOCK_DIR / "natcomms_submission_final_lock_validator_summary.json"

AUTHOR_REPLY_FIELDS = AUTHOR_REPLY_DIR / "author_reply_ingestion_validation.csv"
GATE_FROM_REPLIES = AUTHOR_REPLY_DIR / "gate_closure_from_author_replies.csv"
ANCILLARY_STATUS = AUTHOR_REPLY_DIR / "ancillary_reply_sheet_ingestion_status.csv"
POST_DISPATCH_MATRIX = POST_DISPATCH_DIR / "post_dispatch_evidence_intake_matrix.csv"
MANUAL_TARGETS = MANUAL_ENTRY_DIR / "manual_evidence_target_preflight.csv"
MANUAL_BLOCKERS = MANUAL_ENTRY_DIR / "manual_evidence_preflight_blockers.csv"
GATE_BINDER = GATE_BINDER_DIR / "gate_closure_evidence_binder.csv"
GATE_REQS = GATE_BINDER_DIR / "gate_artifact_evidence_requirements.csv"


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
    marker = "### 19.12 Manual evidence final intake validator update"
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

    author_summary = read_json(AUTHOR_REPLY_SUMMARY)
    post_summary = read_json(POST_DISPATCH_SUMMARY)
    manual_summary = read_json(MANUAL_ENTRY_SUMMARY)
    binder_summary = read_json(GATE_BINDER_SUMMARY)
    submission_summary = read_json(SUBMISSION_LOCK_SUMMARY)

    author_rows = read_csv(AUTHOR_REPLY_FIELDS)
    gate_reply_rows = read_csv(GATE_FROM_REPLIES)
    ancillary_rows = read_csv(ANCILLARY_STATUS)
    post_rows = read_csv(POST_DISPATCH_MATRIX)
    target_rows = read_csv(MANUAL_TARGETS)
    blocker_rows_import = read_csv(MANUAL_BLOCKERS)
    binder_rows = read_csv(GATE_BINDER)
    gate_req_rows = read_csv(GATE_REQS)

    filled_author_rows = [row for row in author_rows if row.get("author_reply_blank") == "no"]
    evidence_passed_rows = [row for row in post_rows if row.get("intake_status") == "passed"]
    safe_edit_rows = [row for row in blocker_rows_import if row.get("safe_to_edit_now") == "yes"]
    safe_rerun_rows = [row for row in blocker_rows_import if row.get("safe_to_rerun_after_edit") == "yes"]
    closed_gate_rows = [row for row in binder_rows if row.get("master_closed_status") == "yes"]
    open_gate_req_rows = [row for row in gate_req_rows if row.get("current_status", "open") != "closed"]

    gate_rows = [
        {
            "gate_id": "MANUAL-FINAL-001",
            "requirement": "Author replies are complete",
            "current_state": f"blank_author_reply_fields={author_summary.get('blank_author_reply_fields')} of {author_summary.get('author_reply_fields_audited')}",
            "passes_now": "no",
            "blocking_reason": "All core author reply fields remain blank.",
        },
        {
            "gate_id": "MANUAL-FINAL-002",
            "requirement": "Post-dispatch evidence rows pass intake",
            "current_state": f"passed={post_summary.get('evidence_rows_passed')} of {post_summary.get('evidence_rows')}",
            "passes_now": "no",
            "blocking_reason": "No real post-dispatch evidence has passed intake.",
        },
        {
            "gate_id": "MANUAL-FINAL-003",
            "requirement": "Branch commands are safe to rerun after manual entry",
            "current_state": f"branch_commands_safe_to_run_now={manual_summary.get('branch_commands_safe_to_run_now')}",
            "passes_now": "no",
            "blocking_reason": "Manual evidence is absent, so branch commands remain unsafe.",
        },
        {
            "gate_id": "MANUAL-FINAL-004",
            "requirement": "Gate closure evidence requirements are closed",
            "current_state": f"open_evidence_requirements={binder_summary.get('open_evidence_requirements')} of {binder_summary.get('artifact_evidence_requirements')}",
            "passes_now": "no",
            "blocking_reason": "All artifact evidence requirements remain open.",
        },
        {
            "gate_id": "MANUAL-FINAL-005",
            "requirement": "Submission final lock is allowed",
            "current_state": f"gate_closure_allowed={submission_summary.get('gate_closure_allowed')}; submission_ready={submission_summary.get('submission_ready')}",
            "passes_now": "no",
            "blocking_reason": "Submission final lock validator remains blocked.",
        },
    ]

    intake_rows = []
    for row in post_rows:
        intake_rows.append(
            {
                "evidence_type": row.get("evidence_type"),
                "observed_evidence": row.get("observed_evidence"),
                "intake_status": row.get("intake_status"),
                "gate_effect": row.get("gate_effect"),
                "final_intake_allowed_now": "no",
            }
        )

    edit_rows = []
    for row in blocker_rows_import:
        edit_rows.append(
            {
                "worksheet_id": row.get("worksheet_id"),
                "evidence_type": row.get("evidence_type"),
                "safe_to_edit_now": row.get("safe_to_edit_now"),
                "safe_to_rerun_after_edit": row.get("safe_to_rerun_after_edit"),
                "reason": row.get("reason"),
                "required_next_proof": row.get("required_next_proof"),
            }
        )

    blocker_rows = [
        {
            "blocker_id": "MANUAL-BLOCK-001",
            "blocker": "no_real_sendout_record",
            "evidence": "sent_rows=0 and email_sent=false",
            "next_required_evidence": "Real send log rows with sent status, timestamp and sender.",
        },
        {
            "blocker_id": "MANUAL-BLOCK-002",
            "blocker": "no_returned_author_reply_files",
            "evidence": "returned_rows=0 and all core author reply fields blank",
            "next_required_evidence": "Returned reply files with file paths and validation status.",
        },
        {
            "blocker_id": "MANUAL-BLOCK-003",
            "blocker": "backend_scope_not_selected",
            "evidence": "backend_valid=false and scope_valid=false",
            "next_required_evidence": "Allowed backend and figure scope choice from author/analysis lead.",
        },
        {
            "blocker_id": "MANUAL-BLOCK-004",
            "blocker": "external_rights_reporting_reference_evidence_missing",
            "evidence": "external asset, rights, Reporting Summary and reference authorization rows are missing",
            "next_required_evidence": "Strict-SHA external asset, rights decisions, Reporting Summary replies and reference replacement authorization.",
        },
    ]

    qa_rows = [
        {
            "check": "all_author_reply_fields_blank",
            "result": "PASS" if len(filled_author_rows) == 0 and author_summary.get("blank_author_reply_fields") == 12 else "FAIL",
            "detail": f"filled_author_rows={len(filled_author_rows)}; blank={author_summary.get('blank_author_reply_fields')}",
        },
        {
            "check": "no_post_dispatch_evidence_passed",
            "result": "PASS" if len(evidence_passed_rows) == 0 and post_summary.get("evidence_rows_missing") == 7 else "FAIL",
            "detail": f"evidence_passed_rows={len(evidence_passed_rows)}; missing={post_summary.get('evidence_rows_missing')}",
        },
        {
            "check": "no_safe_branch_reruns",
            "result": "PASS" if len(safe_rerun_rows) == 0 and manual_summary.get("branch_commands_safe_to_run_now") == 0 else "FAIL",
            "detail": f"safe_rerun_rows={len(safe_rerun_rows)}; branch_safe={manual_summary.get('branch_commands_safe_to_run_now')}",
        },
        {
            "check": "gate_closure_requirements_open",
            "result": "PASS" if len(closed_gate_rows) == 0 and binder_summary.get("open_evidence_requirements") == 16 else "FAIL",
            "detail": f"closed_gate_rows={len(closed_gate_rows)}; open_requirements={binder_summary.get('open_evidence_requirements')}",
        },
        {
            "check": "submission_still_blocked",
            "result": "PASS" if submission_summary.get("submission_ready") is False and submission_summary.get("gate_closure_allowed") is False else "FAIL",
            "detail": f"submission_ready={submission_summary.get('submission_ready')}; gate_closure_allowed={submission_summary.get('gate_closure_allowed')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "manual_evidence_final_intake_gate_matrix.csv", gate_rows, ["gate_id", "requirement", "current_state", "passes_now", "blocking_reason"])
    write_csv(OUT_DIR / "manual_evidence_final_intake_status.csv", intake_rows, ["evidence_type", "observed_evidence", "intake_status", "gate_effect", "final_intake_allowed_now"])
    write_csv(OUT_DIR / "manual_evidence_safe_edit_matrix.csv", edit_rows, ["worksheet_id", "evidence_type", "safe_to_edit_now", "safe_to_rerun_after_edit", "reason", "required_next_proof"])
    write_csv(OUT_DIR / "manual_evidence_final_intake_blockers.csv", blocker_rows, ["blocker_id", "blocker", "evidence", "next_required_evidence"])
    write_csv(OUT_DIR / "manual_evidence_final_intake_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Manual evidence final intake validator 2026-08-10",
        "",
        "Status: `manual_evidence_final_intake_validator_ready_blocked`",
        "",
        f"1. Author reply fields audited: {author_summary.get('author_reply_fields_audited')}",
        f"2. Blank author reply fields: {author_summary.get('blank_author_reply_fields')}",
        f"3. Post-dispatch evidence rows passed: {post_summary.get('evidence_rows_passed')} of {post_summary.get('evidence_rows')}",
        f"4. Safe edit rows: {len(safe_edit_rows)}",
        f"5. Safe rerun rows: {len(safe_rerun_rows)}",
        f"6. Open gate evidence requirements: {binder_summary.get('open_evidence_requirements')}",
        f"7. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator does not write manual evidence, ingest replies or close gates.",
        "",
    ]
    write_text(OUT_DIR / "MANUAL_EVIDENCE_FINAL_INTAKE_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "manual_evidence_final_intake_validator_report.md", "\n".join(report))

    summary = {
        "package": "manual_evidence_final_intake_validator_20260810",
        "gate_rows": len(gate_rows),
        "intake_status_rows": len(intake_rows),
        "safe_edit_rows": len(safe_edit_rows),
        "safe_rerun_rows": len(safe_rerun_rows),
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "author_reply_fields_audited": author_summary.get("author_reply_fields_audited"),
        "blank_author_reply_fields": author_summary.get("blank_author_reply_fields"),
        "evidence_rows": post_summary.get("evidence_rows"),
        "evidence_rows_passed": post_summary.get("evidence_rows_passed"),
        "evidence_rows_missing": post_summary.get("evidence_rows_missing"),
        "branch_commands_safe_to_run_now": manual_summary.get("branch_commands_safe_to_run_now"),
        "open_evidence_requirements": binder_summary.get("open_evidence_requirements"),
        "manual_evidence_final_intake_allowed": False,
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "manual_evidence_final_intake_validator_ready_blocked",
    }

    section = f"""### 19.12 Manual evidence final intake validator update

Added a final intake validator for manual/author evidence before gate closure.

New directory: `{OUT_DIR}`

New files:
1. `manual_evidence_final_intake_gate_matrix.csv`
2. `manual_evidence_final_intake_status.csv`
3. `manual_evidence_safe_edit_matrix.csv`
4. `manual_evidence_final_intake_blockers.csv`
5. `manual_evidence_final_intake_qa.csv`
6. `MANUAL_EVIDENCE_FINAL_INTAKE_VALIDATOR_README.md`
7. `manual_evidence_final_intake_validator_report.md`
8. `manual_evidence_final_intake_validator_summary.json`

Current result:
1. author_reply_fields_audited = {summary['author_reply_fields_audited']}
2. blank_author_reply_fields = {summary['blank_author_reply_fields']}
3. evidence_rows_passed = {summary['evidence_rows_passed']}
4. evidence_rows_missing = {summary['evidence_rows_missing']}
5. safe_rerun_rows = {summary['safe_rerun_rows']}
6. open_evidence_requirements = {summary['open_evidence_requirements']}
7. manual_evidence_final_intake_allowed = false
8. gate_closure_allowed = false
9. submission_ready = false

Boundary:
1. This validator checks manual evidence intake readiness only.
2. It does not write manual evidence or ingest replies.
3. It does not close finalization gates or make the submission ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_evidence_final_intake_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual evidence final intake validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
