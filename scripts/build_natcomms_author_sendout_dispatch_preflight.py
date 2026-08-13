#!/usr/bin/env python3
"""Build a final pre-dispatch preflight for the Nat Comms author sendout bundle."""

from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_dispatch_preflight_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

BUNDLE_DIR = BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810"
GUARD_DIR = BENCH_ROOT / "reports" / "natcomms_manual_sendout_execution_guard_20260810"
TRACKER_DIR = BENCH_ROOT / "reports" / "natcomms_author_response_tracker_20260810"

BUNDLE_SUMMARY = BUNDLE_DIR / "author_sendout_bundle_v2_summary.json"
BUNDLE_MANIFEST = BUNDLE_DIR / "author_sendout_bundle_v2_manifest.csv"
BUNDLE_ROUTE = BUNDLE_DIR / "author_sendout_bundle_v2_recipient_route.csv"
REPORT_ZIP = BUNDLE_DIR / "NatComms_author_sendout_bundle_v2_20260810.zip"
DESKTOP_ZIP = Path.home() / "Desktop" / "NatComms_author_sendout_bundle_v2_20260810.zip"
GUARD_SUMMARY = GUARD_DIR / "manual_sendout_execution_guard_summary.json"
GUARD_CHECKLIST = GUARD_DIR / "manual_sendout_execution_checklist.csv"
SEND_LOG = TRACKER_DIR / "author_response_send_log_template.csv"
RETURN_TRACKER = TRACKER_DIR / "author_response_return_tracker.csv"


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_member_count(path: Path) -> int:
    if not path.exists():
        return 0
    with zipfile.ZipFile(path, "r") as handle:
        return len([item for item in handle.infolist() if not item.is_dir()])


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.07 Nature Communications author sendout dispatch preflight update"
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

    bundle_summary = read_json(BUNDLE_SUMMARY)
    guard_summary = read_json(GUARD_SUMMARY)
    manifest_rows = read_csv(BUNDLE_MANIFEST)
    route_rows = read_csv(BUNDLE_ROUTE)
    guard_rows = read_csv(GUARD_CHECKLIST)
    send_rows = read_csv(SEND_LOG)
    return_rows = read_csv(RETURN_TRACKER)

    report_zip_exists = REPORT_ZIP.exists()
    desktop_zip_exists = DESKTOP_ZIP.exists()
    report_zip_sha = sha256(REPORT_ZIP) if report_zip_exists else ""
    desktop_zip_sha = sha256(DESKTOP_ZIP) if desktop_zip_exists else ""
    zip_sha_match = report_zip_sha == desktop_zip_sha and bool(report_zip_sha)
    report_zip_members = zip_member_count(REPORT_ZIP)
    desktop_zip_members = zip_member_count(DESKTOP_ZIP)

    unique_recipients = sorted({row.get("recipient", "") for row in manifest_rows if row.get("recipient")})
    not_sent_rows = [row for row in send_rows if row.get("send_status") != "sent"]

    dispatch_rows = [
        {
            "check_id": "DISPATCH-001",
            "check": "v2_bundle_summary_passed",
            "current_state": f"qa_pass={bundle_summary.get('qa_pass')}; files={bundle_summary.get('total_bundled_files')}",
            "passes_now": "yes" if bundle_summary.get("qa_pass") is True and bundle_summary.get("total_bundled_files") == 19 else "no",
            "action_before_send": "Use only the v2 bundle and do not substitute older zips.",
        },
        {
            "check_id": "DISPATCH-002",
            "check": "desktop_and_report_zip_match",
            "current_state": f"report_members={report_zip_members}; desktop_members={desktop_zip_members}; sha_match={zip_sha_match}",
            "passes_now": "yes" if zip_sha_match and report_zip_members == desktop_zip_members and report_zip_members > 0 else "no",
            "action_before_send": "If this fails, rebuild bundle v2 and manual sendout guard before sending.",
        },
        {
            "check_id": "DISPATCH-003",
            "check": "recipient_routes_defined",
            "current_state": f"route_rows={len(route_rows)}; recipients={len(unique_recipients)}",
            "passes_now": "yes" if len(route_rows) >= 5 and len(unique_recipients) >= 5 else "no",
            "action_before_send": "Confirm the real recipients for each logical recipient role.",
        },
        {
            "check_id": "DISPATCH-004",
            "check": "manual_sendout_guard_ready",
            "current_state": f"qa_pass={guard_summary.get('qa_pass')}; manual_steps={guard_summary.get('manual_execution_steps')}",
            "passes_now": "yes" if guard_summary.get("qa_pass") is True and guard_summary.get("manual_execution_steps") == 9 else "no",
            "action_before_send": "Follow the manual sendout execution guard in order.",
        },
        {
            "check_id": "DISPATCH-005",
            "check": "send_log_still_not_sent",
            "current_state": f"send_rows={len(send_rows)}; not_sent_rows={len(not_sent_rows)}",
            "passes_now": "yes" if len(send_rows) == len(not_sent_rows) and len(send_rows) >= 5 else "no",
            "action_before_send": "Fill send status only after real manual transmission.",
        },
    ]

    recipient_rows = []
    for recipient in unique_recipients:
        files = [row for row in manifest_rows if row.get("recipient") == recipient]
        recipient_rows.append(
            {
                "recipient_role": recipient,
                "attachment_count": len(files),
                "attachment_ids": ";".join(row["attachment_id"] for row in files),
                "recommended_bundle": str(DESKTOP_ZIP),
                "send_status_now": "not_sent",
                "required_real_world_action": "Confirm person/email/channel, send manually, then record timestamp and sender in send log.",
            }
        )

    evidence_rows = [
        {
            "evidence_id": "SEND-EVID-001",
            "field": "actual_recipient_name_or_email",
            "where_to_record": str(SEND_LOG.relative_to(BENCH_ROOT)),
            "allowed_now": "after_real_send_only",
            "current_value": "",
        },
        {
            "evidence_id": "SEND-EVID-002",
            "field": "sent_datetime_local",
            "where_to_record": str(SEND_LOG.relative_to(BENCH_ROOT)),
            "allowed_now": "after_real_send_only",
            "current_value": "",
        },
        {
            "evidence_id": "SEND-EVID-003",
            "field": "returned_file_path",
            "where_to_record": str(RETURN_TRACKER.relative_to(BENCH_ROOT)),
            "allowed_now": "after_returned_file_received_only",
            "current_value": "",
        },
        {
            "evidence_id": "SEND-EVID-004",
            "field": "backend_choice",
            "where_to_record": "reports/natcomms_author_finalization_reply_packet_20260810/figure_backend_decision_ticket.csv",
            "allowed_now": "after_author_reply_only",
            "current_value": "",
        },
        {
            "evidence_id": "SEND-EVID-005",
            "field": "rights_licence_decision",
            "where_to_record": "reports/natcomms_author_finalization_reply_packet_20260810/licence_rights_reply_sheet.csv",
            "allowed_now": "after_author_reply_only",
            "current_value": "",
        },
    ]

    no_go_rows = [
        {"rule_id": "DISPATCH-NOGO-001", "rule": "Do not mark email_sent=true from this preflight; only a real manual send record can do that."},
        {"rule_id": "DISPATCH-NOGO-002", "rule": "Do not send older author bundles when v2 is available and checked."},
        {"rule_id": "DISPATCH-NOGO-003", "rule": "Do not edit protected author/manual fields before returned evidence exists."},
        {"rule_id": "DISPATCH-NOGO-004", "rule": "Do not infer backend_selected, author_replies_collected or submission_ready from dispatch readiness."},
        {"rule_id": "DISPATCH-NOGO-005", "rule": "Do not claim blind external validation, DOI/rights, final figures, final references or Reporting Summary are complete."},
    ]

    qa_rows = [
        {
            "check": "bundle_v2_manifest_complete",
            "result": "PASS" if len(manifest_rows) == 19 else "FAIL",
            "detail": f"manifest_rows={len(manifest_rows)}",
        },
        {
            "check": "zip_copies_match",
            "result": "PASS" if zip_sha_match and report_zip_members == desktop_zip_members else "FAIL",
            "detail": f"zip_sha_match={zip_sha_match}; report_members={report_zip_members}; desktop_members={desktop_zip_members}",
        },
        {
            "check": "recipient_dispatch_sheet_ready",
            "result": "PASS" if len(recipient_rows) >= 5 else "FAIL",
            "detail": f"recipient_rows={len(recipient_rows)}",
        },
        {
            "check": "send_log_preserves_not_sent_state",
            "result": "PASS" if len(send_rows) == len(not_sent_rows) and len(send_rows) >= 5 else "FAIL",
            "detail": f"send_rows={len(send_rows)}; not_sent_rows={len(not_sent_rows)}",
        },
        {
            "check": "guard_inputs_indexed",
            "result": "PASS" if len(guard_rows) == 9 and guard_summary.get("qa_pass") is True else "FAIL",
            "detail": f"guard_rows={len(guard_rows)}; guard_qa_pass={guard_summary.get('qa_pass')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "author_sendout_dispatch_preflight_matrix.csv", dispatch_rows, ["check_id", "check", "current_state", "passes_now", "action_before_send"])
    write_csv(OUT_DIR / "author_sendout_recipient_dispatch_sheet.csv", recipient_rows, ["recipient_role", "attachment_count", "attachment_ids", "recommended_bundle", "send_status_now", "required_real_world_action"])
    write_csv(OUT_DIR / "author_sendout_evidence_record_template.csv", evidence_rows, ["evidence_id", "field", "where_to_record", "allowed_now", "current_value"])
    write_csv(OUT_DIR / "author_sendout_dispatch_no_go_rules.csv", no_go_rows, ["rule_id", "rule"])
    write_csv(OUT_DIR / "author_sendout_dispatch_preflight_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Nat Comms author sendout dispatch preflight 2026-08-10",
        "",
        "Status: `author_sendout_dispatch_preflight_ready_not_sent`",
        "",
        f"1. Bundle v2 manifest rows: {len(manifest_rows)}",
        f"2. Recipient dispatch rows: {len(recipient_rows)}",
        f"3. Dispatch preflight checks: {len(dispatch_rows)}",
        f"4. Evidence template rows: {len(evidence_rows)}",
        f"5. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this preflight makes manual dispatch safer, but it does not send email, collect replies, select backend or close submission gates.",
        "",
    ]
    write_text(OUT_DIR / "AUTHOR_SENDOUT_DISPATCH_PREFLIGHT_README.md", "\n".join(report))
    write_text(OUT_DIR / "author_sendout_dispatch_preflight_report.md", "\n".join(report))

    summary = {
        "package": "natcomms_author_sendout_dispatch_preflight_20260810",
        "bundle_manifest_rows": len(manifest_rows),
        "recipient_dispatch_rows": len(recipient_rows),
        "dispatch_preflight_checks": len(dispatch_rows),
        "evidence_template_rows": len(evidence_rows),
        "no_go_rules": len(no_go_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "report_zip_members": report_zip_members,
        "desktop_zip_members": desktop_zip_members,
        "zip_sha_match": zip_sha_match,
        "email_sent": False,
        "author_replies_collected": False,
        "backend_selected": False,
        "submission_ready": False,
        "status": "author_sendout_dispatch_preflight_ready_not_sent",
    }

    section = f"""### 19.07 Nature Communications author sendout dispatch preflight update

Added a final pre-dispatch preflight for the Nature Communications author sendout bundle v2.

New directory: `{OUT_DIR}`

New files:
1. `author_sendout_dispatch_preflight_matrix.csv`
2. `author_sendout_recipient_dispatch_sheet.csv`
3. `author_sendout_evidence_record_template.csv`
4. `author_sendout_dispatch_no_go_rules.csv`
5. `author_sendout_dispatch_preflight_qa.csv`
6. `AUTHOR_SENDOUT_DISPATCH_PREFLIGHT_README.md`
7. `author_sendout_dispatch_preflight_report.md`
8. `author_sendout_dispatch_preflight_summary.json`

Current result:
1. bundle_manifest_rows = {summary['bundle_manifest_rows']}
2. recipient_dispatch_rows = {summary['recipient_dispatch_rows']}
3. dispatch_preflight_checks = {summary['dispatch_preflight_checks']}
4. evidence_template_rows = {summary['evidence_template_rows']}
5. zip_sha_match = {str(summary['zip_sha_match']).lower()}
6. email_sent = false
7. author_replies_collected = false
8. backend_selected = false
9. submission_ready = false

Boundary:
1. This preflight makes manual dispatch safer.
2. It does not send email or collect replies.
3. It does not select backend, lock figures or close submission gates."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "author_sendout_dispatch_preflight_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Author sendout dispatch preflight QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
