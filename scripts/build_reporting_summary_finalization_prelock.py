#!/usr/bin/env python3
"""Build a non-final Reporting Summary finalization prelock package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "reporting_summary_finalization_prelock_20260810"
REPORTING_DIR = BENCH_ROOT / "reports" / "reporting_summary_draft_20260810"
AVAIL_DIR = BENCH_ROOT / "reports" / "availability_statement_prelock_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    draft_summary = json.loads((REPORTING_DIR / "reporting_summary_draft_summary.json").read_text(encoding="utf-8"))
    availability_summary = json.loads((AVAIL_DIR / "availability_statement_prelock_summary.json").read_text(encoding="utf-8"))
    draft_rows = read_csv(REPORTING_DIR / "reporting_summary_draft_answers.csv")
    unresolved_rows = read_csv(REPORTING_DIR / "reporting_summary_unresolved_items.csv")
    availability_gates = read_csv(AVAIL_DIR / "availability_statement_gate_requirements.csv")

    owner_by_item = {
        "Study design": "writing/analysis lead",
        "Sample size and exclusions": "analysis lead",
        "Randomization and split strategy": "analysis lead",
        "Blinding": "external holder/analysis lead",
        "Statistical analysis": "analysis lead/statistics reviewer",
        "Software and code availability": "author/repository lead",
        "Data availability": "author/repository lead",
        "External validation": "external holder/author",
    }
    trigger_by_item = {
        "Study design": "Final article framing, final figure/table set and claim hierarchy are locked.",
        "Sample size and exclusions": "Final asset inclusion/exclusion table, licence boundaries and sample counts are locked.",
        "Randomization and split strategy": "Frozen split manifests, seed table and final figure source-data mapping are complete.",
        "Blinding": "A real external asset passes strict SHA intake, labels are held outside the analyst workflow and predictions are frozen before label unlock.",
        "Statistical analysis": "Final metric list, uncertainty policy, tests if any, and multiple-comparison policy are locked.",
        "Software and code availability": "Public repository URL, release tag, software licence and archive DOI exist.",
        "Data availability": "Data repository DOI/accession, README, licence, final Source Data and rights review are complete.",
        "External validation": "One locked evaluation is run after label unlock, or the manuscript explicitly preserves external validation as an open gate.",
    }
    forbidden_by_item = {
        "Study design": "Do not imply a finished submission package while figures, validation and repository gates remain open.",
        "Sample size and exclusions": "Do not count TIGPR as an executable core asset while local sample rows remain zero.",
        "Randomization and split strategy": "Do not state that all final splits are frozen before final figure/source-data lock.",
        "Blinding": "Do not write completed blinding or blind validation from protocol templates or dry runs.",
        "Statistical analysis": "Do not imply inferential testing, uncertainty intervals or multiple-comparison correction unless actually added.",
        "Software and code availability": "Do not write public code repository, release tag or code DOI until they exist.",
        "Data availability": "Do not write data DOI, full public data availability or all-data-in-paper until source data, licence and rights are closed.",
        "External validation": "Do not write completed external validation without held labels, frozen predictions and one locked evaluation.",
    }

    lock_rows: list[dict[str, str]] = []
    for row in draft_rows:
        item = row["reporting_item"]
        current = row["current_status"]
        is_final_ready = current == "draft_answer_ready_not_final" and item in {"Study design", "Sample size and exclusions", "Randomization and split strategy", "Statistical analysis"}
        lock_rows.append(
            {
                "reporting_item": item,
                "current_status": current,
                "owner": owner_by_item[item],
                "can_lock_now": "no",
                "prelock_level": "content_draft_ready" if is_final_ready else "gate_blocked",
                "final_lock_trigger": trigger_by_item[item],
                "missing_before_submission": row["missing_before_submission"],
                "forbidden_final_wording": forbidden_by_item[item],
            }
        )
    write_csv(
        OUT_DIR / "reporting_summary_final_lock_matrix.csv",
        lock_rows,
        ["reporting_item", "current_status", "owner", "can_lock_now", "prelock_level", "final_lock_trigger", "missing_before_submission", "forbidden_final_wording"],
    )

    author_rows = [
        {
            "confirmation_id": "RS-C001",
            "owner": "corresponding author",
            "question": "Confirm final figure set and whether Figure 1-Figure 6 or a reduced set will be used.",
            "blocks": "Study design, randomization/split strategy, source-data mapping",
        },
        {
            "confirmation_id": "RS-C002",
            "owner": "analysis/statistics reviewer",
            "question": "Confirm whether the final paper reports descriptive metrics only or adds inferential tests/uncertainty intervals.",
            "blocks": "Statistical analysis Reporting Summary fields",
        },
        {
            "confirmation_id": "RS-C003",
            "owner": "external data holder",
            "question": "Confirm whether a real blind external asset exists, whether labels can be held back and whether aggregate metrics may be published.",
            "blocks": "Blinding and external validation fields",
        },
        {
            "confirmation_id": "RS-C004",
            "owner": "repository/rights lead",
            "question": "Confirm data DOI/accession, code DOI, licences and third-party redistribution boundaries.",
            "blocks": "Data availability and software/code availability fields",
        },
    ]
    write_csv(OUT_DIR / "reporting_summary_author_confirmation_checklist.csv", author_rows, ["confirmation_id", "owner", "question", "blocks"])

    forbidden_rows = [
        {
            "forbidden_claim": "The study was externally blinded.",
            "reason": "Only protocol templates and dry runs exist.",
            "allowed_replacement": "A blind external validation protocol has been prepared, but no real held-label asset has been evaluated.",
        },
        {
            "forbidden_claim": "Data and code are publicly available under DOI.",
            "reason": "Repository DOI and code DOI do not exist.",
            "allowed_replacement": "Repository metadata and availability wording are prepared for author review; identifiers remain unresolved.",
        },
        {
            "forbidden_claim": "All source data for final figures are available.",
            "reason": "Final rendered figures and panel-level source-data mapping are not complete.",
            "allowed_replacement": "Source-data skeletons and mapping plans exist; final Source Data remain pending figure rendering.",
        },
        {
            "forbidden_claim": "Final Reporting Summary is ready.",
            "reason": "High-risk blinding, data, code and external validation fields remain blocked.",
            "allowed_replacement": "Reporting Summary draft and finalization prelock are ready, but final lock is not ready.",
        },
    ]
    write_csv(OUT_DIR / "reporting_summary_forbidden_final_wording.csv", forbidden_rows, ["forbidden_claim", "reason", "allowed_replacement"])

    availability_rows = [
        {
            "availability_gate": row["gate"],
            "required_evidence": row["required_evidence"],
            "current_state": row["current_state"],
            "reporting_summary_field_impact": {
                "data_repository_identifier": "Data availability",
                "code_repository_identifier": "Software and code availability",
                "third_party_rights": "Data availability; sample handling",
                "figure_source_data": "Study design; Data availability",
                "blind_external_data": "Blinding; External validation",
            }[row["gate"]],
        }
        for row in availability_gates
    ]
    write_csv(OUT_DIR / "reporting_summary_availability_gate_crosswalk.csv", availability_rows, ["availability_gate", "required_evidence", "current_state", "reporting_summary_field_impact"])

    qa_rows = [
        {"check": "final_reporting_summary_not_claimed", "result": "PASS", "detail": f"final_reporting_summary_ready={draft_summary['final_reporting_summary_ready']}"},
        {"check": "all_items_marked_not_lockable_now", "result": "PASS" if all(row["can_lock_now"] == "no" for row in lock_rows) else "FAIL", "detail": f"rows={len(lock_rows)}"},
        {"check": "high_risk_items_preserved", "result": "PASS" if draft_summary["high_risk_items"] >= 4 else "FAIL", "detail": f"high_risk_items={draft_summary['high_risk_items']}"},
        {"check": "availability_not_final", "result": "PASS" if availability_summary["status"] == "availability_statement_prelock_ready_not_final" else "FAIL", "detail": availability_summary["status"]},
        {"check": "unresolved_items_preserved", "result": "PASS" if len(unresolved_rows) >= 6 else "FAIL", "detail": f"unresolved_items={len(unresolved_rows)}"},
    ]
    write_csv(OUT_DIR / "reporting_summary_prelock_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# Reporting Summary finalization prelock 2026-08-10

This package turns the Reporting Summary draft into a finalization-control artifact. It does not make the Reporting Summary final.

## Use

1. Use `reporting_summary_final_lock_matrix.csv` to decide which fields can be finalized after evidence arrives.
2. Use `reporting_summary_author_confirmation_checklist.csv` for author/external confirmations.
3. Use `reporting_summary_forbidden_final_wording.csv` to prevent protocol-only or local-only evidence from becoming final submission claims.

## Stop rules

1. Do not mark blinding complete before a real external asset, label holdout and frozen prediction submission exist.
2. Do not mark data/code availability complete before DOI/accession, licence and rights clearance exist.
3. Do not mark figure/source-data fields complete before final rendered figures and panel-level Source Data exist.
4. Do not mark Reporting Summary final while any high-risk field remains blocked.
"""
    (OUT_DIR / "REPORTING_SUMMARY_PRELOCK_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_reporting_summary_finalization_prelock",
        "reporting_items": len(lock_rows),
        "author_confirmations": len(author_rows),
        "forbidden_wording_rows": len(forbidden_rows),
        "availability_crosswalk_rows": len(availability_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "final_reporting_summary_ready": False,
        "submission_ready": False,
        "status": "reporting_summary_finalization_prelock_ready_not_final",
        "boundary": "This package controls finalization of Reporting Summary fields; it does not close blinding, external validation, DOI, rights, final figures or availability gates.",
    }
    (OUT_DIR / "reporting_summary_finalization_prelock_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = [
        "# Reporting Summary finalization prelock report 2026-08-10",
        "",
        f"- Reporting items: {summary['reporting_items']}",
        f"- Author confirmations: {summary['author_confirmations']}",
        f"- Forbidden wording rows: {summary['forbidden_wording_rows']}",
        f"- Availability crosswalk rows: {summary['availability_crosswalk_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: Reporting Summary fields are organized for finalization, but the final Reporting Summary remains blocked by unresolved scientific and repository gates.",
        "",
    ]
    (OUT_DIR / "reporting_summary_finalization_prelock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
