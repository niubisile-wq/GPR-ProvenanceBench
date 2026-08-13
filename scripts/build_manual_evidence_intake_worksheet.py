#!/usr/bin/env python3
"""Build a consolidated worksheet for entering real manual-dispatch evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manual_evidence_intake_worksheet_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

VALIDATOR_SUMMARY = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"
VALIDATOR_MATRIX = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_matrix.csv"
DISPATCH_QUEUE = REPORTS / "manual_dispatch_master_packet_20260810" / "manual_dispatch_master_queue.csv"


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
    text = DESKTOP_PLAN.read_text(encoding="utf-8")
    marker = "### 18.82 Manual evidence intake worksheet update"
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

    validator_summary = read_json(VALIDATOR_SUMMARY)
    validator_rows = read_csv(VALIDATOR_MATRIX)
    dispatch_rows = read_csv(DISPATCH_QUEUE)

    worksheet_rows = [
        {
            "worksheet_id": "MEW-001",
            "dispatch_id": "MD-001",
            "evidence_type": "real_author_sendout",
            "target_file": "reports/natcomms_author_response_tracker_20260810/author_response_send_log_template.csv",
            "target_rows": "all five recipient rows",
            "fields_to_fill": "send_status; sent_datetime_local; sender",
            "allowed_values_or_format": "send_status=sent; sent_datetime_local=YYYY-MM-DD HH:MM; sender=real sender name/account",
            "do_not_edit": "recipient; bundle_zip; bundle_zip_sha256; required_manual_action",
            "after_fill_validation": "py scripts\\build_natcomms_author_response_log_validator.py",
        },
        {
            "worksheet_id": "MEW-002",
            "dispatch_id": "MD-001",
            "evidence_type": "returned_author_reply_files",
            "target_file": "reports/natcomms_author_response_tracker_20260810/author_response_return_tracker.csv",
            "target_rows": "returned attachment rows",
            "fields_to_fill": "return_status; returned_file_path; returned_datetime_local",
            "allowed_values_or_format": "return_status=returned; returned_file_path=existing returned file; returned_datetime_local=YYYY-MM-DD HH:MM",
            "do_not_edit": "attachment_id; recipient; bundle_file; expected_reply_field; gate_effect",
            "after_fill_validation": "py scripts\\build_natcomms_author_reply_ingestion_validator.py",
        },
        {
            "worksheet_id": "MEW-003",
            "dispatch_id": "MD-002",
            "evidence_type": "backend_and_scope_choice",
            "target_file": "reports/natcomms_author_finalization_reply_packet_20260810/figure_backend_decision_ticket.csv",
            "target_rows": "FIG-BACKEND-001; FIG-BACKEND-002",
            "fields_to_fill": "current_choice",
            "allowed_values_or_format": "Python or R; Figure 1-Figure 6 or reduced display set with SI relocation",
            "do_not_edit": "recommended_choice; allowed_choices; evidence_or_reason; after_choice_action",
            "after_fill_validation": "py scripts\\build_figure_backend_decision_validator.py",
        },
        {
            "worksheet_id": "MEW-004",
            "dispatch_id": "MD-003",
            "evidence_type": "external_blind_asset_payload",
            "target_file": "external_blind/<dated_asset_folder> plus data_manifests/external_blind_manifest_<asset>_YYYYMMDD.csv",
            "target_rows": "new files, not existing README",
            "fields_to_fill": "unlabeled payload files; manifest rows; sealed label holder information outside analyst workflow",
            "allowed_values_or_format": "No labels or label hints before prediction freeze; strict SHA manifest required",
            "do_not_edit": "do not place label files in analyst-visible folder before prediction freeze",
            "after_fill_validation": "py scripts\\validate_external_blind_intake.py --strict-sha",
        },
        {
            "worksheet_id": "MEW-005",
            "dispatch_id": "MD-004",
            "evidence_type": "rights_licence_decisions",
            "target_file": "reports/rights_licence_completion_handoff_20260810/rights_licence_decision_matrix.csv or upstream author/rights reply sheet",
            "target_rows": "Code/scripts; Derived source-data; Rendered figures; raw third-party exclusion",
            "fields_to_fill": "current_decision plus documented evidence in returned rights file",
            "allowed_values_or_format": "explicit licence or explicit exclusion/permission decision; raw third-party data excluded unless written permission",
            "do_not_edit": "required_evidence_to_close; release_consequence_if_open",
            "after_fill_validation": "py scripts\\build_rights_licence_completion_handoff.py",
        },
        {
            "worksheet_id": "MEW-006",
            "dispatch_id": "MD-005",
            "evidence_type": "reporting_summary_author_replies",
            "target_file": "reports/natcomms_author_finalization_reply_packet_20260810/reporting_summary_author_reply_sheet.csv",
            "target_rows": "all four confirmation rows",
            "fields_to_fill": "author_reply",
            "allowed_values_or_format": "specific confirmation text; no placeholder such as yes/ok without context",
            "do_not_edit": "blocks_if_blank",
            "after_fill_validation": "py scripts\\build_reporting_summary_completion_handoff.py",
        },
        {
            "worksheet_id": "MEW-007",
            "dispatch_id": "MD-006",
            "evidence_type": "reference_replacement_authorized",
            "target_file": "reports/reference_completion_handoff_20260810/citation_marker_final_replacement_queue.csv after final prose is stable",
            "target_rows": "all citation marker rows",
            "fields_to_fill": "replacement_allowed_now; current_decision",
            "allowed_values_or_format": "replacement_allowed_now=true only after final prose, figure/table calls and reference order are stable",
            "do_not_edit": "marker; candidate_ids; replacement_blocker; minimum_replacement_evidence",
            "after_fill_validation": "py scripts\\build_reference_completion_handoff.py",
        },
    ]

    field_dictionary_rows = [
        {"field": "send_status", "meaning": "Real send status for each recipient.", "valid_examples": "sent", "invalid_examples": "ready; planned; not_sent"},
        {"field": "sent_datetime_local", "meaning": "Local timestamp of real manual send.", "valid_examples": "2026-08-10 15:30", "invalid_examples": "TBD; tomorrow"},
        {"field": "returned_file_path", "meaning": "Path to actual returned attachment.", "valid_examples": "reports/returned_author_forms/<file>.csv", "invalid_examples": "email received but no file"},
        {"field": "current_choice", "meaning": "Author-selected backend/scope or decision value.", "valid_examples": "Python; Figure 1-Figure 6", "invalid_examples": "either; recommended"},
        {"field": "author_reply", "meaning": "Substantive author confirmation.", "valid_examples": "Confirm descriptive metrics only; no inferential tests.", "invalid_examples": "yes; ok; noted"},
        {"field": "current_decision", "meaning": "Rights/reference decision backed by evidence.", "valid_examples": "MIT selected with author confirmation; exclude_by_default_not_public_release", "invalid_examples": "open; maybe"},
    ]

    writeback_rows = [
        {
            "dispatch_id": row["dispatch_id"],
            "owner": row["recipient_or_owner"],
            "packet_material": row["packet_material"],
            "acceptance_evidence": row["acceptance_evidence"],
            "current_status": row["current_status"],
        }
        for row in dispatch_rows
    ]

    qa_rows = [
        {
            "check": "worksheet_covers_all_validator_evidence_types",
            "result": "PASS" if len(worksheet_rows) == len(validator_rows) == 7 else "FAIL",
            "detail": f"worksheet_rows={len(worksheet_rows)}; validator_rows={len(validator_rows)}",
        },
        {
            "check": "dispatch_queue_imported",
            "result": "PASS" if len(dispatch_rows) == 6 else "FAIL",
            "detail": f"dispatch_rows={len(dispatch_rows)}",
        },
        {
            "check": "current_validator_waiting_state_preserved",
            "result": "PASS" if validator_summary.get("evidence_rows_passed") == 0 and validator_summary.get("submission_ready") is False else "FAIL",
            "detail": f"evidence_rows_passed={validator_summary.get('evidence_rows_passed')}; submission_ready={validator_summary.get('submission_ready')}",
        },
        {
            "check": "worksheet_does_not_claim_written_back",
            "result": "PASS",
            "detail": "Worksheet names target files and fields only; it does not write manual evidence into target files.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "manual_evidence_intake_worksheet.csv",
        worksheet_rows,
        ["worksheet_id", "dispatch_id", "evidence_type", "target_file", "target_rows", "fields_to_fill", "allowed_values_or_format", "do_not_edit", "after_fill_validation"],
    )
    write_csv(OUT_DIR / "manual_evidence_field_dictionary.csv", field_dictionary_rows, ["field", "meaning", "valid_examples", "invalid_examples"])
    write_csv(OUT_DIR / "manual_evidence_dispatch_writeback_map.csv", writeback_rows, ["dispatch_id", "owner", "packet_material", "acceptance_evidence", "current_status"])
    write_csv(OUT_DIR / "manual_evidence_intake_worksheet_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Manual Evidence Intake Worksheet 2026-08-10

This package provides a consolidated worksheet for entering real manual-dispatch evidence into the correct target files.

Boundary: it does not write evidence into those files and does not close any gate. Use it as an operator checklist before rerunning the post-dispatch evidence intake validator.
"""
    write_text(OUT_DIR / "MANUAL_EVIDENCE_INTAKE_WORKSHEET_README.md", readme)

    report = [
        "# Manual evidence intake worksheet report 2026-08-10",
        "",
        "Status: `manual_evidence_intake_worksheet_ready_waiting_real_inputs`",
        "",
        f"- Worksheet rows: {len(worksheet_rows)}",
        f"- Field dictionary rows: {len(field_dictionary_rows)}",
        f"- Dispatch writeback rows: {len(writeback_rows)}",
        f"- QA pass: {qa_pass}",
        "",
        "Conclusion: manual evidence entry points are consolidated, but no evidence is written or claimed.",
        "",
    ]
    write_text(OUT_DIR / "manual_evidence_intake_worksheet_report.md", "\n".join(report))

    summary = {
        "package": "manual_evidence_intake_worksheet_20260810",
        "worksheet_rows": len(worksheet_rows),
        "field_dictionary_rows": len(field_dictionary_rows),
        "dispatch_writeback_rows": len(writeback_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_evidence_written": False,
        "evidence_rows_passed": validator_summary.get("evidence_rows_passed"),
        "submission_ready": False,
        "status": "manual_evidence_intake_worksheet_ready_waiting_real_inputs",
    }

    section = f"""### 18.82 Manual evidence intake worksheet update

Added a manual evidence intake worksheet. This tells the operator exactly which target file and field to fill after real dispatch evidence exists.

New directory: `{OUT_DIR}`

New files:
1. `manual_evidence_intake_worksheet.csv`
2. `manual_evidence_field_dictionary.csv`
3. `manual_evidence_dispatch_writeback_map.csv`
4. `manual_evidence_intake_worksheet_qa.csv`
5. `MANUAL_EVIDENCE_INTAKE_WORKSHEET_README.md`
6. `manual_evidence_intake_worksheet_report.md`
7. `manual_evidence_intake_worksheet_summary.json`

Current result:
1. worksheet_rows = {summary['worksheet_rows']}
2. field_dictionary_rows = {summary['field_dictionary_rows']}
3. dispatch_writeback_rows = {summary['dispatch_writeback_rows']}
4. qa_pass = {str(qa_pass).lower()}
5. manual_evidence_written = false
6. evidence_rows_passed = {summary['evidence_rows_passed']}
7. submission_ready = false
8. status = `manual_evidence_intake_worksheet_ready_waiting_real_inputs`

Boundary:
1. This step does not write manual evidence into target files.
2. This step does not send email, choose backend/scope, acquire external assets or clear rights.
3. This step does not close gates or make the manuscript submission-ready."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_evidence_intake_worksheet_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual evidence intake worksheet QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
