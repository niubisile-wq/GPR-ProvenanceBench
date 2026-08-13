#!/usr/bin/env python3
"""Audit guarded writeback coverage for FMR-001 through FMR-006."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr_guarded_writeback_coverage_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


FMR_CONFIG = {
    "FMR-001": {
        "preflight": "reports/fmr001_sendout_completion_writeback_preflight_20260810/fmr001_sendout_completion_writeback_preflight_summary.json",
        "applier": "reports/fmr001_guarded_writeback_applier_20260810/fmr001_guarded_writeback_applier_summary.json",
        "regression": "reports/fmr001_guarded_writeback_regression_20260810/fmr001_guarded_writeback_regression_summary.json",
        "candidate_key": "fmr001_candidate_rows",
        "writeback_key": "fmr001_writeback_allowed",
    },
    "FMR-002": {
        "preflight": "reports/fmr002_author_decision_writeback_preflight_20260810/fmr002_author_decision_writeback_preflight_summary.json",
        "applier": "reports/fmr002_guarded_writeback_applier_20260810/fmr002_guarded_writeback_applier_summary.json",
        "regression": "reports/fmr002_guarded_writeback_regression_20260810/fmr002_guarded_writeback_regression_summary.json",
        "candidate_key": "fmr002_candidate_rows",
        "writeback_key": "fmr002_writeback_allowed",
    },
    "FMR-003": {
        "preflight": "reports/fmr003_returned_evidence_writeback_preflight_20260810/fmr003_returned_evidence_writeback_preflight_summary.json",
        "applier": "reports/fmr003_guarded_writeback_applier_20260810/fmr003_guarded_writeback_applier_summary.json",
        "regression": "reports/fmr003_guarded_writeback_regression_20260810/fmr003_guarded_writeback_regression_summary.json",
        "candidate_key": "fmr003_candidate_rows",
        "writeback_key": "fmr003_writeback_allowed",
    },
    "FMR-004": {
        "preflight": "reports/fmr004_figure_review_writeback_preflight_20260810/fmr004_figure_review_writeback_preflight_summary.json",
        "applier": "reports/fmr004_guarded_writeback_applier_20260810/fmr004_guarded_writeback_applier_summary.json",
        "regression": "reports/fmr004_guarded_writeback_regression_20260810/fmr004_guarded_writeback_regression_summary.json",
        "candidate_key": "fmr004_candidate_rows",
        "writeback_key": "fmr004_writeback_allowed",
    },
    "FMR-005": {
        "preflight": "reports/fmr005_repository_rights_doi_writeback_preflight_20260810/fmr005_repository_rights_doi_writeback_preflight_summary.json",
        "applier": "reports/fmr005_guarded_writeback_applier_20260810/fmr005_guarded_writeback_applier_summary.json",
        "regression": "reports/fmr005_guarded_writeback_regression_20260810/fmr005_guarded_writeback_regression_summary.json",
        "candidate_key": "fmr005_candidate_rows",
        "writeback_key": "fmr005_writeback_allowed",
    },
    "FMR-006": {
        "preflight": "reports/fmr006_guarded_recheck_receipt_writeback_preflight_20260810/fmr006_guarded_recheck_receipt_writeback_preflight_summary.json",
        "applier": "reports/fmr006_guarded_writeback_applier_20260810/fmr006_guarded_writeback_applier_summary.json",
        "regression": "reports/fmr006_guarded_writeback_regression_20260810/fmr006_guarded_writeback_regression_summary.json",
        "candidate_key": "fmr006_candidate_rows",
        "writeback_key": "fmr006_writeback_allowed",
    },
}


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
    marker = "### 19.78 FMR guarded writeback coverage audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr_guarded_writeback_coverage_audit_20260810/` to audit coverage of all FMR-001 to FMR-006 guarded writeback layers.
- Current `fmr_rows={summary["fmr_rows"]}`, `coverage_complete_rows={summary["coverage_complete_rows"]}`, `regression_pass_rows={summary["regression_pass_rows"]}`.
- Current `writeback_allowed_rows={summary["writeback_allowed_rows"]}`, `writeback_executed_rows={summary["writeback_executed_rows"]}`, `real_fmr_template_modified_rows={summary["real_fmr_template_modified_rows"]}`.
- Boundary: this is a coverage audit only. It does not write any FMR row, execute guarded writeback, execute recheck, upload portal files or submit.
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

    coverage_rows = []
    blocker_rows = []
    qa_rows = []

    for receipt_id, config in FMR_CONFIG.items():
        preflight_path = BENCH_ROOT / str(config["preflight"])
        applier_path = BENCH_ROOT / str(config["applier"])
        regression_path = BENCH_ROOT / str(config["regression"])
        paths_exist = preflight_path.exists() and applier_path.exists() and regression_path.exists()

        preflight = read_json(preflight_path) if preflight_path.exists() else {}
        applier = read_json(applier_path) if applier_path.exists() else {}
        regression = read_json(regression_path) if regression_path.exists() else {}

        candidate_rows = int(preflight.get(str(config["candidate_key"]), 0) or 0)
        writeback_allowed = preflight.get(str(config["writeback_key"])) is True
        applier_refuses_now = (
            applier.get("writeback_preflight_allowed") is False
            and applier.get("writeback_executed") is False
            and applier.get("real_fmr_template_modified") is False
        )
        regression_pass = regression.get("regression_pass") is True and regression.get("qa_pass") is True
        submission_false = (
            preflight.get("submission_ready") is False
            and applier.get("submission_ready") is False
            and regression.get("submission_ready") is False
        )
        coverage_complete = paths_exist and regression_pass and applier_refuses_now and submission_false

        coverage_rows.append(
            {
                "receipt_id": receipt_id,
                "preflight_summary_exists": "yes" if preflight_path.exists() else "no",
                "applier_summary_exists": "yes" if applier_path.exists() else "no",
                "regression_summary_exists": "yes" if regression_path.exists() else "no",
                "preflight_candidate_rows": candidate_rows,
                "preflight_writeback_allowed": str(writeback_allowed).lower(),
                "applier_writeback_preflight_allowed": str(applier.get("writeback_preflight_allowed") is True).lower(),
                "applier_writeback_executed": str(applier.get("writeback_executed") is True).lower(),
                "real_fmr_template_modified": str(applier.get("real_fmr_template_modified") is True).lower(),
                "regression_pass": str(regression_pass).lower(),
                "submission_ready_any_layer": str(not submission_false).lower(),
                "coverage_complete": str(coverage_complete).lower(),
            }
        )

        if not coverage_complete:
            blocker_rows.append(
                {
                    "receipt_id": receipt_id,
                    "blocker": "coverage incomplete or unsafe current state",
                    "evidence": (
                        f"paths_exist={paths_exist}; regression_pass={regression_pass}; "
                        f"applier_refuses_now={applier_refuses_now}; submission_false={submission_false}"
                    ),
                    "blocks": "declaring guarded writeback coverage complete",
                }
            )

    coverage_complete_rows = sum(row["coverage_complete"] == "true" for row in coverage_rows)
    regression_pass_rows = sum(row["regression_pass"] == "true" for row in coverage_rows)
    writeback_allowed_rows = sum(row["preflight_writeback_allowed"] == "true" for row in coverage_rows)
    writeback_executed_rows = sum(row["applier_writeback_executed"] == "true" for row in coverage_rows)
    real_modified_rows = sum(row["real_fmr_template_modified"] == "true" for row in coverage_rows)
    submission_ready_rows = sum(row["submission_ready_any_layer"] == "true" for row in coverage_rows)

    qa_rows.extend(
        [
            {
                "check": "all six FMR coverage rows present",
                "result": "PASS" if len(coverage_rows) == 6 else "FAIL",
                "detail": f"coverage_rows={len(coverage_rows)}",
            },
            {
                "check": "all six FMR rows have complete guarded coverage",
                "result": "PASS" if coverage_complete_rows == 6 else "FAIL",
                "detail": f"coverage_complete_rows={coverage_complete_rows}",
            },
            {
                "check": "all regressions pass",
                "result": "PASS" if regression_pass_rows == 6 else "FAIL",
                "detail": f"regression_pass_rows={regression_pass_rows}",
            },
            {
                "check": "no real writeback executed in current state",
                "result": "PASS" if writeback_executed_rows == 0 and real_modified_rows == 0 else "FAIL",
                "detail": f"writeback_executed_rows={writeback_executed_rows}; real_fmr_template_modified_rows={real_modified_rows}",
            },
            {
                "check": "submission remains false in all guarded writeback layers",
                "result": "PASS" if submission_ready_rows == 0 else "FAIL",
                "detail": f"submission_ready_rows={submission_ready_rows}",
            },
        ]
    )

    summary = {
        "package": "fmr_guarded_writeback_coverage_audit_20260810",
        "fmr_rows": len(coverage_rows),
        "coverage_complete_rows": coverage_complete_rows,
        "regression_pass_rows": regression_pass_rows,
        "writeback_allowed_rows": writeback_allowed_rows,
        "writeback_executed_rows": writeback_executed_rows,
        "real_fmr_template_modified_rows": real_modified_rows,
        "submission_ready_rows": submission_ready_rows,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "portal_upload_allowed": False,
        "submission_ready": False,
        "status": (
            "fmr_guarded_writeback_coverage_audit_passed_all_layers_guarded"
            if len(blocker_rows) == 0 and all(row["result"] == "PASS" for row in qa_rows)
            else "fmr_guarded_writeback_coverage_audit_failed_or_incomplete"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr_guarded_writeback_coverage_matrix.csv",
        [
            "receipt_id",
            "preflight_summary_exists",
            "applier_summary_exists",
            "regression_summary_exists",
            "preflight_candidate_rows",
            "preflight_writeback_allowed",
            "applier_writeback_preflight_allowed",
            "applier_writeback_executed",
            "real_fmr_template_modified",
            "regression_pass",
            "submission_ready_any_layer",
            "coverage_complete",
        ],
        coverage_rows,
    )
    write_csv(OUT_DIR / "fmr_guarded_writeback_coverage_blockers.csv", ["receipt_id", "blocker", "evidence", "blocks"], blocker_rows)
    write_csv(OUT_DIR / "fmr_guarded_writeback_coverage_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# FMR Guarded Writeback Coverage Audit

Status: `{summary["status"]}`

Current result:

1. FMR rows: {summary["fmr_rows"]}
2. Coverage complete rows: {summary["coverage_complete_rows"]}
3. Regression pass rows: {summary["regression_pass_rows"]}
4. Writeback allowed rows: {summary["writeback_allowed_rows"]}
5. Writeback executed rows: {summary["writeback_executed_rows"]}
6. Real FMR template modified rows: {summary["real_fmr_template_modified_rows"]}
7. Submission ready rows: {summary["submission_ready_rows"]}
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this audit verifies that FMR-001 through FMR-006 each have a
preflight, guarded applier and regression layer, and that the current state has
not executed real writeback. It does not complete receipts, write any FMR row,
execute recheck, upload portal files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR_GUARDED_WRITEBACK_COVERAGE_AUDIT_README.md", report)
    write_text(OUT_DIR / "fmr_guarded_writeback_coverage_audit_report.md", report)
    write_text(OUT_DIR / "fmr_guarded_writeback_coverage_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
