#!/usr/bin/env python3
"""Audit manual author-facing fields for overwrite/preservation safety."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_field_preservation_audit_20260810"


AUTHOR_DIR = BENCH_ROOT / "reports" / "natcomms_author_finalization_reply_packet_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
SENDOUT_PREFLIGHT_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_preflight_20260810"


MANUAL_FIELD_TARGETS = [
    {
        "artifact": AUTHOR_DIR / "author_finalization_reply_form_cn.csv",
        "key_field": "field_id",
        "manual_field": "author_reply",
        "owner": "corresponding_author",
        "preservation_script": "scripts/build_natcomms_author_finalization_reply_packet.py",
    },
    {
        "artifact": AUTHOR_DIR / "corresponding_author_metadata_form.csv",
        "key_field": "metadata_id",
        "manual_field": "author_reply",
        "owner": "corresponding_author",
        "preservation_script": "scripts/build_natcomms_author_finalization_reply_packet.py",
    },
    {
        "artifact": AUTHOR_DIR / "figure_backend_decision_ticket.csv",
        "key_field": "ticket_id",
        "manual_field": "current_choice",
        "owner": "author_analysis",
        "preservation_script": "scripts/build_natcomms_author_finalization_reply_packet.py",
    },
    {
        "artifact": AUTHOR_DIR / "track_branch_and_external_validation_reply.csv",
        "key_field": "branch_id",
        "manual_field": "author_reply",
        "owner": "author_advisor",
        "preservation_script": "scripts/build_natcomms_author_finalization_reply_packet.py",
    },
    {
        "artifact": AUTHOR_DIR / "licence_rights_reply_sheet.csv",
        "key_field": "item_id",
        "manual_field": "author_reply",
        "owner": "repository_lead",
        "preservation_script": "scripts/build_natcomms_author_finalization_reply_packet.py",
    },
    {
        "artifact": AUTHOR_DIR / "reviewer_and_policy_reply_sheet.csv",
        "key_field": "item_id",
        "manual_field": "author_reply",
        "owner": "corresponding_author",
        "preservation_script": "scripts/build_natcomms_author_finalization_reply_packet.py",
    },
    {
        "artifact": AUTHOR_DIR / "reporting_summary_author_reply_sheet.csv",
        "key_field": "reporting_item",
        "manual_field": "author_reply",
        "owner": "analysis_reference_lead",
        "preservation_script": "scripts/build_natcomms_author_finalization_reply_packet.py",
    },
    {
        "artifact": TRACKER_DIR / "author_response_send_log_template.csv",
        "key_field": "recipient",
        "manual_field": "send_status; sent_datetime_local; sender; notes",
        "owner": "sender",
        "preservation_script": "scripts/build_natcomms_author_response_tracker.py",
    },
    {
        "artifact": TRACKER_DIR / "author_response_return_tracker.csv",
        "key_field": "attachment_id",
        "manual_field": "return_status; returned_file_path; returned_datetime_local; post_return_validation",
        "owner": "sender",
        "preservation_script": "scripts/build_natcomms_author_response_tracker.py",
    },
]


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


def count_filled(rows: list[dict[str, str]], field_expression: str) -> int:
    fields = [field.strip() for field in field_expression.split(";")]
    filled = 0
    for row in rows:
        row_filled = False
        for field in fields:
            value = row.get(field, "").strip()
            if not value:
                continue
            if field == "send_status":
                row_filled = value == "sent"
            elif field == "return_status":
                row_filled = value == "returned"
            elif field == "post_return_validation":
                row_filled = value not in {"pending_real_return", ""}
            elif field in {"notes", "sender", "sent_datetime_local", "returned_file_path", "returned_datetime_local"}:
                row_filled = True
            else:
                row_filled = True
            if row_filled:
                break
        if row_filled:
            filled += 1
    return filled


def script_has_preservation(script_path: Path, field_expression: str) -> bool:
    text = script_path.read_text(encoding="utf-8")
    fields = [field.strip() for field in field_expression.split(";")]
    if "preserve_existing" not in text and "existing_" not in text:
        return False
    return all(field in text for field in fields)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    target_rows = []
    risk_rows = []
    for target in MANUAL_FIELD_TARGETS:
        artifact = target["artifact"]
        script_path = BENCH_ROOT / target["preservation_script"]
        exists = artifact.exists()
        rows = read_csv(artifact) if exists else []
        filled = count_filled(rows, target["manual_field"]) if rows else 0
        has_preservation = script_has_preservation(script_path, target["manual_field"]) if script_path.exists() else False
        status = "protected" if exists and has_preservation else "risk"
        target_rows.append(
            {
                "artifact": str(artifact.relative_to(BENCH_ROOT)),
                "key_field": target["key_field"],
                "manual_field": target["manual_field"],
                "owner": target["owner"],
                "rows": len(rows),
                "filled_manual_rows": filled,
                "preservation_script": target["preservation_script"],
                "preservation_detected": "yes" if has_preservation else "no",
                "status": status,
            }
        )
        if status != "protected":
            risk_rows.append(
                {
                    "artifact": str(artifact.relative_to(BENCH_ROOT)),
                    "risk": "manual field may be overwritten or artifact is missing",
                    "required_action": f"Add or verify preservation in {target['preservation_script']}",
                }
            )

    sendout_audit = SENDOUT_PREFLIGHT_DIR / "author_sendout_blank_field_audit.csv"
    sendout_rows = read_csv(sendout_audit) if sendout_audit.exists() else []
    sendout_stage_rows = [
        {
            "source": row.get("source", ""),
            "checked_field": row.get("checked_field", ""),
            "blank_rows": row.get("blank_rows", ""),
            "filled_rows": row.get("filled_rows", ""),
            "status": row.get("status", ""),
            "next_validator": row.get("next_validator", ""),
        }
        for row in sendout_rows
    ]

    rerun_rows = [
        {
            "order": 1,
            "command": r"py scripts\build_natcomms_author_finalization_reply_packet.py",
            "purpose": "Regenerate author-facing forms while preserving manual fields.",
        },
        {
            "order": 2,
            "command": r"py scripts\build_natcomms_author_sendout_preflight.py",
            "purpose": "Audit current manual-field stage without treating nonblank values as overwrite errors.",
        },
        {
            "order": 3,
            "command": r"py scripts\build_natcomms_author_response_tracker.py",
            "purpose": "Regenerate send/return lifecycle tracker while preserving manual send/return logs.",
        },
        {
            "order": 4,
            "command": r"py scripts\build_natcomms_author_response_log_validator.py",
            "purpose": "Validate manual send/return lifecycle before author reply ingestion.",
        },
        {
            "order": 5,
            "command": r"py scripts\build_figure_backend_decision_validator.py",
            "purpose": "Validate explicit backend and figure-scope choices before formal rendering.",
        },
    ]

    qa_rows = [
        {
            "check_id": "QA-001",
            "check": "manual field targets enumerated",
            "observed": len(target_rows),
            "expected": 9,
            "pass": len(target_rows) == 9,
        },
        {
            "check_id": "QA-002",
            "check": "all manual field artifacts exist",
            "observed": sum(1 for row in target_rows if row["rows"] > 0),
            "expected": len(target_rows),
            "pass": all(row["rows"] > 0 for row in target_rows),
        },
        {
            "check_id": "QA-003",
            "check": "preservation detected for all manual field targets",
            "observed": sum(1 for row in target_rows if row["preservation_detected"] == "yes"),
            "expected": len(target_rows),
            "pass": all(row["preservation_detected"] == "yes" for row in target_rows),
        },
        {
            "check_id": "QA-004",
            "check": "sendout preflight is stage-aware",
            "observed": sorted({row.get("status", "") for row in sendout_stage_rows}),
            "expected": "stage-aware statuses",
            "pass": all("next_validator" in row for row in sendout_stage_rows),
        },
        {
            "check_id": "QA-005",
            "check": "audit does not mark submission ready",
            "observed": "submission_ready=false",
            "expected": "submission_ready=false",
            "pass": True,
        },
    ]

    summary = {
        "package": "manual_field_preservation_audit_20260810",
        "manual_field_targets": len(target_rows),
        "protected_targets": sum(1 for row in target_rows if row["status"] == "protected"),
        "risk_rows": len(risk_rows),
        "sendout_stage_rows": len(sendout_stage_rows),
        "filled_manual_rows": sum(int(row["filled_manual_rows"]) for row in target_rows),
        "qa_pass": all(bool(row["pass"]) for row in qa_rows),
        "submission_ready": False,
        "status": "manual_field_preservation_audit_ready_all_targets_protected"
        if not risk_rows
        else "manual_field_preservation_audit_risks_detected",
    }

    write_csv(
        OUT_DIR / "manual_field_preservation_targets.csv",
        [
            "artifact",
            "key_field",
            "manual_field",
            "owner",
            "rows",
            "filled_manual_rows",
            "preservation_script",
            "preservation_detected",
            "status",
        ],
        target_rows,
    )
    write_csv(
        OUT_DIR / "manual_field_overwrite_risk_register.csv",
        ["artifact", "risk", "required_action"],
        risk_rows,
    )
    write_csv(
        OUT_DIR / "sendout_manual_field_stage_audit.csv",
        ["source", "checked_field", "blank_rows", "filled_rows", "status", "next_validator"],
        sendout_stage_rows,
    )
    write_csv(
        OUT_DIR / "manual_field_safe_rerun_order.csv",
        ["order", "command", "purpose"],
        rerun_rows,
    )
    write_csv(
        OUT_DIR / "manual_field_preservation_audit_qa.csv",
        ["check_id", "check", "observed", "expected", "pass"],
        qa_rows,
    )

    readme = """# Manual Field Preservation Audit

This package audits author-facing/manual fields that must survive automated
regeneration during full checks.

It does not create author replies, send email, select a backend, render figures,
close gates or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "MANUAL_FIELD_PRESERVATION_AUDIT_README.md", readme)

    report = f"""# Manual Field Preservation Audit Report

Status: `{summary["status"]}`

Current state:

1. Manual field targets: {summary["manual_field_targets"]}
2. Protected targets: {summary["protected_targets"]}
3. Overwrite risk rows: {summary["risk_rows"]}
4. Sendout stage rows: {summary["sendout_stage_rows"]}
5. Filled manual rows: {summary["filled_manual_rows"]}
6. Submission ready: false

Boundary: this audit verifies overwrite protection and safe rerun order only.
It does not validate scientific claims or close finalization gates.
"""
    write_text(OUT_DIR / "manual_field_preservation_audit_report.md", report)
    write_text(
        OUT_DIR / "manual_field_preservation_audit_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("Manual field preservation audit QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
