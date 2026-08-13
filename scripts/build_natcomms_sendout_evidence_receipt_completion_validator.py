#!/usr/bin/env python3
"""Validate completion of the Nat Comms manual sendout evidence receipt."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_sendout_evidence_receipt_completion_validator_20260810"
SENDOUT_GUARD_DIR = BENCH_ROOT / "reports" / "natcomms_manual_sendout_execution_guard_20260810"
V2_AUDIT_DIR = BENCH_ROOT / "reports" / "natcomms_sendout_v2_lifecycle_consistency_audit_20260810"
LOG_VALIDATOR_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_log_validator_20260810"
POST_DISPATCH_DIR = BENCH_ROOT / "reports" / "post_dispatch_evidence_intake_validator_20260810"
RB001_DASHBOARD_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dashboard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

REQUIRED_BEFORE_SEND_FIELDS = {"recipient_list_confirmed", "email_body_boundary_checked"}
REQUIRED_AFTER_SEND_FIELDS = {"sent_zip_path", "sent_datetime_local"}
REQUIRED_RETURN_FIELDS = {"all_returned_files_stored"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def is_filled(value: str) -> bool:
    return bool(str(value).strip())


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.35 NatComms sendout evidence receipt completion validator update"
    next_marker = "### 19.36 NatComms canonical send log v2 overlay update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/natcomms_sendout_evidence_receipt_completion_validator_20260810/`，验证手工发送证据收据是否完整，作为 returned-file/RB-001 intake 前置门。
- 当前 `evidence_rows={summary["evidence_rows"]}`，`filled_evidence_rows={summary["filled_evidence_rows"]}`，`before_send_complete={str(summary["before_send_complete"]).lower()}`，`after_send_complete={str(summary["after_send_complete"]).lower()}`。
- 当前 `send_receipt_complete={str(summary["send_receipt_complete"]).lower()}`，`return_intake_allowed={str(summary["return_intake_allowed"]).lower()}`，`rb001_drop_allowed={str(summary["rb001_drop_allowed"]).lower()}`。
- 当前 `email_sent=false`，`author_replies_collected=false`，`candidate_return_files=0`，`submission_ready=false`。
- 边界：该验证器不发送邮件、不收集回复、不写入返回文件、不写 protected targets、不关闭 gate。
"""
    if marker in text:
        start = text.index(marker)
        following = text.find("\n### ", start + len(marker))
        if following == -1:
            text = text[:start].rstrip()
        else:
            text = text[:start].rstrip() + "\n\n" + text[following:].lstrip("\n")
    if next_marker in text:
        insert_at = text.index(next_marker)
        text = text[:insert_at].rstrip() + block + "\n\n" + text[insert_at:].lstrip("\n")
    else:
        text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    evidence_rows = read_csv(SENDOUT_GUARD_DIR / "sendout_evidence_capture_template.csv")
    v2_audit = read_json(V2_AUDIT_DIR / "sendout_v2_lifecycle_consistency_audit_summary.json")
    log_summary = read_json(LOG_VALIDATOR_DIR / "author_response_log_validator_summary.json")
    post_dispatch_summary = read_json(POST_DISPATCH_DIR / "post_dispatch_evidence_intake_validator_summary.json")
    rb001_summary = read_json(RB001_DASHBOARD_DIR / "rb001_closeout_dashboard_summary.json")

    validation_rows = []
    field_to_row = {row.get("field", ""): row for row in evidence_rows}
    for row in evidence_rows:
        current_value = row.get("current_value", "")
        filled = is_filled(current_value)
        field = row.get("field", "")
        if field in REQUIRED_BEFORE_SEND_FIELDS:
            stage = "before_send"
        elif field in REQUIRED_AFTER_SEND_FIELDS:
            stage = "after_send"
        elif field in REQUIRED_RETURN_FIELDS:
            stage = "return_intake"
        else:
            stage = "unknown"
        validation_rows.append(
            {
                "record_id": row.get("record_id", ""),
                "field": field,
                "stage": stage,
                "when_to_fill": row.get("when_to_fill", ""),
                "current_value_filled": filled,
                "validation_status": "pass" if filled else "missing",
                "issue": "" if filled else "manual_evidence_not_filled",
            }
        )

    before_send_complete = all(
        is_filled(field_to_row.get(field, {}).get("current_value", "")) for field in REQUIRED_BEFORE_SEND_FIELDS
    )
    after_send_complete = all(
        is_filled(field_to_row.get(field, {}).get("current_value", "")) for field in REQUIRED_AFTER_SEND_FIELDS
    )
    return_evidence_complete = all(
        is_filled(field_to_row.get(field, {}).get("current_value", "")) for field in REQUIRED_RETURN_FIELDS
    )
    v2_lifecycle_consistent = (
        v2_audit.get("qa_pass") is True
        and v2_audit.get("stale_v1_reference_rows") == 0
        and v2_audit.get("fingerprint_hashes_match") is True
    )
    log_send_complete = log_summary.get("send_log_valid") is True and log_summary.get("all_sent") is True
    log_return_complete = log_summary.get("return_log_valid") is True and log_summary.get("all_returned") is True
    post_dispatch_complete = post_dispatch_summary.get("evidence_rows_missing") == 0
    rb001_closed = rb001_summary.get("rb001_closed") is True

    send_receipt_complete = before_send_complete and after_send_complete and v2_lifecycle_consistent and log_send_complete
    return_intake_allowed = send_receipt_complete and return_evidence_complete and log_return_complete
    rb001_drop_allowed = return_intake_allowed and post_dispatch_complete

    gate_rows = [
        {
            "gate": "v2_lifecycle_consistent",
            "current": v2_lifecycle_consistent,
            "required": "true",
            "passes_now": "yes" if v2_lifecycle_consistent else "no",
        },
        {
            "gate": "before_send_evidence_complete",
            "current": before_send_complete,
            "required": "true",
            "passes_now": "yes" if before_send_complete else "no",
        },
        {
            "gate": "after_send_evidence_complete",
            "current": after_send_complete,
            "required": "true",
            "passes_now": "yes" if after_send_complete else "no",
        },
        {
            "gate": "response_send_log_complete",
            "current": log_send_complete,
            "required": "true",
            "passes_now": "yes" if log_send_complete else "no",
        },
        {
            "gate": "send_receipt_complete",
            "current": send_receipt_complete,
            "required": "true",
            "passes_now": "yes" if send_receipt_complete else "no",
        },
        {
            "gate": "return_evidence_complete",
            "current": return_evidence_complete,
            "required": "true",
            "passes_now": "yes" if return_evidence_complete else "no",
        },
        {
            "gate": "response_return_log_complete",
            "current": log_return_complete,
            "required": "true",
            "passes_now": "yes" if log_return_complete else "no",
        },
        {
            "gate": "return_intake_allowed",
            "current": return_intake_allowed,
            "required": "true",
            "passes_now": "yes" if return_intake_allowed else "no",
        },
        {
            "gate": "rb001_drop_allowed",
            "current": rb001_drop_allowed,
            "required": "true",
            "passes_now": "yes" if rb001_drop_allowed else "no",
        },
        {
            "gate": "rb001_closed",
            "current": rb001_closed,
            "required": "true",
            "passes_now": "yes" if rb001_closed else "no",
        },
        {
            "gate": "submission_ready",
            "current": False,
            "required": "false",
            "passes_now": "yes",
        },
    ]

    next_action_rows = [
        {
            "order": 1,
            "action": "Before sending, fill recipient_list_confirmed and email_body_boundary_checked in sendout_evidence_capture_template.csv.",
            "allowed_now": "manual_only",
        },
        {
            "order": 2,
            "action": "After real sendout, fill sent_zip_path and sent_datetime_local and update the author response send log.",
            "allowed_now": "after_real_send_only",
        },
        {
            "order": 3,
            "action": "Run build_natcomms_author_response_log_validator.py and this validator again.",
            "allowed_now": "after_real_send_only",
        },
        {
            "order": 4,
            "action": "After returned files exist, fill return tracker and all_returned_files_stored before any intake/writeback.",
            "allowed_now": "after_real_returns_only",
        },
        {
            "order": 5,
            "action": "Do not enter RB-001 drop/writeback until return_intake_allowed=true and post-dispatch evidence passes.",
            "allowed_now": "blocked_now",
        },
    ]

    qa_rows = [
        {
            "check": "evidence rows present",
            "result": "PASS" if len(evidence_rows) == 5 else "FAIL",
            "detail": f"rows={len(evidence_rows)}",
        },
        {
            "check": "v2 lifecycle must already pass",
            "result": "PASS" if v2_lifecycle_consistent else "FAIL",
            "detail": f"status={v2_audit.get('status')}",
        },
        {
            "check": "empty evidence does not grant send receipt",
            "result": "PASS" if not send_receipt_complete else "FAIL",
            "detail": f"filled_rows={sum(1 for row in validation_rows if row['current_value_filled'])}",
        },
        {
            "check": "return intake stays blocked",
            "result": "PASS" if not return_intake_allowed else "FAIL",
            "detail": f"log_return_complete={log_return_complete}",
        },
        {
            "check": "RB-001 drop stays blocked",
            "result": "PASS" if not rb001_drop_allowed and rb001_summary.get("candidate_return_files") == 0 else "FAIL",
            "detail": f"candidate_return_files={rb001_summary.get('candidate_return_files')}",
        },
    ]

    summary = {
        "package": "natcomms_sendout_evidence_receipt_completion_validator_20260810",
        "evidence_rows": len(evidence_rows),
        "filled_evidence_rows": sum(1 for row in validation_rows if row["current_value_filled"]),
        "missing_evidence_rows": sum(1 for row in validation_rows if not row["current_value_filled"]),
        "before_send_complete": before_send_complete,
        "after_send_complete": after_send_complete,
        "return_evidence_complete": return_evidence_complete,
        "v2_lifecycle_consistent": v2_lifecycle_consistent,
        "log_send_complete": log_send_complete,
        "log_return_complete": log_return_complete,
        "send_receipt_complete": send_receipt_complete,
        "return_intake_allowed": return_intake_allowed,
        "rb001_drop_allowed": rb001_drop_allowed,
        "email_sent": False,
        "author_replies_collected": False,
        "candidate_return_files": rb001_summary.get("candidate_return_files", 0),
        "rb001_closed": rb001_closed,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "natcomms_sendout_evidence_receipt_completion_validator_ready_waiting_manual_sendout_evidence",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "sendout_evidence_receipt_completion_validation.csv",
        ["record_id", "field", "stage", "when_to_fill", "current_value_filled", "validation_status", "issue"],
        validation_rows,
    )
    write_csv(
        OUT_DIR / "sendout_evidence_receipt_gate_matrix.csv",
        ["gate", "current", "required", "passes_now"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "sendout_to_rb001_intake_next_actions.csv",
        ["order", "action", "allowed_now"],
        next_action_rows,
    )
    write_csv(
        OUT_DIR / "sendout_evidence_receipt_completion_validator_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Nat Comms Sendout Evidence Receipt Completion Validator

This validator checks whether the manual sendout evidence receipt is complete
enough to permit returned-file intake and later RB-001 drop handling.

Boundary: it does not send email, collect replies, copy returned files, write
protected targets, close gates or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "NATCOMMS_SENDOUT_EVIDENCE_RECEIPT_COMPLETION_VALIDATOR_README.md", readme)

    report = f"""# Nat Comms Sendout Evidence Receipt Completion Validator Report

Status: `{summary["status"]}`

Current result:

1. Evidence rows: {summary["evidence_rows"]}
2. Filled evidence rows: {summary["filled_evidence_rows"]}
3. Missing evidence rows: {summary["missing_evidence_rows"]}
4. Before-send complete: {str(summary["before_send_complete"]).lower()}
5. After-send complete: {str(summary["after_send_complete"]).lower()}
6. Send receipt complete: {str(summary["send_receipt_complete"]).lower()}
7. Return intake allowed: {str(summary["return_intake_allowed"]).lower()}
8. RB-001 drop allowed: {str(summary["rb001_drop_allowed"]).lower()}
9. Candidate return files: {summary["candidate_return_files"]}
10. Submission ready: false

Interpretation: the v2 package is internally consistent, but manual sendout
evidence is not filled. Returned-file intake and RB-001 drop/writeback remain
blocked.
"""
    write_text(OUT_DIR / "sendout_evidence_receipt_completion_validator_report.md", report)
    write_text(
        OUT_DIR / "sendout_evidence_receipt_completion_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("NatComms sendout evidence receipt completion validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
