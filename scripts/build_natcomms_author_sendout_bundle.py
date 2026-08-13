#!/usr/bin/env python3
"""Build a zipped author sendout bundle without sending any message."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_20260810"
ATTACH_DIR = OUT_DIR / "attachments"
DESKTOP_ZIP = Path.home() / "Desktop" / "NatComms_author_sendout_bundle_20260810.zip"

PREFLIGHT_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_preflight_20260810"
ATTACHMENT_MANIFEST = PREFLIGHT_DIR / "author_sendout_attachment_manifest.csv"
EMAIL_DRAFT = PREFLIGHT_DIR / "author_sendout_email_ready_draft_cn.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if ATTACH_DIR.exists():
        shutil.rmtree(ATTACH_DIR)
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)

    attachment_rows = read_csv(ATTACHMENT_MANIFEST)
    bundle_rows = []
    for row in attachment_rows:
        src = BENCH_ROOT / row["file"]
        dest = ATTACH_DIR / src.name
        shutil.copy2(src, dest)
        bundle_rows.append(
            {
                "attachment_id": row["attachment_id"],
                "source_file": row["file"],
                "bundle_file": str(dest.relative_to(OUT_DIR)),
                "recipient": row["recipient"],
                "purpose": row["purpose"],
                "bytes": str(dest.stat().st_size),
                "sha256": sha256(dest),
            }
        )

    send_instruction = [
        "# Nat Comms author sendout bundle instructions",
        "",
        "This bundle is ready for manual sendout, but it has not been sent.",
        "",
        "Send the files under `attachments/` together with `author_sendout_email_ready_draft_cn.md` as the email body.",
        "",
        "After replies return, rerun:",
        "",
        "1. `py GPR-ProvenanceBench\\scripts\\build_natcomms_author_reply_ingestion_validator.py`",
        "2. `py GPR-ProvenanceBench\\scripts\\build_natcomms_gate_closure_evidence_binder.py`",
        "3. `py GPR-ProvenanceBench\\scripts\\build_natcomms_finalization_command_dashboard_v3.py`",
        "4. `py GPR-ProvenanceBench\\scripts\\run_m0_m2_checks.ps1`",
        "",
        "Boundary: this bundle does not send email, collect replies, select a backend, render figures, create DOI records, close gates or submit the manuscript.",
        "",
    ]
    instruction_path = OUT_DIR / "AUTHOR_SENDOUT_BUNDLE_INSTRUCTIONS.md"
    instruction_path.write_text("\n".join(send_instruction), encoding="utf-8")

    shutil.copy2(EMAIL_DRAFT, OUT_DIR / "author_sendout_email_ready_draft_cn.md")

    write_csv(
        OUT_DIR / "author_sendout_bundle_manifest.csv",
        bundle_rows,
        ["attachment_id", "source_file", "bundle_file", "recipient", "purpose", "bytes", "sha256"],
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
    write_csv(OUT_DIR / "author_sendout_recipient_route.csv", route_rows, ["recipient", "attachment_id", "bundle_file", "send_instruction"])

    zip_path = OUT_DIR / "NatComms_author_sendout_bundle_20260810.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(instruction_path, instruction_path.name)
        zf.write(OUT_DIR / "author_sendout_email_ready_draft_cn.md", "author_sendout_email_ready_draft_cn.md")
        zf.write(OUT_DIR / "author_sendout_bundle_manifest.csv", "author_sendout_bundle_manifest.csv")
        zf.write(OUT_DIR / "author_sendout_recipient_route.csv", "author_sendout_recipient_route.csv")
        for row in bundle_rows:
            path = OUT_DIR / row["bundle_file"]
            zf.write(path, row["bundle_file"].replace("\\", "/"))
    shutil.copy2(zip_path, DESKTOP_ZIP)

    qa_rows = [
        {"check": "All attachments copied", "result": "PASS" if len(bundle_rows) == 8 and all((OUT_DIR / row["bundle_file"]).exists() for row in bundle_rows) else "FAIL", "detail": f"{len(bundle_rows)} copied attachments."},
        {"check": "Checksums generated", "result": "PASS" if all(len(row["sha256"]) == 64 for row in bundle_rows) else "FAIL", "detail": "SHA256 recorded for each copied file."},
        {"check": "Zip created in report directory", "result": "PASS" if zip_path.exists() else "FAIL", "detail": str(zip_path)},
        {"check": "Zip copied to Desktop", "result": "PASS" if DESKTOP_ZIP.exists() else "FAIL", "detail": str(DESKTOP_ZIP)},
        {"check": "No send state asserted", "result": "PASS", "detail": "email_sent remains false by design."},
    ]
    write_csv(OUT_DIR / "author_sendout_bundle_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = [
        "# Nat Comms author sendout bundle",
        "",
        "Purpose: package the preflighted author finalization materials into a single zip for manual sendout.",
        "",
        "Boundary: this package does not send email, collect replies, select a backend, render figures, create DOI records, close gates or make the manuscript submission-ready.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_AUTHOR_SENDOUT_BUNDLE_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Author sendout bundle report",
        "",
        f"- Copied attachments: {len(bundle_rows)}",
        f"- Report zip: {zip_path}",
        f"- Desktop zip: {DESKTOP_ZIP}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_author_sendout_bundle_ready_not_sent",
        "",
    ]
    (OUT_DIR / "author_sendout_bundle_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_author_sendout_bundle",
        "copied_attachments": len(bundle_rows),
        "report_zip": str(zip_path),
        "desktop_zip": str(DESKTOP_ZIP),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "email_sent": False,
        "author_replies_collected": False,
        "backend_selected": False,
        "submission_ready": False,
        "status": "natcomms_author_sendout_bundle_ready_not_sent",
        "boundary": "Bundle packages ready-to-send files only; it does not send, collect replies, close gates or make submission ready.",
    }
    (OUT_DIR / "author_sendout_bundle_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
