#!/usr/bin/env python3
"""Scan canonical final return-evidence inboxes before any writeback."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

ROUTES_CSV = BENCH_ROOT / "reports" / "final_return_evidence_inbox_scaffold_20260810" / "final_return_evidence_canonical_routes.csv"
INBOX_SUMMARY = BENCH_ROOT / "reports" / "final_return_evidence_inbox_scaffold_20260810" / "final_return_evidence_inbox_scaffold_summary.json"
HANDOFF_SUMMARY = BENCH_ROOT / "reports" / "final_human_execution_handoff_packet_20260810" / "final_human_execution_handoff_packet_summary.json"

IGNORED_NAMES = {".gitkeep", "README_RETURN_EVIDENCE.md"}


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_extensions(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(";") if item.strip()}


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 19.16 Final return evidence intake scanner update"
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
    routes = read_csv(ROUTES_CSV)
    inbox_summary = read_json(INBOX_SUMMARY)
    handoff_summary = read_json(HANDOFF_SUMMARY)

    route_scan_rows: list[dict[str, object]] = []
    file_rows: list[dict[str, object]] = []
    invalid_file_rows: list[dict[str, object]] = []
    command_rows: list[dict[str, object]] = []

    for route in routes:
        folder = Path(route["canonical_location"])
        accepted_extensions = split_extensions(route["accepted_extensions"])
        candidate_files = []
        if folder.exists():
            candidate_files = [
                path
                for path in sorted(folder.iterdir())
                if path.is_file() and path.name not in IGNORED_NAMES and not path.name.startswith(".")
            ]

        accepted_count = 0
        rejected_count = 0
        for path in candidate_files:
            suffix = path.suffix.lower()
            extension_allowed = suffix in accepted_extensions
            row = {
                "route_id": route["route_id"],
                "closeout_action": route["closeout_action"],
                "file_name": path.name,
                "file_path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "extension": suffix,
                "extension_allowed": "yes" if extension_allowed else "no",
                "writeback_allowed_now": "no",
                "reason": "Candidate evidence must be manually inspected and validator-specific fields must be written before gate closure.",
            }
            file_rows.append(row)
            if extension_allowed:
                accepted_count += 1
            else:
                rejected_count += 1
                invalid_file_rows.append(row)

        route_status = "ready_empty" if not candidate_files else "candidate_files_present_needs_manual_intake"
        route_scan_rows.append(
            {
                "route_id": route["route_id"],
                "closeout_action": route["closeout_action"],
                "canonical_folder": route["canonical_folder"],
                "canonical_location": str(folder),
                "folder_exists": "yes" if folder.exists() else "no",
                "candidate_files": len(candidate_files),
                "accepted_extension_files": accepted_count,
                "rejected_extension_files": rejected_count,
                "writeback_allowed_now": "no",
                "route_status": route_status,
            }
        )
        command_rows.append(
            {
                "sequence": len(command_rows) + 1,
                "route_id": route["route_id"],
                "run_when": "after candidate files are manually inspected and mapped to protected fields",
                "command": route["validation_command"],
                "currently_allowed": "no",
                "reason": "No automatic writeback is allowed from raw returned files.",
            }
        )

    total_candidate_files = sum(int(row["candidate_files"]) for row in route_scan_rows)
    accepted_extension_files = sum(int(row["accepted_extension_files"]) for row in route_scan_rows)
    rejected_extension_files = sum(int(row["rejected_extension_files"]) for row in route_scan_rows)
    folders_missing = [row for row in route_scan_rows if row["folder_exists"] != "yes"]

    qa_rows = [
        {
            "check": "all_routes_scanned",
            "result": "PASS" if len(route_scan_rows) == inbox_summary.get("routes_mapped") == handoff_summary.get("return_routes") == 7 else "FAIL",
            "detail": f"scanned={len(route_scan_rows)}; inbox_routes={inbox_summary.get('routes_mapped')}; handoff_routes={handoff_summary.get('return_routes')}",
        },
        {
            "check": "all_canonical_folders_present",
            "result": "PASS" if not folders_missing else "FAIL",
            "detail": f"folders_missing={len(folders_missing)}",
        },
        {
            "check": "no_invalid_return_file_extensions",
            "result": "PASS" if rejected_extension_files == 0 else "FAIL",
            "detail": f"rejected_extension_files={rejected_extension_files}",
        },
        {
            "check": "empty_inbox_preserves_blocked_state",
            "result": "PASS" if total_candidate_files == 0 and inbox_summary.get("submission_ready") is False else "FAIL",
            "detail": f"candidate_files={total_candidate_files}; submission_ready={inbox_summary.get('submission_ready')}",
        },
        {
            "check": "no_automatic_writeback",
            "result": "PASS" if all(row["writeback_allowed_now"] == "no" for row in route_scan_rows) else "FAIL",
            "detail": "all route writeback_allowed_now values must remain no",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(OUT_DIR / "final_return_evidence_route_scan.csv", route_scan_rows, ["route_id", "closeout_action", "canonical_folder", "canonical_location", "folder_exists", "candidate_files", "accepted_extension_files", "rejected_extension_files", "writeback_allowed_now", "route_status"])
    write_csv(OUT_DIR / "final_return_evidence_file_manifest.csv", file_rows, ["route_id", "closeout_action", "file_name", "file_path", "bytes", "sha256", "extension", "extension_allowed", "writeback_allowed_now", "reason"])
    write_csv(OUT_DIR / "final_return_evidence_invalid_files.csv", invalid_file_rows, ["route_id", "closeout_action", "file_name", "file_path", "bytes", "sha256", "extension", "extension_allowed", "writeback_allowed_now", "reason"])
    write_csv(OUT_DIR / "final_return_evidence_next_validation_commands.csv", command_rows, ["sequence", "route_id", "run_when", "command", "currently_allowed", "reason"])
    write_csv(OUT_DIR / "final_return_evidence_intake_scanner_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Final return evidence intake scanner 2026-08-10",
        "",
        "Status: `final_return_evidence_intake_scanner_ready_empty_no_writeback`",
        "",
        f"1. Routes scanned: {len(route_scan_rows)}",
        f"2. Candidate returned files: {total_candidate_files}",
        f"3. Accepted-extension files: {accepted_extension_files}",
        f"4. Rejected-extension files: {rejected_extension_files}",
        f"5. Validation commands queued: {len(command_rows)}",
        f"6. QA pass: {str(qa_pass).lower()}",
        "",
        "Boundary: this scanner hashes and classifies files in the canonical return inbox only. It does not inspect scientific content, write back tracker fields, close gates, rerun branch validators automatically, upload files or submit the manuscript.",
        "",
    ]
    write_text(OUT_DIR / "FINAL_RETURN_EVIDENCE_INTAKE_SCANNER_README.md", "\n".join(report))
    write_text(OUT_DIR / "final_return_evidence_intake_scanner_report.md", "\n".join(report))

    summary = {
        "package": "final_return_evidence_intake_scanner_20260810",
        "routes_scanned": len(route_scan_rows),
        "candidate_return_files": total_candidate_files,
        "accepted_extension_files": accepted_extension_files,
        "rejected_extension_files": rejected_extension_files,
        "validation_commands": len(command_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_actions_executed": False,
        "evidence_writeback_performed": False,
        "writeback_allowed_routes": 0,
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "final_return_evidence_intake_scanner_ready_empty_no_writeback",
    }

    section = f"""### 19.16 Final return evidence intake scanner update

Added a scanner for the canonical final-return evidence inbox.

New directory: `{OUT_DIR}`

New files:
1. `final_return_evidence_route_scan.csv`
2. `final_return_evidence_file_manifest.csv`
3. `final_return_evidence_invalid_files.csv`
4. `final_return_evidence_next_validation_commands.csv`
5. `final_return_evidence_intake_scanner_qa.csv`
6. `FINAL_RETURN_EVIDENCE_INTAKE_SCANNER_README.md`
7. `final_return_evidence_intake_scanner_report.md`
8. `final_return_evidence_intake_scanner_summary.json`

Current result:
1. routes_scanned = {summary['routes_scanned']}
2. candidate_return_files = {summary['candidate_return_files']}
3. accepted_extension_files = {summary['accepted_extension_files']}
4. rejected_extension_files = {summary['rejected_extension_files']}
5. validation_commands = {summary['validation_commands']}
6. writeback_allowed_routes = 0
7. manual_actions_executed = false
8. evidence_writeback_performed = false
9. gate_closure_allowed = false
10. submission_ready = false

Boundary:
1. This scanner only hashes and classifies files in the canonical return inbox.
2. It does not inspect scientific content or write back tracker fields.
3. It does not close gates, rerun branch validators automatically, upload files or submit the manuscript."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "final_return_evidence_intake_scanner_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Final return evidence intake scanner QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
