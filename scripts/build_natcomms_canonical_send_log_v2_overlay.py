#!/usr/bin/env python3
"""Overlay the canonical author send log with the final Nat Comms v2 bundle path."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_canonical_send_log_v2_overlay_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
V2_BUNDLE_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

CANONICAL_SEND_LOG = TRACKER_DIR / "author_response_send_log_template.csv"
TRACKER_SUMMARY = TRACKER_DIR / "author_response_tracker_summary.json"
TRACKER_REPORT = TRACKER_DIR / "author_response_tracker_report.md"
V2_ZIP_REL = r"reports\natcomms_author_sendout_bundle_v2_20260810\NatComms_author_sendout_bundle_v2_20260810.zip"
V1_ZIP_MARKER = "NatComms_author_sendout_bundle_20260810.zip"


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


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.36 NatComms canonical send log v2 overlay update"
    anchor = "### 19.35 NatComms sendout evidence receipt completion validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/natcomms_canonical_send_log_v2_overlay_20260810/`，在 v2 发送包生成后修正 canonical send log 的 bundle_zip 指向，避免 response log validator 继续读到旧 v1 zip。
- 当前 `send_log_rows={summary["send_log_rows"]}`，`rows_overlaid={summary["rows_overlaid"]}`，`stale_v1_rows_after={summary["stale_v1_rows_after"]}`，`v2_reference_rows_after={summary["v2_reference_rows_after"]}`。
- 当前 `tracker_summary_updated={str(summary["tracker_summary_updated"]).lower()}`，`tracker_summary_sha_matches_v2={str(summary["tracker_summary_sha_matches_v2"]).lower()}`。
- 当前 `manual_status_preserved={str(summary["manual_status_preserved"]).lower()}`，`email_sent=false`，`author_replies_collected=false`，`submission_ready=false`。
- 边界：该 overlay 只更新 canonical send log 的包路径/指纹，不发送邮件、不填写 sender/timestamp、不接收回复、不关闭 gate。
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            text = text[:start].rstrip()
        else:
            text = text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    if anchor in text:
        anchor_start = text.index(anchor)
        insert_at = text.find("\n### ", anchor_start + len(anchor))
        if insert_at == -1:
            text = text.rstrip() + block
        else:
            text = text[:insert_at].rstrip() + block + "\n\n" + text[insert_at:].lstrip("\n")
    else:
        text = text.rstrip() + block
    DESKTOP_PLAN.write_text(text + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    send_rows = read_csv(CANONICAL_SEND_LOG)
    fingerprint_rows = read_csv(V2_BUNDLE_DIR / "author_sendout_bundle_v2_zip_fingerprint.csv")
    desktop_hash = next((row["sha256"] for row in fingerprint_rows if row.get("artifact") == "desktop_zip"), "")
    tracker_summary_before = read_json(TRACKER_SUMMARY)

    before_rows = []
    overlaid_rows = []
    for row in send_rows:
        before_rows.append(
            {
                "recipient": row.get("recipient", ""),
                "send_status": row.get("send_status", ""),
                "bundle_zip_before": row.get("bundle_zip", ""),
                "bundle_zip_sha256_before": row.get("bundle_zip_sha256", ""),
                "stale_v1_before": V1_ZIP_MARKER in row.get("bundle_zip", ""),
            }
        )
        updated = dict(row)
        updated["bundle_zip"] = V2_ZIP_REL
        updated["bundle_zip_sha256"] = desktop_hash
        updated["required_manual_action"] = (
            "Send the v2 zip outside this script and fill sent_datetime_local only after real sendout."
        )
        overlaid_rows.append(updated)

    fieldnames = [
        "recipient",
        "send_status",
        "sent_datetime_local",
        "sender",
        "bundle_zip",
        "bundle_zip_sha256",
        "required_manual_action",
        "notes",
    ]
    write_csv(CANONICAL_SEND_LOG, fieldnames, overlaid_rows)

    tracker_summary_after = dict(tracker_summary_before)
    tracker_summary_after["bundle_zip"] = V2_ZIP_REL
    tracker_summary_after["bundle_zip_sha256"] = desktop_hash
    tracker_summary_after["bundle_zip_source"] = "natcomms_author_sendout_bundle_v2_20260810"
    tracker_summary_after["canonical_send_log_overlay_applied"] = True
    tracker_summary_after["canonical_send_log_overlay_status"] = "v2_bundle_reference_applied_not_sent"
    write_text(TRACKER_SUMMARY, json.dumps(tracker_summary_after, indent=2, ensure_ascii=False) + "\n")

    tracker_report = f"""# Nat Comms Author Response Tracker Report

Status: `{tracker_summary_after["status"]}`

Generated rows:

1. Send log rows: {tracker_summary_after["send_log_rows"]}
2. Return tracker rows: {tracker_summary_after["return_tracker_rows"]}
3. Validation plan rows: {tracker_summary_after["validation_plan_rows"]}
4. Post-reply rerun commands: {tracker_summary_after["post_reply_rerun_commands"]}
5. Stop rules: {tracker_summary_after["stop_rules"]}

Canonical sendout bundle after v2 overlay:

1. Bundle zip: `{V2_ZIP_REL}`
2. Bundle zip SHA256: `{desktop_hash}`
3. Overlay applied: true
4. Email sent: false

Boundary flags:

1. `email_sent=false`
2. `author_replies_collected=false`
3. `backend_selected=false`
4. `submission_ready=false`

Interpretation: the canonical response tracker now points to the v2 sendout
bundle and external v2 zip fingerprint. The manual send/reply cycle is still
controlled by explicit send timestamps and returned-file paths. All downstream
gates must remain blocked until real returned files are logged and validators
pass.
"""
    write_text(TRACKER_REPORT, tracker_report)

    after_audit_rows = []
    for before, after in zip(before_rows, overlaid_rows, strict=True):
        after_audit_rows.append(
            {
                "recipient": after.get("recipient", ""),
                "send_status_before": before.get("send_status", ""),
                "send_status_after": after.get("send_status", ""),
                "sender_after": after.get("sender", ""),
                "sent_datetime_after": after.get("sent_datetime_local", ""),
                "bundle_zip_before": before.get("bundle_zip_before", ""),
                "bundle_zip_after": after.get("bundle_zip", ""),
                "stale_v1_before": before.get("stale_v1_before", False),
                "stale_v1_after": V1_ZIP_MARKER in after.get("bundle_zip", ""),
                "manual_status_preserved": before.get("send_status") == after.get("send_status", ""),
            }
        )

    gate_rows = [
        {
            "gate": "canonical_send_log_exists",
            "current": CANONICAL_SEND_LOG.exists(),
            "required": "true",
            "passes_now": "yes" if CANONICAL_SEND_LOG.exists() else "no",
        },
        {
            "gate": "v2_desktop_hash_available",
            "current": bool(desktop_hash) and len(desktop_hash) == 64,
            "required": "true",
            "passes_now": "yes" if bool(desktop_hash) and len(desktop_hash) == 64 else "no",
        },
        {
            "gate": "no_stale_v1_rows_after_overlay",
            "current": sum(1 for row in after_audit_rows if row["stale_v1_after"]),
            "required": "0",
            "passes_now": "yes" if all(not row["stale_v1_after"] for row in after_audit_rows) else "no",
        },
        {
            "gate": "all_rows_reference_v2_after_overlay",
            "current": sum(1 for row in overlaid_rows if row.get("bundle_zip") == V2_ZIP_REL),
            "required": len(overlaid_rows),
            "passes_now": "yes" if all(row.get("bundle_zip") == V2_ZIP_REL for row in overlaid_rows) else "no",
        },
        {
            "gate": "manual_status_preserved",
            "current": all(row["manual_status_preserved"] for row in after_audit_rows),
            "required": "true",
            "passes_now": "yes" if all(row["manual_status_preserved"] for row in after_audit_rows) else "no",
        },
        {
            "gate": "tracker_summary_sha_matches_v2",
            "current": tracker_summary_after.get("bundle_zip_sha256") == desktop_hash,
            "required": "true",
            "passes_now": "yes" if tracker_summary_after.get("bundle_zip_sha256") == desktop_hash else "no",
        },
        {
            "gate": "manual_send_state_not_asserted",
            "current": all(row.get("send_status") != "sent" for row in overlaid_rows),
            "required": "true unless already manually sent before overlay",
            "passes_now": "yes",
        },
        {
            "gate": "submission_ready",
            "current": False,
            "required": "false",
            "passes_now": "yes",
        },
    ]

    qa_rows = [
        {
            "check": "send log rows present",
            "result": "PASS" if len(overlaid_rows) >= 1 else "FAIL",
            "detail": f"rows={len(overlaid_rows)}",
        },
        {
            "check": "v2 hash available",
            "result": "PASS" if bool(desktop_hash) and len(desktop_hash) == 64 else "FAIL",
            "detail": f"hash_len={len(desktop_hash)}",
        },
        {
            "check": "no stale v1 rows after overlay",
            "result": "PASS" if all(not row["stale_v1_after"] for row in after_audit_rows) else "FAIL",
            "detail": f"stale_after={sum(1 for row in after_audit_rows if row['stale_v1_after'])}",
        },
        {
            "check": "manual status preserved",
            "result": "PASS" if all(row["manual_status_preserved"] for row in after_audit_rows) else "FAIL",
            "detail": "send_status is not changed by overlay.",
        },
        {
            "check": "tracker summary fingerprint updated",
            "result": "PASS" if tracker_summary_after.get("bundle_zip_sha256") == desktop_hash else "FAIL",
            "detail": "summary bundle_zip_sha256 must match v2 desktop zip hash.",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "overlay cannot change submission readiness.",
        },
    ]

    summary = {
        "package": "natcomms_canonical_send_log_v2_overlay_20260810",
        "send_log_rows": len(overlaid_rows),
        "rows_overlaid": len(overlaid_rows),
        "stale_v1_rows_before": sum(1 for row in before_rows if row["stale_v1_before"]),
        "stale_v1_rows_after": sum(1 for row in after_audit_rows if row["stale_v1_after"]),
        "v2_reference_rows_after": sum(1 for row in overlaid_rows if row.get("bundle_zip") == V2_ZIP_REL),
        "manual_status_preserved": all(row["manual_status_preserved"] for row in after_audit_rows),
        "tracker_summary_updated": tracker_summary_after.get("canonical_send_log_overlay_applied") is True,
        "tracker_summary_sha_before": tracker_summary_before.get("bundle_zip_sha256", ""),
        "tracker_summary_sha_after": tracker_summary_after.get("bundle_zip_sha256", ""),
        "tracker_summary_sha_matches_v2": tracker_summary_after.get("bundle_zip_sha256") == desktop_hash,
        "email_sent": False,
        "author_replies_collected": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "natcomms_canonical_send_log_v2_overlay_applied_not_sent",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "canonical_send_log_v2_overlay_before_after.csv",
        [
            "recipient",
            "send_status_before",
            "send_status_after",
            "sender_after",
            "sent_datetime_after",
            "bundle_zip_before",
            "bundle_zip_after",
            "stale_v1_before",
            "stale_v1_after",
            "manual_status_preserved",
        ],
        after_audit_rows,
    )
    write_csv(
        OUT_DIR / "canonical_send_log_v2_overlay_gate_matrix.csv",
        ["gate", "current", "required", "passes_now"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "canonical_send_log_v2_overlay_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Nat Comms Canonical Send Log v2 Overlay

This package updates the canonical author response send log so downstream
validators read the final v2 sendout zip path and external zip fingerprint.

Boundary: it does not send email, fill sender/timestamp fields, collect replies,
write returned files, close gates or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "NATCOMMS_CANONICAL_SEND_LOG_V2_OVERLAY_README.md", readme)

    report = f"""# Nat Comms Canonical Send Log v2 Overlay Report

Status: `{summary["status"]}`

Current result:

1. Send log rows: {summary["send_log_rows"]}
2. Rows overlaid: {summary["rows_overlaid"]}
3. Stale v1 rows before: {summary["stale_v1_rows_before"]}
4. Stale v1 rows after: {summary["stale_v1_rows_after"]}
5. V2 reference rows after: {summary["v2_reference_rows_after"]}
6. Manual status preserved: {str(summary["manual_status_preserved"]).lower()}
7. Tracker summary updated: {str(summary["tracker_summary_updated"]).lower()}
8. Tracker summary SHA matches v2: {str(summary["tracker_summary_sha_matches_v2"]).lower()}
9. Email sent: false
10. Author replies collected: false
11. Submission ready: false

Interpretation: canonical response-log validation now uses the v2 sendout zip
reference and v2 external fingerprint while preserving the unsent manual state.
"""
    write_text(OUT_DIR / "canonical_send_log_v2_overlay_report.md", report)
    write_text(
        OUT_DIR / "canonical_send_log_v2_overlay_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("NatComms canonical send log v2 overlay QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
