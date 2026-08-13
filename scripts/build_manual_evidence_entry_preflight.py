#!/usr/bin/env python3
"""Preflight manual evidence entry targets without writing evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "manual_evidence_entry_preflight_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "8月10日cns.md"

WORKSHEET = REPORTS / "manual_evidence_intake_worksheet_20260810" / "manual_evidence_intake_worksheet.csv"
POST_DISPATCH_SUMMARY = REPORTS / "post_dispatch_evidence_intake_validator_20260810" / "post_dispatch_evidence_intake_validator_summary.json"
RERUN_SUMMARY = REPORTS / "post_evidence_safe_rerun_guard_20260810" / "post_evidence_safe_rerun_guard_summary.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def split_fields(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def resolve_target(target_file: str) -> Path | None:
    if target_file.startswith("external_blind/"):
        return None
    first_path = target_file.split(" or ")[0].split(" after ")[0].strip()
    return BENCH_ROOT / first_path


def current_completion_status(evidence_type: str, rows: list[dict[str, str]], fields: list[str]) -> tuple[str, str]:
    if not rows:
        return "not_applicable", "no target rows are available"

    if evidence_type == "real_author_sendout":
        sent = sum(1 for row in rows if row.get("send_status") == "sent" and row.get("sent_datetime_local") and row.get("sender"))
        return ("complete" if sent == len(rows) else "open", f"sent_complete_rows={sent}; total_rows={len(rows)}")

    if evidence_type == "returned_author_reply_files":
        returned = sum(1 for row in rows if row.get("return_status") == "returned" and row.get("returned_file_path") and row.get("returned_datetime_local"))
        return ("complete" if returned == len(rows) else "open", f"returned_complete_rows={returned}; total_rows={len(rows)}")

    if evidence_type == "backend_and_scope_choice":
        chosen = sum(1 for row in rows if row.get("current_choice") in {"Python", "R", "Figure 1-Figure 6", "reduced display set with SI relocation"})
        return ("complete" if chosen == len(rows) else "open", f"valid_choice_rows={chosen}; total_rows={len(rows)}")

    if evidence_type == "rights_licence_decisions":
        open_rows = sum(1 for row in rows if row.get("current_decision") == "open")
        return ("complete" if open_rows == 0 else "open", f"open_decision_rows={open_rows}; total_rows={len(rows)}")

    if evidence_type == "reporting_summary_author_replies":
        filled = sum(1 for row in rows if row.get("author_reply", "").strip())
        return ("complete" if filled == len(rows) else "open", f"filled_author_reply_rows={filled}; total_rows={len(rows)}")

    if evidence_type == "reference_replacement_authorized":
        allowed = sum(1 for row in rows if row.get("replacement_allowed_now") == "true")
        return ("complete" if allowed == len(rows) else "open", f"replacement_allowed_rows={allowed}; total_rows={len(rows)}")

    nonblank = sum(1 for row in rows for field in fields if row.get(field, "").strip())
    return ("complete" if nonblank else "open", f"nonblank_target_cells={nonblank}")


def update_desktop_plan(section: str) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    marker = "### 18.85 Manual evidence entry preflight update"
    if marker in text:
        start = text.index(marker)
        next_start = text.find("\n### ", start + len(marker))
        if next_start == -1:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n"
        else:
            updated = text[:start].rstrip() + "\n\n" + section.strip() + "\n\n" + text[next_start:].lstrip("\n")
    else:
        updated = text.rstrip() + "\n\n" + section.strip() + "\n"
    DESKTOP_PLAN.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    worksheet_rows = read_csv(WORKSHEET)
    post_dispatch = read_json(POST_DISPATCH_SUMMARY)
    rerun = read_json(RERUN_SUMMARY)

    target_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    blockers: list[dict[str, object]] = []

    for row in worksheet_rows:
        fields = split_fields(row["fields_to_fill"])
        target_path = resolve_target(row["target_file"])
        target_exists = bool(target_path and target_path.exists())
        target_kind = "external_payload" if target_path is None else "csv_file"
        current_rows: list[dict[str, str]] = []
        headers: list[str] = []

        if target_exists and target_path:
            current_rows = read_csv(target_path)
            headers = list(current_rows[0].keys()) if current_rows else []

        missing_fields = [field for field in fields if target_exists and field not in headers]
        completion_status, completion_detail = current_completion_status(row["evidence_type"], current_rows, fields)

        if target_path is None:
            target_status = "external_payload_not_present_expected"
            blocking_reason = "Real external blind asset must be acquired and manifest must pass strict SHA before rerun."
        elif not target_exists:
            target_status = "missing_target_file"
            blocking_reason = "Target file is missing; regenerate upstream packet before manual entry."
        elif missing_fields:
            target_status = "schema_mismatch"
            blocking_reason = "One or more worksheet fields are absent from the target file."
        elif completion_status == "complete":
            target_status = "complete_needs_validator"
            blocking_reason = "Manual values appear complete; run the after-fill validator before any gate closure."
        else:
            target_status = "ready_for_manual_entry"
            blocking_reason = "Real evidence is still absent or incomplete."

        target_rows.append(
            {
                "worksheet_id": row["worksheet_id"],
                "evidence_type": row["evidence_type"],
                "target_kind": target_kind,
                "target_file": row["target_file"],
                "resolved_target_exists": target_exists,
                "target_status": target_status,
                "completion_detail": completion_detail,
                "after_fill_validation": row["after_fill_validation"],
                "blocking_reason": blocking_reason,
            }
        )

        for field in fields:
            field_rows.append(
                {
                    "worksheet_id": row["worksheet_id"],
                    "evidence_type": row["evidence_type"],
                    "target_file": row["target_file"],
                    "field_to_fill": field,
                    "field_present": "external_payload" if target_path is None else field in headers,
                    "allowed_values_or_format": row["allowed_values_or_format"],
                    "do_not_edit": row["do_not_edit"],
                    "after_fill_validation": row["after_fill_validation"],
                }
            )

        blockers.append(
            {
                "worksheet_id": row["worksheet_id"],
                "evidence_type": row["evidence_type"],
                "safe_to_edit_now": "yes" if target_status == "ready_for_manual_entry" else "no",
                "safe_to_rerun_after_edit": "no",
                "reason": blocking_reason,
                "required_next_proof": row["allowed_values_or_format"],
            }
        )

    qa_rows = [
        {
            "check": "worksheet_rows_imported",
            "result": "PASS" if len(worksheet_rows) == 7 else "FAIL",
            "detail": f"worksheet_rows={len(worksheet_rows)}",
        },
        {
            "check": "schema_checks_have_rows",
            "result": "PASS" if target_rows and field_rows else "FAIL",
            "detail": f"target_rows={len(target_rows)}; field_rows={len(field_rows)}",
        },
        {
            "check": "known_missing_evidence_preserved",
            "result": "PASS" if post_dispatch.get("evidence_rows_passed") == 0 and rerun.get("branch_commands_safe_to_run_now") == 0 else "FAIL",
            "detail": f"evidence_rows_passed={post_dispatch.get('evidence_rows_passed')}; branch_commands_safe_to_run_now={rerun.get('branch_commands_safe_to_run_now')}",
        },
        {
            "check": "no_gate_closure_claim",
            "result": "PASS",
            "detail": "Preflight does not write evidence or close gates.",
        },
    ]
    qa_pass = all(row["result"] == "PASS" for row in qa_rows)

    write_csv(
        OUT_DIR / "manual_evidence_target_preflight.csv",
        target_rows,
        ["worksheet_id", "evidence_type", "target_kind", "target_file", "resolved_target_exists", "target_status", "completion_detail", "after_fill_validation", "blocking_reason"],
    )
    write_csv(
        OUT_DIR / "manual_evidence_field_constraint_matrix.csv",
        field_rows,
        ["worksheet_id", "evidence_type", "target_file", "field_to_fill", "field_present", "allowed_values_or_format", "do_not_edit", "after_fill_validation"],
    )
    write_csv(
        OUT_DIR / "manual_evidence_preflight_blockers.csv",
        blockers,
        ["worksheet_id", "evidence_type", "safe_to_edit_now", "safe_to_rerun_after_edit", "reason", "required_next_proof"],
    )
    write_csv(OUT_DIR / "manual_evidence_entry_preflight_qa.csv", qa_rows, ["check", "result", "detail"])

    report = [
        "# Manual evidence entry preflight report 2026-08-10",
        "",
        "Status: `manual_evidence_entry_preflight_ready_waiting_real_evidence`",
        "",
        f"1. Worksheet rows checked: {len(worksheet_rows)}",
        f"2. Target preflight rows: {len(target_rows)}",
        f"3. Field constraint rows: {len(field_rows)}",
        f"4. QA pass: {str(qa_pass).lower()}",
        "",
        "Conclusion: manual-entry targets and fields are indexed, but no real evidence is entered and no branch rerun is authorized.",
        "",
    ]
    write_text(OUT_DIR / "MANUAL_EVIDENCE_ENTRY_PREFLIGHT_README.md", "\n".join(report))
    write_text(OUT_DIR / "manual_evidence_entry_preflight_report.md", "\n".join(report))

    summary = {
        "package": "manual_evidence_entry_preflight_20260810",
        "worksheet_rows": len(worksheet_rows),
        "target_preflight_rows": len(target_rows),
        "field_constraint_rows": len(field_rows),
        "blocker_rows": len(blockers),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "manual_evidence_written": False,
        "branch_commands_safe_to_run_now": rerun.get("branch_commands_safe_to_run_now"),
        "submission_ready": False,
        "status": "manual_evidence_entry_preflight_ready_waiting_real_evidence",
    }

    section = f"""### 18.85 Manual evidence entry preflight update

Added a manual evidence entry preflight package that checks every worksheet target before any gate closure.

New directory: `{OUT_DIR}`

New files:
1. `manual_evidence_target_preflight.csv`
2. `manual_evidence_field_constraint_matrix.csv`
3. `manual_evidence_preflight_blockers.csv`
4. `manual_evidence_entry_preflight_qa.csv`
5. `MANUAL_EVIDENCE_ENTRY_PREFLIGHT_README.md`
6. `manual_evidence_entry_preflight_report.md`
7. `manual_evidence_entry_preflight_summary.json`

Current result:
1. worksheet_rows = {summary['worksheet_rows']}
2. target_preflight_rows = {summary['target_preflight_rows']}
3. field_constraint_rows = {summary['field_constraint_rows']}
4. qa_pass = {str(qa_pass).lower()}
5. manual_evidence_written = false
6. branch_commands_safe_to_run_now = {summary['branch_commands_safe_to_run_now']}
7. submission_ready = false

Boundary:
1. This step does not enter evidence.
2. This step does not authorize branch reruns.
3. This step does not close submission gates."""
    summary["desktop_plan_updated"] = update_desktop_plan(section)
    write_text(OUT_DIR / "manual_evidence_entry_preflight_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    if not qa_pass:
        raise SystemExit("Manual evidence entry preflight QA failed")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
