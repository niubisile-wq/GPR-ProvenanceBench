#!/usr/bin/env python3
"""Build a guarded preflight for FMR-001 sendout-completion writeback."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr001_sendout_completion_writeback_preflight_20260810"
FMR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
EDS_DIR = BENCH_ROOT / "reports" / "external_dependency_escalation_sendout_receipt_validator_20260810"
POST_REVALIDATION_DIR = BENCH_ROOT / "reports" / "external_dependency_post_writeback_revalidation_orchestrator_20260810"
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


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.60 FMR-001 sendout completion writeback preflight update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr001_sendout_completion_writeback_preflight_20260810/` to guard future FMR-001 writeback after all EDS send receipts validate.
- Current `eds_sent_receipt_rows={summary["eds_sent_receipt_rows"]}`, `eds_missing_send_receipts={summary["eds_missing_send_receipts"]}`, `fmr001_candidate_rows={summary["fmr001_candidate_rows"]}`.
- Current `fmr001_writeback_allowed={str(summary["fmr001_writeback_allowed"]).lower()}`, `real_fmr_template_modified=false`, `guarded_recheck_allowed=false`, `submission_ready=false`.
- Boundary: this preflight only proposes the FMR-001 value after verified EDS evidence. It does not write the FMR intake template, run validators, upload portal files or submit.
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
    eds_rows = read_csv(EDS_DIR / "external_dependency_escalation_sendout_receipt_template.csv")
    eds_summary = read_json(EDS_DIR / "external_dependency_escalation_sendout_receipt_validator_summary.json")
    post_revalidation_summary = read_json(
        POST_REVALIDATION_DIR / "external_dependency_post_writeback_revalidation_orchestrator_summary.json"
    )

    fmr001_rows = [row for row in fmr_rows if row.get("receipt_id") == "FMR-001"]
    sent_verified_rows = [row for row in eds_rows if row.get("current_status") == "sent_verified"]
    eds_ids = {row.get("send_receipt_id", "") for row in sent_verified_rows}
    expected_eds_ids = {f"EDS-{idx:03d}" for idx in range(1, 6)}
    eds_complete = (
        eds_summary.get("sent_receipt_rows") == 5
        and eds_summary.get("missing_send_receipts") == 0
        and eds_summary.get("fmr001_unlock_allowed") is True
        and eds_ids == expected_eds_ids
    )
    post_revalidation_complete = post_revalidation_summary.get("fmr001_unlock_allowed_after_revalidation") is True
    fmr001_writeback_allowed = len(fmr001_rows) == 1 and eds_complete and post_revalidation_complete

    source_evidence = "; ".join(
        f"{row.get('send_receipt_id')}:{row.get('sent_message_sha256')}" for row in sent_verified_rows
    )
    candidate_rows = []
    if fmr001_writeback_allowed:
        fmr001 = fmr001_rows[0]
        candidate_rows.append(
            {
                "receipt_id": "FMR-001",
                "target_or_route": fmr001.get("target_or_route", ""),
                "current_status_after_writeback": "complete",
                "value_to_fill_after_manual_action": (
                    "EDS sendout verified for EDS-001..EDS-005; "
                    f"sent_receipt_rows={eds_summary.get('sent_receipt_rows')}; "
                    f"source_hashes={source_evidence}"
                ),
                "first_validator": fmr001.get("first_validator", ""),
                "writeback_allowed": "yes",
            }
        )

    guard_rows = [
        {
            "guard": "single_FMR_001_row_present",
            "current": len(fmr001_rows),
            "required": 1,
            "passes_now": "yes" if len(fmr001_rows) == 1 else "no",
        },
        {
            "guard": "all_EDS_rows_sent_verified",
            "current": len(sent_verified_rows),
            "required": 5,
            "passes_now": "yes" if eds_complete else "no",
        },
        {
            "guard": "post_revalidation_unlock_confirmed",
            "current": post_revalidation_complete,
            "required": "true",
            "passes_now": "yes" if post_revalidation_complete else "no",
        },
        {
            "guard": "FMR_001_writeback_allowed",
            "current": fmr001_writeback_allowed,
            "required": "true",
            "passes_now": "yes" if fmr001_writeback_allowed else "no",
        },
    ]

    blocker_rows = [
        {
            "blocker": "EDS send receipts incomplete",
            "evidence": f"sent_receipt_rows={eds_summary.get('sent_receipt_rows')}; missing_send_receipts={eds_summary.get('missing_send_receipts')}",
            "blocks": "FMR-001 writeback candidate",
        }
    ] if not eds_complete else []
    if not post_revalidation_complete:
        blocker_rows.append(
            {
                "blocker": "post-writeback revalidation not complete",
                "evidence": f"fmr001_unlock_allowed_after_revalidation={post_revalidation_complete}",
                "blocks": "FMR-001 writeback candidate",
            }
        )

    qa_rows = [
        {
            "check": "FMR-001 row imported",
            "result": "PASS" if len(fmr001_rows) == 1 else "FAIL",
            "detail": f"fmr001_rows={len(fmr001_rows)}",
        },
        {
            "check": "candidate generation follows EDS and revalidation gates",
            "result": "PASS" if len(candidate_rows) == (1 if fmr001_writeback_allowed else 0) else "FAIL",
            "detail": f"candidate_rows={len(candidate_rows)}; fmr001_writeback_allowed={fmr001_writeback_allowed}",
        },
        {
            "check": "real FMR template is not modified",
            "result": "PASS",
            "detail": "real_fmr_template_modified=false",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "guarded_recheck_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr001_sendout_completion_writeback_preflight_20260810",
        "fmr001_rows": len(fmr001_rows),
        "eds_sent_receipt_rows": eds_summary.get("sent_receipt_rows", 0),
        "eds_missing_send_receipts": eds_summary.get("missing_send_receipts", 0),
        "eds_complete": eds_complete,
        "post_revalidation_complete": post_revalidation_complete,
        "fmr001_candidate_rows": len(candidate_rows),
        "fmr001_writeback_allowed": fmr001_writeback_allowed,
        "real_fmr_template_modified": False,
        "guarded_recheck_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "fmr001_sendout_completion_writeback_preflight_candidate_ready"
            if fmr001_writeback_allowed
            else "fmr001_sendout_completion_writeback_preflight_ready_blocked_waiting_verified_eds"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr001_sendout_completion_writeback_guard_matrix.csv",
        ["guard", "current", "required", "passes_now"],
        guard_rows,
    )
    write_csv(
        OUT_DIR / "fmr001_sendout_completion_writeback_candidates.csv",
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
        OUT_DIR / "fmr001_sendout_completion_writeback_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "fmr001_sendout_completion_writeback_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# FMR-001 Sendout Completion Writeback Preflight

Status: `{summary["status"]}`

Current result:

1. FMR-001 rows: {summary["fmr001_rows"]}
2. EDS sent receipt rows: {summary["eds_sent_receipt_rows"]}
3. EDS missing send receipts: {summary["eds_missing_send_receipts"]}
4. FMR-001 candidate rows: {summary["fmr001_candidate_rows"]}
5. FMR-001 writeback allowed: {str(summary["fmr001_writeback_allowed"]).lower()}
6. Real FMR template modified: false
7. Guarded recheck allowed: false
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this preflight only proposes the FMR-001 completion value after EDS
sendout evidence has been verified and post-writeback revalidation confirms the
unlock. It does not write the FMR intake template, run validators, upload portal
files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR001_SENDOUT_COMPLETION_WRITEBACK_PREFLIGHT_README.md", report)
    write_text(OUT_DIR / "fmr001_sendout_completion_writeback_preflight_report.md", report)
    write_text(
        OUT_DIR / "fmr001_sendout_completion_writeback_preflight_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
