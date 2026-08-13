#!/usr/bin/env python3
"""Build a Track B manuscript branch prelock package."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "track_b_manuscript_branch_prelock_20260810"
AUTHOR_REVIEW = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_v0_1.md"
AUTHOR_SUMMARY = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_summary.json"
CONTINGENCY_DIR = BENCH_ROOT / "reports" / "external_validation_contingency_framing_20260810"
DASHBOARD_SUMMARY = BENCH_ROOT / "reports" / "submission_command_dashboard_v2_20260810" / "submission_command_dashboard_v2_summary.json"
CLAIM_AUDIT = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "manuscript_claim_readiness_audit.csv"
FORBIDDEN_DASHBOARD = BENCH_ROOT / "reports" / "submission_command_dashboard_v2_20260810" / "global_forbidden_claims_dashboard.csv"


TRACK_B_ABSTRACT = """Ground-penetrating radar (GPR) recognition models are often evaluated within curated datasets whose samples may share acquisition, environment or processing histories. We assembled GPR-ProvenanceBench as an auditable workflow linking dated manifests, grouped split logic, environment-transfer tests, model-family comparisons and source-data traceability. At the current checkpoint, Res-SAM environment transfer provides the strongest reproducible signal: real-to-synthetic transfer showed directional and material balanced-accuracy drops in all five model families, with a mean delta of 0.4239, and synthetic-to-real transfer showed directional and material drops in four of five families, with a mean delta of 0.3743. Mojahid provides directional but modest split-sensitivity support, whereas 4TU defines stress-test and feasibility boundaries. These results support a provenance-aware benchmark-trust argument for GPR recognition. Blind external validation remains an open gate rather than a completed result."""


TITLE_ROWS = [
    {
        "title_id": "TB-T1",
        "title": "Environment transfer exposes fragile generalization in ground-penetrating-radar recognition",
        "type": "finding_led",
        "recommendation": "recommended_current_default",
        "boundary": "Finding-led but bounded to current executable evidence; does not imply completed external validation.",
    },
    {
        "title_id": "TB-T2",
        "title": "GPR-ProvenanceBench audits benchmark trust under environment transfer",
        "type": "resource_plus_argument",
        "recommendation": "strong_track_b_alternative",
        "boundary": "Emphasizes benchmark/resource contribution and avoids external generalization wording.",
    },
    {
        "title_id": "TB-T3",
        "title": "Auditing provenance sensitivity in ground-penetrating-radar recognition benchmarks",
        "type": "workflow_led",
        "recommendation": "conservative_low_risk",
        "boundary": "Most conservative; weaker hook but lowest overclaim risk.",
    },
    {
        "title_id": "TB-T4",
        "title": "Environment-aware evaluation reveals brittle GPR recognition across model families",
        "type": "broad_interest",
        "recommendation": "use_only_if_figures_support_visual_hierarchy",
        "boundary": "Requires Figure 2 to remain dominant and no external-validation wording.",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    author_summary = json.loads(AUTHOR_SUMMARY.read_text(encoding="utf-8"))
    dashboard_summary = json.loads(DASHBOARD_SUMMARY.read_text(encoding="utf-8"))
    branch_rows = read_csv(CONTINGENCY_DIR / "external_validation_branch_decision_matrix.csv")
    claim_rows = read_csv(CLAIM_AUDIT)
    forbidden_rows = read_csv(FORBIDDEN_DASHBOARD)
    manuscript_text = AUTHOR_REVIEW.read_text(encoding="utf-8")
    track_b = next(row for row in branch_rows if row["branch_id"] == "TRACK-B")

    argument = "In GPR recognition benchmarking, we show that provenance- and environment-aware evaluation exposes brittle Res-SAM transfer across five model families using auditable local manifests, model-family contrasts and stress-test boundaries, while blind external validation remains open."
    (OUT_DIR / "track_b_one_sentence_argument.md").write_text(argument + "\n", encoding="utf-8")

    write_csv(OUT_DIR / "track_b_title_candidates.csv", TITLE_ROWS, ["title_id", "title", "type", "recommendation", "boundary"])
    (OUT_DIR / "track_b_abstract_prelock.md").write_text("# Track B abstract prelock\n\n" + TRACK_B_ABSTRACT + "\n", encoding="utf-8")

    branch_lock_rows = [
        {
            "field": "current_applicable_branch",
            "value": dashboard_summary["current_applicable_branch"],
            "lock_status": "track_b_currently_applicable_not_author_final",
            "boundary": "Track B remains applicable because no real blind external asset has passed strict intake and locked evaluation.",
        },
        {
            "field": "manuscript_positioning",
            "value": track_b["manuscript_positioning"],
            "lock_status": "prelock",
            "boundary": track_b["still_forbidden"],
        },
        {
            "field": "allowed_external_validation_language",
            "value": track_b["allowed_external_validation_language"],
            "lock_status": "prelock",
            "boundary": "External validation must be described as an open gate.",
        },
        {
            "field": "nat_comms_word_budget",
            "value": f"current_body_words={author_summary['body_words_excluding_title_abstract']}; abstract_words={word_count(TRACK_B_ABSTRACT)}; article_reference_limit=5000 including Methods",
            "lock_status": "within_current_budget_but_not_final",
            "boundary": "Word count must be recomputed after figures, references and final statements are inserted.",
        },
    ]
    write_csv(OUT_DIR / "track_b_branch_lock_matrix.csv", branch_lock_rows, ["field", "value", "lock_status", "boundary"])

    section_rows = [
        {
            "section": "Title",
            "prelock_action": "Use TB-T1 as the default or TB-T2 if resource positioning is preferred.",
            "must_preserve": "No external-validation or deployment-robustness wording.",
            "final_blocker": "Author route decision and final figure hierarchy.",
        },
        {
            "section": "Abstract",
            "prelock_action": "Use the Track B abstract if external validation remains unavailable.",
            "must_preserve": "Res-SAM transfer is the main result; Mojahid and 4TU are bounded; blind validation remains open.",
            "final_blocker": "Final figures, reference numbering and availability statements.",
        },
        {
            "section": "Discussion",
            "prelock_action": "Interpret the benchmark as provenance-aware evidence boundary, not external generalization.",
            "must_preserve": "Limitations must name missing blind external validation, DOI/rights, rendered figures and Reporting Summary.",
            "final_blocker": "Figure rendering and final repository/availability decisions.",
        },
        {
            "section": "Conclusion",
            "prelock_action": "End with a bounded benchmark-trust implication.",
            "must_preserve": "No universal GPR leakage, no completed blind validation and no repository release claim.",
            "final_blocker": "Final claim-source map and references.",
        },
    ]
    write_csv(OUT_DIR / "track_b_section_prelock_actions.csv", section_rows, ["section", "prelock_action", "must_preserve", "final_blocker"])

    claim_rows_out = []
    for row in claim_rows:
        claim_rows_out.append(
            {
                "claim_id": row["claim_id"],
                "track_b_role": row["allowed_strength"],
                "allowed_wording": row["required_wording"],
                "forbidden_upgrade": row["forbidden_upgrade"],
                "figure_or_table": row["figure_or_table"],
                "track_b_status": "allowed_with_boundary" if row["readiness"] != "open_gate_only" else "open_gate_only",
            }
        )
    write_csv(OUT_DIR / "track_b_claim_role_lock.csv", claim_rows_out, ["claim_id", "track_b_role", "allowed_wording", "forbidden_upgrade", "figure_or_table", "track_b_status"])

    no_go_rows = [
        {
            "no_go_id": f"TB-NG{i+1:02d}",
            "forbidden_statement": row.get("forbidden_claim", row.get("claim", "")),
            "reason": row.get("reason", "Contradicts current hard-gate status."),
            "track_b_replacement": "Use bounded/open-gate wording from the Track B branch lock matrix.",
        }
        for i, row in enumerate(forbidden_rows)
    ]
    no_go_rows.extend(
        [
            {
                "no_go_id": "TB-NG99A",
                "forbidden_statement": "The benchmark demonstrates deployment robustness across GPR settings.",
                "reason": "No completed blind external validation exists.",
                "track_b_replacement": "The benchmark exposes environment-transfer fragility within the current executable evidence boundary.",
            },
            {
                "no_go_id": "TB-NG99B",
                "forbidden_statement": "All source data and code are publicly available under DOI.",
                "reason": "Repository DOI, code DOI, licence and rights clearance are not complete.",
                "track_b_replacement": "Availability statements remain prelock until identifiers and rights are resolved.",
            },
        ]
    )
    write_csv(OUT_DIR / "track_b_forbidden_upgrade_ledger.csv", no_go_rows, ["no_go_id", "forbidden_statement", "reason", "track_b_replacement"])

    qa_rows = [
        {
            "qa_check": "track_b_currently_applicable",
            "status": "pass" if dashboard_summary["current_applicable_branch"] == "TRACK-B" else "fail",
            "evidence": dashboard_summary["current_applicable_branch"],
        },
        {
            "qa_check": "abstract_under_nat_comms_limit",
            "status": "pass" if word_count(TRACK_B_ABSTRACT) <= 150 else "fail",
            "evidence": f"abstract_words={word_count(TRACK_B_ABSTRACT)}",
        },
        {
            "qa_check": "submission_not_ready_preserved",
            "status": "pass" if not dashboard_summary["submission_ready"] and not author_summary["submission_ready"] else "fail",
            "evidence": "dashboard and author manuscript summaries both record submission_ready=false",
        },
        {
            "qa_check": "no_completed_external_validation_wording",
            "status": "pass" if "completed blind external validation" not in TRACK_B_ABSTRACT.lower() else "fail",
            "evidence": "Track B abstract states open gate",
        },
        {
            "qa_check": "no_final_repository_claim",
            "status": "pass" if "doi" not in TRACK_B_ABSTRACT.lower() and "publicly available" not in TRACK_B_ABSTRACT.lower() else "fail",
            "evidence": "Track B abstract omits DOI/public release claims",
        },
    ]
    write_csv(OUT_DIR / "track_b_branch_prelock_qa.csv", qa_rows, ["qa_check", "status", "evidence"])

    prelock_manuscript = [
        "# Track B manuscript branch prelock",
        "",
        f"One-sentence argument: {argument}",
        "",
        "## Recommended title",
        "",
        TITLE_ROWS[0]["title"],
        "",
        "## Abstract",
        "",
        TRACK_B_ABSTRACT,
        "",
        "## Required branch boundary",
        "",
        "Track B is a benchmark/resource and evidence-boundary route. It must not be rewritten as completed external validation, deployment robustness, repository release or final submission readiness.",
        "",
    ]
    (OUT_DIR / "track_b_manuscript_branch_prelock.md").write_text("\n".join(prelock_manuscript), encoding="utf-8")

    readme = """# Track B manuscript branch prelock 2026-08-10

This package locks the currently applicable no-external-validation manuscript branch.

It does not finalize the manuscript. Formal figures, repository identifiers, rights, Reporting Summary and final references remain open.
"""
    (OUT_DIR / "TRACK_B_MANUSCRIPT_BRANCH_PRELOCK_README.md").write_text(readme, encoding="utf-8")

    qa_pass = all(row["status"] == "pass" for row in qa_rows)
    summary = {
        "run_id": "20260810_track_b_manuscript_branch_prelock",
        "current_applicable_branch": dashboard_summary["current_applicable_branch"],
        "title_candidates": len(TITLE_ROWS),
        "abstract_words": word_count(TRACK_B_ABSTRACT),
        "claim_role_rows": len(claim_rows_out),
        "forbidden_upgrade_rows": len(no_go_rows),
        "section_action_rows": len(section_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": qa_pass,
        "submission_ready": False,
        "status": "track_b_manuscript_branch_prelock_ready_not_submission_final",
        "boundary": "This package locks Track B branch wording and boundaries; it does not finalize manuscript, figures, references, DOI, rights or Reporting Summary.",
    }
    (OUT_DIR / "track_b_manuscript_branch_prelock_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Track B manuscript branch prelock report 2026-08-10",
        "",
        f"- Current applicable branch: {summary['current_applicable_branch']}",
        f"- Title candidates: {summary['title_candidates']}",
        f"- Abstract words: {summary['abstract_words']}",
        f"- Claim-role rows: {summary['claim_role_rows']}",
        f"- Forbidden-upgrade rows: {summary['forbidden_upgrade_rows']}",
        f"- Section action rows: {summary['section_action_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: Track B wording is prelocked for the current no-external-validation route, but submission remains blocked by figures, DOI/rights, Reporting Summary and final references.",
        "",
    ]
    (OUT_DIR / "track_b_manuscript_branch_prelock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
