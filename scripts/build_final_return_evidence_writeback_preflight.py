#!/usr/bin/env python3
"""Preflight protected writeback targets for final returned evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_return_evidence_writeback_preflight_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

ROUTE_SCAN = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_route_scan.csv"
SCANNER_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json"
MANUAL_WORKSHEET = BENCH_ROOT / "reports" / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet.csv"
MANUAL_PREFLIGHT = BENCH_ROOT / "reports" / "manual_evidence_entry_preflight_20260810" / "manual_evidence_target_preflight.csv"
SAFE_EDIT = BENCH_ROOT / "reports" / "manual_evidence_final_intake_validator_20260810" / "manual_evidence_safe_edit_matrix.csv"
PRESERVATION_TARGETS = BENCH_ROOT / "reports" / "manual_field_preservation_audit_20260810" / "manual_field_preservation_targets.csv"

ROUTE_TO_WORKSHEET = {
    "RTE-001": "MEW-001",
    "RTE-002": "MEW-002",
    "RTE-003": "MEW-003",
    "RTE-004": "MEW-005",
    "RTE-005": "MEW-006",
    "RTE-006": "MEW-007",
    "RTE-007": "",
}

PORTAL_TARGET = {
    "worksheet_id": "PORTAL-LOCK",
    "evidence_type": "submission_portal_upload",
    "target_file": "reports/natcomms_submission_final_lock_validator_20260810/natcomms_submission_final_lock_portal_overlay.csv",
    "target_rows": "all portal upload rows after all upstream gates close",
    "fields_to_fill": "none until open_master_gates=0 and portal_upload_ready=true",
    "allowed_values_or_format": "real portal upload evidence only after final lock validator passes",
    "do_not_edit": "all generated portal overlay fields before final lock",
    "after_fill_validation": "py scripts/build_natcomms_submission_final_lock_validator.py",
}


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
    marker = "### 19.17 Final return evidence writeback preflight update"
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

    route_rows = read_csv(ROUTE_SCAN)
    scanner_summary = read_json(SCANNER_SUMMARY)
    worksheet_rows = {row["worksheet_id"]: row for row in read_csv(MANUAL_WORKSHEET)}
    preflight_rows = {row["worksheet_id"]: row for row in read_csv(MANUAL_PREFLIGHT)}
    safe_rows = {row["worksheet_id"]: row for row in read_csv(SAFE_EDIT)}
    preservation_rows = read_csv(PRESERVATION_TARGETS)

    writeback_rows: list[dict[str, object]] = []
    protected_rows: list[dict[str, object]] = []
    command_rows: list[dict[str, object]] = []

    for route in route_rows:
        route_id = route["route_id"]
        worksheet_id = ROUTE_TO_WORKSHEET.get(route_id, "")
        if worksheet_id:
            worksheet = worksheet_rows.get(worksheet_id, {})
            preflight = preflight_rows.get(worksheet_id, {})
            safe = safe_rows.get(worksheet_id, {})
        else:
            worksheet = PORTAL_TARGET
            preflight = {
                "target_status": "blocked_until_all_upstream_gates_close",
                "completion_detail": "portal upload remains disallowed",
                "blocking_reason": "submission_ready=false and portal_upload_ready=false",
                "resolved_target_exists": "True",
            }
            safe = {
                "safe_to_edit_now": "no",
                "safe_to_rerun_after_edit": "no",
                "required_next_proof": "open_master_gates=0; portal_upload_ready=true; final portal upload evidence",
            }
            worksheet_id = PORTAL_TARGET["worksheet_id"]

        candidate_files = int(route.get("candidate_files", 0))
        safe_to_edit_now = safe.get("safe_to_edit_now", "no")
        target_status = preflight.get("target_status", "")
        writeback_allowed = "yes" if candidate_files > 0 and safe_to_edit_now == "yes" and target_status == "ready_for_manual_entry" else "no"
        reason = (
            "Candidate files exist and target is ready for protected manual entry."
            if writeback_allowed == "yes"
            else "No writeback: candidate files are absent or target is not ready for protected manual entry."
        )
        if route_id == "RTE-007":
            reason = "No writeback: portal submission evidence is forbidden until all upstream final lock gates close."

        writeback_rows.append(
            {
                "route_id": route_id,
                "closeout_action": route["closeout_action"],
                "worksheet_id": worksheet_id,
                "evidence_type": worksheet.get("evidence_type", ""),
                "target_file": worksheet.get("target_file", ""),
                "target_status": target_status,
                "candidate_files": candidate_files,
                "safe_to_edit_now": safe_to_edit_now,
                "safe_to_rerun_after_edit": safe.get("safe_to_rerun_after_edit", "no"),
                "fields_to_fill": worksheet.get("fields_to_fill", ""),
                "do_not_edit": worksheet.get("do_not_edit", ""),
                "required_next_proof": safe.get("required_next_proof", ""),
                "writeback_allowed_now": writeback_allowed,
                "reason": reason,
            }
        )
        command_rows.append(
            {
                "sequence": len(command_rows) + 1,
                "route_id": route_id,
                "worksheet_id": worksheet_id,
                "command": worksheet.get("after_fill_validation", ""),
                "currently_allowed": "yes" if writeback_allowed == "yes" else "no",
                "reason": reason,
            }
        )

    for row in preservation_rows:
        protected_rows.append(
            {
                "artifact": row.get("artifact", ""),
                "key_field": row.get("key_field", ""),
                "manual_field": row.get("manual_field", ""),
                "owner": row.get("owner", ""),
                "preservation_detected": row.get("preservation_detected", ""),
                "status": row.get("status", ""),
            }
        )

    no_go_rows = [
        {
            "rule_id": "WB-NG-001",
            "rule": "Do not write raw returned files directly into generated tracker summaries.",
            "reason": "Only protected target fields may be edited after evidence is manually inspected.",
        },
        {
            "rule_id": "WB-NG-002",
            "rule": "Do not rerun finalization validators as if evidence passed when candidate_return_files=0.",
            "reason": "The scanner reports no returned evidence.",
        },
        {
            "rule_id": "WB-NG-003",
            "rule": "Do not edit portal upload overlay fields before all upstream gates close.",
            "reason": "submission_ready=false and portal upload remains blocked.",
        },
        {
            "rule_id": "WB-NG-004",
            "rule": "Do not overwrite protected author/manual fields by regenerating blank packets.",
            "reason": "Manual field preservation targets must remain protected across reruns.",
        },
    ]

    writeback_allowed_rows = [row for row in writeback_rows if row["writeback_allowed_now"] == "yes"]
    safe_edit_rows = [row for row in writeback_rows if row["safe_to_edit_now"] == "yes"]
    safe_rerun_rows = [row for row in writeback_rows if row["safe_to_rerun_after_edit"] == "yes"]

    qa_rows = [
        {
            "check": "all_routes_have_writeback_decision",
            "result": "PASS" if len(writeback_rows) == scanner_summary.get("routes_scanned") == 7 else "FAIL",
            "detail": f"writeback_rows={len(writeback_rows)}; routes_scanned={scanner_summary.get('routes_scanned')}",
        },
        {
            "check": "no_writeback_without_candidate_files",
            "result": "PASS" if scanner_summary.get("candidate_return_files") == 0 and not writeback_allowed_rows else "FAIL",
            "detail": f"candidate_return_files={scanner_summary.get('candidate_return_files')}; writeback_allowed_rows={len(writeback_allowed_rows)}",
        },
        {
            "check": "protected_fields_imported",
            "result": "PASS" if len(protected_rows) >= 9 and all(row["status"] == "protected" for row in protected_rows) else "FAIL",
            "detail": f"protected_rows={len(protected_rows)}",
        },
        {
            "check": "no_safe_rerun_after_edit",
            "result": "PASS" if not safe_rerun_rows else "FAIL",
            "detail": f"safe_rerun_rows={len(safe_rerun_rows)}",
        },
        {
            "check": "submission_still_blocked",
            "result": "PASS" if scanner_summary.get("submission_ready") is False else "FAIL",
            "detail": f"submission_ready={scanner_summary.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "final_return_writeback_route_matrix.csv", writeback_rows, ["route_id", "closeout_action", "worksheet_id", "evidence_type", "target_file", "target_status", "candidate_files", "safe_to_edit_now", "safe_to_rerun_after_edit", "fields_to_fill", "do_not_edit", "required_next_proof", "writeback_allowed_now", "reason"])
    write_csv(OUT_DIR / "final_return_writeback_protected_targets.csv", protected_rows, ["artifact", "key_field", "manual_field", "owner", "preservation_detected", "status"])
    write_csv(OUT_DIR / "final_return_writeback_validation_commands.csv", command_rows, ["sequence", "route_id", "worksheet_id", "command", "currently_allowed", "reason"])
    write_csv(OUT_DIR / "final_return_writeback_no_go_rules.csv", no_go_rows, ["rule_id", "rule", "reason"])
    write_csv(OUT_DIR / "final_return_writeback_preflight_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Final return evidence writeback preflight 2026-08-10",
        "",
        "Status: `final_return_evidence_writeback_preflight_ready_no_writeback`",
        "",
        f"1. Writeback route rows: {len(writeback_rows)}",
        f"2. Safe edit rows: {len(safe_edit_rows)}",
        f"3. Writeback allowed rows: {len(writeback_allowed_rows)}",
        f"4. Protected target rows: {len(protected_rows)}",
        f"5. Validation command rows: {len(command_rows)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this preflight maps returned evidence routes to protected manual targets only. It does not edit files, write back tracker fields, close gates, rerun validators automatically, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_RETURN_EVIDENCE_WRITEBACK_PREFLIGHT_README.md", "\n".join(report))
    write_text(OUT_DIR / "final_return_evidence_writeback_preflight_report.md", "\n".join(report))

    summary = {
        "package": "final_return_evidence_writeback_preflight_20260810",
        "writeback_route_rows": len(writeback_rows),
        "safe_edit_rows": len(safe_edit_rows),
        "safe_rerun_rows": len(safe_rerun_rows),
        "writeback_allowed_rows": len(writeback_allowed_rows),
        "protected_target_rows": len(protected_rows),
        "validation_command_rows": len(command_rows),
        "no_go_rules": len(no_go_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": scanner_summary.get("candidate_return_files"),
        "manual_actions_executed": False,
        "evidence_writeback_performed": False,
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "final_return_evidence_writeback_preflight_ready_no_writeback",
    }

    section = f"""### 19.17 Final return evidence writeback preflight update

Added a writeback preflight that maps the seven canonical return routes to protected manual targets before any tracker edit.

New directory: `{OUT_DIR}`

New files:
1. `final_return_writeback_route_matrix.csv`
2. `final_return_writeback_protected_targets.csv`
3. `final_return_writeback_validation_commands.csv`
4. `final_return_writeback_no_go_rules.csv`
5. `final_return_writeback_preflight_qa.csv`
6. `FINAL_RETURN_EVIDENCE_WRITEBACK_PREFLIGHT_README.md`
7. `final_return_evidence_writeback_preflight_report.md`
8. `final_return_evidence_writeback_preflight_summary.json`

Current result:
1. writeback_route_rows = {summary['writeback_route_rows']}
2. safe_edit_rows = {summary['safe_edit_rows']}
3. safe_rerun_rows = {summary['safe_rerun_rows']}
4. writeback_allowed_rows = {summary['writeback_allowed_rows']}
5. protected_target_rows = {summary['protected_target_rows']}
6. validation_command_rows = {summary['validation_command_rows']}
7. candidate_return_files = {summary['candidate_return_files']}
8. evidence_writeback_performed = false
9. gate_closure_allowed = false
10. submission_ready = false

Boundary:
1. This preflight maps returned evidence routes to protected manual target fields only.
2. It does not edit tracker files or write back evidence.
3. It does not close gates, rerun validators automatically, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_return_evidence_writeback_preflight_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Final return evidence writeback preflight QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
