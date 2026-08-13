#!/usr/bin/env python3
"""Build an enhanced author sendout bundle with fill guides and lifecycle logs."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810"
ATTACH_DIR = OUT_DIR / "attachments"
DESKTOP_ZIP = Path.home() / "Desktop" / "NatComms_author_sendout_bundle_v2_20260810.zip"

PREFLIGHT_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_preflight_20260810"
GUIDE_DIR = BENCH_ROOT / "reports" / "author_fill_guide_packet_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
LOG_VALIDATOR_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_log_validator_20260810"
MANUAL_AUDIT_DIR = BENCH_ROOT / "reports" / "manual_field_preservation_audit_20260810"

ATTACHMENT_MANIFEST = PREFLIGHT_DIR / "author_sendout_attachment_manifest.csv"
EMAIL_DRAFT = PREFLIGHT_DIR / "author_sendout_email_ready_draft_cn.md"


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


def write_v2_send_log_template(path: Path) -> None:
    """Create a send log that points to the v2 bundle without a circular zip hash."""
    source_rows = read_csv(TRACKER_DIR / "author_response_send_log_template.csv")
    rows = []
    for row in source_rows:
        rows.append(
            {
                "recipient": row["recipient"],
                "send_status": "not_sent",
                "sent_datetime_local": "",
                "sender": "",
                "bundle_zip": r"reports\natcomms_author_sendout_bundle_v2_20260810\NatComms_author_sendout_bundle_v2_20260810.zip",
                "bundle_zip_sha256": "COMPUTE_AFTER_FINAL_ZIP_COPY",
                "required_manual_action": "Send the v2 zip outside this script and fill sent_datetime_local only after real sendout.",
                "notes": "Use the external v2 zip fingerprint generated after packaging; the hash cannot be embedded inside the zip without changing the zip.",
            }
        )
    write_csv(
        path,
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
        rows,
    )


def copy_item(src: Path, bundle_subdir: str, item_id: str, recipient: str, purpose: str) -> dict[str, object]:
    dest = ATTACH_DIR / bundle_subdir / src.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return {
        "attachment_id": item_id,
        "source_file": str(src.relative_to(BENCH_ROOT)),
        "bundle_file": str(dest.relative_to(OUT_DIR)),
        "recipient": recipient,
        "purpose": purpose,
        "bytes": dest.stat().st_size,
        "sha256": sha256(dest),
        }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if ATTACH_DIR.exists():
        shutil.rmtree(ATTACH_DIR)
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)

    bundle_rows: list[dict[str, object]] = []
    for row in read_csv(ATTACHMENT_MANIFEST):
        src = BENCH_ROOT / row["file"]
        bundle_rows.append(
            copy_item(
                src=src,
                bundle_subdir="reply_forms",
                item_id=row["attachment_id"],
                recipient=row["recipient"],
                purpose=row["purpose"],
            )
        )

    guide_items = [
        ("GUIDE-001", GUIDE_DIR / "AUTHOR_FILL_GUIDE_CN.md", "all_recipients", "Chinese fill guide for all author-facing fields."),
        ("GUIDE-002", GUIDE_DIR / "author_core_reply_fill_guide.csv", "corresponding_author", "Allowed values and examples for the 12 AFR core fields."),
        ("GUIDE-003", GUIDE_DIR / "backend_and_scope_fill_guide.csv", "author_analysis", "Allowed backend and figure-scope choices."),
        ("GUIDE-004", GUIDE_DIR / "ancillary_reply_sheet_fill_guide.csv", "all_recipients", "How to fill ancillary reply sheets."),
        ("GUIDE-005", GUIDE_DIR / "owner_specific_fill_assignments.csv", "all_recipients", "Owner-specific task assignments and validation commands."),
        ("GUIDE-006", GUIDE_DIR / "prohibited_short_replies.csv", "all_recipients", "Replies that must not be used because they overclaim readiness."),
        ("GUIDE-007", GUIDE_DIR / "send_return_log_fill_guide.csv", "sender", "How to fill send and return logs."),
    ]
    for item_id, src, recipient, purpose in guide_items:
        bundle_rows.append(copy_item(src, "fill_guides", item_id, recipient, purpose))

    v2_send_log = OUT_DIR / "author_response_send_log_template.csv"
    write_v2_send_log_template(v2_send_log)

    lifecycle_items = [
        ("LOG-001", v2_send_log, "sender", "Send log template for the v2 zip; fill only after real manual sendout."),
        ("LOG-002", TRACKER_DIR / "author_response_return_tracker.csv", "sender", "Return tracker; fill only after returned files are received."),
        ("LOG-003", LOG_VALIDATOR_DIR / "AUTHOR_RESPONSE_LOG_VALIDATOR_README.md", "sender", "Validation rule summary for send/return lifecycle."),
        ("LOG-004", MANUAL_AUDIT_DIR / "manual_field_safe_rerun_order.csv", "analysis", "Safe rerun order after manual fields are filled."),
    ]
    for item_id, src, recipient, purpose in lifecycle_items:
        bundle_rows.append(copy_item(src, "lifecycle_logs", item_id, recipient, purpose))

    shutil.copy2(EMAIL_DRAFT, OUT_DIR / "author_sendout_email_ready_draft_cn.md")

    instruction = """# Nat Comms Author Sendout Bundle v2

This v2 bundle includes the original author reply forms plus the new fill guide,
send/return lifecycle templates and safe rerun order.

Manual use:

1. Send the files under `attachments/reply_forms/` and the guide under
   `attachments/fill_guides/`.
2. Do not mark `email_sent=true` until the message is actually sent outside this
   script.
3. After real sendout, fill `attachments/lifecycle_logs/author_response_send_log_template.csv`.
4. After returned files are received, fill
   `attachments/lifecycle_logs/author_response_return_tracker.csv`.
5. Then rerun the validators and full checks listed in
   `attachments/lifecycle_logs/manual_field_safe_rerun_order.csv`.

Boundary: this bundle does not send email, collect replies, select a backend,
render figures, create DOI records, close gates, generate final files or submit
the manuscript.
"""
    instruction_path = OUT_DIR / "AUTHOR_SENDOUT_BUNDLE_V2_INSTRUCTIONS.md"
    write_text(instruction_path, instruction)

    write_csv(
        OUT_DIR / "author_sendout_bundle_v2_manifest.csv",
        ["attachment_id", "source_file", "bundle_file", "recipient", "purpose", "bytes", "sha256"],
        bundle_rows,
    )

    route_rows = [
        {
            "recipient": row["recipient"],
            "attachment_id": row["attachment_id"],
            "bundle_file": row["bundle_file"],
            "send_instruction": "Manual send only; do not mark email_sent true until actually sent outside this script.",
        }
        for row in bundle_rows
    ]
    write_csv(
        OUT_DIR / "author_sendout_bundle_v2_recipient_route.csv",
        ["recipient", "attachment_id", "bundle_file", "send_instruction"],
        route_rows,
    )

    inventory_rows = [
        {"category": "reply_forms", "items": 8, "purpose": "Files recipients fill."},
        {"category": "fill_guides", "items": len(guide_items), "purpose": "Allowed values, examples and owner assignments."},
        {"category": "lifecycle_logs", "items": len(lifecycle_items), "purpose": "Manual send/return logs and validation order."},
    ]
    write_csv(
        OUT_DIR / "author_sendout_bundle_v2_inventory.csv",
        ["category", "items", "purpose"],
        inventory_rows,
    )

    zip_path = OUT_DIR / "NatComms_author_sendout_bundle_v2_20260810.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(instruction_path, instruction_path.name)
        zf.write(OUT_DIR / "author_sendout_email_ready_draft_cn.md", "author_sendout_email_ready_draft_cn.md")
        zf.write(OUT_DIR / "author_sendout_bundle_v2_manifest.csv", "author_sendout_bundle_v2_manifest.csv")
        zf.write(OUT_DIR / "author_sendout_bundle_v2_recipient_route.csv", "author_sendout_bundle_v2_recipient_route.csv")
        zf.write(OUT_DIR / "author_sendout_bundle_v2_inventory.csv", "author_sendout_bundle_v2_inventory.csv")
        for row in bundle_rows:
            path = OUT_DIR / str(row["bundle_file"])
            zf.write(path, str(row["bundle_file"]).replace("\\", "/"))
    shutil.copy2(zip_path, DESKTOP_ZIP)

    fingerprint_rows = [
        {
            "artifact": "report_zip",
            "path": str(zip_path.relative_to(BENCH_ROOT)),
            "exists": zip_path.exists(),
            "sha256": sha256(zip_path),
            "usage": "Record this hash externally after packaging; do not embed it in the zipped send log.",
        },
        {
            "artifact": "desktop_zip",
            "path": str(DESKTOP_ZIP),
            "exists": DESKTOP_ZIP.exists(),
            "sha256": sha256(DESKTOP_ZIP),
            "usage": "Use this hash when documenting the manually sent Desktop copy.",
        },
    ]
    write_csv(
        OUT_DIR / "author_sendout_bundle_v2_zip_fingerprint.csv",
        ["artifact", "path", "exists", "sha256", "usage"],
        fingerprint_rows,
    )

    qa_rows = [
        {
            "check": "Original reply forms included",
            "result": "PASS" if sum(1 for row in bundle_rows if str(row["attachment_id"]).startswith("ATT-")) == 8 else "FAIL",
            "detail": "Eight reply-form attachments expected.",
        },
        {
            "check": "Fill guides included",
            "result": "PASS" if sum(1 for row in bundle_rows if str(row["attachment_id"]).startswith("GUIDE-")) == len(guide_items) else "FAIL",
            "detail": f"{len(guide_items)} guide files expected.",
        },
        {
            "check": "Lifecycle logs included",
            "result": "PASS" if sum(1 for row in bundle_rows if str(row["attachment_id"]).startswith("LOG-")) == len(lifecycle_items) else "FAIL",
            "detail": f"{len(lifecycle_items)} lifecycle files expected.",
        },
        {
            "check": "Checksums generated",
            "result": "PASS" if all(len(str(row["sha256"])) == 64 for row in bundle_rows) else "FAIL",
            "detail": "SHA256 recorded for every copied file.",
        },
        {"check": "Zip created in report directory", "result": "PASS" if zip_path.exists() else "FAIL", "detail": str(zip_path)},
        {"check": "Zip copied to Desktop", "result": "PASS" if DESKTOP_ZIP.exists() else "FAIL", "detail": str(DESKTOP_ZIP)},
        {
            "check": "V2 zip fingerprint generated",
            "result": "PASS" if all(len(str(row["sha256"])) == 64 for row in fingerprint_rows) else "FAIL",
            "detail": "External fingerprint avoids circular in-zip hash mutation.",
        },
        {"check": "No send state asserted", "result": "PASS", "detail": "email_sent remains false by design."},
    ]
    write_csv(OUT_DIR / "author_sendout_bundle_v2_qa.csv", ["check", "result", "detail"], qa_rows)

    readme = """# Nat Comms Author Sendout Bundle v2

Purpose: package the author reply forms together with the fill guide and manual
send/return lifecycle logs into one zip for manual sendout.

Boundary: this package does not send email, collect replies, select a backend,
render figures, create DOI records, close gates or make the manuscript
submission-ready.
"""
    write_text(OUT_DIR / "NATCOMMS_AUTHOR_SENDOUT_BUNDLE_V2_README.md", readme)

    report = f"""# Author Sendout Bundle v2 Report

Status: `natcomms_author_sendout_bundle_v2_ready_not_sent`

Current state:

1. Total bundled files: {len(bundle_rows)}
2. Reply forms: 8
3. Fill guides: {len(guide_items)}
4. Lifecycle files: {len(lifecycle_items)}
5. Report zip: `{zip_path}`
6. Desktop zip: `{DESKTOP_ZIP}`
7. Email sent: false
8. Author replies collected: false
9. Submission ready: false
"""
    write_text(OUT_DIR / "author_sendout_bundle_v2_report.md", report)

    summary = {
        "package": "natcomms_author_sendout_bundle_v2_20260810",
        "total_bundled_files": len(bundle_rows),
        "reply_forms": 8,
        "fill_guides": len(guide_items),
        "lifecycle_files": len(lifecycle_items),
        "report_zip": str(zip_path),
        "desktop_zip": str(DESKTOP_ZIP),
        "zip_fingerprint_file": str(OUT_DIR / "author_sendout_bundle_v2_zip_fingerprint.csv"),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "email_sent": False,
        "author_replies_collected": False,
        "backend_selected": False,
        "submission_ready": False,
        "status": "natcomms_author_sendout_bundle_v2_ready_not_sent",
    }
    write_text(OUT_DIR / "author_sendout_bundle_v2_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not summary["qa_pass"]:
        raise SystemExit("Author sendout bundle v2 QA failed")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
