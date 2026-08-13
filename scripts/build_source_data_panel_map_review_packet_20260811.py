#!/usr/bin/env python3
"""Assemble a Source Data panel-map review packet for figure finalization."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "source_data_panel_map_review_packet_20260811"
PACKAGE_DIR = OUT_DIR / "candidate_source_files"
DESKTOP_REPORT = Path.home() / "Desktop" / "NatComms_20260811_source_data_panel_map_review_packet.md"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def copy_rel(rel_path: str, target_dir: Path) -> str:
    source = BENCH_ROOT / rel_path
    target = target_dir / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.exists():
        shutil.copy2(source, target)
        return str(target.relative_to(BENCH_ROOT))
    return ""


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 20.05 Source Data panel-map review packet update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/source_data_panel_map_review_packet_20260811/` and Desktop report `NatComms_20260811_source_data_panel_map_review_packet.md`.
- Current Source Data review state: `figures_mapped={summary["figures_mapped"]}`, `source_files_packaged={summary["source_files_packaged"]}`, `missing_source_files={summary["missing_source_files"]}`, `review_packet_ready={str(summary["review_packet_ready"]).lower()}`.
- Final Source Data state remains guarded: `source_data_panel_map_locked=false`, `repository_identifier_present=false`, `submission_ready=false`.
- Boundary: this is a Source Data review/prelock packet only; it does not create final panel maps, repository DOI/accession, licence clearance or submission-ready Source Data.
"""
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        text = text[:start].rstrip() if next_start == -1 else text[:start].rstrip() + "\n\n" + text[next_start:].lstrip("\n")
    DESKTOP_PLAN.write_text(text.rstrip() + block + "\n", encoding="utf-8")
    return True


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    preflight_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "python_figure_source_data_panel_map_preflight_20260810"
        / "python_figure_source_data_panel_map_preflight.csv"
    )
    lock_requirements = read_csv(
        BENCH_ROOT
        / "reports"
        / "python_figure_source_data_panel_map_preflight_20260810"
        / "python_figure_source_data_lock_requirements.csv"
    )
    candidate_summary = read_json(
        BENCH_ROOT
        / "reports"
        / "figure_final_candidate_review_packet_20260811"
        / "figure_final_candidate_review_packet_summary.json"
    )
    source_deposit = read_json(
        BENCH_ROOT
        / "reports"
        / "source_data_deposit_package_20260810"
        / "source_data_deposit_summary.json"
    )

    map_rows: list[dict[str, object]] = []
    copied_source_files: list[dict[str, object]] = []
    missing = 0
    for row in preflight_rows:
        figure_dir = PACKAGE_DIR / row["figure_id"].lower().replace(" ", "_")
        copied = []
        source_files = [part.strip() for part in row["source_files"].split(";") if part.strip()]
        for rel_path in source_files:
            copied_path = copy_rel(rel_path, figure_dir)
            if copied_path:
                copied.append(copied_path)
                copied_source_files.append(
                    {
                        "figure_id": row["figure_id"],
                        "source_data_filename": row["source_data_filename"],
                        "source_file": rel_path,
                        "copied_file": copied_path,
                        "copy_status": "copied",
                    }
                )
            else:
                missing += 1
                copied_source_files.append(
                    {
                        "figure_id": row["figure_id"],
                        "source_data_filename": row["source_data_filename"],
                        "source_file": rel_path,
                        "copied_file": "",
                        "copy_status": "missing",
                    }
                )
        map_rows.append(
            {
                "figure_id": row["figure_id"],
                "source_data_filename": row["source_data_filename"],
                "source_file_count": row["source_file_count"],
                "copied_source_file_count": len(copied),
                "all_source_files_exist": row["all_source_files_exist"],
                "panel_map_review_status": "ready_for_review" if copied and row["all_source_files_exist"] == "yes" else "not_ready",
                "panel_map_lock_status": "blocked_until_final_figures_and_export_qa",
                "blocking_reason": row["blocking_reason"],
            }
        )

    gate_rows = [
        {
            "gate": "final-candidate review packet",
            "current_state": f"review_packet_ready={candidate_summary.get('review_packet_ready')}",
            "passes_for_source_data_review": "yes",
            "passes_for_final_source_data_lock": "no",
        },
        {
            "gate": "source files",
            "current_state": f"figures_mapped={len(map_rows)}; missing_source_files={missing}",
            "passes_for_source_data_review": "yes" if missing == 0 else "no",
            "passes_for_final_source_data_lock": "no",
        },
        {
            "gate": "repository identifier",
            "current_state": f"repository_identifier={source_deposit.get('repository_identifier')}",
            "passes_for_source_data_review": "yes",
            "passes_for_final_source_data_lock": "no",
        },
        {
            "gate": "lock requirements",
            "current_state": f"requirements={len(lock_requirements)}; all_pass_now={all(row['passes_now'] == 'yes' for row in lock_requirements)}",
            "passes_for_source_data_review": "yes",
            "passes_for_final_source_data_lock": "no",
        },
    ]

    qa_rows = [
        {
            "check": "six figure Source Data rows mapped",
            "result": "PASS" if len(map_rows) == 6 else "FAIL",
            "detail": f"figures_mapped={len(map_rows)}",
        },
        {
            "check": "no source files missing",
            "result": "PASS" if missing == 0 else "FAIL",
            "detail": f"missing_source_files={missing}",
        },
        {
            "check": "final Source Data lock remains blocked",
            "result": "PASS" if all(row["passes_now"] == "no" for row in lock_requirements) else "FAIL",
            "detail": "lock requirements intentionally not satisfied before final figures",
        },
        {
            "check": "repository identifier remains absent",
            "result": "PASS" if source_deposit.get("repository_identifier") is None else "FAIL",
            "detail": f"repository_identifier={source_deposit.get('repository_identifier')}",
        },
    ]

    summary = {
        "package": "source_data_panel_map_review_packet_20260811",
        "figures_mapped": len(map_rows),
        "source_files_packaged": sum(1 for row in copied_source_files if row["copy_status"] == "copied"),
        "missing_source_files": missing,
        "lock_requirement_rows": len(lock_requirements),
        "review_packet_ready": len(map_rows) == 6 and missing == 0,
        "source_data_panel_map_locked": False,
        "repository_identifier_present": source_deposit.get("repository_identifier") is not None,
        "final_figures_ready": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "desktop_report": str(DESKTOP_REPORT),
        "status": "source_data_panel_map_review_packet_ready_final_lock_blocked",
    }

    report = f"""# Source Data Panel-map Review Packet

This packet consolidates figure-level Source Data source files and lock
requirements for local review before final figures exist.

Current state:

1. `figures_mapped={summary["figures_mapped"]}`.
2. `source_files_packaged={summary["source_files_packaged"]}`.
3. `missing_source_files={summary["missing_source_files"]}`.
4. `review_packet_ready={str(summary["review_packet_ready"]).lower()}`.
5. `source_data_panel_map_locked=false`.
6. `repository_identifier_present={str(summary["repository_identifier_present"]).lower()}`.
7. `final_figures_ready=false`.
8. `submission_ready=false`.

Use: review whether each Figure's planned Source_Data file has the correct
source files before final panel-level Source Data lock.

Boundary: this is a review/prelock packet only. It does not create final panel
maps, repository DOI/accession, licence clearance or submission-ready Source
Data.
"""

    write_csv(
        OUT_DIR / "source_data_panel_map_review_matrix.csv",
        [
            "figure_id",
            "source_data_filename",
            "source_file_count",
            "copied_source_file_count",
            "all_source_files_exist",
            "panel_map_review_status",
            "panel_map_lock_status",
            "blocking_reason",
        ],
        map_rows,
    )
    write_csv(
        OUT_DIR / "source_data_panel_map_copied_sources.csv",
        ["figure_id", "source_data_filename", "source_file", "copied_file", "copy_status"],
        copied_source_files,
    )
    write_csv(
        OUT_DIR / "source_data_panel_map_gate_matrix.csv",
        ["gate", "current_state", "passes_for_source_data_review", "passes_for_final_source_data_lock"],
        gate_rows,
    )
    write_csv(OUT_DIR / "source_data_panel_map_review_packet_qa.csv", ["check", "result", "detail"], qa_rows)
    write_text(OUT_DIR / "SOURCE_DATA_PANEL_MAP_REVIEW_PACKET_README.md", report)
    write_text(OUT_DIR / "source_data_panel_map_review_packet_report.md", report)
    write_text(DESKTOP_REPORT, report)
    summary["desktop_plan_updated"] = update_desktop_plan(summary)
    write_text(OUT_DIR / "source_data_panel_map_review_packet_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
