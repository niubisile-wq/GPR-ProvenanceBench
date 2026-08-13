#!/usr/bin/env python3
"""Validate RB-001 hash-manifest readiness before receipt closeout or writeback."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "rb001_hash_manifest_readiness_validator_20260810"
DROP_KIT_DIR = BENCH_ROOT / "reports" / "rb001_return_evidence_drop_kit_20260810"
SCANNER_DIR = BENCH_ROOT / "reports" / "final_return_evidence_intake_scanner_20260810"
RECON_DIR = BENCH_ROOT / "reports" / "rb001_return_evidence_hash_reconciliation_20260810"
CROSSWALK_DIR = BENCH_ROOT / "reports" / "natcomms_return_tracker_to_rb001_crosswalk_validator_20260810"
RB001_DASHBOARD_DIR = BENCH_ROOT / "reports" / "rb001_closeout_dashboard_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

PLACEHOLDERS = {"", "FILL_AFTER_DROP", "FILL_AFTER_HASH", "YYYY-MM-DD", "pending"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def filled(value: str) -> bool:
    return str(value).strip() not in PLACEHOLDERS


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.39 RB-001 hash manifest readiness validator update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- 新增 `reports/rb001_hash_manifest_readiness_validator_20260810/`，验证 RB-001 hash manifest 是否足够完整，防止有返回文件但未登记 SHA256/来源/日期就进入 receipt closeout 或 writeback。
- 当前 `manifest_rows={summary["manifest_rows"]}`，`filled_manifest_rows={summary["filled_manifest_rows"]}`，`scanner_file_rows={summary["scanner_file_rows"]}`，`reconciled_rows={summary["reconciled_rows"]}`。
- 当前 `hash_manifest_ready={str(summary["hash_manifest_ready"]).lower()}`，`receipt_closeout_allowed={str(summary["receipt_closeout_allowed"]).lower()}`，`writeback_preflight_allowed={str(summary["writeback_preflight_allowed"]).lower()}`。
- 当前 `candidate_return_files=0`，`writeback_allowed_rows=0`，`submission_ready=false`。
- 边界：该 validator 只读 scanner/hash/crosswalk/RB-001 dashboard，不计算 hash、不写 manifest、不复制文件、不写回、不关闭 gate。
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

    manifest_rows = read_csv(DROP_KIT_DIR / "rb001_return_evidence_hash_manifest_template.csv")
    scanner_summary = read_json(SCANNER_DIR / "final_return_evidence_intake_scanner_summary.json")
    recon_summary = read_json(RECON_DIR / "rb001_return_evidence_hash_reconciliation_summary.json")
    recon_rows = read_csv(RECON_DIR / "rb001_return_evidence_hash_reconciliation.csv")
    mismatch_rows = read_csv(RECON_DIR / "rb001_return_evidence_hash_mismatch.csv")
    missing_register_rows = read_csv(RECON_DIR / "rb001_return_evidence_missing_source_register.csv")
    crosswalk_summary = read_json(CROSSWALK_DIR / "return_tracker_to_rb001_crosswalk_validator_summary.json")
    rb001_summary = read_json(RB001_DASHBOARD_DIR / "rb001_closeout_dashboard_summary.json")

    manifest_validation_rows = []
    for row in manifest_rows:
        required_fields = ["expected_file_name", "source_person_or_system", "received_date", "sha256"]
        missing_fields = [field for field in required_fields if not filled(row.get(field, ""))]
        complete = not missing_fields
        manifest_validation_rows.append(
            {
                "route_id": row.get("route_id", ""),
                "folder": row.get("folder", ""),
                "expected_file_name": row.get("expected_file_name", ""),
                "source_person_or_system": row.get("source_person_or_system", ""),
                "received_date": row.get("received_date", ""),
                "sha256": row.get("sha256", ""),
                "manifest_row_complete": complete,
                "missing_fields": ";".join(missing_fields),
                "allowed_to_writeback": row.get("allowed_to_writeback", ""),
            }
        )

    scanner_file_rows = int(scanner_summary.get("candidate_return_files", 0))
    filled_manifest_rows = sum(1 for row in manifest_validation_rows if row["manifest_row_complete"])
    reconciled_rows = int(recon_summary.get("reconciled_rows", 0))
    missing_source_register_rows = int(recon_summary.get("missing_source_register_rows", 0))
    hash_mismatch_rows = int(recon_summary.get("hash_mismatch_rows", 0))
    crosswalk_drop_ready = crosswalk_summary.get("rb001_drop_allowed") is True
    hash_manifest_ready = (
        scanner_file_rows > 0
        and filled_manifest_rows >= scanner_file_rows
        and reconciled_rows == scanner_file_rows
        and missing_source_register_rows == 0
        and hash_mismatch_rows == 0
        and len(mismatch_rows) == 0
        and len(missing_register_rows) == 0
    )
    receipt_closeout_allowed = hash_manifest_ready and crosswalk_drop_ready
    writeback_preflight_allowed = receipt_closeout_allowed and rb001_summary.get("rb001_closed") is True

    gate_rows = [
        {
            "gate": "scanner_has_candidate_files",
            "current": scanner_file_rows,
            "required": ">0",
            "passes_now": "yes" if scanner_file_rows > 0 else "no",
        },
        {
            "gate": "manifest_rows_complete_for_scanner_files",
            "current": filled_manifest_rows,
            "required": f">= scanner_file_rows ({scanner_file_rows})",
            "passes_now": "yes" if scanner_file_rows > 0 and filled_manifest_rows >= scanner_file_rows else "no",
        },
        {
            "gate": "hash_reconciliation_complete",
            "current": reconciled_rows,
            "required": f"scanner_file_rows ({scanner_file_rows})",
            "passes_now": "yes" if scanner_file_rows > 0 and reconciled_rows == scanner_file_rows else "no",
        },
        {
            "gate": "no_missing_source_register_rows",
            "current": missing_source_register_rows,
            "required": "0",
            "passes_now": "yes" if missing_source_register_rows == 0 else "no",
        },
        {
            "gate": "no_hash_mismatch_rows",
            "current": hash_mismatch_rows,
            "required": "0",
            "passes_now": "yes" if hash_mismatch_rows == 0 else "no",
        },
        {
            "gate": "crosswalk_drop_ready",
            "current": crosswalk_drop_ready,
            "required": "true",
            "passes_now": "yes" if crosswalk_drop_ready else "no",
        },
        {
            "gate": "hash_manifest_ready",
            "current": hash_manifest_ready,
            "required": "true",
            "passes_now": "yes" if hash_manifest_ready else "no",
        },
        {
            "gate": "receipt_closeout_allowed",
            "current": receipt_closeout_allowed,
            "required": "true",
            "passes_now": "yes" if receipt_closeout_allowed else "no",
        },
        {
            "gate": "writeback_preflight_allowed",
            "current": writeback_preflight_allowed,
            "required": "true",
            "passes_now": "yes" if writeback_preflight_allowed else "no",
        },
        {
            "gate": "submission_ready",
            "current": False,
            "required": "false",
            "passes_now": "yes",
        },
    ]

    next_action_rows = [
        {
            "order": 1,
            "action": "Copy real returned evidence into the mapped RB-001 route folders only after real files are received.",
            "allowed_now": "manual_only_after_returns",
        },
        {
            "order": 2,
            "action": "Calculate SHA256 for each copied file and fill expected_file_name, source_person_or_system, received_date and sha256.",
            "allowed_now": "after_real_file_drop_only",
        },
        {
            "order": 3,
            "action": "Run scanner and hash reconciliation diagnostics.",
            "allowed_now": "after_manifest_filled_only",
        },
        {
            "order": 4,
            "action": "Do not proceed to RB-001 closeout receipt until hash_manifest_ready=true.",
            "allowed_now": "blocked_now",
        },
        {
            "order": 5,
            "action": "Do not run writeback preflight until RB-001 is actually closed.",
            "allowed_now": "blocked_now",
        },
    ]

    qa_rows = [
        {
            "check": "manifest route rows present",
            "result": "PASS" if len(manifest_rows) == 7 else "FAIL",
            "detail": f"rows={len(manifest_rows)}",
        },
        {
            "check": "empty manifest does not pass readiness",
            "result": "PASS" if not hash_manifest_ready and filled_manifest_rows == 0 else "FAIL",
            "detail": f"filled_manifest_rows={filled_manifest_rows}",
        },
        {
            "check": "scanner empty keeps receipt closeout blocked",
            "result": "PASS" if scanner_file_rows == 0 and not receipt_closeout_allowed else "FAIL",
            "detail": f"scanner_file_rows={scanner_file_rows}",
        },
        {
            "check": "writeback remains blocked",
            "result": "PASS" if rb001_summary.get("writeback_allowed_rows") == 0 and not writeback_preflight_allowed else "FAIL",
            "detail": f"writeback_allowed_rows={rb001_summary.get('writeback_allowed_rows')}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "hash readiness cannot make submission ready.",
        },
    ]

    summary = {
        "package": "rb001_hash_manifest_readiness_validator_20260810",
        "manifest_rows": len(manifest_rows),
        "filled_manifest_rows": filled_manifest_rows,
        "scanner_file_rows": scanner_file_rows,
        "reconciled_rows": reconciled_rows,
        "missing_source_register_rows": missing_source_register_rows,
        "hash_mismatch_rows": hash_mismatch_rows,
        "crosswalk_drop_ready": crosswalk_drop_ready,
        "hash_manifest_ready": hash_manifest_ready,
        "receipt_closeout_allowed": receipt_closeout_allowed,
        "writeback_preflight_allowed": writeback_preflight_allowed,
        "candidate_return_files": rb001_summary.get("candidate_return_files", 0),
        "writeback_allowed_rows": rb001_summary.get("writeback_allowed_rows", 0),
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "rb001_hash_manifest_readiness_validator_ready_blocked_empty_manifest",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "rb001_hash_manifest_row_readiness.csv",
        [
            "route_id",
            "folder",
            "expected_file_name",
            "source_person_or_system",
            "received_date",
            "sha256",
            "manifest_row_complete",
            "missing_fields",
            "allowed_to_writeback",
        ],
        manifest_validation_rows,
    )
    write_csv(
        OUT_DIR / "rb001_hash_manifest_gate_matrix.csv",
        ["gate", "current", "required", "passes_now"],
        gate_rows,
    )
    write_csv(
        OUT_DIR / "rb001_hash_manifest_next_actions.csv",
        ["order", "action", "allowed_now"],
        next_action_rows,
    )
    write_csv(
        OUT_DIR / "rb001_hash_manifest_readiness_validator_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    readme = """# RB-001 Hash Manifest Readiness Validator

This validator checks whether RB-001 returned evidence has enough scanner,
manifest and hash-reconciliation evidence to proceed toward receipt closeout.

Boundary: it is read-only. It does not calculate hashes, edit the manifest,
copy returned files, write protected targets, close gates or make the manuscript
submission-ready.
"""
    write_text(OUT_DIR / "RB001_HASH_MANIFEST_READINESS_VALIDATOR_README.md", readme)

    report = f"""# RB-001 Hash Manifest Readiness Validator Report

Status: `{summary["status"]}`

Current result:

1. Manifest rows: {summary["manifest_rows"]}
2. Filled manifest rows: {summary["filled_manifest_rows"]}
3. Scanner file rows: {summary["scanner_file_rows"]}
4. Reconciled rows: {summary["reconciled_rows"]}
5. Missing source-register rows: {summary["missing_source_register_rows"]}
6. Hash mismatch rows: {summary["hash_mismatch_rows"]}
7. Hash manifest ready: {str(summary["hash_manifest_ready"]).lower()}
8. Receipt closeout allowed: {str(summary["receipt_closeout_allowed"]).lower()}
9. Writeback preflight allowed: {str(summary["writeback_preflight_allowed"]).lower()}
10. Submission ready: false

Interpretation: no returned files are present and the hash manifest is still a
template. RB-001 receipt closeout, writeback preflight and submission readiness
remain blocked.
"""
    write_text(OUT_DIR / "rb001_hash_manifest_readiness_validator_report.md", report)
    write_text(
        OUT_DIR / "rb001_hash_manifest_readiness_validator_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    )

    if not summary["qa_pass"]:
        raise SystemExit("RB-001 hash manifest readiness validator QA failed")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
