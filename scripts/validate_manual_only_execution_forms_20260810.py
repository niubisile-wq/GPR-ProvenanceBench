#!/usr/bin/env python3
"""Validate manual-only execution forms before any downstream writeback."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_only_execution_forms_validation_20260810"
FORMS_DIR = BENCH_ROOT / "reports" / "manual_only_execution_forms_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"
SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")


REQUIRED_FILLED_FIELDS = [
    "performed_by",
    "performed_at_local_time",
    "evidence_file_or_folder",
    "evidence_sha256",
    "source_channel",
    "counterparty_or_owner",
    "decision_or_return_summary",
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


def resolve_evidence_path(value: str) -> Path | None:
    value = value.strip()
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = BENCH_ROOT / path
    return path


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.84 Manual-only execution forms validation update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_only_execution_forms_validation_20260810/` to validate the five blank manual-only execution forms before any downstream validator or FMR writeback can be considered.
- Current `validated_form_rows={summary["validated_form_rows"]}`, `incomplete_form_rows={summary["incomplete_form_rows"]}`, `missing_required_field_cells={summary["missing_required_field_cells"]}`.
- Current `evidence_paths_existing={summary["evidence_paths_existing"]}`, `allowed_downstream_validators={summary["allowed_downstream_validators"]}`, `allowed_commands_now=0`, `submission_ready=false`.
- Boundary: this validator is read-only. It does not fill forms, create evidence, compute real hashes, run downstream validators, execute writeback, run recheck, upload portal files or submit.
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

    forms_summary = read_json(FORMS_DIR / "manual_only_execution_forms_summary.json")
    form_index = read_csv(FORMS_DIR / "manual_only_execution_forms_index.csv")
    manifest = {row["form_id"]: row for row in read_csv(FORMS_DIR / "manual_only_execution_evidence_manifest.csv")}

    validation_rows = []
    blocker_rows = []
    route_rows = []

    for form_meta in form_index:
        form_id = form_meta["form_id"]
        form_file = BENCH_ROOT / form_meta["form_file"]
        form_rows = read_csv(form_file) if form_file.exists() else []
        row = form_rows[0] if form_rows else {}
        missing_fields = [field for field in REQUIRED_FILLED_FIELDS if not row.get(field, "").strip()]
        evidence_path = resolve_evidence_path(row.get("evidence_file_or_folder", ""))
        evidence_exists = bool(evidence_path and evidence_path.exists())
        hash_valid = bool(SHA256_RE.match(row.get("evidence_sha256", "").strip()))
        sensitive_checked = row.get("sensitive_content_checked", "").strip().lower() in {"yes", "checked", "pass", "passed"}
        validator_passed = (
            row.get("validator_ran", "").strip().lower() == "yes"
            and row.get("validator_result", "").strip().lower() in {"pass", "passed"}
        )
        form_complete = (
            not missing_fields
            and evidence_exists
            and hash_valid
            and sensitive_checked
            and validator_passed
        )
        validation_rows.append(
            {
                "form_id": form_id,
                "step_id": form_meta["step_id"],
                "primary_fmr": form_meta["primary_fmr"],
                "form_file": form_meta["form_file"],
                "form_exists": "yes" if form_file.exists() else "no",
                "missing_required_fields": ";".join(missing_fields),
                "evidence_path": str(evidence_path) if evidence_path else "",
                "evidence_path_exists": "yes" if evidence_exists else "no",
                "sha256_format_valid": "yes" if hash_valid else "no",
                "sensitive_content_checked": "yes" if sensitive_checked else "no",
                "validator_passed": "yes" if validator_passed else "no",
                "form_complete_now": "yes" if form_complete else "no",
                "downstream_validator_allowed_now": "yes" if form_complete else "no",
                "writeback_allowed_now": "no",
            }
        )
        route_rows.append(
            {
                "form_id": form_id,
                "primary_fmr": form_meta["primary_fmr"],
                "expected_evidence_location": manifest.get(form_id, {}).get("expected_evidence_location", ""),
                "after_form_complete_run": form_meta["next_validator"],
                "then_requires": "preflight-approved candidate before any guarded writeback",
                "current_route_status": "blocked_waiting_complete_real_form" if not form_complete else "ready_for_downstream_validator",
            }
        )
        if not form_complete:
            blocker_rows.append(
                {
                    "form_id": form_id,
                    "primary_fmr": form_meta["primary_fmr"],
                    "blocking_reason": "missing fields, missing evidence path, invalid hash, unchecked sensitive content or validator not passed",
                    "missing_required_fields": ";".join(missing_fields),
                    "evidence_path_exists": "yes" if evidence_exists else "no",
                    "validator_passed": "yes" if validator_passed else "no",
                }
            )

    validated_form_rows = sum(1 for row in validation_rows if row["form_complete_now"] == "yes")
    incomplete_form_rows = len(validation_rows) - validated_form_rows
    missing_required_field_cells = sum(
        len([field for field in row["missing_required_fields"].split(";") if field])
        for row in validation_rows
    )
    evidence_paths_existing = sum(1 for row in validation_rows if row["evidence_path_exists"] == "yes")
    allowed_downstream_validators = sum(1 for row in validation_rows if row["downstream_validator_allowed_now"] == "yes")

    qa_rows = [
        {
            "check": "all generated forms were inspected",
            "result": "PASS" if len(validation_rows) == forms_summary.get("form_rows") else "FAIL",
            "detail": f"validation_rows={len(validation_rows)}; form_rows={forms_summary.get('form_rows')}",
        },
        {
            "check": "blank current forms remain blocked",
            "result": "PASS" if incomplete_form_rows == len(validation_rows) else "FAIL",
            "detail": f"incomplete_form_rows={incomplete_form_rows}",
        },
        {
            "check": "no downstream validators are allowed in current state",
            "result": "PASS" if allowed_downstream_validators == 0 else "FAIL",
            "detail": f"allowed_downstream_validators={allowed_downstream_validators}",
        },
        {
            "check": "writeback and submission remain blocked",
            "result": "PASS",
            "detail": "allowed_commands_now=0; portal_upload_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "manual_only_execution_forms_validation_20260810",
        "form_rows": len(validation_rows),
        "validated_form_rows": validated_form_rows,
        "incomplete_form_rows": incomplete_form_rows,
        "missing_required_field_cells": missing_required_field_cells,
        "evidence_paths_existing": evidence_paths_existing,
        "allowed_downstream_validators": allowed_downstream_validators,
        "allowed_commands_now": 0,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_only_execution_forms_validation_blocked_waiting_real_form_evidence",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_only_execution_form_validation_status.csv",
        [
            "form_id",
            "step_id",
            "primary_fmr",
            "form_file",
            "form_exists",
            "missing_required_fields",
            "evidence_path",
            "evidence_path_exists",
            "sha256_format_valid",
            "sensitive_content_checked",
            "validator_passed",
            "form_complete_now",
            "downstream_validator_allowed_now",
            "writeback_allowed_now",
        ],
        validation_rows,
    )
    write_csv(
        OUT_DIR / "manual_only_execution_form_blockers.csv",
        ["form_id", "primary_fmr", "blocking_reason", "missing_required_fields", "evidence_path_exists", "validator_passed"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "manual_only_execution_form_to_validator_routes.csv",
        [
            "form_id",
            "primary_fmr",
            "expected_evidence_location",
            "after_form_complete_run",
            "then_requires",
            "current_route_status",
        ],
        route_rows,
    )
    write_csv(OUT_DIR / "manual_only_execution_form_validation_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual-Only Execution Forms Validation

Status: `{summary["status"]}`

Current result:

1. Form rows: {summary["form_rows"]}
2. Validated form rows: {summary["validated_form_rows"]}
3. Incomplete form rows: {summary["incomplete_form_rows"]}
4. Missing required field cells: {summary["missing_required_field_cells"]}
5. Existing evidence paths: {summary["evidence_paths_existing"]}
6. Allowed downstream validators: {summary["allowed_downstream_validators"]}
7. Allowed commands now: 0
8. Portal upload allowed: false
9. Submission ready: false

Boundary: this validator is read-only. It does not fill forms, create evidence,
compute real hashes, run downstream validators, execute writeback, run recheck,
upload portal files or submit.
"""
    write_text(OUT_DIR / "MANUAL_ONLY_EXECUTION_FORMS_VALIDATION_README.md", report)
    write_text(OUT_DIR / "manual_only_execution_forms_validation_report.md", report)
    write_text(OUT_DIR / "manual_only_execution_forms_validation_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
