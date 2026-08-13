#!/usr/bin/env python3
"""Build a guarded preflight for FMR-003 returned-evidence writeback."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr003_returned_evidence_writeback_preflight_20260810"
FMR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
RETURN_SCANNER_DIR = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810"
RB001_HASH_DIR = BENCH_ROOT / "reports" / "rb001_hash_manifest_readiness_validator_20260810"
RB001_RECEIPT_DIR = BENCH_ROOT / "reports" / "rb001_receipt_completion_validator_20260810"
RB001_CLOSEOUT_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dashboard_20260810"
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
    marker = "### 19.66 FMR-003 returned evidence writeback preflight update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr003_returned_evidence_writeback_preflight_20260810/` to guard future FMR-003 writeback from real returned-evidence drops.
- Current `candidate_return_files={summary["candidate_return_files"]}`, `hash_manifest_ready={str(summary["hash_manifest_ready"]).lower()}`, `rb001_receipt_complete={str(summary["rb001_receipt_complete"]).lower()}`, `rb001_closed={str(summary["rb001_closed"]).lower()}`.
- Current `fmr003_candidate_rows={summary["fmr003_candidate_rows"]}`, `fmr003_writeback_allowed={str(summary["fmr003_writeback_allowed"]).lower()}`, `real_fmr_template_modified=false`.
- Boundary: scanner output, hash manifest, RB-001 receipt completion and RB-001 closeout must all pass before FMR-003 can move from `FILL_AFTER_DROP/missing`. This preflight does not write the FMR intake template, close RB-001, run guarded recheck or submit.
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
    scanner_summary = read_json(RETURN_SCANNER_DIR / "final_return_evidence_intake_scanner_summary.json")
    hash_summary = read_json(RB001_HASH_DIR / "rb001_hash_manifest_readiness_validator_summary.json")
    receipt_summary = read_json(RB001_RECEIPT_DIR / "rb001_receipt_completion_validator_summary.json")
    closeout_summary = read_json(RB001_CLOSEOUT_DIR / "rb001_closeout_dashboard_summary.json")

    fmr003_rows = [row for row in fmr_rows if row.get("receipt_id") == "FMR-003"]
    candidate_return_files = int(scanner_summary.get("candidate_return_files", 0) or 0)
    scanner_qa_pass = scanner_summary.get("qa_pass") is True
    scanner_gate_closure_allowed = scanner_summary.get("gate_closure_allowed") is True
    hash_manifest_ready = hash_summary.get("hash_manifest_ready") is True
    hash_reconciled_rows = int(hash_summary.get("reconciled_rows", 0) or 0)
    receipt_complete = receipt_summary.get("receipt_complete") is True
    rb001_closed = closeout_summary.get("rb001_closed") is True

    fmr003_writeback_allowed = (
        len(fmr003_rows) == 1
        and candidate_return_files > 0
        and scanner_qa_pass
        and scanner_gate_closure_allowed
        and hash_manifest_ready
        and hash_reconciled_rows == candidate_return_files
        and receipt_complete
        and rb001_closed
    )

    candidate_rows = []
    if fmr003_writeback_allowed:
        fmr003 = fmr003_rows[0]
        candidate_rows.append(
            {
                "receipt_id": "FMR-003",
                "target_or_route": fmr003.get("target_or_route", ""),
                "current_status_after_writeback": "complete",
                "value_to_fill_after_manual_action": (
                    f"Returned evidence drop accepted: candidate_return_files={candidate_return_files}; "
                    f"hash_reconciled_rows={hash_reconciled_rows}; rb001_closed=true"
                ),
                "first_validator": fmr003.get("first_validator", ""),
                "writeback_allowed": "yes",
            }
        )

    guard_rows = [
        {
            "guard": "single_FMR_003_row_present",
            "current": len(fmr003_rows),
            "required": 1,
            "passes_now": "yes" if len(fmr003_rows) == 1 else "no",
        },
        {
            "guard": "returned_evidence_scanner_has_candidate_files",
            "current": candidate_return_files,
            "required": ">0",
            "passes_now": "yes" if candidate_return_files > 0 else "no",
        },
        {
            "guard": "scanner_qa_and_gate_closure_allowed",
            "current": f"qa_pass={scanner_qa_pass}; gate_closure_allowed={scanner_gate_closure_allowed}",
            "required": "both true",
            "passes_now": "yes" if scanner_qa_pass and scanner_gate_closure_allowed else "no",
        },
        {
            "guard": "hash_manifest_ready_and_reconciled_to_scanner",
            "current": f"hash_manifest_ready={hash_manifest_ready}; reconciled_rows={hash_reconciled_rows}",
            "required": f"hash_manifest_ready=true; reconciled_rows={candidate_return_files}",
            "passes_now": "yes" if hash_manifest_ready and hash_reconciled_rows == candidate_return_files and candidate_return_files > 0 else "no",
        },
        {
            "guard": "rb001_receipt_complete",
            "current": receipt_complete,
            "required": "true",
            "passes_now": "yes" if receipt_complete else "no",
        },
        {
            "guard": "rb001_closeout_complete",
            "current": rb001_closed,
            "required": "true",
            "passes_now": "yes" if rb001_closed else "no",
        },
    ]

    blocker_rows = []
    if candidate_return_files == 0:
        blocker_rows.append(
            {
                "blocker": "no real returned evidence files detected",
                "evidence": "candidate_return_files=0",
                "blocks": "FMR-003 writeback candidate and RB-001 closeout",
            }
        )
    if not scanner_gate_closure_allowed:
        blocker_rows.append(
            {
                "blocker": "returned evidence scanner gate closure not allowed",
                "evidence": f"qa_pass={scanner_qa_pass}; gate_closure_allowed={scanner_gate_closure_allowed}",
                "blocks": "FMR-003 writeback candidate",
            }
        )
    if not hash_manifest_ready:
        blocker_rows.append(
            {
                "blocker": "RB-001 hash manifest not ready",
                "evidence": f"hash_manifest_ready={hash_manifest_ready}; reconciled_rows={hash_reconciled_rows}",
                "blocks": "FMR-003 writeback candidate",
            }
        )
    if not receipt_complete:
        blocker_rows.append(
            {
                "blocker": "RB-001 receipt not complete",
                "evidence": f"receipt_complete={receipt_complete}; completed_receipt_rows={receipt_summary.get('completed_receipt_rows')}",
                "blocks": "FMR-003 writeback candidate",
            }
        )
    if not rb001_closed:
        blocker_rows.append(
            {
                "blocker": "RB-001 closeout not complete",
                "evidence": f"rb001_closed={rb001_closed}; writeback_allowed_rows={closeout_summary.get('writeback_allowed_rows')}",
                "blocks": "FMR-003 writeback candidate and guarded recheck",
            }
        )

    qa_rows = [
        {
            "check": "FMR-003 row imported",
            "result": "PASS" if len(fmr003_rows) == 1 else "FAIL",
            "detail": f"fmr003_rows={len(fmr003_rows)}",
        },
        {
            "check": "candidate generation follows all returned-evidence gates",
            "result": "PASS" if len(candidate_rows) == (1 if fmr003_writeback_allowed else 0) else "FAIL",
            "detail": f"candidate_rows={len(candidate_rows)}; fmr003_writeback_allowed={fmr003_writeback_allowed}",
        },
        {
            "check": "empty scanner does not unlock writeback",
            "result": "PASS" if candidate_return_files > 0 or not fmr003_writeback_allowed else "FAIL",
            "detail": f"candidate_return_files={candidate_return_files}; fmr003_writeback_allowed={fmr003_writeback_allowed}",
        },
        {
            "check": "real FMR template untouched",
            "result": "PASS",
            "detail": "real_fmr_template_modified=false",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "guarded_recheck_allowed=false; portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr003_returned_evidence_writeback_preflight_20260810",
        "fmr003_rows": len(fmr003_rows),
        "candidate_return_files": candidate_return_files,
        "scanner_qa_pass": scanner_qa_pass,
        "scanner_gate_closure_allowed": scanner_gate_closure_allowed,
        "hash_manifest_ready": hash_manifest_ready,
        "hash_reconciled_rows": hash_reconciled_rows,
        "rb001_receipt_complete": receipt_complete,
        "rb001_closed": rb001_closed,
        "fmr003_candidate_rows": len(candidate_rows),
        "fmr003_writeback_allowed": fmr003_writeback_allowed,
        "real_fmr_template_modified": False,
        "guarded_recheck_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "fmr003_returned_evidence_writeback_preflight_candidate_ready"
            if fmr003_writeback_allowed
            else "fmr003_returned_evidence_writeback_preflight_ready_blocked_waiting_real_returned_evidence"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr003_returned_evidence_writeback_guard_matrix.csv",
        ["guard", "current", "required", "passes_now"],
        guard_rows,
    )
    write_csv(
        OUT_DIR / "fmr003_returned_evidence_writeback_candidates.csv",
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
        OUT_DIR / "fmr003_returned_evidence_writeback_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "fmr003_returned_evidence_writeback_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# FMR-003 Returned Evidence Writeback Preflight

Status: `{summary["status"]}`

Current result:

1. FMR-003 rows: {summary["fmr003_rows"]}
2. Candidate returned files: {summary["candidate_return_files"]}
3. Scanner gate closure allowed: {str(summary["scanner_gate_closure_allowed"]).lower()}
4. Hash manifest ready: {str(summary["hash_manifest_ready"]).lower()}
5. RB-001 receipt complete: {str(summary["rb001_receipt_complete"]).lower()}
6. RB-001 closed: {str(summary["rb001_closed"]).lower()}
7. FMR-003 candidate rows: {summary["fmr003_candidate_rows"]}
8. FMR-003 writeback allowed: {str(summary["fmr003_writeback_allowed"]).lower()}
9. Real FMR template modified: false
10. Guarded recheck allowed: false
11. Portal upload allowed: false
12. Submission ready: false

Boundary: FMR-003 remains blocked until real returned evidence files are
present, the scanner allows gate closure, the RB-001 hash manifest reconciles,
the RB-001 receipt is complete and the RB-001 closeout dashboard reports closed.
This preflight does not write the FMR intake template, close RB-001, run guarded
recheck, upload portal files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR003_RETURNED_EVIDENCE_WRITEBACK_PREFLIGHT_README.md", report)
    write_text(OUT_DIR / "fmr003_returned_evidence_writeback_preflight_report.md", report)
    write_text(
        OUT_DIR / "fmr003_returned_evidence_writeback_preflight_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
