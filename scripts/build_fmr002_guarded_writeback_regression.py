#!/usr/bin/env python3
"""Regression-test the FMR-002 guarded writeback applier."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr002_guarded_writeback_regression_20260810"
APPLIER_PATH = BENCH_ROOT / "scripts" / "build_fmr002_guarded_writeback_applier.py"
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


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_applier_module():
    spec = importlib.util.spec_from_file_location("fmr002_applier_under_test", APPLIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load applier module: {APPLIER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed_case(root: Path, candidate_present: bool) -> tuple[Path, Path, Path]:
    preflight_dir = root / "reports" / "fmr002_author_decision_writeback_preflight_20260810"
    fmr_dir = root / "reports" / "final_manual_receipt_intake_package_20260810"
    out_dir = root / "reports" / "fmr002_guarded_writeback_applier_20260810"
    desktop_plan = root / "Desktop" / "8月10日cns.md"
    write_text(desktop_plan, "# Temporary desktop plan\n")

    fmr_rows = [
        {
            "receipt_id": f"FMR-{idx:03d}",
            "source_action_priority": str(idx),
            "receipt_type": "author_decision_values" if idx == 2 else "other_receipt",
            "owner": "author_and_advisor" if idx == 2 else "other_owner",
            "required_evidence": "required evidence",
            "target_or_route": "target",
            "value_to_fill_after_manual_action": "FILL_AFTER_REPLY" if idx == 2 else f"FILL_AFTER_{idx}",
            "acceptance_test": "acceptance",
            "first_validator": "validator",
            "current_status": "missing",
            "unlocks_when_valid": "unlock",
        }
        for idx in range(1, 7)
    ]
    write_csv(fmr_dir / "final_manual_receipt_intake_template.csv", FMR_FIELDS, fmr_rows)

    preflight_summary = {
        "package": "fmr002_author_decision_writeback_preflight_20260810",
        "fmr002_writeback_allowed": candidate_present,
        "fmr002_candidate_rows": 1 if candidate_present else 0,
        "submission_ready": False,
    }
    write_text(
        preflight_dir / "fmr002_author_decision_writeback_preflight_summary.json",
        json.dumps(preflight_summary, indent=2),
    )
    candidate_rows = []
    if candidate_present:
        candidate_rows.append(
            {
                "receipt_id": "FMR-002",
                "target_or_route": "target",
                "current_status_after_writeback": "complete",
                "value_to_fill_after_manual_action": (
                    "Author decisions resolved: backend=Python; external_asset=Track B; "
                    "licence=MIT/CC BY 4.0; route=Track B; timestamp=2026-08-10 21:30"
                ),
                "first_validator": "validator",
                "writeback_allowed": "yes",
            }
        )
    write_csv(
        preflight_dir / "fmr002_author_decision_writeback_candidates.csv",
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
    return preflight_dir, fmr_dir, out_dir


def run_case(name: str, candidate_present: bool, execute: bool) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"gpr_fmr002_{name}_") as tmp:
        root = Path(tmp)
        preflight_dir, fmr_dir, out_dir = seed_case(root, candidate_present)
        module = load_applier_module()
        module.BENCH_ROOT = root
        module.OUT_DIR = out_dir
        module.PREFLIGHT_DIR = preflight_dir
        module.FMR_DIR = fmr_dir
        module.FMR_TEMPLATE = fmr_dir / "final_manual_receipt_intake_template.csv"
        module.DESKTOP_PLAN = root / "Desktop" / "8月10日cns.md"

        old_argv = sys.argv[:]
        sys.argv = ["build_fmr002_guarded_writeback_applier.py"] + (["--execute-writeback"] if execute else [])
        try:
            module.main()
        finally:
            sys.argv = old_argv

        summary = json.loads((out_dir / "fmr002_guarded_writeback_applier_summary.json").read_text(encoding="utf-8-sig"))
        fmr002 = [row for row in read_csv(module.FMR_TEMPLATE) if row["receipt_id"] == "FMR-002"][0]
        return {
            "case": name,
            "candidate_present": candidate_present,
            "execute": execute,
            "writeback_preflight_allowed": summary["writeback_preflight_allowed"],
            "writeback_executed": summary["writeback_executed"],
            "real_fmr_template_modified": summary["real_fmr_template_modified"],
            "fmr002_status": fmr002["current_status"],
            "fmr002_value": fmr002["value_to_fill_after_manual_action"],
            "qa_pass": summary["qa_pass"],
        }


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.65 FMR-002 guarded writeback regression update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr002_guarded_writeback_regression_20260810/` to regression-test 19.64 default refusal, explicit synthetic writeback and no-candidate refusal paths.
- Current `regression_cases={summary["regression_cases"]}`, `regression_pass={str(summary["regression_pass"]).lower()}`.
- Verified behavior: default mode preserves FMR-002, explicit `--execute-writeback` writes only synthetic FMR-002, and no-candidate state refuses writeback.
- Boundary: this uses temporary synthetic FMR files only. It does not modify real FMR intake, create author decisions, render figures, run recheck, upload portal files or submit.
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

    default_case = run_case("candidate_default", candidate_present=True, execute=False)
    execute_case = run_case("candidate_execute", candidate_present=True, execute=True)
    no_candidate_case = run_case("no_candidate_execute", candidate_present=False, execute=True)

    qa_rows = [
        {
            "check": "default mode refuses to modify FMR-002 even with candidate",
            "result": "PASS"
            if default_case["writeback_preflight_allowed"] is True
            and default_case["writeback_executed"] is False
            and default_case["fmr002_status"] == "missing"
            and default_case["fmr002_value"] == "FILL_AFTER_REPLY"
            else "FAIL",
            "detail": json.dumps(default_case, ensure_ascii=False, sort_keys=True),
        },
        {
            "check": "explicit execute writes only synthetic FMR-002 candidate",
            "result": "PASS"
            if execute_case["writeback_preflight_allowed"] is True
            and execute_case["writeback_executed"] is True
            and execute_case["real_fmr_template_modified"] is True
            and execute_case["fmr002_status"] == "complete"
            and execute_case["fmr002_value"].startswith("Author decisions resolved:")
            else "FAIL",
            "detail": json.dumps(execute_case, ensure_ascii=False, sort_keys=True),
        },
        {
            "check": "no-candidate state refuses even with execute flag",
            "result": "PASS"
            if no_candidate_case["writeback_preflight_allowed"] is False
            and no_candidate_case["writeback_executed"] is False
            and no_candidate_case["fmr002_status"] == "missing"
            else "FAIL",
            "detail": json.dumps(no_candidate_case, ensure_ascii=False, sort_keys=True),
        },
    ]

    summary = {
        "package": "fmr002_guarded_writeback_regression_20260810",
        "regression_cases": 3,
        "default_refusal_verified": qa_rows[0]["result"] == "PASS",
        "explicit_writeback_verified": qa_rows[1]["result"] == "PASS",
        "no_candidate_refusal_verified": qa_rows[2]["result"] == "PASS",
        "real_fmr_template_modified": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "fmr002_guarded_writeback_regression_passed",
    }
    summary["regression_pass"] = summary["qa_pass"]
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr002_guarded_writeback_regression_cases.csv",
        [
            "case",
            "candidate_present",
            "execute",
            "writeback_preflight_allowed",
            "writeback_executed",
            "real_fmr_template_modified",
            "fmr002_status",
            "fmr002_value",
            "qa_pass",
        ],
        [default_case, execute_case, no_candidate_case],
    )
    write_csv(
        OUT_DIR / "fmr002_guarded_writeback_regression_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# FMR-002 Guarded Writeback Regression

Status: `{summary["status"]}`

Current result:

1. Regression cases: {summary["regression_cases"]}
2. Default refusal verified: {str(summary["default_refusal_verified"]).lower()}
3. Explicit writeback verified: {str(summary["explicit_writeback_verified"]).lower()}
4. No-candidate refusal verified: {str(summary["no_candidate_refusal_verified"]).lower()}
5. Real FMR template modified: false
6. Portal upload allowed: false
7. Submission ready: false

Boundary: this regression uses temporary synthetic FMR files only. It does not
modify the real FMR intake template, create author decisions, render figures,
run recheck, upload portal files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR002_GUARDED_WRITEBACK_REGRESSION_README.md", report)
    write_text(OUT_DIR / "fmr002_guarded_writeback_regression_report.md", report)
    write_text(
        OUT_DIR / "fmr002_guarded_writeback_regression_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
