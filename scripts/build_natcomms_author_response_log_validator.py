#!/usr/bin/env python3
"""Validate the manual Nat Comms author send/reply tracker state."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_log_validator_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    send_rows = read_csv(TRACKER_DIR / "author_response_send_log_template.csv")
    return_rows = read_csv(TRACKER_DIR / "author_response_return_tracker.csv")

    send_validation_rows = []
    for row in send_rows:
        status = row.get("send_status", "")
        sent_ok = status == "sent" and bool(row.get("sent_datetime_local")) and bool(row.get("sender"))
        not_sent_ok = status == "not_sent" and not row.get("sent_datetime_local") and not row.get("sender")
        issue = ""
        if status not in {"not_sent", "sent"}:
            issue = "invalid_send_status"
        elif status == "sent" and not sent_ok:
            issue = "sent_requires_sender_and_sent_datetime_local"
        elif status == "not_sent" and not not_sent_ok:
            issue = "not_sent_rows_should_not_have_sender_or_timestamp"
        send_validation_rows.append(
            {
                "recipient": row.get("recipient", ""),
                "send_status": status,
                "sent_datetime_local": row.get("sent_datetime_local", ""),
                "sender": row.get("sender", ""),
                "validation_status": "pass" if not issue else "fail",
                "issue": issue,
            }
        )

    return_validation_rows = []
    for row in return_rows:
        status = row.get("return_status", "")
        returned_ok = (
            status == "returned"
            and bool(row.get("returned_file_path"))
            and bool(row.get("returned_datetime_local"))
        )
        not_returned_ok = status == "not_returned" and not row.get("returned_file_path")
        issue = ""
        if status not in {"not_returned", "returned"}:
            issue = "invalid_return_status"
        elif status == "returned" and not returned_ok:
            issue = "returned_requires_file_path_and_returned_datetime_local"
        elif status == "not_returned" and not not_returned_ok:
            issue = "not_returned_rows_should_not_have_returned_file_path"
        return_validation_rows.append(
            {
                "attachment_id": row.get("attachment_id", ""),
                "recipient": row.get("recipient", ""),
                "return_status": status,
                "returned_file_path": row.get("returned_file_path", ""),
                "returned_datetime_local": row.get("returned_datetime_local", ""),
                "validation_status": "pass" if not issue else "fail",
                "issue": issue,
            }
        )

    send_log_valid = all(row["validation_status"] == "pass" for row in send_validation_rows)
    return_log_valid = all(row["validation_status"] == "pass" for row in return_validation_rows)
    all_sent = all(row["send_status"] == "sent" for row in send_validation_rows)
    all_returned = all(row["return_status"] == "returned" for row in return_validation_rows)

    gate_rows = [
        {
            "gate": "manual_sendout_recorded",
            "decision": "pass" if send_log_valid and all_sent else "blocked",
            "evidence": "all recipients must have send_status=sent plus sender and sent_datetime_local",
        },
        {
            "gate": "manual_replies_recorded",
            "decision": "pass" if return_log_valid and all_returned else "blocked",
            "evidence": "all attachments must have return_status=returned plus returned_file_path and returned_datetime_local",
        },
        {
            "gate": "author_reply_ingestion_allowed",
            "decision": "pass" if send_log_valid and return_log_valid and all_sent and all_returned else "blocked",
            "evidence": "ingestion is allowed only after send and return logs are complete",
        },
        {
            "gate": "figure_backend_decision_allowed",
            "decision": "blocked",
            "evidence": "backend selection still requires explicit author choice and separate figure workflow",
        },
        {
            "gate": "submission_ready",
            "decision": "blocked",
            "evidence": "validator cannot make submission ready",
        },
    ]

    qa_rows = [
        {
            "check_id": "QA-001",
            "check": "send log rows present",
            "observed": len(send_rows),
            "expected": ">=1",
            "pass": len(send_rows) >= 1,
        },
        {
            "check_id": "QA-002",
            "check": "return log rows present",
            "observed": len(return_rows),
            "expected": ">=1",
            "pass": len(return_rows) >= 1,
        },
        {
            "check_id": "QA-003",
            "check": "send log schema/status valid",
            "observed": send_log_valid,
            "expected": True,
            "pass": send_log_valid,
        },
        {
            "check_id": "QA-004",
            "check": "return log schema/status valid",
            "observed": return_log_valid,
            "expected": True,
            "pass": return_log_valid,
        },
        {
            "check_id": "QA-005",
            "check": "submission remains blocked by validator",
            "observed": [row["decision"] for row in gate_rows if row["gate"] == "submission_ready"][0],
            "expected": "blocked",
            "pass": True,
        },
    ]

    summary = {
        "package": "natcomms_author_response_log_validator_20260810",
        "send_rows_validated": len(send_validation_rows),
        "return_rows_validated": len(return_validation_rows),
        "send_log_valid": send_log_valid,
        "return_log_valid": return_log_valid,
        "all_sent": all_sent,
        "all_returned": all_returned,
        "author_reply_ingestion_allowed": send_log_valid and return_log_valid and all_sent and all_returned,
        "backend_selected": False,
        "submission_ready": False,
        "qa_pass": all(bool(row["pass"]) for row in qa_rows),
        "status": "natcomms_author_response_log_validator_ready_waiting_manual_sendout",
    }
    if all_sent and not all_returned:
        summary["status"] = "natcomms_author_response_log_validator_sent_waiting_returns"
    if all_sent and all_returned:
        summary["status"] = "natcomms_author_response_log_validator_returns_ready_for_ingestion"

    write_csv(
        OUT_DIR / "author_response_send_log_validation.csv",
        ["recipient", "send_status", "sent_datetime_local", "sender", "validation_status", "issue"],
        send_validation_rows,
    )
    write_csv(
        OUT_DIR / "author_response_return_log_validation.csv",
        [
            "attachment_id",
            "recipient",
            "return_status",
            "returned_file_path",
            "returned_datetime_local",
            "validation_status",
            "issue",
        ],
        return_validation_rows,
    )
    write_csv(
        OUT_DIR / "author_response_lifecycle_gate_decision.csv",
        ["gate", "decision", "evidence"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "author_response_log_validator_qa.csv",
        ["check_id", "check", "observed", "expected", "pass"],
        qa_rows,
    )

    readme = """# Nat Comms Author Response Log Validator

This package validates the manual send and returned-file ledger generated by the
author response tracker.

It does not send email, edit returned files, ingest author replies, select a
figure backend, close finalization gates or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "AUTHOR_RESPONSE_LOG_VALIDATOR_README.md", readme)

    report = f"""# Nat Comms Author Response Log Validator Report

Status: `{summary["status"]}`

Validated rows:

1. Send rows: {summary["send_rows_validated"]}
2. Return rows: {summary["return_rows_validated"]}
3. Send log valid: {str(summary["send_log_valid"]).lower()}
4. Return log valid: {str(summary["return_log_valid"]).lower()}
5. All sent: {str(summary["all_sent"]).lower()}
6. All returned: {str(summary["all_returned"]).lower()}
7. Author reply ingestion allowed: {str(summary["author_reply_ingestion_allowed"]).lower()}
8. Submission ready: false

Interpretation: this validator is the bridge between manual send/reply tracking
and automated reply ingestion. In the current state, downstream ingestion remains
blocked unless all send and return records are explicitly completed.
"""
    write_text(OUT_DIR / "author_response_log_validator_report.md", report)
    write_text(
        OUT_DIR / "author_response_log_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("Author response log validator QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
