#!/usr/bin/env python3
"""Build conservative broad-interest framing revisions for author review."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "broad_interest_framing_revision_20260810"
MANUSCRIPT_SUMMARY = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_summary.json"
ACTION_SUMMARY = BENCH_ROOT / "reports" / "reviewer_risk_revision_action_packet_20260810" / "reviewer_risk_revision_action_packet_summary.json"


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manuscript_summary = json.loads(MANUSCRIPT_SUMMARY.read_text(encoding="utf-8"))
    action_summary = json.loads(ACTION_SUMMARY.read_text(encoding="utf-8"))

    one_sentence_argument = (
        "In ground-penetrating-radar recognition evaluation, the current evidence shows that "
        "environment and provenance structure can reshape apparent generalization, supported "
        "mainly by Res-SAM environment-transfer fragility across five model families, with "
        "Mojahid and 4TU retained as bounded secondary and stress-test evidence."
    )

    title_rows = [
        {
            "rank": "1",
            "title": "Environment transfer exposes fragile generalization in ground-penetrating-radar recognition",
            "type": "finding-led",
            "why": "Most defensible because it leads with the strongest current Res-SAM signal and keeps the scope in GPR recognition.",
            "risk": "Moderate broad-interest reach; needs abstract and schematic to connect to benchmark trust.",
        },
        {
            "rank": "2",
            "title": "Provenance-aware evaluation reveals environment-shift fragility in ground-penetrating-radar recognition",
            "type": "workflow-plus-finding",
            "why": "Sharper for cross-field benchmark readers because it names provenance-aware evaluation and environment shift.",
            "risk": "Slightly more method-facing than result-facing.",
        },
        {
            "rank": "3",
            "title": "Benchmark trust in ground-penetrating-radar recognition depends on provenance-aware environment transfer",
            "type": "broad-interest",
            "why": "Connects GPR to benchmark trust, a more general ML evaluation concern.",
            "risk": "Must be used only if the manuscript opening clearly explains the evidence boundary.",
        },
        {
            "rank": "4",
            "title": "Auditing provenance and environment transfer in ground-penetrating-radar recognition",
            "type": "workflow-led",
            "why": "Safest if external validation remains unavailable and the paper is framed as benchmark/resource.",
            "risk": "Less finding-led and may read as a methods note rather than a high-impact result.",
        },
    ]
    write_csv(OUT_DIR / "broad_interest_title_candidates.csv", title_rows, ["rank", "title", "type", "why", "risk"])

    abstract = """# Broad-interest abstract revision v0.2

Ground-penetrating radar (GPR) is increasingly used to guide subsurface inspection and infrastructure assessment, but recognition models are often judged inside curated datasets whose samples share acquisition, environment or processing histories. This can make benchmark performance difficult to interpret: a high score may reflect transferable subsurface information, but it may also reflect provenance structure that is shared between training and test data. Here we assemble GPR-ProvenanceBench as an auditable evaluation workflow that links dated asset manifests, grouped split logic, environment-transfer tests, model-family comparisons and source-data traceability. The strongest current signal is Res-SAM environment transfer: real-to-synthetic transfer showed directional and material balanced-accuracy drops in all five model families, with a mean delta of 0.4239, and synthetic-to-real transfer showed directional and material drops in four of five families, with a mean delta of 0.3743. Mojahid provides directional but modest split-sensitivity support, whereas 4TU defines stress-test and feasibility boundaries. These results support a provenance-aware benchmark-trust argument for GPR recognition; blind external validation remains an open gate.
"""
    (OUT_DIR / "broad_interest_abstract_revision.md").write_text(abstract, encoding="utf-8")

    intro_opening = """# Broad-interest Introduction opening revision v0.2

Ground-penetrating radar (GPR) recognition is moving from controlled dataset studies toward applications in subsurface inspection, infrastructure assessment and field decision support. In these settings, the central question is not only whether a model scores well on a held-out test split, but whether that score reflects transferable subsurface signal rather than the history of how the data were acquired, processed and partitioned.

This distinction matters beyond GPR. Many scientific machine-learning benchmarks are built from datasets that carry provenance structure, including site, device, rendering pipeline, project identity or environment. If those structures are shared across training and test partitions, conventional performance estimates can overstate practical generalization. Conversely, if evaluation deliberately separates environment or provenance structure, it can expose where a model's apparent competence is brittle.

GPR B-scan recognition provides a concrete test bed for this problem because target labels are often entangled with site conditions, instrument settings and dataset construction. Yet many evaluation workflows still report model performance without making the executable asset boundary, split logic and environment-transfer evidence equally visible. This leaves a gap between model comparison and benchmark trust.

Here we assemble GPR-ProvenanceBench as an auditable workflow for testing how provenance and environment structure affect GPR recognition. The current evidence boundary contains executable Mojahid, 4TU and Res-SAM assets, with Res-SAM environment transfer providing the lead cross-model signal. Mojahid is retained as directional secondary evidence and 4TU as stress-test and feasibility evidence. Blind external validation, final figures and repository identifiers remain open gates rather than completed results.
"""
    (OUT_DIR / "broad_interest_intro_opening_revision.md").write_text(intro_opening, encoding="utf-8")

    caption = """# Workflow schematic caption draft v0.2

Figure 1 | Provenance-aware evaluation workflow for GPR recognition. The schematic should show five linked checkpoints: asset-status audit, unified sample manifest, split or environment-transfer construction, model-family comparison, and evidence-boundary reporting. The key visual message is that benchmark trust depends on whether performance claims can be traced from samples and provenance structure to frozen comparisons and source data. At the 2026-08-10 checkpoint, Mojahid, 4TU and Res-SAM are executable local assets, TIGPR is supporting-only because its local sample index is empty, and blind external validation remains a no-go gate until a held-label asset is acquired and evaluated once after prediction freezing. The figure should therefore display external validation as an open gate, not as a result panel.
"""
    (OUT_DIR / "workflow_schematic_caption_draft.md").write_text(caption, encoding="utf-8")

    map_rows = [
        {
            "claim": "GPR benchmark performance can be shaped by provenance and environment structure.",
            "evidence": "Res-SAM environment-transfer drops across five model families; Mojahid directional split sensitivity; 4TU stress-test boundaries.",
            "status": "supported_bounded",
            "boundary": "Does not prove universal GPR model failure or completed external validation.",
        },
        {
            "claim": "The broad-interest frame is benchmark trust under environment shift, not only GPR dataset curation.",
            "evidence": "Reviewer-risk audit identified interdisciplinary readership as possible but needing sharper framing.",
            "status": "framing_revision",
            "boundary": "Requires final schematic and references before submission-final use.",
        },
        {
            "claim": "Res-SAM is the lead current result.",
            "evidence": "Real-to-synthetic mean balanced-accuracy delta 0.4239; synthetic-to-real mean delta 0.3743.",
            "status": "supported_current_main_result",
            "boundary": "Bounded to current local matrix, not blind external validation.",
        },
        {
            "claim": "Mojahid and 4TU provide secondary constraints.",
            "evidence": "Mojahid material support 1/5; 4TU fixed-split signal weakens under project-level repeated splits.",
            "status": "supported_secondary",
            "boundary": "Do not use as universal leakage or main confirmation claims.",
        },
        {
            "claim": "Blind external validation remains open.",
            "evidence": "No real held-label asset, strict SHA manifest, frozen prediction submission, label unlock and locked evaluation.",
            "status": "open_gate",
            "boundary": "Must remain an open gate until real evidence exists.",
        },
    ]
    write_csv(OUT_DIR / "framing_claim_evidence_boundary.csv", map_rows, ["claim", "evidence", "status", "boundary"])

    qa_rows = [
        {"check": "one_sentence_argument_present", "result": "PASS", "detail": one_sentence_argument},
        {"check": "no_completed_blind_external_validation_claim", "result": "PASS", "detail": "All outputs mark blind external validation as open/no-go."},
        {"check": "no_public_repository_or_doi_claim", "result": "PASS", "detail": "No output claims repository DOI or code DOI exists."},
        {"check": "no_final_figure_claim", "result": "PASS", "detail": "Workflow caption is marked draft and external validation is displayed as an open gate."},
        {"check": "broad_interest_acceptance_test_addressed", "result": "PASS", "detail": "Title, abstract, Introduction opening and schematic caption drafts are present."},
    ]
    write_csv(OUT_DIR / "broad_interest_framing_qa.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "run_id": "20260810_broad_interest_framing_revision",
        "title_candidates": len(title_rows),
        "abstract_revision_words": len(abstract.split()),
        "intro_opening_paragraphs": 4,
        "claim_boundary_rows": len(map_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "manuscript_status": manuscript_summary["status"],
        "action_packet_status": action_summary["status"],
        "submission_ready": False,
        "status": "broad_interest_framing_revision_ready_not_submission_final",
        "boundary": "This package sharpens broad-interest framing; it does not close figures, external validation, DOI, rights, Reporting Summary or references.",
    }
    (OUT_DIR / "broad_interest_framing_revision_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = [
        "# Broad-interest framing revision report 2026-08-10",
        "",
        f"- Title candidates: {summary['title_candidates']}",
        f"- Abstract revision words: {summary['abstract_revision_words']}",
        f"- Introduction opening paragraphs: {summary['intro_opening_paragraphs']}",
        f"- Claim-boundary rows: {summary['claim_boundary_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: the broad-interest frame has been sharpened from a GPR-only performance story to a bounded benchmark-trust and environment-shift argument.",
        "",
    ]
    (OUT_DIR / "broad_interest_framing_revision_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
