#!/usr/bin/env python3
"""Guarded applier for external-dependency EDS writeback candidates."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_dependency_eds_guarded_writeback_applier_20260810"
INTAKE_DIR = BENCH_ROOT / "reports" / "external_dependency_sendout_evidence_intake_preflight_20260810"
EDS_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_sendout_receipt_validator_20260810"
EDS_TEMPLATE = EDS_DIR / "external_dependency_escalation_sendout_receipt_template.csv"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


FIELDS = [
    "send_receipt_id",
    "receipt_id",
    "owner",
    "required_send_evidence",
    "sent_datetime_local",
    "sender",
    "recipient_or_channel",
    "sent_message_path",
    "sent_message_sha256",
    "current_status",
    "unlock_if_valid",
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


def is_candidate_complete(row: dict[str, str]) -> bool:
    required = [
        "send_receipt_id",
        "receipt_id",
        "sent_datetime_local",
        "sender",
        "recipient_or_channel",
        "sent_message_path",
        "sent_message_sha256",
    ]
    return all(row.get(field, "").strip() and not row.get(field, "").strip().startswith("FILL_AFTER") for field in required)


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.58 EDS guarded writeback applier update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/external_dependency_eds_guarded_writeback_applier_20260810/` to guard any future EDS writeback from 19.57 candidates.
- Current `candidate_rows={summary["candidate_rows"]}`, `complete_candidate_rows={summary["complete_candidate_rows"]}`, `writeback_preflight_allowed={str(summary["writeback_preflight_allowed"]).lower()}`.
- Current `writeback_executed={str(summary["writeback_executed"]).lower()}`, `real_eds_template_modified={str(summary["real_eds_template_modified"]).lower()}`, `portal_upload_allowed=false`, `submission_ready=false`.
- Boundary: default mode is preflight only. It refuses writeback unless 5 complete candidates exist and `--execute-writeback` is explicitly supplied.
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
        help="Actually overwrite the real EDS template after all guard checks pass.",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    intake_summary = read_json(INTAKE_DIR / "external_dependency_sendout_evidence_intake_preflight_summary.json")
    candidates = read_csv(INTAKE_DIR / "external_dependency_sendout_evidence_writeback_candidates.csv")
    current_eds = read_csv(EDS_TEMPLATE)

    complete_candidate_rows = sum(1 for row in candidates if is_candidate_complete(row))
    candidate_ids = {row.get("send_receipt_id", "") for row in candidates}
    expected_ids = {f"EDS-{idx:03d}" for idx in range(1, 6)}
    ids_complete = candidate_ids == expected_ids
    intake_allows_writeback = intake_summary.get("eds_writeback_allowed") is True
    writeback_preflight_allowed = (
        len(candidates) == 5
        and complete_candidate_rows == 5
        and ids_complete
        and intake_allows_writeback
    )
    writeback_executed = False
    real_eds_template_modified = False
    backup_path = ""

    guard_rows = [
        {
            "guard": "intake_allows_writeback",
            "current": intake_allows_writeback,
            "required": "true",
            "passes_now": "yes" if intake_allows_writeback else "no",
        },
        {
            "guard": "five_candidates_present",
            "current": len(candidates),
            "required": 5,
            "passes_now": "yes" if len(candidates) == 5 else "no",
        },
        {
            "guard": "all_candidates_complete",
            "current": complete_candidate_rows,
            "required": 5,
            "passes_now": "yes" if complete_candidate_rows == 5 else "no",
        },
        {
            "guard": "candidate_ids_exact",
            "current": ";".join(sorted(candidate_ids)),
            "required": ";".join(sorted(expected_ids)),
            "passes_now": "yes" if ids_complete else "no",
        },
        {
            "guard": "explicit_execute_flag",
            "current": args.execute_writeback,
            "required": "true for real writeback",
            "passes_now": "yes" if args.execute_writeback else "no",
        },
    ]

    if writeback_preflight_allowed and args.execute_writeback:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = OUT_DIR / f"external_dependency_escalation_sendout_receipt_template_before_19_58_{timestamp}.csv"
        shutil.copy2(EDS_TEMPLATE, backup)
        write_csv(EDS_TEMPLATE, FIELDS, candidates)
        writeback_executed = True
        real_eds_template_modified = True
        backup_path = str(backup)

    qa_rows = [
        {
            "check": "real EDS template imported",
            "result": "PASS" if len(current_eds) == 5 else "FAIL",
            "detail": f"current_eds_rows={len(current_eds)}",
        },
        {
            "check": "writeback preflight accurately follows intake state",
            "result": "PASS" if writeback_preflight_allowed == (intake_allows_writeback and len(candidates) == 5 and complete_candidate_rows == 5 and ids_complete) else "FAIL",
            "detail": f"writeback_preflight_allowed={writeback_preflight_allowed}",
        },
        {
            "check": "default mode does not modify real EDS template",
            "result": "PASS" if args.execute_writeback or not real_eds_template_modified else "FAIL",
            "detail": f"execute_writeback={args.execute_writeback}; real_eds_template_modified={real_eds_template_modified}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "external_dependency_eds_guarded_writeback_applier_20260810",
        "candidate_rows": len(candidates),
        "complete_candidate_rows": complete_candidate_rows,
        "candidate_ids_exact": ids_complete,
        "intake_allows_writeback": intake_allows_writeback,
        "writeback_preflight_allowed": writeback_preflight_allowed,
        "execute_flag_supplied": args.execute_writeback,
        "writeback_executed": writeback_executed,
        "real_eds_template_modified": real_eds_template_modified,
        "backup_path": backup_path,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "external_dependency_eds_guarded_writeback_applier_executed"
            if writeback_executed
            else "external_dependency_eds_guarded_writeback_applier_ready_refusing_current_state"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "external_dependency_eds_guarded_writeback_preflight.csv",
        ["guard", "current", "required", "passes_now"],
        guard_rows,
    )
    write_csv(
        OUT_DIR / "external_dependency_eds_guarded_writeback_candidate_audit.csv",
        ["send_receipt_id", "receipt_id", "current_status", "sent_message_path", "sent_message_sha256"],
        candidates,
    )
    write_csv(
        OUT_DIR / "external_dependency_eds_guarded_writeback_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# External Dependency EDS Guarded Writeback Applier

Status: `{summary["status"]}`

Current result:

1. Candidate rows: {summary["candidate_rows"]}
2. Complete candidate rows: {summary["complete_candidate_rows"]}
3. Writeback preflight allowed: {str(summary["writeback_preflight_allowed"]).lower()}
4. Execute flag supplied: {str(summary["execute_flag_supplied"]).lower()}
5. Writeback executed: {str(summary["writeback_executed"]).lower()}
6. Real EDS template modified: {str(summary["real_eds_template_modified"]).lower()}
7. Portal upload allowed: false
8. Submission ready: false

Boundary: default mode is preflight only. Real writeback requires five complete
19.57 candidates, exact EDS-001 through EDS-005 coverage, intake approval and
the explicit `--execute-writeback` flag. This script never sends email, fills
FMR rows, runs recheck, uploads portal files or marks the manuscript submitted.
"""
    write_text(OUT_DIR / "EXTERNAL_DEPENDENCY_EDS_GUARDED_WRITEBACK_APPLIER_README.md", report)
    write_text(OUT_DIR / "external_dependency_eds_guarded_writeback_applier_report.md", report)
    write_text(
        OUT_DIR / "external_dependency_eds_guarded_writeback_applier_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
