#!/usr/bin/env python3
"""Audit that the Nat Comms sendout v2 lifecycle files point to the v2 bundle."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_sendout_v2_lifecycle_consistency_audit_20260810"
BUNDLE_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"
V2_PACKAGE_NAME = "NatComms_author_sendout_bundle_v2_20260810.zip"
V1_PACKAGE_MARKER = "NatComms_author_sendout_bundle_20260810.zip"
HASH_PLACEHOLDER = "COMPUTE_AFTER_FINAL_ZIP_COPY"


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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.34 NatComms sendout v2 lifecycle consistency audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/natcomms_sendout_v2_lifecycle_consistency_audit_20260810/`，专门检查 v2 发送包和 lifecycle 发送日志是否错指旧 v1 zip。
- 当前 `send_log_rows={summary["send_log_rows"]}`，`stale_v1_reference_rows={summary["stale_v1_reference_rows"]}`，`v2_reference_rows={summary["v2_reference_rows"]}`。
- 当前 `hash_placeholder_rows={summary["hash_placeholder_rows"]}`，`fingerprint_rows={summary["fingerprint_rows"]}`，`fingerprint_hashes_match={str(summary["fingerprint_hashes_match"]).lower()}`。
- 当前 `email_sent=false`，`author_replies_collected=false`，`candidate_return_files=0`，`submission_ready=false`。
- 边界：该审计只验证 v2 包生命周期一致性，不发送邮件、不接收作者回复、不写回证据、不关闭 gate。
"""
    if marker in text:
        text = text[: text.index(marker)].rstrip() + block
    else:
        text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = read_csv(BUNDLE_DIR / "author_sendout_bundle_v2_manifest.csv")
    send_log = read_csv(BUNDLE_DIR / "attachments" / "lifecycle_logs" / "author_response_send_log_template.csv")
    fingerprint_rows = read_csv(BUNDLE_DIR / "author_sendout_bundle_v2_zip_fingerprint.csv")
    summary_source = json.loads((BUNDLE_DIR / "author_sendout_bundle_v2_summary.json").read_text(encoding="utf-8"))

    report_zip = BUNDLE_DIR / V2_PACKAGE_NAME
    desktop_zip = Path.home() / "Desktop" / V2_PACKAGE_NAME
    actual_hash_rows = []
    for artifact, path in [("report_zip", report_zip), ("desktop_zip", desktop_zip)]:
        actual_hash_rows.append(
            {
                "artifact": artifact,
                "path": str(path),
                "exists": path.exists(),
                "sha256": sha256(path) if path.exists() else "",
            }
        )

    expected_hash = {row["artifact"]: row["sha256"] for row in fingerprint_rows}
    actual_hash = {row["artifact"]: row["sha256"] for row in actual_hash_rows}
    fingerprint_hashes_match = (
        expected_hash.get("report_zip") == actual_hash.get("report_zip")
        and expected_hash.get("desktop_zip") == actual_hash.get("desktop_zip")
        and bool(actual_hash.get("report_zip"))
        and actual_hash.get("report_zip") == actual_hash.get("desktop_zip")
    )

    send_log_audit_rows = []
    for row in send_log:
        bundle_zip = row.get("bundle_zip", "")
        bundle_zip_sha = row.get("bundle_zip_sha256", "")
        stale_v1 = V1_PACKAGE_MARKER in bundle_zip
        v2_ref = V2_PACKAGE_NAME in bundle_zip and "sendout_bundle_v2_20260810" in bundle_zip
        hash_deferred_or_valid = bundle_zip_sha == HASH_PLACEHOLDER or len(bundle_zip_sha) == 64
        issue = ""
        if stale_v1:
            issue = "stale_v1_bundle_reference"
        elif not v2_ref:
            issue = "missing_v2_bundle_reference"
        elif not hash_deferred_or_valid:
            issue = "invalid_bundle_hash_or_placeholder"
        send_log_audit_rows.append(
            {
                "recipient": row.get("recipient", ""),
                "send_status": row.get("send_status", ""),
                "bundle_zip": bundle_zip,
                "bundle_zip_sha256": bundle_zip_sha,
                "stale_v1_reference": stale_v1,
                "v2_reference": v2_ref,
                "hash_deferred_or_valid": hash_deferred_or_valid,
                "audit_status": "pass" if not issue else "fail",
                "issue": issue,
            }
        )

    manifest_log_rows = [row for row in manifest if row.get("attachment_id") == "LOG-001"]
    gate_rows = [
        {
            "gate": "v2_send_log_in_manifest",
            "current": len(manifest_log_rows),
            "required": "1",
            "passes_now": "yes" if len(manifest_log_rows) == 1 else "no",
        },
        {
            "gate": "no_stale_v1_zip_references",
            "current": sum(1 for row in send_log_audit_rows if row["stale_v1_reference"]),
            "required": "0",
            "passes_now": "yes" if all(not row["stale_v1_reference"] for row in send_log_audit_rows) else "no",
        },
        {
            "gate": "all_send_rows_point_to_v2_zip",
            "current": sum(1 for row in send_log_audit_rows if row["v2_reference"]),
            "required": len(send_log_audit_rows),
            "passes_now": "yes" if all(row["v2_reference"] for row in send_log_audit_rows) else "no",
        },
        {
            "gate": "zip_fingerprints_match",
            "current": fingerprint_hashes_match,
            "required": "true",
            "passes_now": "yes" if fingerprint_hashes_match else "no",
        },
        {
            "gate": "manual_send_state_not_asserted",
            "current": summary_source.get("email_sent"),
            "required": "false",
            "passes_now": "yes" if summary_source.get("email_sent") is False else "no",
        },
        {
            "gate": "submission_ready",
            "current": summary_source.get("submission_ready"),
            "required": "false",
            "passes_now": "yes" if summary_source.get("submission_ready") is False else "no",
        },
    ]

    qa_rows = [
        {
            "check": "send log rows present",
            "result": "PASS" if len(send_log_audit_rows) >= 1 else "FAIL",
            "detail": f"rows={len(send_log_audit_rows)}",
        },
        {
            "check": "no stale v1 references",
            "result": "PASS" if all(not row["stale_v1_reference"] for row in send_log_audit_rows) else "FAIL",
            "detail": f"stale_rows={sum(1 for row in send_log_audit_rows if row['stale_v1_reference'])}",
        },
        {
            "check": "all send rows reference v2 package",
            "result": "PASS" if all(row["v2_reference"] for row in send_log_audit_rows) else "FAIL",
            "detail": f"v2_rows={sum(1 for row in send_log_audit_rows if row['v2_reference'])}",
        },
        {
            "check": "zip fingerprints match current artifacts",
            "result": "PASS" if fingerprint_hashes_match else "FAIL",
            "detail": "report and Desktop zip hashes must match the recorded fingerprint file.",
        },
        {
            "check": "manual send state remains false",
            "result": "PASS" if summary_source.get("email_sent") is False else "FAIL",
            "detail": "audit must not assert a real send.",
        },
    ]

    summary = {
        "package": "natcomms_sendout_v2_lifecycle_consistency_audit_20260810",
        "send_log_rows": len(send_log_audit_rows),
        "manifest_rows": len(manifest),
        "fingerprint_rows": len(fingerprint_rows),
        "stale_v1_reference_rows": sum(1 for row in send_log_audit_rows if row["stale_v1_reference"]),
        "v2_reference_rows": sum(1 for row in send_log_audit_rows if row["v2_reference"]),
        "hash_placeholder_rows": sum(1 for row in send_log_audit_rows if row["bundle_zip_sha256"] == HASH_PLACEHOLDER),
        "fingerprint_hashes_match": fingerprint_hashes_match,
        "email_sent": False,
        "author_replies_collected": False,
        "candidate_return_files": 0,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "natcomms_sendout_v2_lifecycle_consistency_audit_passed_not_sent",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "sendout_v2_lifecycle_send_log_audit.csv",
        [
            "recipient",
            "send_status",
            "bundle_zip",
            "bundle_zip_sha256",
            "stale_v1_reference",
            "v2_reference",
            "hash_deferred_or_valid",
            "audit_status",
            "issue",
        ],
        send_log_audit_rows,
    )
    write_csv(
        OUT_DIR / "sendout_v2_zip_fingerprint_audit.csv",
        ["artifact", "path", "exists", "sha256"],
        actual_hash_rows,
    )
    write_csv(
        OUT_DIR / "sendout_v2_lifecycle_gate_matrix.csv",
        ["gate", "current", "required", "passes_now"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "sendout_v2_lifecycle_consistency_audit_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Nat Comms Sendout v2 Lifecycle Consistency Audit

This audit checks that the v2 author sendout bundle's lifecycle send log points
to the v2 zip, not the older v1 zip, and that the external report/Desktop zip
fingerprints match.

Boundary: this audit does not send email, collect author replies, ingest
evidence, write protected targets, close gates or make the manuscript
submission-ready.
"""
    write_text(OUT_DIR / "NATCOMMS_SENDOUT_V2_LIFECYCLE_CONSISTENCY_AUDIT_README.md", readme)

    report = f"""# Nat Comms Sendout v2 Lifecycle Consistency Audit Report

Status: `{summary["status"]}`

Current result:

1. Send log rows: {summary["send_log_rows"]}
2. Stale v1 reference rows: {summary["stale_v1_reference_rows"]}
3. V2 reference rows: {summary["v2_reference_rows"]}
4. Hash placeholder rows: {summary["hash_placeholder_rows"]}
5. Fingerprint rows: {summary["fingerprint_rows"]}
6. Fingerprint hashes match: {str(summary["fingerprint_hashes_match"]).lower()}
7. Email sent: false
8. Author replies collected: false
9. Candidate return files: 0
10. Submission ready: false

Interpretation: the v2 sendout lifecycle is internally consistent and still
blocked before any real manual send or returned-file intake.
"""
    write_text(OUT_DIR / "sendout_v2_lifecycle_consistency_audit_report.md", report)
    write_text(
        OUT_DIR / "sendout_v2_lifecycle_consistency_audit_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("NatComms sendout v2 lifecycle consistency audit QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
