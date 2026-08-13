#!/usr/bin/env python3
"""Build a preflight intake package for real external-dependency send evidence."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_dependency_sendout_evidence_intake_preflight_20260810"
DROP_DIR = BENCH_ROOT / "manual_evidence" / "external_dependency_sendout_20260810"
SAFE_SEND_DIR = BENCH_ROOT / "reports" / "external_dependency_safe_send_execution_packet_20260810"
EDS_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_sendout_receipt_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_GUIDE = Path.home() / "Desktop" / "NatComms_19.57_sendout_evidence_intake_preflight_20260810.md"
METADATA_PATH = OUT_DIR / "external_dependency_sendout_evidence_metadata_template.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_placeholder(value: str) -> bool:
    value = (value or "").strip()
    return not value or value.startswith("FILL_AFTER")


def resolve_evidence_path(path_text: str) -> Path:
    path = Path(path_text.strip())
    if not path.is_absolute():
        path = BENCH_ROOT / path
    return path


def build_default_metadata(send_tasks: list[dict[str, str]]) -> list[dict[str, object]]:
    return [
        {
            "send_receipt_id": row.get("send_receipt_id", ""),
            "receipt_id": row.get("receipt_id", ""),
            "owner": row.get("owner", ""),
            "sent_datetime_local": "FILL_AFTER_SEND",
            "sender": "FILL_AFTER_SEND",
            "recipient_or_channel": "FILL_AFTER_SEND",
            "sent_message_path": f"manual_evidence/external_dependency_sendout_20260810/{row.get('send_receipt_id', '').lower()}_sent_message.eml",
            "notes": "FILL_AFTER_SEND",
        }
        for row in send_tasks
    ]


def merge_existing_metadata(default_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not METADATA_PATH.exists():
        return default_rows
    existing = {row.get("send_receipt_id", ""): row for row in read_csv(METADATA_PATH)}
    merged_rows = []
    for default in default_rows:
        row = default.copy()
        existing_row = existing.get(str(default["send_receipt_id"]), {})
        for field in ["sent_datetime_local", "sender", "recipient_or_channel", "sent_message_path", "notes"]:
            if existing_row.get(field):
                row[field] = existing_row[field]
        merged_rows.append(row)
    return merged_rows


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.57 Sendout evidence intake preflight update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/external_dependency_sendout_evidence_intake_preflight_20260810/` and drop zone `manual_evidence/external_dependency_sendout_20260810/` for real sent-message evidence intake.
- Desktop guide generated: `NatComms_19.57_sendout_evidence_intake_preflight_20260810.md`.
- Current `metadata_rows={summary["metadata_rows"]}`, `complete_metadata_rows={summary["complete_metadata_rows"]}`, `writeback_candidate_rows={summary["writeback_candidate_rows"]}`.
- Current `evidence_intake_complete={str(summary["evidence_intake_complete"]).lower()}`, `eds_writeback_allowed={str(summary["eds_writeback_allowed"]).lower()}`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: this preflight computes SHA256 and proposes EDS writeback candidates only. It does not send email, overwrite the real EDS template, fill FMR rows, run recheck or submit.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
        else:
            text = text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DROP_DIR.mkdir(parents=True, exist_ok=True)

    safe_summary = read_json(SAFE_SEND_DIR / "external_dependency_safe_send_execution_summary.json")
    send_tasks = read_csv(SAFE_SEND_DIR / "external_dependency_safe_send_task_list.csv")
    existing_eds_rows = read_csv(EDS_DIR / "external_dependency_escalation_sendout_receipt_template.csv")

    metadata_rows = merge_existing_metadata(build_default_metadata(send_tasks))
    write_csv(
        METADATA_PATH,
        [
            "send_receipt_id",
            "receipt_id",
            "owner",
            "sent_datetime_local",
            "sender",
            "recipient_or_channel",
            "sent_message_path",
            "notes",
        ],
        metadata_rows,
    )

    status_rows = []
    candidate_rows = []
    existing_eds_by_id = {row.get("send_receipt_id", ""): row for row in existing_eds_rows}
    for row in metadata_rows:
        missing_fields = [
            field
            for field in ["sent_datetime_local", "sender", "recipient_or_channel", "sent_message_path"]
            if is_placeholder(str(row.get(field, "")))
        ]
        evidence_path = resolve_evidence_path(str(row.get("sent_message_path", "")))
        evidence_exists = evidence_path.exists() and evidence_path.is_file()
        digest = sha256_file(evidence_path) if evidence_exists else ""
        complete = not missing_fields and evidence_exists
        status_rows.append(
            {
                "send_receipt_id": row["send_receipt_id"],
                "receipt_id": row["receipt_id"],
                "metadata_complete": "yes" if not missing_fields else "no",
                "evidence_file_exists": "yes" if evidence_exists else "no",
                "computed_sent_message_sha256": digest,
                "candidate_ready": "yes" if complete else "no",
                "blocking_reason": "" if complete else "; ".join(missing_fields + ([] if evidence_exists else ["sent_message_path file missing"])),
            }
        )
        if complete:
            existing_eds = existing_eds_by_id.get(str(row["send_receipt_id"]), {})
            candidate_rows.append(
                {
                    "send_receipt_id": row["send_receipt_id"],
                    "receipt_id": row["receipt_id"],
                    "owner": row["owner"],
                    "required_send_evidence": existing_eds.get(
                        "required_send_evidence",
                        "sent_datetime_local; sender; recipient_or_channel; sent_message_path; sent_message_sha256",
                    ),
                    "sent_datetime_local": row["sent_datetime_local"],
                    "sender": row["sender"],
                    "recipient_or_channel": row["recipient_or_channel"],
                    "sent_message_path": str(evidence_path),
                    "sent_message_sha256": digest,
                    "current_status": "candidate_ready_for_eds_writeback",
                    "unlock_if_valid": existing_eds.get(
                        "unlock_if_valid",
                        "FMR-001 can be considered only after all send-now receipts are sent and verified.",
                    ),
                }
            )

    complete_metadata_rows = sum(1 for row in status_rows if row["candidate_ready"] == "yes")
    evidence_intake_complete = len(metadata_rows) == 5 and complete_metadata_rows == 5
    eds_writeback_allowed = evidence_intake_complete

    qa_rows = [
        {
            "check": "safe-send task list imported",
            "result": "PASS" if safe_summary.get("send_task_rows") == 5 and len(send_tasks) == 5 else "FAIL",
            "detail": f"safe_send_rows={len(send_tasks)}",
        },
        {
            "check": "metadata template has one row per EDS task",
            "result": "PASS" if len(metadata_rows) == 5 else "FAIL",
            "detail": f"metadata_rows={len(metadata_rows)}",
        },
        {
            "check": "writeback is gated by complete evidence files",
            "result": "PASS" if eds_writeback_allowed == (complete_metadata_rows == 5) else "FAIL",
            "detail": f"complete_metadata_rows={complete_metadata_rows}; eds_writeback_allowed={eds_writeback_allowed}",
        },
        {
            "check": "preflight does not alter submission state",
            "result": "PASS",
            "detail": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "external_dependency_sendout_evidence_intake_preflight_20260810",
        "metadata_rows": len(metadata_rows),
        "complete_metadata_rows": complete_metadata_rows,
        "incomplete_metadata_rows": len(metadata_rows) - complete_metadata_rows,
        "writeback_candidate_rows": len(candidate_rows),
        "evidence_intake_complete": evidence_intake_complete,
        "eds_writeback_allowed": eds_writeback_allowed,
        "real_eds_template_modified": False,
        "manual_drop_dir": str(DROP_DIR),
        "desktop_guide": str(DESKTOP_GUIDE),
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "external_dependency_sendout_evidence_intake_preflight_complete_writeback_candidate_ready"
            if eds_writeback_allowed
            else "external_dependency_sendout_evidence_intake_preflight_ready_waiting_real_sent_messages"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "external_dependency_sendout_evidence_intake_status.csv",
        [
            "send_receipt_id",
            "receipt_id",
            "metadata_complete",
            "evidence_file_exists",
            "computed_sent_message_sha256",
            "candidate_ready",
            "blocking_reason",
        ],
        status_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_sendout_evidence_writeback_candidates.csv",
        [
            "send_receipt_id",
            "receipt_id",
            "owner",
            "required_send_evidence",
            "sent_datetime_local",
            "sender",
            "recipient_or_channel",
            "sent_message_path",
            "sent_message_sha256",
            "current_status",
            "unlock_if_valid",
        ],
        candidate_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_sendout_evidence_intake_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    guide = f"""# NatComms 19.57 Sendout Evidence Intake Preflight

Status: `{summary["status"]}`

Use this package after the five 19.55 manual send tasks have actually been
sent by a human account.

Manual drop zone:

`{DROP_DIR}`

Fill this metadata file:

`{METADATA_PATH}`

Required fields per row:

1. `sent_datetime_local`
2. `sender`
3. `recipient_or_channel`
4. `sent_message_path`

The script computes `sent_message_sha256` from each file and writes candidate
EDS rows to:

`reports/external_dependency_sendout_evidence_intake_preflight_20260810/external_dependency_sendout_evidence_writeback_candidates.csv`

Current result:

1. Metadata rows: {summary["metadata_rows"]}
2. Complete metadata rows: {summary["complete_metadata_rows"]}
3. Writeback candidate rows: {summary["writeback_candidate_rows"]}
4. EDS writeback allowed: {str(summary["eds_writeback_allowed"]).lower()}
5. Portal upload allowed: false
6. Submission ready: false

Boundary: this preflight does not send email, overwrite the real EDS template,
fill FMR rows, run recheck, upload portal files or mark the manuscript
submitted.
"""
    write_text(OUT_DIR / "EXTERNAL_DEPENDENCY_SENDOUT_EVIDENCE_INTAKE_PREFLIGHT_README.md", guide)
    write_text(OUT_DIR / "external_dependency_sendout_evidence_intake_preflight_report.md", guide)
    write_text(DESKTOP_GUIDE, guide)
    summary["desktop_guide_exists"] = DESKTOP_GUIDE.exists()
    write_text(
        OUT_DIR / "external_dependency_sendout_evidence_intake_preflight_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
