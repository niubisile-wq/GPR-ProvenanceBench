#!/usr/bin/env python3
"""Map inbox evidence folders to tracker writeback targets without editing trackers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "inbox_to_tracker_writeback_queue_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

INBOX_MANIFEST = REPORTS / "manual_evidence_inbox_scaffold_20260810" / "manual_evidence_inbox_manifest.csv"
INBOX_AUDIT = REPORTS / "manual_evidence_inbox_audit_20260810" / "manual_evidence_inbox_folder_audit.csv"
WORKSHEET = REPORTS / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet.csv"
FIELD_CONSTRAINTS = REPORTS / "manual_evidence_entry_preflight_20260810" / "manual_evidence_field_constraint_matrix.csv"
NEXT_COMMANDS = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_next_validation_commands.csv"
POST_DISPATCH_SUMMARY = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"


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
    marker = "### 18.92 Inbox-to-tracker writeback queue update"
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

    inbox_rows = read_csv(INBOX_MANIFEST)
    audit_rows = read_csv(INBOX_AUDIT)
    worksheet_rows = read_csv(WORKSHEET)
    field_rows = read_csv(FIELD_CONSTRAINTS)
    next_commands = read_csv(NEXT_COMMANDS)
    post_dispatch = read_json(POST_DISPATCH_SUMMARY)

    inbox_by_dispatch = {row["dispatch_id"]: row for row in inbox_rows}
    audit_by_dispatch = {row["dispatch_id"]: row for row in audit_rows}
    next_by_evidence = {row["condition"].replace(" pass", ""): row for row in next_commands}
    fields_by_worksheet: dict[str, list[dict[str, str]]] = {}
    for row in field_rows:
        fields_by_worksheet.setdefault(row["worksheet_id"], []).append(row)

    writeback_rows: list[dict[str, object]] = []
    risk_rows: list[dict[str, object]] = []
    for row in worksheet_rows:
        inbox = inbox_by_dispatch.get(row["dispatch_id"], {})
        audit = audit_by_dispatch.get(row["dispatch_id"], {})
        fields = fields_by_worksheet.get(row["worksheet_id"], [])
        missing_fields = [field["field_to_fill"] for field in fields if field["field_present"] == "False"]
        external_payload = any(field["field_present"] == "external_payload" for field in fields)
        candidate_files = int(audit.get("candidate_evidence_files", "0") or 0)
        writeback_allowed = "no"
        if candidate_files > 0 and not missing_fields and not external_payload:
            writeback_allowed = "manual_review_required"
        reason = "No candidate inbox evidence file is present."
        if missing_fields:
            reason = "Target schema mismatch; do not auto-write this worksheet item."
        elif external_payload:
            reason = "External payload must use strict-SHA manifest workflow, not tracker writeback."
        elif candidate_files > 0:
            reason = "Candidate evidence exists; manual review and checksum confirmation required before writeback."

        writeback_rows.append(
            {
                "worksheet_id": row["worksheet_id"],
                "dispatch_id": row["dispatch_id"],
                "evidence_type": row["evidence_type"],
                "inbox_folder": inbox.get("inbox_folder", ""),
                "candidate_evidence_files": candidate_files,
                "target_file": row["target_file"],
                "target_rows": row["target_rows"],
                "fields_to_fill": row["fields_to_fill"],
                "do_not_edit": row["do_not_edit"],
                "allowed_values_or_format": row["allowed_values_or_format"],
                "after_fill_validation": row["after_fill_validation"],
                "post_dispatch_next_command": next_by_evidence.get(row["evidence_type"], {}).get("next_command", ""),
                "writeback_allowed_now": writeback_allowed,
                "reason": reason,
            }
        )

        if missing_fields or external_payload or writeback_allowed == "no":
            risk_rows.append(
                {
                    "worksheet_id": row["worksheet_id"],
                    "dispatch_id": row["dispatch_id"],
                    "risk_type": "schema_mismatch" if missing_fields else "external_or_missing_evidence",
                    "detail": "; ".join(missing_fields) if missing_fields else reason,
                    "operator_action": "Collect real evidence first; rerun inbox audit; only then fill mapped fields manually.",
                }
            )

    command_rows = [
        {
            "order": 1,
            "command": "py scripts\\build_manual_evidence_inbox_audit.py",
            "purpose": "Refresh inbox file counts, checksums and sensitive-name scan after files are dropped.",
            "run_now": "yes",
        },
        {
            "order": 2,
            "command": "manual worksheet writeback",
            "purpose": "Fill only mapped fields for rows whose writeback_allowed_now is manual_review_required.",
            "run_now": "no",
        },
        {
            "order": 3,
            "command": "py scripts\\build_post_dispatch_evidence_intake_validator.py",
            "purpose": "Confirm written tracker evidence is accepted before branch validators.",
            "run_now": "yes",
        },
        {
            "order": 4,
            "command": "run branch validators listed by post-dispatch next commands",
            "purpose": "Run only rows whose blocked_now becomes no.",
            "run_now": "no",
        },
    ]

    qa_rows = [
        {
            "check": "seven_writeback_rows_indexed",
            "result": "PASS" if len(writeback_rows) == 7 else "FAIL",
            "detail": f"writeback_rows={len(writeback_rows)}",
        },
        {
            "check": "current_empty_inbox_blocks_writeback",
            "result": "PASS" if all(row["writeback_allowed_now"] == "no" or "External payload" in row["reason"] or "schema" in row["reason"] for row in writeback_rows) else "FAIL",
            "detail": f"candidate_files_total={sum(int(row['candidate_evidence_files']) for row in writeback_rows)}",
        },
        {
            "check": "post_dispatch_state_preserved",
            "result": "PASS" if post_dispatch.get("evidence_rows_passed") == 0 else "FAIL",
            "detail": f"evidence_rows_passed={post_dispatch.get('evidence_rows_passed')}",
        },
        {
            "check": "no_tracker_write_performed",
            "result": "PASS",
            "detail": "This package is a writeback queue only.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "inbox_to_tracker_writeback_queue.csv",
        writeback_rows,
        [
            "worksheet_id",
            "dispatch_id",
            "evidence_type",
            "inbox_folder",
            "candidate_evidence_files",
            "target_file",
            "target_rows",
            "fields_to_fill",
            "do_not_edit",
            "allowed_values_or_format",
            "after_fill_validation",
            "post_dispatch_next_command",
            "writeback_allowed_now",
            "reason",
        ],
    )
    write_csv(OUT_DIR / "inbox_to_tracker_writeback_risks.csv", risk_rows, ["worksheet_id", "dispatch_id", "risk_type", "detail", "operator_action"])
    write_csv(OUT_DIR / "inbox_to_tracker_command_sequence.csv", command_rows, ["order", "command", "purpose", "run_now"])
    write_csv(OUT_DIR / "inbox_to_tracker_writeback_queue_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Inbox-to-tracker writeback queue report 2026-08-10",
        "",
        "Status: `inbox_to_tracker_writeback_queue_ready_waiting_evidence`",
        "",
        f"1. Writeback rows: {len(writeback_rows)}",
        f"2. Risk rows: {len(risk_rows)}",
        f"3. Command rows: {len(command_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: tracker writeback targets are mapped, but no inbox evidence is present and no tracker writeback is allowed now.",
        "",
    ]
    write_text(OUT_DIR / "INBOX_TO_TRACKER_WRITEBACK_QUEUE_README.md", "\n".join(report))
    write_text(OUT_DIR / "inbox_to_tracker_writeback_queue_report.md", "\n".join(report))

    summary = {
        "package": "inbox_to_tracker_writeback_queue_20260810",
        "writeback_rows": len(writeback_rows),
        "risk_rows": len(risk_rows),
        "command_rows": len(command_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "writeback_allowed_rows": sum(1 for row in writeback_rows if row["writeback_allowed_now"] != "no"),
        "tracker_write_performed": False,
        "manual_evidence_written": False,
        "evidence_rows_passed": post_dispatch.get("evidence_rows_passed"),
        "submission_ready": False,
        "status": "inbox_to_tracker_writeback_queue_ready_waiting_evidence",
    }

    section = f"""### 18.92 Inbox-to-tracker writeback queue update

Added an inbox-to-tracker writeback queue that maps returned-file inbox folders to worksheet targets, editable fields, do-not-edit fields and post-fill validators.

New directory: `{OUT_DIR}`

New files:
1. `inbox_to_tracker_writeback_queue.csv`
2. `inbox_to_tracker_writeback_risks.csv`
3. `inbox_to_tracker_command_sequence.csv`
4. `inbox_to_tracker_writeback_queue_qa.csv`
5. `INBOX_TO_TRACKER_WRITEBACK_QUEUE_README.md`
6. `inbox_to_tracker_writeback_queue_report.md`
7. `inbox_to_tracker_writeback_queue_summary.json`

Current result:
1. writeback_rows = {summary['writeback_rows']}
2. risk_rows = {summary['risk_rows']}
3. writeback_allowed_rows = {summary['writeback_allowed_rows']}
4. qa_pass = {str(qa_pass).lower()}
5. tracker_write_performed = false
6. manual_evidence_written = false
7. submission_ready = false

Boundary:
1. This step does not edit tracker files.
2. This step does not mark inbox files as validated evidence.
3. This step does not close gates or authorize upload."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "inbox_to_tracker_writeback_queue_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Inbox-to-tracker writeback queue QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
