#!/usr/bin/env python3
"""Build a guarded preflight for FMR-006 guarded-recheck receipt writeback."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr006_guarded_recheck_receipt_writeback_preflight_20260810"
FMR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
RECEIPT_COMPLETION_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_completion_validator_20260810"
RECHECK_AUDIT_DIR = BENCH_ROOT / "reports" / "final_guarded_recheck_execution_audit_20260810"
M0_M2_LOG = BENCH_ROOT / "reports" / "latest_run_m0_m2_checks_20260810.log"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


PREREQ_RECEIPTS = ["FMR-001", "FMR-002", "FMR-003", "FMR-004", "FMR-005"]


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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_log_text(path: Path) -> str:
    data = path.read_bytes()
    if b"\x00" in data[:200]:
        return data.decode("utf-16", errors="replace")
    return data.decode("utf-8-sig", errors="replace")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.69 FMR-006 guarded recheck receipt writeback preflight update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr006_guarded_recheck_receipt_writeback_preflight_20260810/` to guard future FMR-006 writeback from a real post-evidence M0-M2 guarded recheck.
- Current `prereq_complete_receipts={summary["prereq_complete_receipts"]}/5`, `m0_m2_log_exists={str(summary["m0_m2_log_exists"]).lower()}`, `m0_m2_pass_detected={str(summary["m0_m2_pass_detected"]).lower()}`.
- Current `guarded_recheck_allowed={str(summary["guarded_recheck_allowed"]).lower()}`, `recheck_executed={str(summary["recheck_executed"]).lower()}`, `fmr006_writeback_allowed={str(summary["fmr006_writeback_allowed"]).lower()}`.
- Boundary: FMR-006 cannot move from `FILL_AFTER_RECHECK/waiting_for_FMR_001_to_FMR_005` until FMR-001 through FMR-005 are complete and the guarded recheck is actually allowed/executed after real evidence. This preflight does not write the FMR intake template, execute recheck, upload portal files or submit.
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fmr_rows = read_csv(FMR_DIR / "final_manual_receipt_intake_template.csv")
    completion_rows = read_csv(RECEIPT_COMPLETION_DIR / "final_manual_receipt_completion_status.csv")
    completion_summary = read_json(RECEIPT_COMPLETION_DIR / "final_manual_receipt_completion_validator_summary.json")
    audit_summary = read_json(RECHECK_AUDIT_DIR / "final_guarded_recheck_execution_audit_summary.json")

    fmr006_rows = [row for row in fmr_rows if row.get("receipt_id") == "FMR-006"]
    completion_by_id = {row.get("receipt_id", ""): row for row in completion_rows}
    prereq_rows = [completion_by_id.get(receipt_id, {}) for receipt_id in PREREQ_RECEIPTS]
    complete_prereq_rows = [row for row in prereq_rows if row.get("completion_passes_now") == "yes"]
    missing_prereq_receipts = [receipt_id for receipt_id, row in zip(PREREQ_RECEIPTS, prereq_rows) if row.get("completion_passes_now") != "yes"]
    receipt_completion_allowed = completion_summary.get("receipt_completion_allowed") is True
    guarded_recheck_allowed = completion_summary.get("guarded_recheck_allowed") is True
    audit_launcher_allowed = audit_summary.get("launcher_execution_allowed") is True
    recheck_executed = audit_summary.get("recheck_executed") is True

    m0_m2_log_exists = M0_M2_LOG.exists()
    m0_m2_log_sha256 = file_sha256(M0_M2_LOG) if m0_m2_log_exists else ""
    m0_m2_text = read_log_text(M0_M2_LOG) if m0_m2_log_exists else ""
    m0_m2_pass_detected = "M0-M2 checks completed" in m0_m2_text and "Exception" not in m0_m2_text

    fmr006_writeback_allowed = (
        len(fmr006_rows) == 1
        and len(complete_prereq_rows) == 5
        and receipt_completion_allowed
        and guarded_recheck_allowed
        and audit_launcher_allowed
        and recheck_executed
        and m0_m2_log_exists
        and m0_m2_pass_detected
    )

    prereq_status_rows = []
    for receipt_id in PREREQ_RECEIPTS:
        row = completion_by_id.get(receipt_id, {})
        passes = row.get("completion_passes_now") == "yes"
        prereq_status_rows.append(
            {
                "receipt_id": receipt_id,
                "current_status": row.get("current_status", ""),
                "placeholder_value": row.get("placeholder_value", ""),
                "completion_passes_now": row.get("completion_passes_now", "no"),
                "blocking_reason": "" if passes else row.get("blocking_reason", "missing completion row"),
            }
        )

    candidate_rows = []
    if fmr006_writeback_allowed:
        fmr006 = fmr006_rows[0]
        candidate_rows.append(
            {
                "receipt_id": "FMR-006",
                "target_or_route": fmr006.get("target_or_route", ""),
                "current_status_after_writeback": "complete",
                "value_to_fill_after_manual_action": f"M0-M2 guarded recheck completed; log={M0_M2_LOG}; sha256={m0_m2_log_sha256}",
                "first_validator": fmr006.get("first_validator", ""),
                "writeback_allowed": "yes",
            }
        )

    guard_rows = [
        {
            "guard": "single_FMR_006_row_present",
            "current": len(fmr006_rows),
            "required": 1,
            "passes_now": "yes" if len(fmr006_rows) == 1 else "no",
        },
        {
            "guard": "FMR_001_to_FMR_005_complete",
            "current": len(complete_prereq_rows),
            "required": 5,
            "passes_now": "yes" if len(complete_prereq_rows) == 5 else "no",
        },
        {
            "guard": "receipt_completion_allows_guarded_recheck",
            "current": f"receipt_completion_allowed={receipt_completion_allowed}; guarded_recheck_allowed={guarded_recheck_allowed}",
            "required": "both true",
            "passes_now": "yes" if receipt_completion_allowed and guarded_recheck_allowed else "no",
        },
        {
            "guard": "launcher_allowed_and_recheck_executed",
            "current": f"launcher_execution_allowed={audit_launcher_allowed}; recheck_executed={recheck_executed}",
            "required": "both true",
            "passes_now": "yes" if audit_launcher_allowed and recheck_executed else "no",
        },
        {
            "guard": "M0_M2_pass_log_available",
            "current": f"log_exists={m0_m2_log_exists}; pass_detected={m0_m2_pass_detected}; sha256={m0_m2_log_sha256}",
            "required": "log_exists=true; pass_detected=true",
            "passes_now": "yes" if m0_m2_log_exists and m0_m2_pass_detected else "no",
        },
    ]

    blocker_rows = []
    if missing_prereq_receipts:
        blocker_rows.append(
            {
                "blocker": "FMR-001 through FMR-005 not complete",
                "evidence": ";".join(missing_prereq_receipts),
                "blocks": "FMR-006 writeback candidate and final guarded recheck receipt",
            }
        )
    if not receipt_completion_allowed or not guarded_recheck_allowed:
        blocker_rows.append(
            {
                "blocker": "receipt completion validator does not allow guarded recheck",
                "evidence": f"receipt_completion_allowed={receipt_completion_allowed}; guarded_recheck_allowed={guarded_recheck_allowed}",
                "blocks": "FMR-006 writeback candidate",
            }
        )
    if not audit_launcher_allowed or not recheck_executed:
        blocker_rows.append(
            {
                "blocker": "guarded recheck not allowed or not executed",
                "evidence": f"launcher_execution_allowed={audit_launcher_allowed}; recheck_executed={recheck_executed}",
                "blocks": "FMR-006 writeback candidate",
            }
        )
    if not m0_m2_log_exists or not m0_m2_pass_detected:
        blocker_rows.append(
            {
                "blocker": "M0-M2 pass log missing or not detected",
                "evidence": f"log_exists={m0_m2_log_exists}; pass_detected={m0_m2_pass_detected}",
                "blocks": "FMR-006 writeback candidate",
            }
        )

    qa_rows = [
        {
            "check": "FMR-006 row imported",
            "result": "PASS" if len(fmr006_rows) == 1 else "FAIL",
            "detail": f"fmr006_rows={len(fmr006_rows)}",
        },
        {
            "check": "prerequisite receipts imported",
            "result": "PASS" if len(prereq_rows) == 5 and all(prereq_rows) else "FAIL",
            "detail": f"prereq_rows={len(prereq_rows)}; missing={';'.join(missing_prereq_receipts)}",
        },
        {
            "check": "M0-M2 log alone does not unlock FMR-006",
            "result": "PASS" if len(complete_prereq_rows) == 5 or not fmr006_writeback_allowed else "FAIL",
            "detail": f"complete_prereq_rows={len(complete_prereq_rows)}; m0_m2_pass_detected={m0_m2_pass_detected}; fmr006_writeback_allowed={fmr006_writeback_allowed}",
        },
        {
            "check": "candidate generation follows recheck gates",
            "result": "PASS" if len(candidate_rows) == (1 if fmr006_writeback_allowed else 0) else "FAIL",
            "detail": f"candidate_rows={len(candidate_rows)}; fmr006_writeback_allowed={fmr006_writeback_allowed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr006_guarded_recheck_receipt_writeback_preflight_20260810",
        "fmr006_rows": len(fmr006_rows),
        "prereq_receipts": len(PREREQ_RECEIPTS),
        "prereq_complete_receipts": len(complete_prereq_rows),
        "missing_prereq_receipts": missing_prereq_receipts,
        "receipt_completion_allowed": receipt_completion_allowed,
        "guarded_recheck_allowed": guarded_recheck_allowed,
        "launcher_execution_allowed": audit_launcher_allowed,
        "recheck_executed": recheck_executed,
        "m0_m2_log_exists": m0_m2_log_exists,
        "m0_m2_pass_detected": m0_m2_pass_detected,
        "m0_m2_log_sha256": m0_m2_log_sha256,
        "fmr006_candidate_rows": len(candidate_rows),
        "fmr006_writeback_allowed": fmr006_writeback_allowed,
        "real_fmr_template_modified": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "fmr006_guarded_recheck_receipt_writeback_preflight_candidate_ready"
            if fmr006_writeback_allowed
            else "fmr006_guarded_recheck_receipt_writeback_preflight_ready_blocked_waiting_fmr001_to_fmr005"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr006_prerequisite_receipt_status.csv",
        ["receipt_id", "current_status", "placeholder_value", "completion_passes_now", "blocking_reason"],
        prereq_status_rows,
    )
    write_csv(
        OUT_DIR / "fmr006_guarded_recheck_receipt_guard_matrix.csv",
        ["guard", "current", "required", "passes_now"],
        guard_rows,
    )
    write_csv(
        OUT_DIR / "fmr006_guarded_recheck_receipt_candidates.csv",
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
    write_csv(
        OUT_DIR / "fmr006_guarded_recheck_receipt_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "fmr006_guarded_recheck_receipt_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# FMR-006 Guarded Recheck Receipt Writeback Preflight

Status: `{summary["status"]}`

Current result:

1. FMR-006 rows: {summary["fmr006_rows"]}
2. Prerequisite complete receipts: {summary["prereq_complete_receipts"]}/5
3. Missing prerequisite receipts: {";".join(summary["missing_prereq_receipts"])}
4. Receipt completion allowed: {str(summary["receipt_completion_allowed"]).lower()}
5. Guarded recheck allowed: {str(summary["guarded_recheck_allowed"]).lower()}
6. Launcher execution allowed: {str(summary["launcher_execution_allowed"]).lower()}
7. Recheck executed: {str(summary["recheck_executed"]).lower()}
8. M0-M2 log exists: {str(summary["m0_m2_log_exists"]).lower()}
9. M0-M2 pass detected: {str(summary["m0_m2_pass_detected"]).lower()}
10. FMR-006 candidate rows: {summary["fmr006_candidate_rows"]}
11. FMR-006 writeback allowed: {str(summary["fmr006_writeback_allowed"]).lower()}
12. Real FMR template modified: false
13. Portal upload allowed: false
14. Submission ready: false

Boundary: FMR-006 remains blocked until FMR-001 through FMR-005 are complete and
a guarded post-evidence M0-M2 recheck is actually allowed and executed. A PASS
log from a routine local run is retained as evidence but is not sufficient by
itself. This preflight does not write the FMR intake template, execute recheck,
upload portal files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR006_GUARDED_RECHECK_RECEIPT_WRITEBACK_PREFLIGHT_README.md", report)
    write_text(OUT_DIR / "fmr006_guarded_recheck_receipt_writeback_preflight_report.md", report)
    write_text(
        OUT_DIR / "fmr006_guarded_recheck_receipt_writeback_preflight_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
