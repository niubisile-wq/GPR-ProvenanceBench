#!/usr/bin/env python3
"""Build a bounded Nature Communications submission-package skeleton."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "submission_package_skeleton_20260810"

RESULTS_MAP = REPORTS / "results_section_skeleton_20260810" / "results_paragraph_claim_evidence_map.csv"
METHODS_MAP = REPORTS / "methods_section_skeleton_20260810" / "methods_module_map.csv"
FIGURE_PLAN = REPORTS / "manuscript_figure_table_plan_20260810" / "figure_table_claim_evidence_map.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def build_terminology_ledger() -> list[dict[str, str]]:
    return [
        {
            "canonical_term": "ground-penetrating radar (GPR)",
            "first_use": "ground-penetrating radar (GPR)",
            "variants_to_avoid": "GPR only at first use; ground penetrating radar without hyphen",
            "decision": "Spell out once in abstract/main text, then use GPR.",
        },
        {
            "canonical_term": "GPR-ProvenanceBench",
            "first_use": "GPR-ProvenanceBench",
            "variants_to_avoid": "GPR provenance benchmark; provenance bench",
            "decision": "Use as the benchmark/workflow name only after the paper framing is finalized.",
        },
        {
            "canonical_term": "environment transfer",
            "first_use": "environment transfer",
            "variants_to_avoid": "domain transfer unless explicitly defined; external validation",
            "decision": "Use for Res-SAM real-world/synthetic transfer contrasts.",
        },
        {
            "canonical_term": "balanced accuracy",
            "first_use": "balanced accuracy",
            "variants_to_avoid": "BA before definition; accuracy when classes are imbalanced",
            "decision": "Use balanced accuracy for all reported deltas in current skeleton.",
        },
        {
            "canonical_term": "material support",
            "first_use": "material support",
            "variants_to_avoid": "significant support; strong proof",
            "decision": "Use only for the predeclared delta >= 0.05 threshold.",
        },
        {
            "canonical_term": "blind external validation",
            "first_use": "blind external validation",
            "variants_to_avoid": "external validation for template dry runs; blind test if labels were visible",
            "decision": "Use only for a future strict-SHA, label-held, one-shot evaluation; current status is open gate.",
        },
    ]


def build_title_candidates() -> list[dict[str, str]]:
    return [
        {
            "rank": "1",
            "title": "Environment transfer exposes brittle generalization in ground-penetrating radar recognition",
            "type": "finding-led",
            "status": "most_defensible_current_title",
            "boundary": "Lead claim is Res-SAM environment transfer; external blind validation is not complete.",
        },
        {
            "rank": "2",
            "title": "A provenance-aware benchmark for evaluating ground-penetrating radar recognition",
            "type": "resource/method-led",
            "status": "fallback_if_framed_as_benchmark",
            "boundary": "Use if external validation remains open and the paper is downgraded to benchmark/resource framing.",
        },
        {
            "rank": "3",
            "title": "Source and environment structure reshape performance estimates in GPR image recognition",
            "type": "mechanism/phenomenon-led",
            "status": "balanced_scope",
            "boundary": "Avoids claiming completed mitigation or blind validation.",
        },
        {
            "rank": "4",
            "title": "Provenance-aware evaluation of GPR recognition under split and environment shifts",
            "type": "methods-led",
            "status": "conservative",
            "boundary": "Best if the manuscript emphasizes evaluation protocol rather than a standalone discovery.",
        },
    ]


def build_claim_map(results_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in results_rows:
        rows.append(
            {
                "claim_id": row["paragraph_id"],
                "claim": row["topic_sentence"],
                "evidence": row["evidence"],
                "status": row["claim_status"],
                "figure_or_table": row["figure_or_table"],
                "allowed_in_abstract": "yes" if row["paragraph_id"] in {"R1", "R2", "R3", "R6"} else "no",
                "boundary": row["boundary"],
            }
        )
    return rows


def build_abstract() -> str:
    return (
        "Ground-penetrating radar (GPR) recognition models are commonly assessed with internal splits that may preserve source and processing structure. "
        "Here we assemble a provenance-aware evaluation skeleton across locally executable Mojahid, 4TU and Res-SAM assets, while keeping TIGPR and blind external validation as open gates. "
        "Across five model families, Res-SAM real-world/synthetic environment transfer produced the strongest current signal, with material support in 5/5 model families for real-to-synthetic transfer and 4/5 for synthetic-to-real transfer. "
        "Mojahid split inflation was directionally consistent but modest, and 4TU multi-layer counterfactual stress tests defined a feasibility-boundary layer rather than a main confirmation result. "
        "These results indicate that GPR recognition claims should report source-aware splits, environment-transfer contrasts and explicit validation gates before being interpreted as robust generalization."
    )


def build_markdown(
    path: Path,
    results_rows: list[dict[str, str]],
    methods_rows: list[dict[str, str]],
    figure_rows: list[dict[str, str]],
    abstract: str,
) -> None:
    title_rows = build_title_candidates()
    claim_rows = build_claim_map(results_rows)
    method_modules = ", ".join(row["module_id"] for row in methods_rows)
    display_items = ", ".join(row["item_id"] for row in figure_rows[:9])
    lines = [
        "# Submission Package Skeleton 2026-08-10",
        "",
        "Purpose: provide a bounded Nature Communications-facing title, abstract and cover-letter scaffold from frozen evidence only.",
        "",
        "## One-Sentence Argument",
        "",
        "In GPR recognition, we show that source and environment structure can materially change apparent model generalization using dated manifests, five model families, split/environment-transfer contrasts and counterfactual stress tests, with blind external validation still open.",
        "",
        "## Recommended Title",
        "",
        title_rows[0]["title"],
        "",
        "## Title Alternatives",
        "",
        "| rank | title | type | status | boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in title_rows:
        lines.append(
            f"| {row['rank']} | {row['title']} | {row['type']} | {row['status']} | {row['boundary']} |"
        )
    lines.extend(
        [
            "",
            "## Abstract Draft",
            "",
            abstract,
            "",
            f"Word count: {word_count(abstract)} / 150.",
            "",
            "## Significance Paragraph Draft",
            "",
            "GPR-based subsurface recognition is increasingly evaluated with machine-learning benchmarks, but internal splits can leave source, acquisition or processing cues shared between training and test data. The current evidence shows that this issue is not a cosmetic reporting detail: in Res-SAM, environment transfer produced the strongest cross-model performance drop, whereas Mojahid and 4TU provided more bounded split-sensitivity, stress-test and feasibility-boundary evidence. A provenance-aware evaluation workflow can therefore make GPR recognition studies more reusable by separating executable local evidence from unresolved confirmation gates, especially blind external validation.",
            "",
            "## Cover Letter Skeleton",
            "",
            "1. What the finding is: We show that source and environment structure can substantially reshape apparent generalization in GPR recognition, with the strongest current evidence from Res-SAM real-world/synthetic transfer across five model families.",
            "2. What makes it new: The manuscript frames GPR recognition around provenance-aware evaluation, combining dated asset manifests, split/transfer contrasts, counterfactual 4TU stress tests and explicit validation gates rather than relying on random split performance.",
            "3. Why it matters across disciplines: The work is relevant to geophysics, infrastructure sensing and machine-learning evaluation because it provides a reproducible way to distinguish robust subsurface recognition from dataset-source or processing-chain shortcuts.",
            "",
            "## Section Budget For Nature Communications Article",
            "",
            "| section | target words | current status |",
            "| --- | ---: | --- |",
            "| Introduction | 700 | outline not yet drafted |",
            "| Results | 1800 | skeleton ready |",
            "| Discussion | 700 | skeleton not yet drafted |",
            "| Methods | 1800 | module skeleton ready |",
            "| Abstract | 150 | draft ready |",
            "",
            "## Required Companion Artifacts",
            "",
            "1. Data Availability statement with public repository identifiers remains missing.",
            "2. Code Availability statement with repository URL and archival DOI remains missing.",
            "3. Reporting Summary remains missing.",
            "4. Final figure files are not rendered yet.",
            "5. Blind external validation remains an open gate, not a completed result.",
            "",
            "## Evidence Backbone",
            "",
            f"Methods modules covered: {method_modules}.",
            "",
            f"Planned display items covered: {display_items}.",
            "",
            "| claim | status | figure/table | boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in claim_rows:
        lines.append(
            f"| {row['claim']} | {row['status']} | {row['figure_or_table']} | {row['boundary']} |"
        )
    lines.extend(
        [
            "",
            "## Drafting Guardrails",
            "",
            "1. Do not state or imply that blind external validation is complete.",
            "2. Do not describe 4TU as a full five-model confirmation layer.",
            "3. Do not lead the abstract with Mojahid split inflation because it is directional_only.",
            "4. Keep the main title and abstract anchored to Res-SAM environment-transfer fragility until stronger external evidence is added.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results_rows = read_csv(RESULTS_MAP)
    methods_rows = read_csv(METHODS_MAP)
    figure_rows = read_csv(FIGURE_PLAN)
    abstract = build_abstract()
    title_rows = build_title_candidates()
    claim_rows = build_claim_map(results_rows)
    terminology_rows = build_terminology_ledger()

    write_csv(
        OUT_DIR / "title_candidates.csv",
        title_rows,
        ["rank", "title", "type", "status", "boundary"],
    )
    write_csv(
        OUT_DIR / "submission_claim_evidence_map.csv",
        claim_rows,
        ["claim_id", "claim", "evidence", "status", "figure_or_table", "allowed_in_abstract", "boundary"],
    )
    write_csv(
        OUT_DIR / "terminology_ledger.csv",
        terminology_rows,
        ["canonical_term", "first_use", "variants_to_avoid", "decision"],
    )
    build_markdown(
        OUT_DIR / "title_abstract_significance.md",
        results_rows,
        methods_rows,
        figure_rows,
        abstract,
    )

    cover_letter = (
        "# Cover Letter Skeleton 2026-08-10\n\n"
        "Dear Editors,\n\n"
        "We show that source and environment structure can substantially reshape apparent generalization in GPR recognition, with the strongest current evidence from Res-SAM real-world/synthetic transfer across five model families.\n\n"
        "The manuscript frames GPR recognition around provenance-aware evaluation, combining dated asset manifests, split/transfer contrasts, counterfactual 4TU stress tests and explicit validation gates rather than relying on random split performance.\n\n"
        "The work is relevant to geophysics, infrastructure sensing and machine-learning evaluation because it provides a reproducible way to distinguish robust subsurface recognition from dataset-source or processing-chain shortcuts.\n\n"
        "Boundary: this cover-letter skeleton must be revised before submission if blind external validation remains incomplete.\n"
    )
    (OUT_DIR / "cover_letter_skeleton.md").write_text(cover_letter, encoding="utf-8")

    result = {
        "run_id": "20260810_submission_package_skeleton",
        "title_candidates": len(title_rows),
        "abstract_words": word_count(abstract),
        "abstract_word_limit": 150,
        "abstract_within_limit": word_count(abstract) <= 150,
        "claim_rows": len(claim_rows),
        "terminology_terms": len(terminology_rows),
        "boundary": "Submission package skeleton only; not final submission text and no completed blind external validation.",
    }
    (OUT_DIR / "submission_package_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["abstract_within_limit"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
