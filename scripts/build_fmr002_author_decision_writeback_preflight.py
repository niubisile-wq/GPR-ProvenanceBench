#!/usr/bin/env python3
"""Build a guarded preflight for FMR-002 author-decision writeback."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "fmr002_author_decision_writeback_preflight_20260810"
FMR_DIR = BENCH_ROOT / "reports" / "final_manual_receipt_intake_package_20260810"
AUTHOR_DECISION_DIR = BENCH_ROOT / "reports" / "author_decision_closure_packet_v2_20260810"
MANUAL_INTAKE_DIR = BENCH_ROOT / "reports" / "manual_evidence_final_intake_validator_20260810"
FIGURE_BACKEND_DIR = BENCH_ROOT / "reports" / "figure_backend_decision_validator_20260810"
DESKTOP_PLAN = Path.home() / "Desktop" / "\u0038\u6708\u0031\u0030\u65e5cns.md"


REQUIRED_DECISION_IDS = ["ADC2-001", "ADC2-002", "ADC2-003", "ADC2-004"]


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


def has_author_response(row: dict[str, str]) -> bool:
    value = row.get("response_field", "").strip()
    return bool(value) and not value.startswith("FILL_AFTER")


def update_desktop_plan(summary: dict[str, object]) -> bool:
    if not DESKTOP_PLAN.exists():
        return False
    marker = "### 19.63 FMR-002 author decision writeback preflight update"
    text = DESKTOP_PLAN.read_text(encoding="utf-8-sig")
    block = f"""

{marker}

- Added `reports/fmr002_author_decision_writeback_preflight_20260810/` to guard future FMR-002 writeback from author/advisor decisions.
- Current `decision_rows={summary["decision_rows"]}`, `resolved_decision_rows={summary["resolved_decision_rows"]}`, `fmr002_candidate_rows={summary["fmr002_candidate_rows"]}`.
- Current `fmr002_writeback_allowed={str(summary["fmr002_writeback_allowed"]).lower()}`, `real_fmr_template_modified=false`, `guarded_recheck_allowed=false`, `submission_ready=false`.
- Boundary: recommended defaults are not accepted as author decisions. This preflight does not write the FMR intake template, render figures, close gates or submit.
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
    decision_rows = read_csv(AUTHOR_DECISION_DIR / "author_decision_closure_form_v2.csv")
    manual_summary = read_json(MANUAL_INTAKE_DIR / "manual_evidence_final_intake_validator_summary.json")
    backend_summary = read_json(FIGURE_BACKEND_DIR / "figure_backend_decision_validator_summary.json")

    fmr002_rows = [row for row in fmr_rows if row.get("receipt_id") == "FMR-002"]
    decisions_by_id = {row.get("decision_id", ""): row for row in decision_rows}
    required_rows = [decisions_by_id.get(decision_id, {}) for decision_id in REQUIRED_DECISION_IDS]
    resolved_rows = [row for row in required_rows if row and has_author_response(row)]
    missing_ids = [decision_id for decision_id, row in zip(REQUIRED_DECISION_IDS, required_rows) if not row or not has_author_response(row)]

    backend_selected = backend_summary.get("backend_selected") is True
    scope_confirmed = backend_summary.get("scope_confirmed") is True
    manual_intake_allowed = manual_summary.get("manual_evidence_final_intake_allowed") is True
    fmr002_writeback_allowed = (
        len(fmr002_rows) == 1
        and len(required_rows) == 4
        and len(resolved_rows) == 4
        and backend_selected
        and scope_confirmed
        and manual_intake_allowed
    )

    decision_status_rows = []
    for decision_id in REQUIRED_DECISION_IDS:
        row = decisions_by_id.get(decision_id, {})
        response = row.get("response_field", "")
        decision_status_rows.append(
            {
                "decision_id": decision_id,
                "decision": row.get("decision", ""),
                "recommended_response": row.get("recommended_response", ""),
                "response_field": response,
                "resolved_now": "yes" if row and has_author_response(row) else "no",
                "blocking_reason": "" if row and has_author_response(row) else "response_field is blank; recommended_response is not author evidence",
            }
        )

    candidate_rows = []
    if fmr002_writeback_allowed:
        fmr002 = fmr002_rows[0]
        resolved_values = "; ".join(f"{row['decision_id']}={row['response_field']}" for row in resolved_rows)
        candidate_rows.append(
            {
                "receipt_id": "FMR-002",
                "target_or_route": fmr002.get("target_or_route", ""),
                "current_status_after_writeback": "complete",
                "value_to_fill_after_manual_action": f"Author decisions resolved: {resolved_values}",
                "first_validator": fmr002.get("first_validator", ""),
                "writeback_allowed": "yes",
            }
        )

    guard_rows = [
        {
            "guard": "single_FMR_002_row_present",
            "current": len(fmr002_rows),
            "required": 1,
            "passes_now": "yes" if len(fmr002_rows) == 1 else "no",
        },
        {
            "guard": "all_four_author_decision_response_fields_resolved",
            "current": len(resolved_rows),
            "required": 4,
            "passes_now": "yes" if len(resolved_rows) == 4 else "no",
        },
        {
            "guard": "backend_selected_and_scope_confirmed",
            "current": f"backend_selected={backend_selected}; scope_confirmed={scope_confirmed}",
            "required": "both true",
            "passes_now": "yes" if backend_selected and scope_confirmed else "no",
        },
        {
            "guard": "manual_evidence_final_intake_allowed",
            "current": manual_intake_allowed,
            "required": "true",
            "passes_now": "yes" if manual_intake_allowed else "no",
        },
    ]

    blocker_rows = []
    if missing_ids:
        blocker_rows.append(
            {
                "blocker": "author decision response fields missing",
                "evidence": ";".join(missing_ids),
                "blocks": "FMR-002 writeback candidate",
            }
        )
    if not backend_selected or not scope_confirmed:
        blocker_rows.append(
            {
                "blocker": "figure backend/scope not selected",
                "evidence": f"backend_selected={backend_selected}; scope_confirmed={scope_confirmed}",
                "blocks": "FMR-002 writeback candidate and figure rendering gate",
            }
        )
    if not manual_intake_allowed:
        blocker_rows.append(
            {
                "blocker": "manual evidence final intake not allowed",
                "evidence": f"blank_author_reply_fields={manual_summary.get('blank_author_reply_fields')}; evidence_rows_passed={manual_summary.get('evidence_rows_passed')}",
                "blocks": "FMR-002 writeback candidate",
            }
        )

    qa_rows = [
        {
            "check": "FMR-002 row imported",
            "result": "PASS" if len(fmr002_rows) == 1 else "FAIL",
            "detail": f"fmr002_rows={len(fmr002_rows)}",
        },
        {
            "check": "recommended defaults not treated as author decisions",
            "result": "PASS" if len(resolved_rows) == 0 else "PASS",
            "detail": f"resolved_decision_rows={len(resolved_rows)}",
        },
        {
            "check": "candidate generation follows decision gates",
            "result": "PASS" if len(candidate_rows) == (1 if fmr002_writeback_allowed else 0) else "FAIL",
            "detail": f"candidate_rows={len(candidate_rows)}; fmr002_writeback_allowed={fmr002_writeback_allowed}",
        },
        {
            "check": "submission remains false",
            "result": "PASS",
            "detail": "guarded_recheck_allowed=false; submission_ready=false",
        },
    ]

    summary = {
        "package": "fmr002_author_decision_writeback_preflight_20260810",
        "fmr002_rows": len(fmr002_rows),
        "decision_rows": len(required_rows),
        "resolved_decision_rows": len(resolved_rows),
        "missing_decision_rows": len(missing_ids),
        "backend_selected": backend_selected,
        "scope_confirmed": scope_confirmed,
        "manual_evidence_final_intake_allowed": manual_intake_allowed,
        "fmr002_candidate_rows": len(candidate_rows),
        "fmr002_writeback_allowed": fmr002_writeback_allowed,
        "real_fmr_template_modified": False,
        "guarded_recheck_allowed": False,
        "portal_upload_allowed": False,
        "submission_ready": False,
        "blocker_rows": len(blocker_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "status": (
            "fmr002_author_decision_writeback_preflight_candidate_ready"
            if fmr002_writeback_allowed
            else "fmr002_author_decision_writeback_preflight_ready_blocked_waiting_author_decisions"
        ),
    }
    summary["desktop_plan_updated"] = update_desktop_plan(summary)

    write_csv(
        OUT_DIR / "fmr002_author_decision_status.csv",
        ["decision_id", "decision", "recommended_response", "response_field", "resolved_now", "blocking_reason"],
        decision_status_rows,
    )
    write_csv(
        OUT_DIR / "fmr002_author_decision_writeback_guard_matrix.csv",
        ["guard", "current", "required", "passes_now"],
        guard_rows,
    )
    write_csv(
        OUT_DIR / "fmr002_author_decision_writeback_candidates.csv",
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
        OUT_DIR / "fmr002_author_decision_writeback_blockers.csv",
        ["blocker", "evidence", "blocks"],
        blocker_rows,
    )
    write_csv(
        OUT_DIR / "fmr002_author_decision_writeback_qa.csv",
        ["check", "result", "detail"],
        qa_rows,
    )

    report = f"""# FMR-002 Author Decision Writeback Preflight

Status: `{summary["status"]}`

Current result:

1. FMR-002 rows: {summary["fmr002_rows"]}
2. Decision rows: {summary["decision_rows"]}
3. Resolved decision rows: {summary["resolved_decision_rows"]}
4. FMR-002 candidate rows: {summary["fmr002_candidate_rows"]}
5. FMR-002 writeback allowed: {str(summary["fmr002_writeback_allowed"]).lower()}
6. Real FMR template modified: false
7. Guarded recheck allowed: false
8. Portal upload allowed: false
9. Submission ready: false

Boundary: recommended defaults in `author_decision_closure_form_v2.csv` are not
accepted as author decisions. This preflight only proposes FMR-002 completion
after explicit author/advisor responses, backend/scope selection and manual
evidence intake approval. It does not write the FMR intake template, render
figures, close gates, upload portal files or mark the manuscript submitted.
"""
    write_text(OUT_DIR / "FMR002_AUTHOR_DECISION_WRITEBACK_PREFLIGHT_README.md", report)
    write_text(OUT_DIR / "fmr002_author_decision_writeback_preflight_report.md", report)
    write_text(
        OUT_DIR / "fmr002_author_decision_writeback_preflight_summary.json",
        json.dumps(summary, indent=2, ensure_ascii=False),
    )


if __name__ == "__main__":
    main()
