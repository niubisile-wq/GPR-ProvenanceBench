#!/usr/bin/env python3
"""Build and audit the required backfill template fields after manual actions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manual_action_backfill_template_audit_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"

REQUIRED_FIELDS = [
    ("performed_by", "human executor name or accountable owner", "non-empty; not placeholder"),
    ("performed_at_local_time", "local execution timestamp", "ISO-like timestamp or unambiguous local time"),
    ("evidence_file_or_folder", "path to real evidence file or folder", "existing path after real action"),
    ("evidence_sha256", "SHA256 of evidence file or manifest", "64 lowercase/uppercase hex characters"),
    ("source_channel", "real channel used", "email; cloud drive; portal; chat; meeting note; repository"),
    ("counterparty_or_owner", "recipient, author, reviewer, repository owner or decision owner", "non-empty"),
    ("decision_or_return_summary", "short summary of what was sent, returned or decided", "non-empty"),
    ("sensitive_content_checked", "sensitive leakage check result", "yes after check; not_checked before action"),
    ("validator_ran", "whether the next validator was run after evidence", "no until allowed; yes only after form complete"),
    ("validator_result", "validator result", "not_run until allowed; pass/fail after validator"),
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
    marker = "### 19.92 Manual action backfill template audit update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/manual_action_backfill_template_audit_20260810/` to define and audit the required MOF fields after the five real manual actions.
- Current `template_rows={summary["template_rows"]}`, `required_field_rows={summary["required_field_rows"]}`, `currently_complete_forms={summary["currently_complete_forms"]}`.
- Current `missing_required_cells={summary["missing_required_cells"]}`, `allowed_commands_now=0`, `submission_ready=false`.
- Boundary: this audit defines and checks backfill requirements only. It does not fill forms, create evidence, run validators, execute writeback, run recheck, upload portal files or submit.
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
    forms = read_csv(BENCH_ROOT / "reports" / "manual_only_execution_forms_20260810" / "manual_only_execution_forms_index.csv")
    route_summary = read_json(BENCH_ROOT / "reports" / "manual_evidence_route_snapshot_20260810" / "manual_evidence_route_snapshot_summary.json")

    template_rows = []
    audit_rows = []
    order_rows = []
    for form in forms:
        form_path = BENCH_ROOT / form["form_file"]
        current = read_csv(form_path)[0] if form_path.exists() else {}
        missing_for_form = []
        for position, (field, meaning, requirement) in enumerate(REQUIRED_FIELDS, start=1):
            value = current.get(field, "").strip()
            is_missing = value == "" or value in {"not_checked", "no", "not_run"}
            if is_missing:
                missing_for_form.append(field)
            template_rows.append(
                {
                    "form_id": form["form_id"],
                    "primary_fmr": form["primary_fmr"],
                    "field_order": position,
                    "field_name": field,
                    "meaning": meaning,
                    "acceptance_requirement": requirement,
                    "current_value": value,
                    "currently_filled": "no" if is_missing else "yes",
                }
            )
        audit_rows.append(
            {
                "form_id": form["form_id"],
                "primary_fmr": form["primary_fmr"],
                "form_file": form["form_file"],
                "missing_required_fields": ";".join(missing_for_form),
                "missing_required_cells": len(missing_for_form),
                "form_backfill_complete": "yes" if not missing_for_form else "no",
                "validator_allowed_after_backfill": "no",
                "writeback_allowed_now": "no",
            }
        )
        order_rows.append(
            {
                "order": form["form_id"].replace("MOF-", ""),
                "form_id": form["form_id"],
                "primary_fmr": form["primary_fmr"],
                "step": "execute real manual action; place evidence; fill required fields; rerun 19.88 watcher; then 19.89 route snapshot",
                "do_not_skip": "do not run validators or writeback before this form passes 19.84 validation",
            }
        )

    missing_required_cells = sum(int(row["missing_required_cells"]) for row in audit_rows)
    currently_complete_forms = sum(1 for row in audit_rows if row["form_backfill_complete"] == "yes")
    qa_rows = [
        {
            "check": "all five forms have required field templates",
            "result": "PASS" if len(audit_rows) == 5 else "FAIL",
            "detail": f"forms={len(audit_rows)}",
        },
        {
            "check": "all required fields are represented per form",
            "result": "PASS" if len(template_rows) == 5 * len(REQUIRED_FIELDS) else "FAIL",
            "detail": f"template_rows={len(template_rows)}",
        },
        {
            "check": "current forms remain incomplete",
            "result": "PASS" if currently_complete_forms == 0 else "FAIL",
            "detail": f"currently_complete_forms={currently_complete_forms}",
        },
        {
            "check": "route snapshot still allows no commands",
            "result": "PASS" if route_summary.get("allowed_commands_now") == 0 else "FAIL",
            "detail": f"allowed_commands_now={route_summary.get('allowed_commands_now')}",
        },
    ]

    summary = {
        "package": "manual_action_backfill_template_audit_20260810",
        "template_rows": len(template_rows),
        "required_field_rows": len(REQUIRED_FIELDS),
        "forms_audited": len(audit_rows),
        "currently_complete_forms": currently_complete_forms,
        "missing_required_cells": missing_required_cells,
        "allowed_commands_now": 0,
        "submission_ready": False,
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": "manual_action_backfill_template_audit_ready_waiting_manual_evidence",
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "manual_action_backfill_required_fields.csv",
        ["form_id", "primary_fmr", "field_order", "field_name", "meaning", "acceptance_requirement", "current_value", "currently_filled"],
        template_rows,
    )
    write_csv(
        OUT_DIR / "manual_action_backfill_form_audit.csv",
        ["form_id", "primary_fmr", "form_file", "missing_required_fields", "missing_required_cells", "form_backfill_complete", "validator_allowed_after_backfill", "writeback_allowed_now"],
        audit_rows,
    )
    write_csv(OUT_DIR / "manual_action_backfill_order.csv", ["order", "form_id", "primary_fmr", "step", "do_not_skip"], order_rows)
    write_csv(OUT_DIR / "manual_action_backfill_template_audit_qa.csv", ["check", "result", "detail"], qa_rows)

    report = f"""# Manual Action Backfill Template Audit

Status: `{summary["status"]}`

Current result:

1. Template rows: {summary["template_rows"]}
2. Required fields per form: {summary["required_field_rows"]}
3. Forms audited: {summary["forms_audited"]}
4. Currently complete forms: {summary["currently_complete_forms"]}
5. Missing required cells: {summary["missing_required_cells"]}
6. Allowed commands now: 0
7. Submission ready: false

Boundary: this audit defines and checks backfill requirements only. It does not
fill forms, create evidence, run validators, execute writeback, run recheck,
upload portal files or submit.
"""
    write_text(OUT_DIR / "MANUAL_ACTION_BACKFILL_TEMPLATE_AUDIT_README.md", report)
    write_text(OUT_DIR / "manual_action_backfill_template_audit_report.md", report)
    write_text(OUT_DIR / "manual_action_backfill_template_audit_summary.json", json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
