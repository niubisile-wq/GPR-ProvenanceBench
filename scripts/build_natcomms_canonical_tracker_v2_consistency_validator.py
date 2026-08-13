#!/usr/bin/env python3
"""Validate Nat Comms canonical tracker consistency after v2 sendout overlay."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_canonical_tracker_v2_consistency_validator_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"
V2_BUNDLE_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810"
OVERLAY_DIR = BENCH_ROOT / "reports" / "natcomms_canonical_send_log_v2_overlay_20260810"
LOG_VALIDATOR_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_log_validator_20260810"
RECEIPT_VALIDATOR_DIR = BENCH_ROOT / "reports" / "natcomms_sendout_evidence_receipt_completion_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

EXPECTED_V2_ZIP = r"reports\natcomms_author_sendout_bundle_v2_20260810\NatComms_author_sendout_bundle_v2_20260810.zip"
STALE_V1_ZIP = "NatComms_author_sendout_bundle_20260810.zip"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.37 NatComms canonical tracker v2 consistency validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/natcomms_canonical_tracker_v2_consistency_validator_20260810/`，把 canonical send log、tracker summary、v2 zip fingerprint、overlay summary、response log validator 和 19.35 receipt validator 的一致性固化为独立验收。
- 当前 `send_log_rows={summary["send_log_rows"]}`，`send_log_v2_rows={summary["send_log_v2_rows"]}`，`send_log_stale_v1_rows={summary["send_log_stale_v1_rows"]}`。
- 当前 `tracker_summary_sha_matches_v2={str(summary["tracker_summary_sha_matches_v2"]).lower()}`，`overlay_summary_pass={str(summary["overlay_summary_pass"]).lower()}`，`response_log_guarded={str(summary["response_log_guarded"]).lower()}`。
- 当前 `receipt_validator_guarded={str(summary["receipt_validator_guarded"]).lower()}`，`email_sent=false`，`author_replies_collected=false`，`submission_ready=false`。
- 边界：该 validator 只读一致性状态，不发送邮件、不填写回执、不接收文件、不写 protected targets、不关闭 gate。
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

    send_log_rows = read_csv(TRACKER_DIR / "author_response_send_log_template.csv")
    tracker_summary = read_json(TRACKER_DIR / "author_response_tracker_summary.json")
    fingerprint_rows = read_csv(V2_BUNDLE_DIR / "author_sendout_bundle_v2_zip_fingerprint.csv")
    overlay_summary = read_json(OVERLAY_DIR / "canonical_send_log_v2_overlay_summary.json")
    response_log_summary = read_json(LOG_VALIDATOR_DIR / "author_response_log_validator_summary.json")
    receipt_summary = read_json(RECEIPT_VALIDATOR_DIR / "sendout_evidence_receipt_completion_validator_summary.json")

    v2_hashes = {row["artifact"]: row["sha256"] for row in fingerprint_rows}
    report_hash = v2_hashes.get("report_zip", "")
    desktop_hash = v2_hashes.get("desktop_zip", "")
    expected_hash = desktop_hash or report_hash

    send_log_audit_rows = []
    for row in send_log_rows:
        bundle_zip = row.get("bundle_zip", "")
        bundle_sha = row.get("bundle_zip_sha256", "")
        send_log_audit_rows.append(
            {
                "recipient": row.get("recipient", ""),
                "send_status": row.get("send_status", ""),
                "bundle_zip": bundle_zip,
                "bundle_zip_sha256": bundle_sha,
                "points_to_expected_v2_zip": bundle_zip == EXPECTED_V2_ZIP,
                "contains_stale_v1_zip": STALE_V1_ZIP in bundle_zip,
                "sha_matches_v2_fingerprint": bool(expected_hash) and bundle_sha == expected_hash,
                "manual_unsent_state_preserved": row.get("send_status") == "not_sent"
                and not row.get("sent_datetime_local")
                and not row.get("sender"),
            }
        )

    tracker_summary_sha_matches_v2 = tracker_summary.get("bundle_zip_sha256") == expected_hash
    tracker_summary_path_matches_v2 = tracker_summary.get("bundle_zip") == EXPECTED_V2_ZIP
    overlay_summary_pass = (
        overlay_summary.get("qa_pass") is True
        and overlay_summary.get("stale_v1_rows_after") == 0
        and overlay_summary.get("tracker_summary_sha_matches_v2") is True
    )
    response_log_guarded = (
        response_log_summary.get("qa_pass") is True
        and response_log_summary.get("send_log_valid") is True
        and response_log_summary.get("all_sent") is False
        and response_log_summary.get("author_reply_ingestion_allowed") is False
        and response_log_summary.get("submission_ready") is False
    )
    receipt_validator_guarded = (
        receipt_summary.get("qa_pass") is True
        and receipt_summary.get("send_receipt_complete") is False
        and receipt_summary.get("return_intake_allowed") is False
        and receipt_summary.get("rb001_drop_allowed") is False
        and receipt_summary.get("submission_ready") is False
    )

    crosscheck_rows = [
        {
            "check": "send_log_all_rows_point_to_v2",
            "current": sum(1 for row in send_log_audit_rows if row["points_to_expected_v2_zip"]),
            "required": len(send_log_audit_rows),
            "passes_now": "yes" if all(row["points_to_expected_v2_zip"] for row in send_log_audit_rows) else "no",
        },
        {
            "check": "send_log_no_stale_v1_rows",
            "current": sum(1 for row in send_log_audit_rows if row["contains_stale_v1_zip"]),
            "required": 0,
            "passes_now": "yes" if all(not row["contains_stale_v1_zip"] for row in send_log_audit_rows) else "no",
        },
        {
            "check": "send_log_sha_matches_v2",
            "current": sum(1 for row in send_log_audit_rows if row["sha_matches_v2_fingerprint"]),
            "required": len(send_log_audit_rows),
            "passes_now": "yes" if all(row["sha_matches_v2_fingerprint"] for row in send_log_audit_rows) else "no",
        },
        {
            "check": "tracker_summary_path_matches_v2",
            "current": tracker_summary_path_matches_v2,
            "required": "true",
            "passes_now": "yes" if tracker_summary_path_matches_v2 else "no",
        },
        {
            "check": "tracker_summary_sha_matches_v2",
            "current": tracker_summary_sha_matches_v2,
            "required": "true",
            "passes_now": "yes" if tracker_summary_sha_matches_v2 else "no",
        },
        {
            "check": "overlay_summary_pass",
            "current": overlay_summary_pass,
            "required": "true",
            "passes_now": "yes" if overlay_summary_pass else "no",
        },
        {
            "check": "response_log_guarded",
            "current": response_log_guarded,
            "required": "true",
            "passes_now": "yes" if response_log_guarded else "no",
        },
        {
            "check": "receipt_validator_guarded",
            "current": receipt_validator_guarded,
            "required": "true",
            "passes_now": "yes" if receipt_validator_guarded else "no",
        },
        {
            "check": "submission_ready",
            "current": False,
            "required": "false",
            "passes_now": "yes",
        },
    ]

    qa_rows = [
        {
            "check": "send log rows present",
            "result": "PASS" if len(send_log_rows) == 5 else "FAIL",
            "detail": f"rows={len(send_log_rows)}",
        },
        {
            "check": "v2 fingerprint hashes match",
            "result": "PASS" if bool(expected_hash) and report_hash == desktop_hash else "FAIL",
            "detail": f"report_hash={report_hash}; desktop_hash={desktop_hash}",
        },
        {
            "check": "send log has no stale v1 references",
            "result": "PASS" if all(not row["contains_stale_v1_zip"] for row in send_log_audit_rows) else "FAIL",
            "detail": f"stale_rows={sum(1 for row in send_log_audit_rows if row['contains_stale_v1_zip'])}",
        },
        {
            "check": "tracker summary matches v2",
            "result": "PASS" if tracker_summary_sha_matches_v2 and tracker_summary_path_matches_v2 else "FAIL",
            "detail": f"summary_sha={tracker_summary.get('bundle_zip_sha256')}",
        },
        {
            "check": "downstream validators remain guarded",
            "result": "PASS" if response_log_guarded and receipt_validator_guarded else "FAIL",
            "detail": "manual sendout and RB-001 drop must remain blocked.",
        },
    ]

    summary = {
        "package": "natcomms_canonical_tracker_v2_consistency_validator_20260810",
        "send_log_rows": len(send_log_rows),
        "send_log_v2_rows": sum(1 for row in send_log_audit_rows if row["points_to_expected_v2_zip"]),
        "send_log_stale_v1_rows": sum(1 for row in send_log_audit_rows if row["contains_stale_v1_zip"]),
        "send_log_sha_match_rows": sum(1 for row in send_log_audit_rows if row["sha_matches_v2_fingerprint"]),
        "tracker_summary_path_matches_v2": tracker_summary_path_matches_v2,
        "tracker_summary_sha_matches_v2": tracker_summary_sha_matches_v2,
        "overlay_summary_pass": overlay_summary_pass,
        "response_log_guarded": response_log_guarded,
        "receipt_validator_guarded": receipt_validator_guarded,
        "email_sent": False,
        "author_replies_collected": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "natcomms_canonical_tracker_v2_consistency_validator_passed_guarded_not_sent",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "canonical_tracker_v2_send_log_audit.csv",
        [
            "recipient",
            "send_status",
            "bundle_zip",
            "bundle_zip_sha256",
            "points_to_expected_v2_zip",
            "contains_stale_v1_zip",
            "sha_matches_v2_fingerprint",
            "manual_unsent_state_preserved",
        ],
        send_log_audit_rows,
    )
    write_csv(
        OUT_DIR / "canonical_tracker_v2_crosscheck_matrix.csv",
        ["check", "current", "required", "passes_now"],
        crosscheck_rows,
    )
    write_csv(
        OUT_DIR / "canonical_tracker_v2_consistency_validator_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# Nat Comms Canonical Tracker v2 Consistency Validator

This validator checks that the canonical author response tracker, v2 sendout zip
fingerprints, overlay summary, response-log validator and sendout receipt
validator agree after v2 packaging.

Boundary: this package is read-only. It does not send email, fill manual
evidence, collect replies, copy returned files, write protected targets, close
gates or make the manuscript submission-ready.
"""
    write_text(OUT_DIR / "NATCOMMS_CANONICAL_TRACKER_V2_CONSISTENCY_VALIDATOR_README.md", readme)

    report = f"""# Nat Comms Canonical Tracker v2 Consistency Validator Report

Status: `{summary["status"]}`

Current result:

1. Send log rows: {summary["send_log_rows"]}
2. Send log v2 rows: {summary["send_log_v2_rows"]}
3. Send log stale v1 rows: {summary["send_log_stale_v1_rows"]}
4. Send log SHA match rows: {summary["send_log_sha_match_rows"]}
5. Tracker summary path matches v2: {str(summary["tracker_summary_path_matches_v2"]).lower()}
6. Tracker summary SHA matches v2: {str(summary["tracker_summary_sha_matches_v2"]).lower()}
7. Overlay summary pass: {str(summary["overlay_summary_pass"]).lower()}
8. Response log guarded: {str(summary["response_log_guarded"]).lower()}
9. Receipt validator guarded: {str(summary["receipt_validator_guarded"]).lower()}
10. Submission ready: false

Interpretation: the canonical tracker is internally aligned to the v2 sendout
package while real sendout, returned-file intake and RB-001 drop remain blocked.
"""
    write_text(OUT_DIR / "canonical_tracker_v2_consistency_validator_report.md", report)
    write_text(
        OUT_DIR / "canonical_tracker_v2_consistency_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("NatComms canonical tracker v2 consistency validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
