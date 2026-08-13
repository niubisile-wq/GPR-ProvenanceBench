#!/usr/bin/env python3
"""Build a manual author-response tracker for the Nat Comms sendout bundle."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
BUNDLE_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_20260810"
BUNDLE_MANIFEST = BUNDLE_DIR / "author_sendout_bundle_manifest.csv"
RECIPIENT_ROUTE = BUNDLE_DIR / "author_sendout_recipient_route.csv"
BUNDLE_ZIP = BUNDLE_DIR / "NatComms_author_sendout_bundle_20260810.zip"


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def index_rows(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key, "")}


def expected_reply_field(bundle_file: str) -> str:
    name = Path(bundle_file).name
    if name == "author_finalization_reply_form_cn.csv":
        return "author_reply"
    if name == "corresponding_author_metadata_form.csv":
        return "current_value_or_confirmed_value"
    if name == "figure_backend_decision_ticket.csv":
        return "current_choice"
    if name == "track_branch_and_external_validation_reply.csv":
        return "current_choice"
    if name == "licence_rights_reply_sheet.csv":
        return "current_choice"
    if name == "reviewer_and_policy_reply_sheet.csv":
        return "current_choice"
    if name == "reporting_summary_author_reply_sheet.csv":
        return "current_choice"
    return "not_applicable"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = read_csv(BUNDLE_MANIFEST)
    route = read_csv(RECIPIENT_ROUTE)
    bundle_sha = sha256(BUNDLE_ZIP)
    existing_send_rows = []
    existing_return_rows = []
    send_log_path = OUT_DIR / "author_response_send_log_template.csv"
    return_tracker_path = OUT_DIR / "author_response_return_tracker.csv"
    if send_log_path.exists():
        existing_send_rows = read_csv(send_log_path)
    if return_tracker_path.exists():
        existing_return_rows = read_csv(return_tracker_path)
    existing_send_by_recipient = index_rows(existing_send_rows, "recipient")
    existing_return_by_attachment = index_rows(existing_return_rows, "attachment_id")

    recipients = sorted({row["recipient"] for row in route})
    send_log_rows = [
        {
            "recipient": recipient,
            "send_status": existing_send_by_recipient.get(recipient, {}).get("send_status", "not_sent") or "not_sent",
            "sent_datetime_local": existing_send_by_recipient.get(recipient, {}).get("sent_datetime_local", ""),
            "sender": existing_send_by_recipient.get(recipient, {}).get("sender", ""),
            "bundle_zip": str(BUNDLE_ZIP.relative_to(BENCH_ROOT)),
            "bundle_zip_sha256": bundle_sha,
            "required_manual_action": "Send the zip outside this script and fill sent_datetime_local only after real sendout.",
            "notes": existing_send_by_recipient.get(recipient, {}).get("notes", ""),
        }
        for recipient in recipients
    ]

    return_tracker_rows = [
        {
            "attachment_id": row["attachment_id"],
            "recipient": row["recipient"],
            "bundle_file": row["bundle_file"],
            "expected_reply_field": expected_reply_field(row["bundle_file"]),
            "return_status": existing_return_by_attachment.get(row["attachment_id"], {}).get("return_status", "not_returned")
            or "not_returned",
            "returned_file_path": existing_return_by_attachment.get(row["attachment_id"], {}).get("returned_file_path", ""),
            "returned_datetime_local": existing_return_by_attachment.get(row["attachment_id"], {}).get(
                "returned_datetime_local", ""
            ),
            "post_return_validation": existing_return_by_attachment.get(row["attachment_id"], {}).get(
                "post_return_validation", "pending_real_return"
            )
            or "pending_real_return",
            "gate_effect": "no_gate_closure_until_ingestion_validator_and_evidence_binder_pass",
        }
        for row in manifest
    ]

    validation_plan_rows = [
        {
            "step_id": "VAL-001",
            "trigger": "after_returned_files_are_filled",
            "command_or_review": r"py scripts\build_natcomms_author_reply_ingestion_validator.py",
            "acceptance_rule": "author replies are non-blank where required; gate_closure_allowed may only change if evidence rules pass.",
            "current_status": "waiting_for_manual_replies",
        },
        {
            "step_id": "VAL-002",
            "trigger": "after_VAL-001_passes",
            "command_or_review": r"py scripts\build_natcomms_gate_closure_evidence_binder.py",
            "acceptance_rule": "all gate evidence requirements have concrete author and artifact evidence.",
            "current_status": "blocked_by_VAL-001",
        },
        {
            "step_id": "VAL-003",
            "trigger": "after_VAL-002_passes",
            "command_or_review": r"py scripts\build_natcomms_finalization_command_dashboard_v3.py",
            "acceptance_rule": "dashboard commands change only when upstream evidence is present.",
            "current_status": "blocked_by_VAL-002",
        },
        {
            "step_id": "VAL-004",
            "trigger": "after_dashboard_refresh",
            "command_or_review": r"& scripts\run_m0_m2_checks.ps1",
            "acceptance_rule": "full run prints M0-M2 checks completed and all required artifacts exist.",
            "current_status": "blocked_by_VAL-003",
        },
        {
            "step_id": "VAL-005",
            "trigger": "after_full_checks_pass",
            "command_or_review": "manual gate review by corresponding author and analyst",
            "acceptance_rule": "no submission-ready flag is changed without explicit evidence and final artifact review.",
            "current_status": "blocked_by_VAL-004",
        },
    ]

    post_reply_commands = [
        {
            "order": 1,
            "command": r"py scripts\build_natcomms_author_reply_ingestion_validator.py",
            "purpose": "Ingest filled author reply sheets after manual return.",
            "run_now": "no",
        },
        {
            "order": 2,
            "command": r"py scripts\build_natcomms_gate_closure_evidence_binder.py",
            "purpose": "Rebind gate closure evidence after ingestion.",
            "run_now": "no",
        },
        {
            "order": 3,
            "command": r"py scripts\build_natcomms_finalization_command_dashboard_v3.py",
            "purpose": "Refresh command dashboard after evidence binder update.",
            "run_now": "no",
        },
        {
            "order": 4,
            "command": r"& scripts\run_m0_m2_checks.ps1",
            "purpose": "Run full artifact and boundary checks.",
            "run_now": "no",
        },
    ]

    stop_rules = [
        {
            "rule_id": "STOP-001",
            "rule": "Do not mark email_sent=true until a human records a real send timestamp and sender.",
        },
        {
            "rule_id": "STOP-002",
            "rule": "Do not mark any attachment returned until the filled file path and return timestamp are recorded.",
        },
        {
            "rule_id": "STOP-003",
            "rule": "Do not infer a figure backend from recommendations; require explicit author choice.",
        },
        {
            "rule_id": "STOP-004",
            "rule": "Do not close a gate from replies alone; require matching artifact evidence and validator pass.",
        },
        {
            "rule_id": "STOP-005",
            "rule": "Do not assemble, upload or submit until full checks pass and submission_ready is explicitly true.",
        },
    ]

    valid_send_statuses = {"not_sent", "sent"}
    valid_return_statuses = {"not_returned", "returned"}
    sent_rows_missing_metadata = [
        row["recipient"]
        for row in send_log_rows
        if row["send_status"] == "sent" and (not row["sent_datetime_local"] or not row["sender"])
    ]
    returned_rows_missing_metadata = [
        row["attachment_id"]
        for row in return_tracker_rows
        if row["return_status"] == "returned" and (not row["returned_file_path"] or not row["returned_datetime_local"])
    ]

    qa_rows = [
        {
            "check_id": "QA-001",
            "check": "all bundle attachments represented in return tracker",
            "observed": len(return_tracker_rows),
            "expected": len(manifest),
            "pass": len(return_tracker_rows) == len(manifest),
        },
        {
            "check_id": "QA-002",
            "check": "send statuses are controlled values and sent rows have sender/timestamp",
            "observed": sorted({row["send_status"] for row in send_log_rows}),
            "expected": "not_sent or sent, with metadata when sent",
            "pass": all(row["send_status"] in valid_send_statuses for row in send_log_rows)
            and not sent_rows_missing_metadata,
        },
        {
            "check_id": "QA-003",
            "check": "return statuses are controlled values and returned rows have file/timestamp",
            "observed": sorted({row["return_status"] for row in return_tracker_rows}),
            "expected": "not_returned or returned, with metadata when returned",
            "pass": all(row["return_status"] in valid_return_statuses for row in return_tracker_rows)
            and not returned_rows_missing_metadata,
        },
        {
            "check_id": "QA-004",
            "check": "post-reply commands are disabled before replies arrive",
            "observed": sorted({row["run_now"] for row in post_reply_commands}),
            "expected": "['no']",
            "pass": sorted({row["run_now"] for row in post_reply_commands}) == ["no"],
        },
        {
            "check_id": "QA-005",
            "check": "submission boundary flags remain false",
            "observed": "backend_selected=false; submission_ready=false",
            "expected": "backend_selected and submission_ready stay false in this script",
            "pass": True,
        },
    ]

    summary = {
        "package": "natcomms_author_response_tracker_20260810",
        "send_log_rows": len(send_log_rows),
        "return_tracker_rows": len(return_tracker_rows),
        "validation_plan_rows": len(validation_plan_rows),
        "post_reply_rerun_commands": len(post_reply_commands),
        "stop_rules": len(stop_rules),
        "bundle_zip_sha256": bundle_sha,
        "qa_pass": all(bool(row["pass"]) for row in qa_rows),
        "email_sent": all(row["send_status"] == "sent" for row in send_log_rows),
        "all_replies_received": all(row["return_status"] == "returned" for row in return_tracker_rows),
        "author_replies_collected": all(row["return_status"] == "returned" for row in return_tracker_rows),
        "backend_selected": False,
        "submission_ready": False,
        "status": "natcomms_author_response_tracker_ready_waiting_manual_sendout",
    }
    if summary["email_sent"] and not summary["author_replies_collected"]:
        summary["status"] = "natcomms_author_response_tracker_sent_waiting_replies"
    if summary["email_sent"] and summary["author_replies_collected"]:
        summary["status"] = "natcomms_author_response_tracker_replies_logged_waiting_validation"

    write_csv(
        send_log_path,
        [
            "recipient",
            "send_status",
            "sent_datetime_local",
            "sender",
            "bundle_zip",
            "bundle_zip_sha256",
            "required_manual_action",
            "notes",
        ],
        send_log_rows,
    )
    write_csv(
        return_tracker_path,
        [
            "attachment_id",
            "recipient",
            "bundle_file",
            "expected_reply_field",
            "return_status",
            "returned_file_path",
            "returned_datetime_local",
            "post_return_validation",
            "gate_effect",
        ],
        return_tracker_rows,
    )
    write_csv(
        OUT_DIR / "returned_attachment_validation_plan.csv",
        ["step_id", "trigger", "command_or_review", "acceptance_rule", "current_status"],
        validation_plan_rows,
    )
    write_csv(
        OUT_DIR / "post_reply_rerun_command_queue.csv",
        ["order", "command", "purpose", "run_now"],
        post_reply_commands,
    )
    write_csv(OUT_DIR / "author_response_tracker_stop_rules.csv", ["rule_id", "rule"], stop_rules)
    write_csv(
        OUT_DIR / "author_response_tracker_qa.csv",
        ["check_id", "check", "observed", "expected", "pass"],
        qa_rows,
    )

    readme = """# Nat Comms Author Response Tracker

This package tracks manual sendout and reply collection after the author sendout
bundle is created.

Current boundary:

1. The email has not been sent by this script.
2. No author replies have been collected by this script.
3. No figure backend has been selected by this script.
4. No final gate is closed by this script.
5. Submission remains not ready.

Use `author_response_send_log_template.csv` only after a real human sendout.
Use `author_response_return_tracker.csv` only after filled files are returned.
Then rerun the ingestion validator, gate binder, command dashboard and full
checks in the order listed in `post_reply_rerun_command_queue.csv`.
"""
    write_text(OUT_DIR / "AUTHOR_RESPONSE_TRACKER_README.md", readme)

    report = f"""# Nat Comms Author Response Tracker Report

Status: `{summary["status"]}`

Generated rows:

1. Send log rows: {summary["send_log_rows"]}
2. Return tracker rows: {summary["return_tracker_rows"]}
3. Validation plan rows: {summary["validation_plan_rows"]}
4. Post-reply rerun commands: {summary["post_reply_rerun_commands"]}
5. Stop rules: {summary["stop_rules"]}

Boundary flags:

1. `email_sent={str(summary["email_sent"]).lower()}`
2. `author_replies_collected={str(summary["author_replies_collected"]).lower()}`
3. `backend_selected=false`
4. `submission_ready=false`

Interpretation: the sendout bundle is packaged, but the manual send/reply cycle
is controlled by explicit send timestamps and returned-file paths. All
downstream gates must remain blocked until real returned files are logged and
validators pass.
"""
    write_text(OUT_DIR / "author_response_tracker_report.md", report)
    write_text(
        OUT_DIR / "author_response_tracker_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("Author response tracker QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
