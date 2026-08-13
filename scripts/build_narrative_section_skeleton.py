#!/usr/bin/env python3
"""Build Introduction, Discussion and Conclusion narrative contracts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "narrative_section_skeleton_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "results_section_skeleton_20260810"
        / "results_paragraph_claim_evidence_map.csv"
    )
    methods_rows = read_csv(
        BENCH_ROOT / "reports" / "methods_section_skeleton_20260810" / "methods_module_map.csv"
    )
    assembly = read_json(
        BENCH_ROOT
        / "reports"
        / "manuscript_assembly_skeleton_20260810"
        / "manuscript_assembly_summary.json"
    )

    result_status = {row["paragraph_id"]: row["claim_status"] for row in results_rows}
    method_titles = {row["module_id"]: row["module_title"] for row in methods_rows}

    intro_rows = [
        {
            "paragraph_id": "I1",
            "paragraph_job": "field scale",
            "target_words": 160,
            "topic_contract": "Open with why reliable ground-penetrating radar recognition matters beyond one curated image set.",
            "must_include": "ground-penetrating radar (GPR); inspection or subsurface recognition; model generalization",
            "evidence_anchor": "No numeric result; this is context and must be citation-backed later.",
            "must_not_claim": "Do not claim the field has solved automated GPR recognition or that this work is first.",
        },
        {
            "paragraph_id": "I2",
            "paragraph_job": "bottleneck",
            "target_words": 180,
            "topic_contract": "Define the evaluation bottleneck: random or weakly structured splits can mix acquisition, environment and processing provenance.",
            "must_include": "provenance structure; split protocol; apparent generalization",
            "evidence_anchor": "Previews R1/R3, but does not report numbers.",
            "must_not_claim": "Do not state that every published GPR model is leaked or invalid.",
        },
        {
            "paragraph_id": "I3",
            "paragraph_job": "prior gap",
            "target_words": 190,
            "topic_contract": "Position the unresolved gap as a lack of executable, multi-asset, model-family-level provenance stress testing.",
            "must_include": "asset audit; model-family robustness; external blind validation as a missing gate",
            "evidence_anchor": "Previews R1, R2, R4 and R6 as the study scope.",
            "must_not_claim": "Do not imply the blind external gate is already closed.",
        },
        {
            "paragraph_id": "I4",
            "paragraph_job": "present study",
            "target_words": 170,
            "topic_contract": "State what GPR-ProvenanceBench currently does and where its evidence stops.",
            "must_include": "Mojahid, Res-SAM and 4TU; five model families; source-data and reproducibility skeleton",
            "evidence_anchor": "R2 is the lead claim; R3/R4/R5 are bounded support; R6 is an open gate.",
            "must_not_claim": "Do not call the package submission-ready or externally validated.",
        },
    ]

    discussion_rows = [
        {
            "paragraph_id": "D1",
            "paragraph_job": "central advance",
            "target_words": 140,
            "topic_contract": "Interpret the central advance as evidence that environment and provenance structure reshape apparent GPR generalization.",
            "must_include": "Res-SAM environment transfer as the strongest current result",
            "evidence_anchor": "R2 status: " + result_status.get("R2", "unknown"),
            "hedging_rule": "Use shows for observed transfer drops; use suggests for broader field implication.",
        },
        {
            "paragraph_id": "D2",
            "paragraph_job": "meaning of secondary evidence",
            "target_words": 150,
            "topic_contract": "Explain why Mojahid and 4TU are useful but bounded evidence layers.",
            "must_include": "Mojahid directional_only; 4TU stress-test/failure-mode",
            "evidence_anchor": "R3 status: "
            + result_status.get("R3", "unknown")
            + "; R4 status: "
            + result_status.get("R4", "unknown"),
            "hedging_rule": "Do not convert directional-only or stress-test support into decisive confirmation.",
        },
        {
            "paragraph_id": "D3",
            "paragraph_job": "rival explanations",
            "target_words": 150,
            "topic_contract": "Address rival explanations including model-family dependence, label imbalance and project-level grouping limits.",
            "must_include": "TinyCNN mixed behavior; 4TU group-aware weakening; label feasibility limits",
            "evidence_anchor": "R3/R4/R5 boundaries and Methods M3/M5.",
            "hedging_rule": "Use may reflect or is consistent with; avoid mechanism proof language.",
        },
        {
            "paragraph_id": "D4",
            "paragraph_job": "reuse and reproducibility",
            "target_words": 130,
            "topic_contract": "State what the current reproducibility package enables: regeneration, audit, source-data mapping and release staging.",
            "must_include": method_titles.get("M7", "reproducibility checks") + "; source-data deposit skeleton; sanitized release staging",
            "evidence_anchor": "M7 and manuscript assembly skeleton.",
            "hedging_rule": "Do not call the staging preview a public repository.",
        },
        {
            "paragraph_id": "D5",
            "paragraph_job": "limitations and open gates",
            "target_words": 170,
            "topic_contract": "Close the Discussion with specific limitations that must be solved before a final Nat Commun submission.",
            "must_include": "blind external validation NO-GO; figures not rendered; data/code DOI missing; Reporting Summary incomplete; third-party rights not cleared",
            "evidence_anchor": "manuscript_blocker_checklist.csv and assembly reason_not_ready.",
            "hedging_rule": "Use explicit blocking language rather than generic future-work language.",
        },
    ]

    conclusion_rows = [
        {
            "paragraph_id": "C1",
            "paragraph_job": "contribution",
            "target_words": 70,
            "sentence_contract": "Restate that GPR-ProvenanceBench turns provenance-aware GPR evaluation into an auditable benchmark workflow.",
            "evidence_anchor": "R1/M1/M7 plus manuscript assembly skeleton",
            "overclaim_guard": "Do not say the benchmark is final or complete.",
        },
        {
            "paragraph_id": "C2",
            "paragraph_job": "decisive current evidence",
            "target_words": 80,
            "sentence_contract": "Name Res-SAM environment transfer as the strongest current cross-model result and Mojahid/4TU as bounded support.",
            "evidence_anchor": "R2 supported_current_main; R3 directional_only; R4 stress_test_supported",
            "overclaim_guard": "Do not describe Mojahid or 4TU as equal-strength confirmation.",
        },
        {
            "paragraph_id": "C3",
            "paragraph_job": "implication and boundary",
            "target_words": 80,
            "sentence_contract": "End with the narrow implication: provenance-aware evaluation should precede claims of GPR generalization, while final submission still requires blind external validation and public release closure.",
            "evidence_anchor": "R6 open gate and assembly blockers",
            "overclaim_guard": "Do not promise clinical, infrastructure or field deployment performance.",
        },
    ]

    risk_rows = [
        {
            "risk_id": "NR1",
            "risk": "Overstating external validation",
            "trigger_terms": "validated externally; blind test passed; independent external result",
            "required_replacement": "protocol-ready but not complete; open blind external gate",
            "evidence_source": "R6 and external_validation_readiness_20260810",
        },
        {
            "risk_id": "NR2",
            "risk": "Overstating Mojahid",
            "trigger_terms": "universal leakage; decisive split inflation",
            "required_replacement": "directionally consistent but modest/model-dependent split sensitivity",
            "evidence_source": "R3 and Table 2 status directional_only",
        },
        {
            "risk_id": "NR3",
            "risk": "Overstating 4TU",
            "trigger_terms": "causal proof; main confirmation; robust 4TU generalization",
            "required_replacement": "raw-trace-derived stress-test and failure-mode evidence",
            "evidence_source": "R4/R5 and 4TU group-aware feasibility audit",
        },
        {
            "risk_id": "NR4",
            "risk": "Overstating release readiness",
            "trigger_terms": "public repository available; data deposited; source data complete",
            "required_replacement": "source-data and sanitized release skeletons exist, but DOI, licence and rights are unresolved",
            "evidence_source": "source_data_deposit_summary, release_readiness_summary and sanitized_release_summary",
        },
        {
            "risk_id": "NR5",
            "risk": "Overstating method replication",
            "trigger_terms": "full Res-SAM replication; TIGPR core asset",
            "required_replacement": "Res-SAM lightweight asset is executable; full SAM checkpoint/runtime and TIGPR local executable asset remain NO-GO",
            "evidence_source": "TIGPR local asset audit and Res-SAM go/no-go",
        },
    ]

    write_csv(OUT_DIR / "introduction_paragraph_contracts.csv", intro_rows)
    write_csv(OUT_DIR / "discussion_paragraph_contracts.csv", discussion_rows)
    write_csv(OUT_DIR / "conclusion_paragraph_contracts.csv", conclusion_rows)
    write_csv(OUT_DIR / "narrative_claim_evidence_risk_map.csv", risk_rows)

    summary = {
        "run_id": "20260810_narrative_section_skeleton",
        "one_sentence_argument": assembly["one_sentence_argument"],
        "introduction_paragraphs": len(intro_rows),
        "discussion_paragraphs": len(discussion_rows),
        "conclusion_paragraphs": len(conclusion_rows),
        "risk_rows": len(risk_rows),
        "total_target_words": sum(int(row["target_words"]) for row in intro_rows + discussion_rows + conclusion_rows),
        "status": "outline_ready_not_final_prose",
        "manuscript_ready": False,
        "boundary": "Narrative contracts only; no final manuscript prose, citations, rendered figures or blind external validation.",
    }

    (OUT_DIR / "narrative_section_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md = f"""# Narrative Section Skeleton 2026-08-10

## One-sentence argument

{assembly["one_sentence_argument"]}

## Introduction contract

| Paragraph | Job | Target words | Topic contract | Must not claim |
| --- | --- | ---: | --- | --- |
"""
    for row in intro_rows:
        md += (
            f"| {row['paragraph_id']} | {row['paragraph_job']} | {row['target_words']} | "
            f"{row['topic_contract']} | {row['must_not_claim']} |\n"
        )

    md += """
## Discussion contract

| Paragraph | Job | Target words | Topic contract | Hedging rule |
| --- | --- | ---: | --- | --- |
"""
    for row in discussion_rows:
        md += (
            f"| {row['paragraph_id']} | {row['paragraph_job']} | {row['target_words']} | "
            f"{row['topic_contract']} | {row['hedging_rule']} |\n"
        )

    md += """
## Conclusion contract

| Paragraph | Job | Target words | Sentence contract | Overclaim guard |
| --- | --- | ---: | --- | --- |
"""
    for row in conclusion_rows:
        md += (
            f"| {row['paragraph_id']} | {row['paragraph_job']} | {row['target_words']} | "
            f"{row['sentence_contract']} | {row['overclaim_guard']} |\n"
        )

    md += """
## Narrative risk map

| Risk | Trigger terms to avoid | Required replacement |
| --- | --- | --- |
"""
    for row in risk_rows:
        md += (
            f"| {row['risk']} | {row['trigger_terms']} | "
            f"{row['required_replacement']} |\n"
        )

    md += """
## Drafting boundary

This package is a paragraph-contract layer. It is safe to use for writing the Introduction, Discussion and Conclusion, but it is not final manuscript prose. Citations, rendered figures, repository identifiers, Reporting Summary answers and a real blind external result remain outside this package.
"""

    (OUT_DIR / "narrative_section_skeleton.md").write_text(md, encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
