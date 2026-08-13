#!/usr/bin/env python3
"""Create canonical return-evidence inboxes for final human closeout evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_return_evidence_inbox_scaffold_20260810"
RETURN_ROOT = BENCH_ROOT / "final_return_evidence_inbox_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

HANDOFF_ROUTING = BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "final_human_execution_return_routing.csv"
HANDOFF_SUMMARY = BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "final_human_execution_handoff_packet_summary.json"
CLOSEOUT_SUMMARY = BENCH_ROOT / "reports" / "final_human_execution_closeout_board_20260810" / "final_human_execution_closeout_board_summary.json"

CANONICAL_ROUTES = [
    {
        "route_id": "RTE-001",
        "closeout_action": "HEC-001",
        "canonical_folder": "01_author_sendout",
        "expected_evidence": "send timestamp, recipients, subject, sent email export/screenshot, handoff zip SHA256",
        "accepted_extensions": ".md;.txt;.csv;.pdf;.png;.jpg;.zip",
        "validation_command": "py scripts/build_post_dispatch_evidence_intake_validator.py",
    },
    {
        "route_id": "RTE-002",
        "closeout_action": "HEC-002",
        "canonical_folder": "02_author_replies",
        "expected_evidence": "completed author reply forms, backend/scope decision, admin confirmations",
        "accepted_extensions": ".csv;.xlsx;.docx;.pdf;.txt;.md;.zip",
        "validation_command": "py scripts/build_natcomms_author_reply_ingestion_validator.py",
    },
    {
        "route_id": "RTE-003",
        "closeout_action": "HEC-003",
        "canonical_folder": "03_figure_review",
        "expected_evidence": "completed figure review form and reviewer-marked preview approvals/revisions",
        "accepted_extensions": ".csv;.xlsx;.pdf;.png;.jpg;.zip",
        "validation_command": "py scripts/build_python_figure_author_review_intake_validator.py",
    },
    {
        "route_id": "RTE-004",
        "closeout_action": "HEC-004",
        "canonical_folder": "04_repository_rights_doi",
        "expected_evidence": "repository DOI, code DOI, licence selection, third-party rights clearance, upload checksums",
        "accepted_extensions": ".csv;.xlsx;.pdf;.txt;.md;.json;.zip",
        "validation_command": "py scripts/build_availability_repository_finalization_validator.py",
    },
    {
        "route_id": "RTE-005",
        "closeout_action": "HEC-005",
        "canonical_folder": "05_reporting_summary",
        "expected_evidence": "completed Reporting Summary answers and author confirmation",
        "accepted_extensions": ".csv;.xlsx;.docx;.pdf;.txt;.md;.zip",
        "validation_command": "py scripts/build_reporting_summary_final_lock_validator.py",
    },
    {
        "route_id": "RTE-006",
        "closeout_action": "HEC-006",
        "canonical_folder": "06_references",
        "expected_evidence": "manual citation verification sheet, final reference export evidence",
        "accepted_extensions": ".csv;.xlsx;.ris;.bib;.enw;.pdf;.txt;.zip",
        "validation_command": "py scripts/build_reference_final_lock_validator.py",
    },
    {
        "route_id": "RTE-007",
        "closeout_action": "HEC-007",
        "canonical_folder": "07_submission_portal",
        "expected_evidence": "final portal upload list, upload screenshots, submission receipt only after all gates close",
        "accepted_extensions": ".csv;.xlsx;.pdf;.png;.jpg;.txt;.md;.zip",
        "validation_command": "py scripts/build_natcomms_submission_final_lock_validator.py",
    },
]


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
    marker = "### 19.15 Final return evidence inbox scaffold update"
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


def folder_readme(route: dict[str, str], folder: Path) -> str:
    return f"""# Return evidence inbox: {route['canonical_folder']}

Route: `{route['route_id']}`
Closeout action: `{route['closeout_action']}`

Put only returned evidence for this route in this folder.

Expected evidence:
{route['expected_evidence']}

Accepted extensions:
{route['accepted_extensions']}

After evidence is copied here, run:
```powershell
{route['validation_command']}
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`{folder}`
"""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RETURN_ROOT.mkdir(parents=True, exist_ok=True)

    handoff_routes = read_csv(HANDOFF_ROUTING)
    handoff_summary = read_json(HANDOFF_SUMMARY)
    closeout_summary = read_json(CLOSEOUT_SUMMARY)
    old_by_route = {row["route_id"]: row for row in handoff_routes}

    route_rows: list[dict[str, object]] = []
    folder_rows: list[dict[str, object]] = []
    migration_rows: list[dict[str, object]] = []

    for route in CANONICAL_ROUTES:
        folder = RETURN_ROOT / route["canonical_folder"]
        folder.mkdir(parents=True, exist_ok=True)
        readme_path = folder / "README_RETURN_EVIDENCE.md"
        write_text(readme_path, folder_readme(route, folder))
        placeholder_path = folder / ".gitkeep"
        if not placeholder_path.exists():
            write_text(placeholder_path, "")

        old_route = old_by_route.get(route["route_id"], {})
        old_location = old_route.get("drop_location", "")
        canonical_location = str(folder)
        route_rows.append(
            {
                **route,
                "canonical_location": canonical_location,
                "readme": str(readme_path),
                "exists": folder.exists(),
                "current_candidate_files": len([p for p in folder.iterdir() if p.is_file() and not p.name.startswith(".") and p.name != "README_RETURN_EVIDENCE.md"]),
                "status": "ready_empty",
            }
        )
        folder_rows.append(
            {
                "folder": str(folder),
                "route_id": route["route_id"],
                "exists": folder.exists(),
                "readme_exists": readme_path.exists(),
                "placeholder_exists": placeholder_path.exists(),
            }
        )
        migration_rows.append(
            {
                "route_id": route["route_id"],
                "old_drop_location": old_location,
                "canonical_drop_location": canonical_location,
                "migration_needed": "yes" if old_location and old_location.replace("\\", "/").rstrip("/") != canonical_location.replace("\\", "/").rstrip("/") else "no",
                "reason": "Use canonical final_return_evidence_inbox_20260810 route for all new returned evidence.",
            }
        )

    candidate_files = sum(int(row["current_candidate_files"]) for row in route_rows)
    migration_needed = [row for row in migration_rows if row["migration_needed"] == "yes"]

    qa_rows = [
        {
            "check": "all_canonical_folders_exist",
            "result": "PASS" if all(row["exists"] for row in folder_rows) else "FAIL",
            "detail": f"folders={len(folder_rows)}",
        },
        {
            "check": "all_folder_readmes_exist",
            "result": "PASS" if all(row["readme_exists"] for row in folder_rows) else "FAIL",
            "detail": f"readmes={sum(1 for row in folder_rows if row['readme_exists'])}",
        },
        {
            "check": "all_handoff_routes_mapped",
            "result": "PASS" if len(route_rows) == handoff_summary.get("return_routes") == 7 else "FAIL",
            "detail": f"canonical_routes={len(route_rows)}; handoff_routes={handoff_summary.get('return_routes')}",
        },
        {
            "check": "inbox_ready_but_empty",
            "result": "PASS" if candidate_files == 0 and closeout_summary.get("submission_ready") is False else "FAIL",
            "detail": f"candidate_files={candidate_files}; submission_ready={closeout_summary.get('submission_ready')}",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "final_return_evidence_canonical_routes.csv", route_rows, ["route_id", "closeout_action", "canonical_folder", "expected_evidence", "accepted_extensions", "validation_command", "canonical_location", "readme", "exists", "current_candidate_files", "status"])
    write_csv(OUT_DIR / "final_return_evidence_folder_manifest.csv", folder_rows, ["folder", "route_id", "exists", "readme_exists", "placeholder_exists"])
    write_csv(OUT_DIR / "final_return_evidence_route_migration_map.csv", migration_rows, ["route_id", "old_drop_location", "canonical_drop_location", "migration_needed", "reason"])
    write_csv(OUT_DIR / "final_return_evidence_inbox_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Final return evidence inbox scaffold 2026-08-10",
        "",
        "Status: `final_return_evidence_inbox_scaffold_ready_empty`",
        "",
        f"1. Canonical return folders: {len(folder_rows)}",
        f"2. Folder README files: {sum(1 for row in folder_rows if row['readme_exists'])}",
        f"3. Routes mapped: {len(route_rows)}",
        f"4. Route migrations flagged: {len(migration_needed)}",
        f"5. Candidate returned evidence files: {candidate_files}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        f"Canonical root: `{RETURN_ROOT}`",
        "",
        "Boundary: this scaffold creates empty return-evidence folders and routing documentation only. It does not import returned evidence, write back manual fields, close gates or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_RETURN_EVIDENCE_INBOX_SCAFFOLD_README.md", "\n".join(report))
    write_text(OUT_DIR / "final_return_evidence_inbox_scaffold_report.md", "\n".join(report))

    summary = {
        "package": "final_return_evidence_inbox_scaffold_20260810",
        "canonical_root": str(RETURN_ROOT),
        "canonical_folders": len(folder_rows),
        "folder_readmes": sum(1 for row in folder_rows if row["readme_exists"]),
        "routes_mapped": len(route_rows),
        "route_migrations_flagged": len(migration_needed),
        "candidate_return_files": candidate_files,
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_actions_executed": False,
        "evidence_writeback_performed": False,
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "final_return_evidence_inbox_scaffold_ready_empty",
    }

    section = f"""### 19.15 Final return evidence inbox scaffold update

Added canonical return-evidence inbox folders for the seven final human closeout routes.

New directory: `{OUT_DIR}`

Canonical return root:
`{RETURN_ROOT}`

New files:
1. `final_return_evidence_canonical_routes.csv`
2. `final_return_evidence_folder_manifest.csv`
3. `final_return_evidence_route_migration_map.csv`
4. `final_return_evidence_inbox_qa.csv`
5. `FINAL_RETURN_EVIDENCE_INBOX_SCAFFOLD_README.md`
6. `final_return_evidence_inbox_scaffold_report.md`
7. `final_return_evidence_inbox_scaffold_summary.json`

Current result:
1. canonical_folders = {summary['canonical_folders']}
2. folder_readmes = {summary['folder_readmes']}
3. routes_mapped = {summary['routes_mapped']}
4. route_migrations_flagged = {summary['route_migrations_flagged']}
5. candidate_return_files = {summary['candidate_return_files']}
6. manual_actions_executed = false
7. evidence_writeback_performed = false
8. gate_closure_allowed = false
9. submission_ready = false

Boundary:
1. This scaffold only creates canonical folders and routing documentation for returned evidence.
2. It does not import evidence, write back manual fields, close gates or submit the manuscript.
3. All real returned evidence should now be dropped under `final_return_evidence_inbox_20260810`."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_return_evidence_inbox_scaffold_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Final return evidence inbox scaffold QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
