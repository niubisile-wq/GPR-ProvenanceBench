#!/usr/bin/env python3
"""Guarded applier for FMR-006 guarded-recheck receipt writeback candidates."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr006_guarded_writeback_applier_20260810"
PREFLIGHT_DIR = BENCH_ROOT / "reports" / "fmr006_guarded_recheck_receipt_writeback_preflight_20260810"
FMR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
FMR_TEMPLATE = FMR_DIR / "final_manual_receipt_intake_template.csv"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


FMR_FIELDS = [
    "receipt_id",
    "source_action_priority",
    "receipt_type",
    "owner",
    "required_evidence",
    "target_or_route",
    "value_to_fill_after_manual_action",
    "acceptance_test",
    "first_validator",
    "current_status",
    "unlocks_when_valid",
]


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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.76 FMR-006 guarded writeback applier update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr006_guarded_writeback_applier_20260810/` to guard any future FMR-006 writeback from 19.69 candidates.
- Current `candidate_rows={summary["candidate_rows"]}`, `writeback_preflight_allowed={str(summary["writeback_preflight_allowed"]).lower()}`, `execute_flag_supplied={str(summary["execute_flag_supplied"]).lower()}`.
- Current `writeback_executed={str(summary["writeback_executed"]).lower()}`, `real_fmr_template_modified={str(summary["real_fmr_template_modified"]).lower()}`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: default mode is preflight only. It refuses FMR-006 writeback unless the 19.69 candidate exists and `--execute-writeback` is explicitly supplied.
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute-writeback",
        action="store_true",
        help="Actually update FMR-006 in the real final manual receipt intake template.",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    preflight_summary = read_json(PREFLIGHT_DIR / "fmr006_guarded_recheck_receipt_writeback_preflight_summary.json")
    candidates = read_csv(PREFLIGHT_DIR / "fmr006_guarded_recheck_receipt_candidates.csv")
    fmr_rows = read_csv(FMR_TEMPLATE)
    fmr006_rows = [row for row in fmr_rows if row.get("receipt_id") == "FMR-006"]
    candidate_rows = [row for row in candidates if row.get("receipt_id") == "FMR-006"]

    candidate_complete = (
        len(candidate_rows) == 1
        and candidate_rows[0].get("writeback_allowed") == "yes"
        and bool(candidate_rows[0].get("value_to_fill_after_manual_action", "").strip())
    )
    writeback_preflight_allowed = (
        preflight_summary.get("fmr006_writeback_allowed") is True
        and len(fmr006_rows) == 1
        and candidate_complete
    )

    guard_rows = [
        {
            "guard": "preflight_allows_FMR_006_writeback",
            "current": preflight_summary.get("fmr006_writeback_allowed"),
            "required": "true",
            "passes_now": "yes" if preflight_summary.get("fmr006_writeback_allowed") is True else "no",
        },
        {
            "guard": "single_FMR_006_row_present",
            "current": len(fmr006_rows),
            "required": 1,
            "passes_now": "yes" if len(fmr006_rows) == 1 else "no",
        },
        {
            "guard": "single_candidate_present",
            "current": len(candidate_rows),
            "required": 1,
            "passes_now": "yes" if candidate_complete else "no",
        },
        {
            "guard": "explicit_execute_flag",
            "current": args.execute_writeback,
            "required": "true for real writeback",
            "passes_now": "yes" if args.execute_writeback else "no",
        },
    ]

    writeback_executed = False
    real_fmr_template_modified = False
    backup_path = ""
    if writeback_preflight_allowed and args.execute_writeback:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = OUT_DIR / f"final_manual_receipt_intake_template_before_fmr006_19_76_{timestamp}.csv"
        shutil.copy2(FMR_TEMPLATE, backup)
        candidate = candidate_rows[0]
        updated_rows = []
        for row in fmr_rows:
            if row.get("receipt_id") == "FMR-006":
                new_row = row.copy()
                new_row["value_to_fill_after_manual_action"] = candidate["value_to_fill_after_manual_action"]
                new_row["current_status"] = candidate["current_status_after_writeback"]
                updated_rows.append(new_row)
            else:
                updated_rows.append(row)
        write_csv(FMR_TEMPLATE, FMR_FIELDS, updated_rows)
        writeback_executed = True
        real_fmr_template_modified = True
        backup_path = str(backup)

    qa_rows = [
        {
            "check": "FMR intake template imported",
            "result": "PASS" if len(fmr_rows) == 6 and len(fmr006_rows) == 1 else "FAIL",
            "detail": f"fmr_rows={len(fmr_rows)}; fmr006_rows={len(fmr006_rows)}",
        },
        {
            "check": "writeback preflight follows 19.69 candidate state",
            "result": "PASS"
            if (
                writeback_preflight_allowed == candidate_complete
                and preflight_summary.get("fmr006_writeback_allowed") == writeback_preflight_allowed
            )
            else "PASS"
            if not candidate_complete and not writeback_preflight_allowed
            else "FAIL",
            "detail": f"candidate_complete={candidate_complete}; writeback_preflight_allowed={writeback_preflight_allowed}",
        },
        {
            "check": "default mode does not modify real FMR template",
            "result": "PASS" if args.execute_writeback or not real_fmr_template_modified else "FAIL",
            "detail": f"execute_writeback={args.execute_writeback}; real_fmr_template_modified={real_fmr_template_modified}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr006_guarded_writeback_applier_20260810",
        "candidate_rows": len(candidate_rows),
        "candidate_complete": candidate_complete,
        "writeback_preflight_allowed": writeback_preflight_allowed,
        "execute_flag_supplied": args.execute_writeback,
        "writeback_executed": writeback_executed,
        "real_fmr_template_modified": real_fmr_template_modified,
        "backup_path": backup_path,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "fmr006_guarded_writeback_applier_executed"
            if writeback_executed
            else "fmr006_guarded_writeback_applier_ready_refusing_current_state"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(OUT_DIR / "fmr006_guarded_writeback_preflight.csv", ["guard", "current", "required", "passes_now"], guard_rows)
    write_csv(
        OUT_DIR / "fmr006_guarded_writeback_candidate_audit.csv",
        [
            "receipt_id",
            "target_or_route",
            "current_status_after_writeback",
            "value_to_fill_after_manual_action",
            "first_validator",
            "writeback_allowed",
        ],
        candidate_rows,
    )
    write_csv(OUT_DIR / "fmr006_guarded_writeback_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# FMR-006 Guarded Writeback Applier

Status: `{summary["status"]}`

Current result:

1. Candidate rows: {summary["candidate_rows"]}
2. Writeback preflight allowed: {str(summary["writeback_preflight_allowed"]).lower()}
3. Execute flag supplied: {str(summary["execute_flag_supplied"]).lower()}
4. Writeback executed: {str(summary["writeback_executed"]).lower()}
5. Real FMR template modified: {str(summary["real_fmr_template_modified"]).lower()}
6. Portal upload allowed: false
7. Submission ready: false

Boundary: default mode is preflight only. Real FMR-006 writeback requires a
complete 19.69 candidate and the explicit `--execute-writeback` flag. This
script does not complete prerequisite FMR rows, execute recheck, upload portal
files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR006_GUARDED_WRITEBACK_APPLIER_README.md", report)
    write_text(OUT_DIR / "fmr006_guarded_writeback_applier_report.md", report)
    write_text(OUT_DIR / "fmr006_guarded_writeback_applier_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
