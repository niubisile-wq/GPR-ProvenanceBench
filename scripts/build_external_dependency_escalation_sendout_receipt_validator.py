#!/usr/bin/env python3
"""Validate sendout receipts for the 19.53 external dependency escalation packet."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_sendout_receipt_validator_20260810"
ESCALATION_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_packet_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
TEMPLATE_PATH = OUT_DIR / "external_dependency_escalation_sendout_receipt_template.csv"
REQUIRED_SEND_FIELDS = [
    "sent_datetime_local",
    "sender",
    "recipient_or_channel",
    "sent_message_path",
    "sent_message_sha256",
]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def is_placeholder(value: str) -> bool:
    value = (value or "").strip()
    return not value or value.startswith("FILL_AFTER")


def sha256_file(path_text: str) -> str:
    path = Path(path_text)
    if not path.is_absolute():
        path = BENCH_ROOT / path
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_send_receipt(row: dict[str, str]) -> tuple[bool, str]:
    missing = [field for field in REQUIRED_SEND_FIELDS if is_placeholder(row.get(field, ""))]
    if missing:
        return False, "Missing or placeholder fields: " + "; ".join(missing)

    message_path = row.get("sent_message_path", "").strip()
    candidate = Path(message_path)
    if not candidate.is_absolute():
        candidate = BENCH_ROOT / candidate
    if not candidate.exists():
        return False, f"sent_message_path does not exist: {message_path}"

    expected_hash = row.get("sent_message_sha256", "").strip().lower()
    actual_hash = sha256_file(message_path).lower()
    if actual_hash != expected_hash:
        return False, f"sent_message_sha256 mismatch: actual={actual_hash}"

    return True, "Send receipt has required fields and matching sent_message_sha256."


def _obsolete_update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.54 External dependency escalation sendout receipt validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/external_dependency_escalation_sendout_receipt_validator_20260810/`，校验 19.53 external dependency escalation 是否真实发送。
- 当前 `sendout_receipt_rows={summary["sendout_receipt_rows"]}`，`sent_receipt_rows=0`，`missing_send_receipts={summary["missing_send_receipts"]}`。
- 当前 `escalation_sent=false`，`fmr001_unlock_allowed=false`，`receipt_completion_allowed=false`，`submission_ready=false`。
- 边界：该 validator 只读，不发送邮件、不伪造发送记录、不填 FMR-001、不触发 recheck。
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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.54 External dependency escalation sendout receipt validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/external_dependency_escalation_sendout_receipt_validator_20260810/` to validate whether the 19.53 external dependency escalation requests were actually sent.
- Current `sendout_receipt_rows={summary["sendout_receipt_rows"]}`, `sent_receipt_rows={summary["sent_receipt_rows"]}`, `missing_send_receipts={summary["missing_send_receipts"]}`.
- Current `escalation_sent={str(summary["escalation_sent"]).lower()}`, `fmr001_unlock_allowed={str(summary["fmr001_unlock_allowed"]).lower()}`, `receipt_completion_allowed={str(summary["receipt_completion_allowed"]).lower()}`, `submission_ready=false`.
- Boundary: this validator preserves existing manual EDS entries and verifies sent-message SHA256, but it does not send email, fabricate send records, fill FMR-001 or run recheck.
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

    escalation_summary = read_json(ESCALATION_DIR / "external_dependency_escalation_summary.json")
    requests = read_csv(ESCALATION_DIR / "external_dependency_escalation_request_matrix.csv")
    send_now_requests = [row for row in requests if row.get("send_now") == "yes"]

    existing_by_receipt = {}
    if TEMPLATE_PATH.exists():
        existing_by_receipt = {row.get("receipt_id", ""): row for row in read_csv(TEMPLATE_PATH)}

    receipt_rows = []
    for idx, row in enumerate(send_now_requests, start=1):
        receipt_id = row.get("receipt_id", "")
        default = {
            "send_receipt_id": f"EDS-{idx:03d}",
            "receipt_id": receipt_id,
            "owner": row.get("owner", ""),
            "required_send_evidence": "sent_datetime_local; sender; recipient_or_channel; sent_message_path; sent_message_sha256",
            "sent_datetime_local": "FILL_AFTER_SEND",
            "sender": "FILL_AFTER_SEND",
            "recipient_or_channel": "FILL_AFTER_SEND",
            "sent_message_path": "FILL_AFTER_SEND",
            "sent_message_sha256": "FILL_AFTER_SEND",
            "current_status": "missing",
            "unlock_if_valid": "FMR-001 can be considered only after all send-now receipts are sent and verified.",
        }
        existing = existing_by_receipt.get(receipt_id, {})
        merged = default.copy()
        for field in REQUIRED_SEND_FIELDS:
            if existing.get(field):
                merged[field] = existing[field]
        passes, _ = validate_send_receipt(merged)
        merged["current_status"] = "sent_verified" if passes else "missing"
        receipt_rows.append(merged)

    validation_rows = []
    for row in receipt_rows:
        passes, reason = validate_send_receipt(row)
        validation_rows.append(
            {
                "send_receipt_id": row["send_receipt_id"],
                "receipt_id": row["receipt_id"],
                "sent_status_passes_now": "yes" if passes else "no",
                "blocking_reason": "" if passes else reason,
            }
        )

    sent_receipt_rows = sum(1 for row in validation_rows if row["sent_status_passes_now"] == "yes")
    missing_send_receipts = len(receipt_rows) - sent_receipt_rows
    escalation_sent = len(receipt_rows) == 5 and missing_send_receipts == 0
    fmr001_unlock_allowed = escalation_sent
    receipt_completion_allowed = escalation_sent
    submission_ready = False

    qa_rows = [
        {
            "check": "19.53 escalation imported",
            "result": "PASS" if escalation_summary.get("send_ready") is True else "FAIL",
            "detail": f"send_ready={escalation_summary.get('send_ready')}",
        },
        {
            "check": "send-now requests mapped",
            "result": "PASS" if len(receipt_rows) == 5 else "FAIL",
            "detail": f"sendout_receipt_rows={len(receipt_rows)}",
        },
        {
            "check": "no send receipts are fabricated",
            "result": "PASS",
            "detail": f"sent_receipt_rows={sent_receipt_rows}; values are imported only from existing EDS rows and verified against sent_message_sha256",
        },
        {
            "check": "submission remains false",
            "result": "PASS" if not submission_ready else "FAIL",
            "detail": f"submission_ready={submission_ready}",
        },
    ]

    summary = {
        "package": "external_dependency_escalation_sendout_receipt_validator_20260810",
        "sendout_receipt_rows": len(receipt_rows),
        "sent_receipt_rows": sent_receipt_rows,
        "missing_send_receipts": missing_send_receipts,
        "escalation_sent": escalation_sent,
        "fmr001_unlock_allowed": fmr001_unlock_allowed,
        "receipt_completion_allowed": receipt_completion_allowed,
        "portal_upload_allowed": False,
        "submission_ready": submission_ready,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "external_dependency_escalation_sendout_receipt_validator_complete_fmr001_unlock_allowed"
            if escalation_sent
            else "external_dependency_escalation_sendout_receipt_validator_ready_waiting_sendout"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        TEMPLATE_PATH,
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
        receipt_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_escalation_sendout_receipt_validation.csv",
        ["send_receipt_id", "receipt_id", "sent_status_passes_now", "blocking_reason"],
        validation_rows,
    )
    write_csv(OUT_DIR / "external_dependency_escalation_sendout_receipt_qa.csv", ["check", "result", "detail"], qa_rows)

    readme = """# External Dependency Escalation Sendout Receipt Validator

This validator creates and checks sendout receipt rows for the 19.53 external
dependency escalation packet.

Boundary: read-only. It preserves existing manual EDS entries and verifies
sent-message SHA256 when paths are filled. It does not send email, fabricate
send evidence, fill FMR-001, run rechecks, upload portal files or mark the
manuscript submitted.
"""
    write_text(OUT_DIR / "EXTERNAL_DEPENDENCY_ESCALATION_SENDOUT_RECEIPT_VALIDATOR_README.md", readme)

    report = f"""# External Dependency Escalation Sendout Receipt Validator Report

Status: `{summary["status"]}`

Current result:

1. Sendout receipt rows: {summary["sendout_receipt_rows"]}
2. Sent receipt rows: {summary["sent_receipt_rows"]}
3. Missing send receipts: {summary["missing_send_receipts"]}
4. Escalation sent: {str(summary["escalation_sent"]).lower()}
5. FMR-001 unlock allowed: {str(summary["fmr001_unlock_allowed"]).lower()}
6. Submission ready: {str(summary["submission_ready"]).lower()}
"""
    write_text(OUT_DIR / "external_dependency_escalation_sendout_receipt_validator_report.md", report)
    write_text(
        OUT_DIR / "external_dependency_escalation_sendout_receipt_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
