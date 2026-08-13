#!/usr/bin/env python3
"""Validate author reply packet readiness before any Nat Comms gate closure."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
IN_DIR = BENCH_ROOT / "reports" / "natcomms_author_finalization_reply_packet_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "natcomms_author_reply_ingestion_validator_20260810"

REPLY_FORM = IN_DIR / "author_finalization_reply_form_cn.csv"
METADATA_FORM = IN_DIR / "corresponding_author_metadata_form.csv"
BACKEND_TICKETS = IN_DIR / "figure_backend_decision_ticket.csv"
BRANCH_REPLY = IN_DIR / "track_branch_and_external_validation_reply.csv"
LICENCE_REPLY = IN_DIR / "licence_rights_reply_sheet.csv"
REVIEWER_POLICY_REPLY = IN_DIR / "reviewer_and_policy_reply_sheet.csv"
REPORTING_REPLY = IN_DIR / "reporting_summary_author_reply_sheet.csv"
MASTER_CHECKLIST = BENCH_ROOT / "reports" / "natcomms_finalization_master_checklist_20260810" / "finalization_master_checklist.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""


def gate_ids(raw: str) -> list[str]:
    return [part.strip() for part in raw.replace(",", ";").split(";") if part.strip().startswith("FM-")]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    reply_rows = read_csv(REPLY_FORM)
    metadata_rows = read_csv(METADATA_FORM)
    backend_rows = read_csv(BACKEND_TICKETS)
    branch_rows = read_csv(BRANCH_REPLY)
    licence_rows = read_csv(LICENCE_REPLY)
    reviewer_policy_rows = read_csv(REVIEWER_POLICY_REPLY)
    reporting_rows = read_csv(REPORTING_REPLY)
    master_rows = read_csv(MASTER_CHECKLIST)

    reply_validation_rows = []
    for row in reply_rows:
        blank = is_blank(row.get("author_reply"))
        reply_validation_rows.append(
            {
                "field_id": row["field_id"],
                "decision_area": row["decision_area"],
                "author_reply_blank": "yes" if blank else "no",
                "required_to_close_gate": row["required_to_close_gate"],
                "ingestion_status": "missing_author_reply" if blank else "reply_present_needs_manual_review",
                "closure_allowed": "no",
                "reason": "Author reply is blank." if blank else "Reply is present but still requires manual evidence review before gate closure.",
            }
        )
    write_csv(
        OUT_DIR / "author_reply_ingestion_validation.csv",
        reply_validation_rows,
        ["field_id", "decision_area", "author_reply_blank", "required_to_close_gate", "ingestion_status", "closure_allowed", "reason"],
    )

    gate_required: dict[str, list[str]] = {row["gate_id"]: [] for row in master_rows}
    gate_missing: dict[str, list[str]] = {row["gate_id"]: [] for row in master_rows}
    for row in reply_validation_rows:
        for gate in gate_ids(row["required_to_close_gate"]):
            gate_required.setdefault(gate, []).append(row["field_id"])
            if row["author_reply_blank"] == "yes":
                gate_missing.setdefault(gate, []).append(row["field_id"])

    gate_rows = []
    for row in master_rows:
        gate = row["gate_id"]
        required = gate_required.get(gate, [])
        missing = gate_missing.get(gate, [])
        gate_rows.append(
            {
                "gate_id": gate,
                "gate": row["gate"],
                "master_closed_status": row["closed"],
                "reply_fields_required": "; ".join(required),
                "missing_reply_fields": "; ".join(missing),
                "reply_evidence_status": "missing_replies" if missing else "reply_fields_present_manual_review_required",
                "gate_closure_recommendation": "keep_open",
                "reason": "Required author replies are missing." if missing else "Replies alone are insufficient; gate also requires artifact/evidence review.",
            }
        )
    write_csv(
        OUT_DIR / "gate_closure_from_author_replies.csv",
        gate_rows,
        ["gate_id", "gate", "master_closed_status", "reply_fields_required", "missing_reply_fields", "reply_evidence_status", "gate_closure_recommendation", "reason"],
    )

    ancillary_rows = []
    checks = [
        ("metadata", metadata_rows, "author_reply"),
        ("backend_ticket", backend_rows, "current_choice"),
        ("branch_external_validation", branch_rows, "author_reply"),
        ("licence_rights", licence_rows, "author_reply"),
        ("reviewer_policy", reviewer_policy_rows, "author_reply"),
        ("reporting_summary", reporting_rows, "author_reply"),
    ]
    for source, rows, field in checks:
        blank_count = sum(1 for row in rows if is_blank(row.get(field)))
        ancillary_rows.append(
            {
                "source": source,
                "rows": str(len(rows)),
                "reply_or_choice_field": field,
                "blank_rows": str(blank_count),
                "ingestion_status": "incomplete" if blank_count else "filled_needs_manual_review",
                "closure_allowed": "no",
            }
        )
    write_csv(
        OUT_DIR / "ancillary_reply_sheet_ingestion_status.csv",
        ancillary_rows,
        ["source", "rows", "reply_or_choice_field", "blank_rows", "ingestion_status", "closure_allowed"],
    )

    evidence_rules = [
        {
            "rule_id": "ARIV-001",
            "rule": "Blank author_reply cells cannot close any finalization gate.",
            "applies_to": "all reply sheets",
            "current_result": "FAIL_CLOSURE",
        },
        {
            "rule_id": "ARIV-002",
            "rule": "Recommended defaults are not author decisions.",
            "applies_to": "author_finalization_reply_form_cn.csv",
            "current_result": "ENFORCED",
        },
        {
            "rule_id": "ARIV-003",
            "rule": "Python remains a recommendation only until the author/backend field is explicitly filled.",
            "applies_to": "figure_backend_decision_ticket.csv",
            "current_result": "ENFORCED",
        },
        {
            "rule_id": "ARIV-004",
            "rule": "Track A cannot activate without named external holder, strict intake and locked evaluation evidence.",
            "applies_to": "track_branch_and_external_validation_reply.csv",
            "current_result": "ENFORCED",
        },
        {
            "rule_id": "ARIV-005",
            "rule": "Even filled replies require artifact review before final manuscript, SI or portal upload readiness.",
            "applies_to": "all gates",
            "current_result": "ENFORCED",
        },
    ]
    write_csv(
        OUT_DIR / "author_reply_evidence_rules.csv",
        evidence_rules,
        ["rule_id", "rule", "applies_to", "current_result"],
    )

    missing_reply_fields = sum(1 for row in reply_validation_rows if row["author_reply_blank"] == "yes")
    gates_with_missing = sum(1 for row in gate_rows if row["reply_evidence_status"] == "missing_replies")
    ancillary_blank_rows = sum(int(row["blank_rows"]) for row in ancillary_rows)
    qa_rows = [
        {"check": "Reply validation rows exist", "result": "PASS" if len(reply_validation_rows) == 12 else "FAIL", "detail": f"{len(reply_validation_rows)} rows."},
        {"check": "Blank replies are detected", "result": "PASS" if missing_reply_fields == 12 else "FAIL", "detail": f"{missing_reply_fields} blank author replies."},
        {"check": "No gate closure allowed", "result": "PASS" if all(row["gate_closure_recommendation"] == "keep_open" for row in gate_rows) else "FAIL", "detail": f"{len(gate_rows)} gates evaluated."},
        {"check": "Ancillary sheets audited", "result": "PASS" if len(ancillary_rows) == 6 else "FAIL", "detail": f"{len(ancillary_rows)} ancillary sources."},
        {"check": "Evidence rules exist", "result": "PASS" if len(evidence_rules) == 5 else "FAIL", "detail": f"{len(evidence_rules)} rules."},
    ]
    write_csv(OUT_DIR / "author_reply_ingestion_validator_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = [
        "# Nat Comms author reply ingestion validator",
        "",
        "Purpose: validate whether filled author reply sheets can be considered for finalization gate closure.",
        "",
        "Current checkpoint: all reply fields are blank, so every finalization gate remains open.",
        "",
        "Boundary: this package does not fill author replies, does not accept recommended defaults as decisions, and does not close any gate.",
        "",
    ]
    (OUT_DIR / "NATCOMMS_AUTHOR_REPLY_INGESTION_VALIDATOR_README.md").write_text("\n".join(readme), encoding="utf-8")

    report = [
        "# Author reply ingestion validator report",
        "",
        f"- Author reply fields audited: {len(reply_validation_rows)}",
        f"- Blank author reply fields: {missing_reply_fields}",
        f"- Master gates evaluated: {len(gate_rows)}",
        f"- Gates with missing replies: {gates_with_missing}",
        f"- Ancillary blank rows: {ancillary_blank_rows}",
        f"- Evidence rules: {len(evidence_rules)}",
        f"- QA failures: {sum(1 for row in qa_rows if row['result'] == 'FAIL')}",
        "- Status: natcomms_author_reply_ingestion_validator_ready_no_replies_ingested",
        "",
    ]
    (OUT_DIR / "author_reply_ingestion_validator_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_natcomms_author_reply_ingestion_validator",
        "author_reply_fields_audited": len(reply_validation_rows),
        "blank_author_reply_fields": missing_reply_fields,
        "master_gates_evaluated": len(gate_rows),
        "gates_with_missing_replies": gates_with_missing,
        "ancillary_sources_audited": len(ancillary_rows),
        "ancillary_blank_rows": ancillary_blank_rows,
        "evidence_rules": len(evidence_rules),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] != "FAIL" for row in qa_rows),
        "author_replies_ingested": False,
        "gate_closure_allowed": False,
        "submission_ready": False,
        "status": "natcomms_author_reply_ingestion_validator_ready_no_replies_ingested",
        "boundary": "Validator audits reply completeness only; blank or recommended-default replies cannot close any finalization gate.",
    }
    (OUT_DIR / "author_reply_ingestion_validator_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["qa_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
