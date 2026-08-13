#!/usr/bin/env python3
"""Validate whether Nature Communications submission files are final-upload ready."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_submission_final_lock_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

MASTER_DIR = BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810"
DASH_DIR = BENCH_ROOT / "reports" / "natcomms_finalization_command_dashboard_v3_20260810"
PORTAL_DIR = BENCH_ROOT / "reports" / "natcomms_portal_upload_manifest_prelock_20260810"
ASSEMBLY_DIR = BENCH_ROOT / "reports" / "natcomms_submission_assembly_preflight_20260810"
PORTAL_FILE_DIR = BENCH_ROOT / "reports" / "portal_submission_file_preflight_20260810"
RS_VALIDATOR_DIR = BENCH_ROOT / "reports" / "reporting_summary_final_lock_validator_20260810"
AVAIL_VALIDATOR_DIR = BENCH_ROOT / "reports" / "availability_repository_finalization_validator_20260810"
REF_VALIDATOR_DIR = BENCH_ROOT / "reports" / "reference_final_lock_validator_20260810"

MASTER_SUMMARY = MASTER_DIR / "finalization_master_checklist_summary.json"
DASH_SUMMARY = DASH_DIR / "finalization_command_dashboard_v3_summary.json"
PORTAL_SUMMARY = PORTAL_DIR / "portal_upload_manifest_summary.json"
ASSEMBLY_SUMMARY = ASSEMBLY_DIR / "natcomms_submission_assembly_preflight_summary.json"
PORTAL_FILE_SUMMARY = PORTAL_FILE_DIR / "portal_submission_file_preflight_summary.json"
RS_SUMMARY = RS_VALIDATOR_DIR / "reporting_summary_final_lock_validator_summary.json"
AVAIL_SUMMARY = AVAIL_VALIDATOR_DIR / "availability_repository_finalization_validator_summary.json"
REF_SUMMARY = REF_VALIDATOR_DIR / "reference_final_lock_validator_summary.json"

MASTER_CHECKLIST = MASTER_DIR / "finalization_master_checklist.csv"
DASHBOARD = DASH_DIR / "finalization_command_dashboard_v3.csv"
CRITICAL_PATH = DASH_DIR / "critical_path_command_queue.csv"
PORTAL_ITEMS = PORTAL_DIR / "portal_upload_item_manifest.csv"
PORTAL_BLOCKERS = PORTAL_DIR / "portal_blocker_crosswalk.csv"
ASSEMBLY_ITEMS = ASSEMBLY_DIR / "natcomms_submission_item_preflight.csv"
PORTAL_INVENTORY = PORTAL_FILE_DIR / "portal_submission_file_inventory.csv"
PORTAL_GATE_GAPS = PORTAL_FILE_DIR / "portal_gate_to_file_gap_matrix.csv"


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
    marker = "### 19.11 Nature Communications submission final lock validator update"
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

    master_summary = read_json(MASTER_SUMMARY)
    dash_summary = read_json(DASH_SUMMARY)
    portal_summary = read_json(PORTAL_SUMMARY)
    assembly_summary = read_json(ASSEMBLY_SUMMARY)
    portal_file_summary = read_json(PORTAL_FILE_SUMMARY)
    rs_summary = read_json(RS_SUMMARY)
    avail_summary = read_json(AVAIL_SUMMARY)
    ref_summary = read_json(REF_SUMMARY)

    master_rows = read_csv(MASTER_CHECKLIST)
    dashboard_rows = read_csv(DASHBOARD)
    critical_rows = read_csv(CRITICAL_PATH)
    portal_rows = read_csv(PORTAL_ITEMS)
    portal_blocker_rows = read_csv(PORTAL_BLOCKERS)
    assembly_rows = read_csv(ASSEMBLY_ITEMS)
    portal_inventory_rows = read_csv(PORTAL_INVENTORY)
    portal_gap_rows = read_csv(PORTAL_GATE_GAPS)

    blocked_commands = [row for row in dashboard_rows if row.get("command_status", "").startswith("blocked")]
    blocked_portal_rows = [row for row in portal_rows if row.get("upload_ready") == "no"]
    blocked_assembly_rows = [row for row in assembly_rows if row.get("assembly_status") == "blocked"]
    upload_allowed_rows = [row for row in portal_inventory_rows if row.get("upload_allowed_now") == "yes"]
    open_portal_gaps = [row for row in portal_gap_rows if row.get("closure_state") == "open"]

    gate_rows = [
        {
            "gate_id": "SUBMIT-FINAL-001",
            "requirement": "All master finalization gates are closed",
            "current_state": f"open_gates={master_summary.get('open_gates')} of {master_summary.get('master_gates')}",
            "passes_now": "no",
            "blocking_reason": "All master gates remain open.",
        },
        {
            "gate_id": "SUBMIT-FINAL-002",
            "requirement": "All finalization commands are unblocked",
            "current_state": f"blocked_commands={dash_summary.get('blocked_commands')} of {dash_summary.get('command_rows')}",
            "passes_now": "no",
            "blocking_reason": "Every finalization command remains blocked.",
        },
        {
            "gate_id": "SUBMIT-FINAL-003",
            "requirement": "Portal upload manifest is upload-ready",
            "current_state": f"upload_ready_rows={portal_summary.get('upload_ready_rows')} of {portal_summary.get('portal_upload_rows')}",
            "passes_now": "no",
            "blocking_reason": "All portal upload rows remain blocked.",
        },
        {
            "gate_id": "SUBMIT-FINAL-004",
            "requirement": "Portal file preflight allows upload",
            "current_state": f"upload_allowed_now={portal_file_summary.get('upload_allowed_now')}; portal_file_rows={portal_file_summary.get('portal_file_rows')}",
            "passes_now": "no",
            "blocking_reason": "No final portal file is upload-allowed.",
        },
        {
            "gate_id": "SUBMIT-FINAL-005",
            "requirement": "Reporting Summary, references and availability are final",
            "current_state": f"reporting_summary={rs_summary.get('final_reporting_summary_ready')}; references={ref_summary.get('final_references_ready')}; availability={avail_summary.get('final_availability_ready')}",
            "passes_now": "no",
            "blocking_reason": "Reporting Summary, references and availability validators are all blocked.",
        },
        {
            "gate_id": "SUBMIT-FINAL-006",
            "requirement": "Submission package is ready",
            "current_state": f"submission_ready flags: assembly={assembly_summary.get('submission_ready')}; dashboard={dash_summary.get('submission_ready')}; portal={portal_summary.get('submission_ready')}",
            "passes_now": "no",
            "blocking_reason": "Submission package is not ready in any upstream validator.",
        },
    ]

    blocker_rows = [
        {"blocker_id": "SUBMIT-BLOCK-001", "blocker": "author_admin_and_branch_replies_missing", "evidence": "FM-001 and FM-002 remain blocked_keep_open", "next_required_evidence": "Returned author/admin and Track B/Track A branch replies."},
        {"blocker_id": "SUBMIT-BLOCK-002", "blocker": "figures_and_source_data_not_final", "evidence": "rendered_figures=0 and Source Data final lock is blocked", "next_required_evidence": "Final figure exports, visual QA, captions and Source Data panel maps."},
        {"blocker_id": "SUBMIT-BLOCK-003", "blocker": "repository_rights_availability_not_final", "evidence": "repository DOI, code DOI, licence and rights are absent", "next_required_evidence": "Resolvable DOI/accession records, licences and rights clearance."},
        {"blocker_id": "SUBMIT-BLOCK-004", "blocker": "reporting_summary_references_not_final", "evidence": "Reporting Summary and reference final lock validators remain blocked", "next_required_evidence": "Final Reporting Summary and numbered references."},
        {"blocker_id": "SUBMIT-BLOCK-005", "blocker": "portal_upload_files_not_final", "evidence": "upload_ready_rows=0 and upload_allowed_now=false", "next_required_evidence": "Final upload package and corresponding-author portal metadata."},
    ]

    command_rows = [
        {"order": 1, "command": "py scripts\\build_natcomms_finalization_master_checklist.py", "run_now": "yes", "purpose": "Refresh master gate state."},
        {"order": 2, "command": "py scripts\\build_natcomms_finalization_command_dashboard_v3.py", "run_now": "yes", "purpose": "Refresh command and portal overlay state."},
        {"order": 3, "command": "py scripts\\build_natcomms_portal_upload_manifest_prelock.py", "run_now": "yes", "purpose": "Refresh portal upload prelock."},
        {"order": 4, "command": "py scripts\\build_portal_submission_file_preflight.py", "run_now": "yes", "purpose": "Refresh portal file preflight."},
        {"order": 5, "command": "py scripts\\build_natcomms_submission_final_lock_validator.py", "run_now": "yes", "purpose": "Refresh this final lock validator."},
        {"order": 6, "command": "Upload or submit files in Nature Communications portal", "run_now": "no", "purpose": "Forbidden until all final submission gates pass."},
    ]

    qa_rows = [
        {
            "check": "master_gates_all_open",
            "result": "PASS" if master_summary.get("master_gates") == 8 and master_summary.get("open_gates") == 8 else "FAIL",
            "detail": f"master_gates={master_summary.get('master_gates')}; open_gates={master_summary.get('open_gates')}",
        },
        {
            "check": "commands_all_blocked",
            "result": "PASS" if len(blocked_commands) == 8 and dash_summary.get("blocked_commands") == 8 else "FAIL",
            "detail": f"blocked_commands={len(blocked_commands)}",
        },
        {
            "check": "portal_upload_all_blocked",
            "result": "PASS" if len(blocked_portal_rows) == 9 and portal_summary.get("upload_ready_rows") == 0 else "FAIL",
            "detail": f"blocked_portal_rows={len(blocked_portal_rows)}; upload_ready_rows={portal_summary.get('upload_ready_rows')}",
        },
        {
            "check": "portal_file_upload_disallowed",
            "result": "PASS" if len(upload_allowed_rows) == 0 and portal_file_summary.get("upload_allowed_now") is False else "FAIL",
            "detail": f"upload_allowed_rows={len(upload_allowed_rows)}; upload_allowed_now={portal_file_summary.get('upload_allowed_now')}",
        },
        {
            "check": "submission_not_ready",
            "result": "PASS" if assembly_summary.get("submission_ready") is False and portal_summary.get("submission_ready") is False and dash_summary.get("submission_ready") is False else "FAIL",
            "detail": f"assembly={assembly_summary.get('submission_ready')}; portal={portal_summary.get('submission_ready')}; dashboard={dash_summary.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "natcomms_submission_final_lock_gate_matrix.csv", gate_rows, ["gate_id", "requirement", "current_state", "passes_now", "blocking_reason"])
    write_csv(OUT_DIR / "natcomms_submission_final_lock_blockers.csv", blocker_rows, ["blocker_id", "blocker", "evidence", "next_required_evidence"])
    write_csv(OUT_DIR / "natcomms_submission_final_lock_command_queue.csv", command_rows, ["order", "command", "run_now", "purpose"])
    write_csv(OUT_DIR / "natcomms_submission_final_lock_portal_overlay.csv", portal_rows, list(portal_rows[0].keys()))
    write_csv(OUT_DIR / "natcomms_submission_final_lock_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Nature Communications submission final lock validator 2026-08-10",
        "",
        "Status: `natcomms_submission_final_lock_validator_ready_blocked`",
        "",
        f"1. Master gates open: {master_summary.get('open_gates')} of {master_summary.get('master_gates')}",
        f"2. Blocked finalization commands: {dash_summary.get('blocked_commands')} of {dash_summary.get('command_rows')}",
        f"3. Portal upload-ready rows: {portal_summary.get('upload_ready_rows')} of {portal_summary.get('portal_upload_rows')}",
        f"4. Portal file upload allowed rows: {len(upload_allowed_rows)} of {len(portal_inventory_rows)}",
        f"5. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this validator does not upload files, create final files or close any submission gate.",
        "",
    ]
    write_text(OUT_DIR / "NATCOMMS_SUBMISSION_FINAL_LOCK_VALIDATOR_README.md", "\n".join(report))
    write_text(OUT_DIR / "natcomms_submission_final_lock_validator_report.md", "\n".join(report))

    summary = {
        "package": "natcomms_submission_final_lock_validator_20260810",
        "gate_rows": len(gate_rows),
        "blocker_rows": len(blocker_rows),
        "command_rows": len(command_rows),
        "portal_overlay_rows": len(portal_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "master_gates": master_summary.get("master_gates"),
        "open_master_gates": master_summary.get("open_gates"),
        "command_rows_upstream": dash_summary.get("command_rows"),
        "blocked_commands": dash_summary.get("blocked_commands"),
        "portal_upload_rows": portal_summary.get("portal_upload_rows"),
        "portal_upload_ready_rows": portal_summary.get("upload_ready_rows"),
        "portal_blocked_upload_rows": portal_summary.get("blocked_upload_rows"),
        "portal_file_rows": portal_file_summary.get("portal_file_rows"),
        "portal_file_upload_allowed_rows": len(upload_allowed_rows),
        "blocked_assembly_rows": len(blocked_assembly_rows),
        "open_portal_gap_rows": len(open_portal_gaps),
        "gate_closure_allowed": False,
        "portal_upload_ready": False,
        "submission_ready": False,
        "status": "natcomms_submission_final_lock_validator_ready_blocked",
    }

    section = f"""### 19.11 Nature Communications submission final lock validator update

Added a final submission-lock validator for Nature Communications portal and final-file readiness.

New directory: `{OUT_DIR}`

New files:
1. `natcomms_submission_final_lock_gate_matrix.csv`
2. `natcomms_submission_final_lock_blockers.csv`
3. `natcomms_submission_final_lock_command_queue.csv`
4. `natcomms_submission_final_lock_portal_overlay.csv`
5. `natcomms_submission_final_lock_qa.csv`
6. `NATCOMMS_SUBMISSION_FINAL_LOCK_VALIDATOR_README.md`
7. `natcomms_submission_final_lock_validator_report.md`
8. `natcomms_submission_final_lock_validator_summary.json`

Current result:
1. open_master_gates = {summary['open_master_gates']}
2. blocked_commands = {summary['blocked_commands']}
3. portal_upload_ready_rows = {summary['portal_upload_ready_rows']}
4. portal_blocked_upload_rows = {summary['portal_blocked_upload_rows']}
5. portal_file_upload_allowed_rows = {summary['portal_file_upload_allowed_rows']}
6. gate_closure_allowed = false
7. portal_upload_ready = false
8. submission_ready = false

Boundary:
1. This validator checks final submission and portal readiness only.
2. It does not upload files or submit the manuscript.
3. It does not create final manuscript, SI, figure, Source Data, reference, DOI or Reporting Summary files."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "natcomms_submission_final_lock_validator_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Nature Communications submission final lock validator QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
