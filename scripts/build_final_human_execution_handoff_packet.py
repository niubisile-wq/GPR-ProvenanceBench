#!/usr/bin/env python3
"""Package final human-execution materials and return-evidence routes."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810"
MATERIALS_DIR = OUT_DIR / "materials"
DESKTOP = Path.home() / "Desktop"
DESKTOP_PLAN = DESKTOP / "8月10日cns.md"
LOCAL_ZIP = OUT_DIR / "NatComms_final_human_execution_handoff_packet_20260810.zip"
DESKTOP_ZIP = DESKTOP / "NatComms_final_human_execution_handoff_packet_20260810.zip"
RETURN_ROOT = BENCH_ROOT / "final_return_evidence_inbox_20260810"

SUMMARY_PATH = BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810" / "final_human_execution_closeout_board_summary.json"

SOURCE_FILES = [
    ("closeout", "final_human_execution_action_queue.csv", BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810" / "final_human_execution_action_queue.csv"),
    ("closeout", "final_human_execution_evidence_matrix.csv", BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810" / "final_human_execution_evidence_matrix.csv"),
    ("closeout", "final_human_execution_no_go_rules.csv", BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810" / "final_human_execution_no_go_rules.csv"),
    ("author_sendout", "NatComms_author_sendout_bundle_v2_20260810.zip", BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810" / "NatComms_author_sendout_bundle_v2_20260810.zip"),
    ("author_sendout", "author_sendout_email_ready_draft_cn.md", BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810" / "author_sendout_email_ready_draft_cn.md"),
    ("author_sendout", "AUTHOR_SENDOUT_BUNDLE_V2_INSTRUCTIONS.md", BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810" / "AUTHOR_SENDOUT_BUNDLE_V2_INSTRUCTIONS.md"),
    ("author_sendout", "author_sendout_bundle_v2_manifest.csv", BENCH_ROOT / "reports" / "natcomms_author_sendout_bundle_v2_20260810" / "author_sendout_bundle_v2_manifest.csv"),
    ("figure_review", "NatComms_python_figure_author_review_packet_20260810.zip", BENCH_ROOT / "reports" / "python_figure_author_review_packet_20260810" / "NatComms_python_figure_author_review_packet_20260810.zip"),
    ("figure_review", "python_figure_author_review_form.csv", BENCH_ROOT / "reports" / "python_figure_author_review_packet_20260810" / "python_figure_author_review_form.csv"),
    ("figure_review", "PYTHON_FIGURE_AUTHOR_REVIEW_INSTRUCTIONS.md", BENCH_ROOT / "reports" / "python_figure_author_review_packet_20260810" / "PYTHON_FIGURE_AUTHOR_REVIEW_INSTRUCTIONS.md"),
    ("manual_evidence", "manual_evidence_intake_worksheet.csv", BENCH_ROOT / "reports" / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet.csv"),
    ("manual_evidence", "manual_evidence_dispatch_writeback_map.csv", BENCH_ROOT / "reports" / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_dispatch_writeback_map.csv"),
    ("manual_evidence", "manual_evidence_inbox_manifest.csv", BENCH_ROOT / "reports" / "manual_evidence_inbox_scaffold_20260810" / "manual_evidence_inbox_manifest.csv"),
    ("manual_evidence", "MANUAL_EVIDENCE_INBOX_README.md", BENCH_ROOT / "reports" / "manual_evidence_inbox_scaffold_20260810" / "MANUAL_EVIDENCE_INBOX_README.md"),
    ("repository_rights", "availability_repository_blockers.csv", BENCH_ROOT / "reports" / "availability_repository_finalization_validator_20260810" / "availability_repository_blockers.csv"),
    ("repository_rights", "availability_repository_command_queue.csv", BENCH_ROOT / "reports" / "availability_repository_finalization_validator_20260810" / "availability_repository_command_queue.csv"),
    ("reporting_summary", "reporting_summary_item_final_lock_status.csv", BENCH_ROOT / "reports" / "reporting_summary_final_lock_validator_20260810" / "reporting_summary_item_final_lock_status.csv"),
    ("reporting_summary", "reporting_summary_final_lock_command_queue.csv", BENCH_ROOT / "reports" / "reporting_summary_final_lock_validator_20260810" / "reporting_summary_final_lock_command_queue.csv"),
    ("references", "reference_final_lock_command_queue.csv", BENCH_ROOT / "reports" / "reference_final_lock_validator_20260810" / "reference_final_lock_command_queue.csv"),
    ("references", "reference_final_lock_no_go_rules.csv", BENCH_ROOT / "reports" / "reference_final_lock_validator_20260810" / "reference_final_lock_no_go_rules.csv"),
    ("submission", "natcomms_submission_final_lock_blockers.csv", BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810" / "natcomms_submission_final_lock_blockers.csv"),
    ("submission", "natcomms_submission_final_lock_portal_overlay.csv", BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810" / "natcomms_submission_final_lock_portal_overlay.csv"),
]


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.14 Final human execution handoff packet update"
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
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

    closeout_summary = read_json(SUMMARY_PATH)
    manifest_rows: list[dict[str, object]] = []
    missing_sources: list[str] = []
    for category, name, source in SOURCE_FILES:
        if not source.exists():
            missing_sources.append(str(source))
            continue
        category_dir = MATERIALS_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        dest = category_dir / name
        shutil.copy2(source, dest)
        manifest_rows.append(
            {
                "category": category,
                "file_name": name,
                "source_path": str(source),
                "packet_path": str(dest.relative_to(OUT_DIR)),
                "bytes": dest.stat().st_size,
                "sha256": sha256_file(dest),
            }
        )

    route_rows = [
        {
            "route_id": "RTE-001",
            "closeout_action": "HEC-001",
            "return_evidence": "sent email timestamp, recipients, subject, bundle zip hash and screenshot/log export",
            "drop_location": str(RETURN_ROOT / "01_author_sendout"),
            "writeback_target": "manual evidence intake worksheet sendout rows",
            "validation_command": "py scripts/build_post_dispatch_evidence_intake_validator.py",
        },
        {
            "route_id": "RTE-002",
            "closeout_action": "HEC-002",
            "return_evidence": "completed author reply forms and backend/scope/admin confirmations",
            "drop_location": str(RETURN_ROOT / "02_author_replies"),
            "writeback_target": "author reply ingestion validator input fields",
            "validation_command": "py scripts/build_natcomms_author_reply_ingestion_validator.py",
        },
        {
            "route_id": "RTE-003",
            "closeout_action": "HEC-003",
            "return_evidence": "completed figure review form plus approved/revise/reject decisions",
            "drop_location": str(RETURN_ROOT / "03_figure_review"),
            "writeback_target": "python_figure_author_review_form.csv",
            "validation_command": "py scripts/build_python_figure_author_review_intake_validator.py",
        },
        {
            "route_id": "RTE-004",
            "closeout_action": "HEC-004",
            "return_evidence": "repository DOI, code DOI, licence, rights clearance and upload checksum records",
            "drop_location": str(RETURN_ROOT / "04_repository_rights_doi"),
            "writeback_target": "availability/repository finalization validator inputs",
            "validation_command": "py scripts/build_availability_repository_finalization_validator.py",
        },
        {
            "route_id": "RTE-005",
            "closeout_action": "HEC-005",
            "return_evidence": "completed Reporting Summary item answers with author confirmation",
            "drop_location": str(RETURN_ROOT / "05_reporting_summary"),
            "writeback_target": "Reporting Summary final lock item status",
            "validation_command": "py scripts/build_reporting_summary_final_lock_validator.py",
        },
        {
            "route_id": "RTE-006",
            "closeout_action": "HEC-006",
            "return_evidence": "manual reference verification sheet and final export evidence",
            "drop_location": str(RETURN_ROOT / "06_references"),
            "writeback_target": "reference final lock validator inputs",
            "validation_command": "py scripts/build_reference_final_lock_validator.py",
        },
        {
            "route_id": "RTE-007",
            "closeout_action": "HEC-007",
            "return_evidence": "final portal upload file list, upload screenshots and submission receipt only after all gates close",
            "drop_location": str(RETURN_ROOT / "07_submission_portal"),
            "writeback_target": "submission final lock validator inputs",
            "validation_command": "py scripts/build_natcomms_submission_final_lock_validator.py",
        },
    ]

    checklist_rows = [
        {
            "step": row["route_id"],
            "must_do": row["return_evidence"],
            "must_not_do": "Do not mark any gate closed until the validation command passes on real returned evidence.",
            "completion_marker": "Returned evidence file exists, hash recorded and corresponding validator changes from blocked to allowed.",
        }
        for row in route_rows
    ]

    validation_rows = [
        {"sequence": 1, "command": "py scripts/build_post_dispatch_evidence_intake_validator.py", "run_when": "after sendout evidence is captured"},
        {"sequence": 2, "command": "py scripts/build_natcomms_author_reply_ingestion_validator.py", "run_when": "after author reply forms are returned"},
        {"sequence": 3, "command": "py scripts/build_manual_evidence_final_intake_validator.py", "run_when": "after all manual evidence worksheets are updated"},
        {"sequence": 4, "command": "py scripts/build_python_figure_author_review_intake_validator.py", "run_when": "after figure review form is returned"},
        {"sequence": 5, "command": "py scripts/build_availability_repository_finalization_validator.py", "run_when": "after DOI/licence/rights evidence is recorded"},
        {"sequence": 6, "command": "py scripts/build_reporting_summary_final_lock_validator.py", "run_when": "after Reporting Summary answers are completed"},
        {"sequence": 7, "command": "py scripts/build_reference_final_lock_validator.py", "run_when": "after reference verification is completed"},
        {"sequence": 8, "command": "py scripts/build_natcomms_submission_final_lock_validator.py", "run_when": "only after upstream gates close"},
        {"sequence": 9, "command": "powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1", "run_when": "after any accepted writeback"},
    ]

    packet_no_go_rows = [
        {"rule_id": "PKT-NG-001", "rule": "Do not edit generated summaries by hand.", "reason": "They must be regenerated from validators after evidence writeback."},
        {"rule_id": "PKT-NG-002", "rule": "Do not treat the zip as proof that manual actions were executed.", "reason": "The zip only packages instructions and templates."},
        {"rule_id": "PKT-NG-003", "rule": "Do not submit or upload portal files from this packet.", "reason": "Submission remains blocked until all upstream gates close."},
        {"rule_id": "PKT-NG-004", "rule": "Do not run final figure export before figure approvals are ingested.", "reason": "approved_figure_rows remains zero."},
    ]

    write_csv(OUT_DIR / "final_human_execution_handoff_manifest.csv", manifest_rows, ["category", "file_name", "source_path", "packet_path", "bytes", "sha256"])
    write_csv(OUT_DIR / "final_human_execution_return_routing.csv", route_rows, ["route_id", "closeout_action", "return_evidence", "drop_location", "writeback_target", "validation_command"])
    write_csv(OUT_DIR / "final_human_execution_operator_checklist.csv", checklist_rows, ["step", "must_do", "must_not_do", "completion_marker"])
    write_csv(OUT_DIR / "final_human_execution_validation_commands.csv", validation_rows, ["sequence", "command", "run_when"])
    write_csv(OUT_DIR / "final_human_execution_packet_no_go_rules.csv", packet_no_go_rows, ["rule_id", "rule", "reason"])

    if LOCAL_ZIP.exists():
        LOCAL_ZIP.unlink()
    with zipfile.ZipFile(LOCAL_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT_DIR.rglob("*")):
            if path == LOCAL_ZIP or path.is_dir():
                continue
            archive.write(path, path.relative_to(OUT_DIR).as_posix())
    shutil.copy2(LOCAL_ZIP, DESKTOP_ZIP)
    zip_members = len(zipfile.ZipFile(LOCAL_ZIP).namelist())

    qa_rows = [
        {
            "check": "all_source_files_present",
            "result": "PASS" if not missing_sources else "FAIL",
            "detail": f"missing_sources={len(missing_sources)}",
        },
        {
            "check": "all_closeout_routes_present",
            "result": "PASS" if len(route_rows) == closeout_summary.get("action_rows") == 7 else "FAIL",
            "detail": f"route_rows={len(route_rows)}; action_rows={closeout_summary.get('action_rows')}",
        },
        {
            "check": "packet_zip_created",
            "result": "PASS" if LOCAL_ZIP.exists() and DESKTOP_ZIP.exists() and zip_members >= len(manifest_rows) else "FAIL",
            "detail": f"local_zip={LOCAL_ZIP.exists()}; desktop_zip={DESKTOP_ZIP.exists()}; zip_members={zip_members}",
        },
        {
            "check": "packet_does_not_claim_execution",
            "result": "PASS" if closeout_summary.get("blocked_action_rows") == 7 and closeout_summary.get("submission_ready") is False else "FAIL",
            "detail": f"blocked_action_rows={closeout_summary.get('blocked_action_rows')}; submission_ready={closeout_summary.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "final_human_execution_handoff_packet_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Final human execution handoff packet 2026-08-10",
        "",
        "Status: `final_human_execution_handoff_packet_ready_not_executed`",
        "",
        f"1. Manifest files copied: {len(manifest_rows)}",
        f"2. Return routes: {len(route_rows)}",
        f"3. Validation commands: {len(validation_rows)}",
        f"4. Local zip: `{LOCAL_ZIP}`",
        f"5. Desktop zip: `{DESKTOP_ZIP}`",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this packet packages execution materials and return routes only. It does not send email, collect evidence, write back manual fields, close gates, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_HUMAN_EXECUTION_HANDOFF_PACKET_README.md", "\n".join(report))
    write_text(OUT_DIR / "final_human_execution_handoff_packet_report.md", "\n".join(report))

    summary = {
        "package": "final_human_execution_handoff_packet_20260810",
        "manifest_rows": len(manifest_rows),
        "missing_source_files": len(missing_sources),
        "return_routes": len(route_rows),
        "operator_checklist_rows": len(checklist_rows),
        "validation_commands": len(validation_rows),
        "packet_no_go_rules": len(packet_no_go_rows),
        "zip_members": zip_members,
        "local_zip": str(LOCAL_ZIP),
        "local_zip_exists": LOCAL_ZIP.exists(),
        "desktop_zip": str(DESKTOP_ZIP),
        "desktop_zip_exists": DESKTOP_ZIP.exists(),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_actions_executed": False,
        "evidence_writeback_performed": False,
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "final_human_execution_handoff_packet_ready_not_executed",
    }

    section = f"""### 19.14 Final human execution handoff packet update

Added a final handoff packet that collects the scattered execution materials for the seven closeout actions into one zip and one return-routing map.

New directory: `{OUT_DIR}`

New files:
1. `final_human_execution_handoff_manifest.csv`
2. `final_human_execution_return_routing.csv`
3. `final_human_execution_operator_checklist.csv`
4. `final_human_execution_validation_commands.csv`
5. `final_human_execution_packet_no_go_rules.csv`
6. `final_human_execution_handoff_packet_qa.csv`
7. `FINAL_HUMAN_EXECUTION_HANDOFF_PACKET_README.md`
8. `final_human_execution_handoff_packet_report.md`
9. `final_human_execution_handoff_packet_summary.json`
10. `NatComms_final_human_execution_handoff_packet_20260810.zip`

Desktop zip:
`{DESKTOP_ZIP}`

Current result:
1. manifest_rows = {summary['manifest_rows']}
2. return_routes = {summary['return_routes']}
3. validation_commands = {summary['validation_commands']}
4. packet_no_go_rules = {summary['packet_no_go_rules']}
5. zip_members = {summary['zip_members']}
6. desktop_zip_exists = true
7. manual_actions_executed = false
8. evidence_writeback_performed = false
9. gate_closure_allowed = false
10. submission_ready = false

Boundary:
1. This packet only packages instructions, templates, routing and validation commands.
2. It does not send email, collect evidence, write back manual fields, close gates, upload files or submit the manuscript.
3. It is the handoff artifact to use before any real human evidence is captured."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_human_execution_handoff_packet_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Final human execution handoff packet QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
