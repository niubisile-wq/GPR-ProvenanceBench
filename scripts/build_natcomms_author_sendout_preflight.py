#!/usr/bin/env python3
"""Build a preflight package for sending Nat Comms author finalization materials."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_preflight_20260810"

AUTHOR_DIR = BENCH_ROOT / "reports" / "natcomms_author_finalization_reply_packet_20260810"
NEXT_DIR = BENCH_ROOT / "reports" / "natcomms_next_execution_packet_20260810"

AUTHOR_FORM = AUTHOR_DIR / "author_finalization_reply_form_cn.csv"
METADATA_FORM = AUTHOR_DIR / "corresponding_author_metadata_form.csv"
BACKEND_TICKET = AUTHOR_DIR / "figure_backend_decision_ticket.csv"
BRANCH_REPLY = AUTHOR_DIR / "track_branch_and_external_validation_reply.csv"
LICENCE_REPLY = AUTHOR_DIR / "licence_rights_reply_sheet.csv"
REVIEWER_POLICY = AUTHOR_DIR / "reviewer_and_policy_reply_sheet.csv"
REPORTING_REPLY = AUTHOR_DIR / "reporting_summary_author_reply_sheet.csv"
EMAIL_DRAFT = AUTHOR_DIR / "coauthor_finalization_email_cn.md"
OWNER_MATRIX = NEXT_DIR / "owner_packet_distribution_matrix.csv"
STOP_RULES = NEXT_DIR / "next_execution_stop_rules.csv"
RESPONSE_TRACKER_SUMMARY = (
    BENCH_ROOT
    / "reports"
    / "natcomms_author_response_tracker_20260810"
    / "author_response_tracker_summary.json"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def blank_count(rows: list[dict[str, str]], field: str) -> int:
    return sum(1 for row in rows if row.get(field, "").strip() == "")


def read_json_if_exists(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def audit_manual_field(source: str, rows: list[dict[str, str]], field: str) -> dict[str, str]:
    blanks = blank_count(rows, field)
    total = len(rows)
    filled = total - blanks
    if filled == 0:
        status = "pass_blank_ready_before_send"
        next_validator = "not_required_until_sendout"
    else:
        status = "manual_fields_present_requires_response_validator"
        next_validator = "run_natcomms_author_response_log_validator_then_author_reply_ingestion_validator"
    return {
        "source": source,
        "checked_field": field,
        "blank_rows": str(blanks),
        "filled_rows": str(filled),
        "expected_blank_rows_before_send": str(total),
        "status": status,
        "next_validator": next_validator,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    owner_rows = read_csv(OWNER_MATRIX)
    stop_rows = read_csv(STOP_RULES)
    author_rows = read_csv(AUTHOR_FORM)
    metadata_rows = read_csv(METADATA_FORM)
    backend_rows = read_csv(BACKEND_TICKET)
    branch_rows = read_csv(BRANCH_REPLY)
    licence_rows = read_csv(LICENCE_REPLY)
    reviewer_rows = read_csv(REVIEWER_POLICY)
    reporting_rows = read_csv(REPORTING_REPLY)
    email_text = EMAIL_DRAFT.read_text(encoding="utf-8")
    response_tracker_summary = read_json_if_exists(RESPONSE_TRACKER_SUMMARY)
    lifecycle_status = response_tracker_summary.get("status", "no_response_tracker_summary_yet")

    attachment_rows = [
        {"attachment_id": "ATT-001", "file": str(AUTHOR_FORM.relative_to(BENCH_ROOT)), "recipient": "corresponding_author", "purpose": "Core 12-field author finalization replies.", "send_ready": "yes", "must_remain_blank_before_author": "author_reply"},
        {"attachment_id": "ATT-002", "file": str(METADATA_FORM.relative_to(BENCH_ROOT)), "recipient": "corresponding_author", "purpose": "Title page and corresponding-author metadata.", "send_ready": "yes", "must_remain_blank_before_author": "author_reply"},
        {"attachment_id": "ATT-003", "file": str(REVIEWER_POLICY.relative_to(BENCH_ROOT)), "recipient": "corresponding_author", "purpose": "Suggested/excluded reviewers and editorial policy choices.", "send_ready": "yes", "must_remain_blank_before_author": "author_reply"},
        {"attachment_id": "ATT-004", "file": str(BRANCH_REPLY.relative_to(BENCH_ROOT)), "recipient": "author_advisor", "purpose": "Track B confirmation or real external blind validation route.", "send_ready": "yes", "must_remain_blank_before_author": "author_reply"},
        {"attachment_id": "ATT-005", "file": str(BACKEND_TICKET.relative_to(BENCH_ROOT)), "recipient": "author_analysis", "purpose": "Single formal figure backend decision.", "send_ready": "yes", "must_remain_blank_before_author": "current_choice"},
        {"attachment_id": "ATT-006", "file": str(LICENCE_REPLY.relative_to(BENCH_ROOT)), "recipient": "repository_lead", "purpose": "Licence, rights and repository release route.", "send_ready": "yes", "must_remain_blank_before_author": "author_reply"},
        {"attachment_id": "ATT-007", "file": str(REPORTING_REPLY.relative_to(BENCH_ROOT)), "recipient": "analysis_reference_lead", "purpose": "Reporting Summary author confirmations.", "send_ready": "yes", "must_remain_blank_before_author": "author_reply"},
        {"attachment_id": "ATT-008", "file": str(EMAIL_DRAFT.relative_to(BENCH_ROOT)), "recipient": "corresponding_author", "purpose": "Chinese email body for collecting finalization replies.", "send_ready": "yes", "must_remain_blank_before_author": "not_applicable"},
    ]
    for row in attachment_rows:
        row["exists"] = "yes" if (BENCH_ROOT / row["file"]).exists() else "no"
    write_csv(
        OUT_DIR / "author_sendout_attachment_manifest.csv",
        attachment_rows,
        ["attachment_id", "file", "recipient", "purpose", "exists", "send_ready", "must_remain_blank_before_author"],
    )

    blank_audit_rows = [
        audit_manual_field("author_finalization_reply_form_cn.csv", author_rows, "author_reply"),
        audit_manual_field("corresponding_author_metadata_form.csv", metadata_rows, "author_reply"),
        audit_manual_field("figure_backend_decision_ticket.csv", backend_rows, "current_choice"),
        audit_manual_field("track_branch_and_external_validation_reply.csv", branch_rows, "author_reply"),
        audit_manual_field("licence_rights_reply_sheet.csv", licence_rows, "author_reply"),
        audit_manual_field("reviewer_and_policy_reply_sheet.csv", reviewer_rows, "author_reply"),
        audit_manual_field("reporting_summary_author_reply_sheet.csv", reporting_rows, "author_reply"),
    ]
    write_csv(
        OUT_DIR / "author_sendout_blank_field_audit.csv",
        blank_audit_rows,
        [
            "source",
            "checked_field",
            "blank_rows",
            "filled_rows",
            "expected_blank_rows_before_send",
            "status",
            "next_validator",
        ],
    )

    email_checks = [
        {"check_id": "EMAIL-001", "check": "Mentions submission-prelock status", "result": "PASS" if "submission-prelock" in email_text else "FAIL"},
        {"check_id": "EMAIL-002", "check": "Mentions Track B or external blind data holder", "result": "PASS" if "Track B" in email_text and "盲外部" in email_text else "FAIL"},
        {"check_id": "EMAIL-003", "check": "Mentions Python or R backend choice", "result": "PASS" if "Python" in email_text and "R" in email_text else "FAIL"},
        {"check_id": "EMAIL-004", "check": "Mentions licence/rights", "result": "PASS" if "licence/rights" in email_text else "FAIL"},
        {"check_id": "EMAIL-005", "check": "States not author approval or final completion", "result": "PASS" if "不代表作者已经同意投稿" in email_text and "不代表 figures" in email_text else "FAIL"},
    ]
    write_csv(OUT_DIR / "author_sendout_email_consistency_check.csv", email_checks, ["check_id", "check", "result"])

    pre_send_rows = [
        {"step": "1", "action": "Attach the eight files in author_sendout_attachment_manifest.csv.", "owner": "sender", "status": "ready_to_send_not_sent"},
        {"step": "2", "action": "Ask recipients to fill only author_reply/current_choice fields; do not edit recommendation or evidence columns.", "owner": "sender", "status": "ready_to_send_not_sent"},
        {"step": "3", "action": "After replies return, rerun author reply ingestion validator.", "owner": "analysis", "status": "waiting_replies"},
        {"step": "4", "action": "Then rerun gate closure evidence binder and finalization command dashboard v3.", "owner": "analysis", "status": "waiting_replies"},
        {"step": "5", "action": "Only after backend is explicitly selected may formal figure rendering be started.", "owner": "analysis", "status": "blocked_backend_unselected"},
    ]
    write_csv(OUT_DIR / "author_sendout_pre_send_checklist.csv", pre_send_rows, ["step", "action", "owner", "status"])

    sendout_email = [
        "# 作者最终确认材料发送稿",
        "",
        email_text,
        "",
        "## 附件清单",
        "",
    ]
    for row in attachment_rows:
        sendout_email.append(f"- {row['file']}: {row['purpose']}")
    sendout_email.extend(
        [
            "",
            "## 回复后验收",
            "",
            "收到回复后，先运行 author reply ingestion validator，再运行 gate closure evidence binder 和 finalization command dashboard v3。任何空白回复、未选择 backend、未完成 DOI/rights 或未完成 Reporting Summary/reference/final-file 证据，都继续视为 open gate。",
            "",
        ]
    )
    (OUT_DIR / "author_sendout_email_ready_draft_cn.md").write_text("\n".join(sendout_email), encoding="utf-8")

    qa_rows = [
        {"check": "Attachment manifest complete", "result": "PASS" if len(attachment_rows) == 8 and all(row["exists"] == "yes" for row in attachment_rows) else "FAIL", "detail": f"{len(attachment_rows)} attachments."},
        {"check": "Manual fields audited without overwrite", "result": "PASS", "detail": f"{sum(int(row['filled_rows']) for row in blank_audit_rows)} filled manual fields; lifecycle={lifecycle_status}."},
        {"check": "Email consistency", "result": "PASS" if all(row["result"] == "PASS" for row in email_checks) else "FAIL", "detail": f"{sum(1 for row in email_checks if row['result'] == 'FAIL')} email check failures."},
        {"check": "Owner matrix imported", "result": "PASS" if len(owner_rows) == 5 else "FAIL", "detail": f"{len(owner_rows)} owner rows."},
        {"check": "Stop rules imported", "result": "PASS" if len(stop_rows) == 5 else "FAIL", "detail": f"{len(stop_rows)} stop rules."},
    ]
    write_csv(OUT_DIR / "author_sendout_preflight_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = [
        "# Nat Comms author sendout preflight",
        "",
        "Purpose: verify that author finalization materials are ready to be sent for replies.",
        "",
        "Boundary: this package does not send email, collect replies, select a backend, render figures, create DOI records or make the submission ready.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_AUTHOR_SENDOUT_PREFLIGHT_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Author sendout preflight report",
        "",
        f"- Attachments: {len(attachment_rows)}",
        f"- Blank-audit sources: {len(blank_audit_rows)}",
        f"- Filled manual fields: {sum(int(row['filled_rows']) for row in blank_audit_rows)}",
        f"- Response lifecycle status: {lifecycle_status}",
        f"- Email consistency checks: {len(email_checks)}",
        f"- Pre-send checklist rows: {len(pre_send_rows)}",
        f"- Owner matrix rows imported: {len(owner_rows)}",
        f"- Stop rules imported: {len(stop_rows)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_author_sendout_preflight_ready_not_sent",
        "",
    ]
    (OUT_DIR / "author_sendout_preflight_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_author_sendout_preflight",
        "attachments": len(attachment_rows),
        "send_ready_attachments": sum(1 for row in attachment_rows if row["send_ready"] == "yes" and row["exists"] == "yes"),
        "blank_audit_sources": len(blank_audit_rows),
        "filled_manual_fields": sum(int(row["filled_rows"]) for row in blank_audit_rows),
        "response_lifecycle_status": lifecycle_status,
        "email_consistency_checks": len(email_checks),
        "pre_send_checklist_rows": len(pre_send_rows),
        "owner_matrix_rows_imported": len(owner_rows),
        "stop_rules_imported": len(stop_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "email_sent": False,
        "author_replies_collected": False,
        "backend_selected": False,
        "submission_ready": False,
        "status": "natcomms_author_sendout_preflight_ready_not_sent",
        "boundary": "Sendout preflight verifies ready-to-send materials only; it does not send, collect replies, close gates or make submission ready.",
    }
    (OUT_DIR / "author_sendout_preflight_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
