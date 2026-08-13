#!/usr/bin/env python3
"""Build the RB-001 return-evidence drop kit.

This creates an operator-facing placement guide and manifest templates for real
returned evidence. It does not add evidence, compute acceptance for absent
evidence or write protected target files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
INBOX_DIR = BENCH_ROOT / "final_return_evidence_inbox_20260810"
INBOX_DISPLAY_ROOT = "final_return_evidence_inbox_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "rb001_return_evidence_drop_kit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
DESKTOP_GUIDE = Path.home() / "Desktop" / "RB001_return_evidence_drop_kit_20260810.md"

SCANNER_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_intake_scanner_summary.json"
SCANNER_ROUTE_SCAN = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810" / "final_return_evidence_route_scan.csv"
CLOSURE_SUMMARY = BENCH_ROOT / "reports" / "final_residual_blocker_closure_packet_20260810" / "final_residual_blocker_closure_packet_summary.json"

ROUTES = [
    {
        "route_id": "RTE-001",
        "folder": "01_author_sendout",
        "evidence_type": "author sendout proof",
        "required_files": "sent email export or screenshot; recipient list; timestamp; subject; handoff zip SHA256",
        "accepted_extensions": ".md;.txt;.csv;.pdf;.png;.jpg;.zip",
        "after_drop_command": "py scripts/build_post_dispatch_evidence_intake_validator.py",
    },
    {
        "route_id": "RTE-002",
        "folder": "02_author_replies",
        "evidence_type": "author replies and backend/scope decision",
        "required_files": "completed reply form; backend/scope decision; administrative confirmations",
        "accepted_extensions": ".csv;.xlsx;.docx;.pdf;.txt;.md;.zip",
        "after_drop_command": "py scripts/build_natcomms_author_reply_ingestion_validator.py",
    },
    {
        "route_id": "RTE-003",
        "folder": "03_figure_review",
        "evidence_type": "final figure review decisions",
        "required_files": "completed figure review form; marked preview approvals or revision notes",
        "accepted_extensions": ".csv;.xlsx;.pdf;.png;.jpg;.zip",
        "after_drop_command": "py scripts/build_python_figure_author_review_intake_validator.py",
    },
    {
        "route_id": "RTE-004",
        "folder": "04_repository_rights_doi",
        "evidence_type": "repository DOI, licence and rights",
        "required_files": "repository DOI proof; licence text; third-party rights proof; restricted-data wording",
        "accepted_extensions": ".csv;.xlsx;.docx;.pdf;.txt;.md;.png;.jpg;.zip",
        "after_drop_command": "py scripts/build_availability_repository_finalization_validator.py",
    },
    {
        "route_id": "RTE-005",
        "folder": "05_reporting_summary",
        "evidence_type": "Reporting Summary answers",
        "required_files": "completed Reporting Summary response file; dependency notes",
        "accepted_extensions": ".csv;.xlsx;.docx;.pdf;.txt;.md;.zip",
        "after_drop_command": "py scripts/build_reporting_summary_final_lock_validator.py",
    },
    {
        "route_id": "RTE-006",
        "folder": "06_references",
        "evidence_type": "final reference verification",
        "required_files": "verified reference list; placeholder replacement authorization; exported citation file",
        "accepted_extensions": ".csv;.xlsx;.ris;.bib;.enw;.txt;.md;.docx;.pdf;.zip",
        "after_drop_command": "py scripts/build_reference_final_lock_validator.py",
    },
    {
        "route_id": "RTE-007",
        "folder": "07_submission_portal",
        "evidence_type": "portal upload and submission proof",
        "required_files": "portal metadata screenshots; upload receipt; submission confirmation only after all gates close",
        "accepted_extensions": ".csv;.xlsx;.pdf;.png;.jpg;.txt;.md;.zip",
        "after_drop_command": "py scripts/build_natcomms_submission_final_lock_validator.py",
    },
]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.24 RB-001 return evidence drop kit update"
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
    scanner = read_json(SCANNER_SUMMARY)
    closure = read_json(CLOSURE_SUMMARY)
    route_scan = read_csv(SCANNER_ROUTE_SCAN)

    route_scan_by_id = {row["route_id"]: row for row in route_scan}
    placement_rows: list[dict[str, object]] = []
    manifest_template_rows: list[dict[str, object]] = []
    for route in ROUTES:
        folder_path = INBOX_DIR / route["folder"]
        readme_path = folder_path / "README_RETURN_EVIDENCE.md"
        scan_row = route_scan_by_id.get(route["route_id"], {})
        placement_rows.append(
            {
                "route_id": route["route_id"],
                "folder": route["folder"],
                "relative_folder": f"{INBOX_DISPLAY_ROOT}/{route['folder']}",
                "folder_exists": folder_path.exists(),
                "readme_exists": readme_path.exists(),
                "evidence_type": route["evidence_type"],
                "required_files": route["required_files"],
                "accepted_extensions": route["accepted_extensions"],
                "current_candidate_files": scan_row.get("candidate_files", "0"),
                "after_drop_command": route["after_drop_command"],
            }
        )
        manifest_template_rows.append(
            {
                "route_id": route["route_id"],
                "folder": route["folder"],
                "expected_file_name": "FILL_AFTER_DROP",
                "source_person_or_system": "FILL_AFTER_DROP",
                "received_date": "YYYY-MM-DD",
                "sha256": "FILL_AFTER_HASH",
                "evidence_meaning": route["evidence_type"],
                "allowed_to_writeback": "no_until_scanner_and_manual_review_pass",
            }
        )

    command_rows = [
        {"step": 1, "command": "Copy real returned evidence into the matching folder under final_return_evidence_inbox_20260810.", "allowed_now": "manual_only", "stop_rule": "Do not edit generated reports or protected target files."},
        {"step": 2, "command": "Record received files in rb001_return_evidence_hash_manifest_template.csv after calculating SHA256.", "allowed_now": "manual_only_after_file_drop", "stop_rule": "Do not invent hashes or source identities."},
        {"step": 3, "command": "py scripts/build_final_return_evidence_intake_scanner.py", "allowed_now": "diagnostic_only", "stop_rule": "Scanner acceptance does not by itself write evidence or close gates."},
        {"step": 4, "command": "py scripts/build_final_return_evidence_writeback_preflight.py", "allowed_now": "no", "stop_rule": "Do not run for closure while writeback_allowed_rows=0."},
        {"step": 5, "command": "powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1", "allowed_now": "after_scanner_rerun", "stop_rule": "A passing M0-M2 run is not submission readiness unless final lock validators pass."},
    ]

    guide_lines = [
        "# RB-001 return evidence drop kit 2026-08-10",
        "",
        "Purpose: place real returned evidence into the canonical inbox without writing protected manuscript, figure, repository, reference or submission targets.",
        "",
        f"Canonical inbox root for manual placement: `{INBOX_DISPLAY_ROOT}`",
        "",
        "## Route Folders",
        "",
    ]
    for row in placement_rows:
        guide_lines.extend(
            [
                f"### {row['route_id']} {row['folder']}",
                f"- Folder: `{row['relative_folder']}`",
                f"- Evidence: {row['evidence_type']}",
                f"- Required files: {row['required_files']}",
                f"- Accepted extensions: {row['accepted_extensions']}",
                f"- Current candidate files: {row['current_candidate_files']}",
                f"- First validation command: `{row['after_drop_command']}`",
                "",
            ]
        )
    guide_lines.extend(
        [
            "## Required Hash Record",
            "",
            "After copying a real file into a route folder, calculate SHA256 and fill `rb001_return_evidence_hash_manifest_template.csv`. Do not fill placeholder rows before real files exist.",
            "",
            "## Hard Boundaries",
            "",
            f"1. candidate_return_files={scanner.get('candidate_return_files')}",
            f"2. ready_to_close_rows={closure.get('ready_to_close_rows')}",
            f"3. writeback_allowed_rows={closure.get('writeback_allowed_rows')}",
            f"4. submission_ready={closure.get('submission_ready')}",
            "5. This kit does not close RB-001; it only makes the evidence drop action unambiguous.",
            "",
        ]
    )
    guide_text = "\n".join(guide_lines)

    write_csv(
        OUT_DIR / "rb001_return_evidence_drop_locations.csv",
        placement_rows,
        ["route_id", "folder", "relative_folder", "folder_exists", "readme_exists", "evidence_type", "required_files", "accepted_extensions", "current_candidate_files", "after_drop_command"],
    )
    write_csv(
        OUT_DIR / "rb001_return_evidence_hash_manifest_template.csv",
        manifest_template_rows,
        ["route_id", "folder", "expected_file_name", "source_person_or_system", "received_date", "sha256", "evidence_meaning", "allowed_to_writeback"],
    )
    write_csv(OUT_DIR / "rb001_return_evidence_after_drop_commands.csv", command_rows, ["step", "command", "allowed_now", "stop_rule"])
    write_text(OUT_DIR / "RB001_RETURN_EVIDENCE_DROP_KIT_README.md", guide_text)
    write_text(OUT_DIR / "rb001_return_evidence_drop_kit_report.md", guide_text)
    shutil.copy2(OUT_DIR / "rb001_return_evidence_drop_kit_report.md", DESKTOP_GUIDE)

    files_for_manifest = [
        OUT_DIR / "rb001_return_evidence_drop_locations.csv",
        OUT_DIR / "rb001_return_evidence_hash_manifest_template.csv",
        OUT_DIR / "rb001_return_evidence_after_drop_commands.csv",
        OUT_DIR / "RB001_RETURN_EVIDENCE_DROP_KIT_README.md",
        OUT_DIR / "rb001_return_evidence_drop_kit_report.md",
    ]
    package_manifest_rows = [
        {"artifact": path.name, "sha256": file_sha256(path), "bytes": path.stat().st_size}
        for path in files_for_manifest
    ]
    write_csv(OUT_DIR / "rb001_return_evidence_drop_kit_manifest.csv", package_manifest_rows, ["artifact", "sha256", "bytes"])

    qa_rows = [
        {"check": "all_route_folders_exist", "result": "PASS" if all(row["folder_exists"] for row in placement_rows) else "FAIL", "detail": f"folders={len(placement_rows)}"},
        {"check": "all_route_readmes_exist", "result": "PASS" if all(row["readme_exists"] for row in placement_rows) else "FAIL", "detail": f"readmes={sum(1 for row in placement_rows if row['readme_exists'])}"},
        {"check": "no_evidence_fabricated", "result": "PASS" if scanner.get("candidate_return_files") == 0 else "FAIL", "detail": f"candidate_return_files={scanner.get('candidate_return_files')}"},
        {"check": "writeback_guard_preserved", "result": "PASS" if closure.get("writeback_allowed_rows") == 0 else "FAIL", "detail": f"writeback_allowed_rows={closure.get('writeback_allowed_rows')}"},
        {"check": "desktop_guide_created", "result": "PASS" if DESKTOP_GUIDE.exists() else "FAIL", "detail": "Desktop/RB001_return_evidence_drop_kit_20260810.md"},
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)
    write_csv(OUT_DIR / "rb001_return_evidence_drop_kit_qa.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "package": "rb001_return_evidence_drop_kit_20260810",
        "route_rows": len(placement_rows),
        "manifest_template_rows": len(manifest_template_rows),
        "after_drop_command_rows": len(command_rows),
        "package_manifest_rows": len(package_manifest_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "candidate_return_files": scanner.get("candidate_return_files"),
        "ready_to_close_rows": closure.get("ready_to_close_rows"),
        "writeback_allowed_rows": closure.get("writeback_allowed_rows"),
        "submission_ready": False,
        "desktop_guide": str(DESKTOP_GUIDE),
        "status": "rb001_return_evidence_drop_kit_ready_waiting_for_real_returned_files",
    }

    section = f"""### 19.24 RB-001 return evidence drop kit update

Added a RB-001 return evidence drop kit so real returned evidence can be placed into the correct canonical inbox folders with hash tracking and safe after-drop commands.

New directory: `{OUT_DIR}`

Desktop guide: `{DESKTOP_GUIDE}`

Current result:
1. route_rows = {summary['route_rows']}
2. manifest_template_rows = {summary['manifest_template_rows']}
3. after_drop_command_rows = {summary['after_drop_command_rows']}
4. package_manifest_rows = {summary['package_manifest_rows']}
5. candidate_return_files = {summary['candidate_return_files']}
6. ready_to_close_rows = {summary['ready_to_close_rows']}
7. writeback_allowed_rows = {summary['writeback_allowed_rows']}
8. submission_ready = false

Boundary:
1. This kit does not create or fabricate returned evidence.
2. It does not write protected target files or close gates.
3. It only makes the RB-001 evidence drop and hash-recording step directly executable."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "rb001_return_evidence_drop_kit_summary.json", json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    if not qa_pass:
        raise SystemExit("RB-001 return evidence drop kit QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
