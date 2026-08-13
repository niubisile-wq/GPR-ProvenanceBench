#!/usr/bin/env python3
"""Build bounded English v0 drafts for narrative manuscript sections."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "narrative_section_drafts_20260810"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    intro_contracts = read_csv(
        BENCH_ROOT
        / "reports"
        / "narrative_section_skeleton_20260810"
        / "introduction_paragraph_contracts.csv"
    )
    discussion_contracts = read_csv(
        BENCH_ROOT
        / "reports"
        / "narrative_section_skeleton_20260810"
        / "discussion_paragraph_contracts.csv"
    )
    conclusion_contracts = read_csv(
        BENCH_ROOT
        / "reports"
        / "narrative_section_skeleton_20260810"
        / "conclusion_paragraph_contracts.csv"
    )
    risk_rows = read_csv(
        BENCH_ROOT
        / "reports"
        / "narrative_section_skeleton_20260810"
        / "narrative_claim_evidence_risk_map.csv"
    )

    drafts = [
        {
            "section": "Introduction",
            "paragraph_id": "I1",
            "paragraph_job": "field scale",
            "draft_text": (
                "Ground-penetrating radar (GPR) is increasingly used to support non-destructive inspection, "
                "subsurface mapping and infrastructure assessment, where recognition models are expected to "
                "work beyond a single curated image collection. For such models, high internal test performance "
                "is useful only if it reflects transferable subsurface information rather than acquisition-, "
                "environment- or processing-specific regularities. This distinction is especially important for "
                "GPR B-scan recognition, because nominally similar images can be shaped by site conditions, "
                "instrument settings, rendering choices and dataset construction. [Citation needed: broad GPR "
                "recognition and non-destructive inspection context.]"
            ),
        },
        {
            "section": "Introduction",
            "paragraph_id": "I2",
            "paragraph_job": "bottleneck",
            "draft_text": (
                "A central evaluation bottleneck is that common random or weakly structured splits can mix "
                "samples that share provenance structure across training and test partitions. When acquisition "
                "setting, environment, project identity or processing chain is correlated with the target label, "
                "a model may appear to generalize while partly exploiting these non-target cues. The problem is "
                "not that every GPR model is invalid, but that conventional split protocols can make it difficult "
                "to separate target recognition from provenance sensitivity. A benchmark intended to support "
                "generalization claims therefore needs to audit executable assets, split construction and "
                "environment transfer explicitly. [Citation needed: evaluation leakage, grouped split and "
                "dataset provenance literature.]"
            ),
        },
        {
            "section": "Introduction",
            "paragraph_id": "I3",
            "paragraph_job": "prior gap",
            "draft_text": (
                "Existing GPR recognition studies often report model performance within individual datasets, "
                "but fewer workflows make the evidence boundary executable: which assets can be regenerated, "
                "which labels support grouped evaluation, which model families agree, and which results survive "
                "environment or project-level stress tests. This leaves an unresolved gap between model "
                "comparison and provenance-aware validation. In particular, a claim that a model generalizes "
                "across GPR settings should be supported by dated manifests, reproducible split logic, "
                "model-family-level checks and, ultimately, blind external validation with labels withheld until "
                "predictions are frozen."
            ),
        },
        {
            "section": "Introduction",
            "paragraph_id": "I4",
            "paragraph_job": "present study",
            "draft_text": (
                "Here we assemble GPR-ProvenanceBench as an auditable workflow for testing how provenance and "
                "environment structure affect GPR recognition. At the current checkpoint, the executable local "
                "evidence includes Mojahid, Res-SAM and 4TU assets, five lightweight model-family comparisons "
                "for Mojahid and Res-SAM, and raw-trace-derived 4TU stress tests. The strongest current result is "
                "the Res-SAM environment transfer drop across model families; Mojahid provides directional but "
                "modest split-sensitivity evidence, and 4TU provides stress-test and feasibility boundaries. "
                "Blind external validation remains an open gate rather than a completed result. [Figure/Table "
                "pointer pending: Figure 1, Figure 2, Table 1 and Table 2.]"
            ),
        },
        {
            "section": "Discussion",
            "paragraph_id": "D1",
            "paragraph_job": "central advance",
            "draft_text": (
                "The central observation from the current executable evidence is that environment and provenance "
                "structure can substantially reshape apparent GPR recognition performance. The Res-SAM "
                "real-world/synthetic environment-transfer contrasts show the strongest support for this point: "
                "the transfer drop is present across multiple model families and is larger than the Mojahid "
                "random-minus-grouped contrast. This result shows a reproducible performance collapse under a "
                "specific environment shift and suggests that internal accuracy alone is an incomplete proxy for "
                "field-facing generalization."
            ),
        },
        {
            "section": "Discussion",
            "paragraph_id": "D2",
            "paragraph_job": "meaning of secondary evidence",
            "draft_text": (
                "The secondary evidence layers sharpen rather than replace this main conclusion. Mojahid shows a "
                "directionally consistent random-minus-grouped split gap, but only one of five model families "
                "reaches the predeclared material-support threshold, so it should be interpreted as modest and "
                "model-dependent split sensitivity. The 4TU experiments show that raw-trace-derived "
                "counterfactual variants can strongly disrupt fixed-split predictions, but the same signal "
                "weakens under project-level repeated splits. Together, these results support a benchmark "
                "argument about evaluation fragility, not a universal claim that all GPR recognition results are "
                "driven by leakage."
            ),
        },
        {
            "section": "Discussion",
            "paragraph_id": "D3",
            "paragraph_job": "rival explanations",
            "draft_text": (
                "Several rival explanations constrain the interpretation. First, the TinyCNN results indicate "
                "that provenance effects can depend on model family, so a single architecture cannot define the "
                "claim. Second, the 4TU group-aware weakening may reflect limited project counts and imbalanced "
                "metadata labels rather than the absence of processing sensitivity. Third, the current 4TU target "
                "audit shows that only some labels can support grouped holdouts with useful coverage. These "
                "constraints are not incidental limitations; they are part of the evidence for why provenance-aware "
                "GPR evaluation must report asset feasibility alongside performance."
            ),
        },
        {
            "section": "Discussion",
            "paragraph_id": "D4",
            "paragraph_job": "reuse and reproducibility",
            "draft_text": (
                "A practical contribution of the current package is the separation of executable evidence from "
                "nominal dataset availability. Dated manifests, source-data packages, Results and Methods "
                "skeletons, manuscript assembly files and the M0-M2 check script create a reproducible audit path "
                "for the current checkpoint. The source-data deposit and sanitized release staging previews also "
                "make the future public-release work explicit. However, these previews are internal release "
                "candidates; they are not a public repository, do not provide persistent identifiers and do not "
                "resolve third-party redistribution rights."
            ),
        },
        {
            "section": "Discussion",
            "paragraph_id": "D5",
            "paragraph_job": "limitations and open gates",
            "draft_text": (
                "The manuscript is therefore not submission-ready. The most important missing evidence is a real "
                "blind external validation asset that is unused during development, hash-frozen, label-held and "
                "evaluated once after prediction freezing. In addition, the main figures have not been rendered, "
                "the Data Availability and Code Availability statements lack repository identifiers, the Reporting "
                "Summary still requires final answers, and third-party data rights are not cleared for public "
                "release. These are blocking items rather than cosmetic production tasks, because they determine "
                "whether the central generalization claim can be evaluated independently."
            ),
        },
        {
            "section": "Conclusion",
            "paragraph_id": "C1",
            "paragraph_job": "contribution",
            "draft_text": (
                "GPR-ProvenanceBench turns provenance-aware GPR evaluation into an auditable workflow by linking "
                "asset status, split construction, model-family comparisons, stress tests, source-data mapping and "
                "dated regeneration checks."
            ),
        },
        {
            "section": "Conclusion",
            "paragraph_id": "C2",
            "paragraph_job": "decisive current evidence",
            "draft_text": (
                "At this checkpoint, Res-SAM environment transfer provides the strongest cross-model evidence "
                "that apparent GPR generalization can be brittle, whereas Mojahid and 4TU provide bounded "
                "directional and stress-test support."
            ),
        },
        {
            "section": "Conclusion",
            "paragraph_id": "C3",
            "paragraph_job": "implication and boundary",
            "draft_text": (
                "The narrow implication is that provenance-aware evaluation should precede broad claims of GPR "
                "model generalization; the final submission case still depends on blind external validation, "
                "rendered figures, repository identifiers and public-release rights being closed."
            ),
        },
    ]

    contract_lookup = {}
    for row in intro_contracts + discussion_contracts + conclusion_contracts:
        contract_lookup[row["paragraph_id"]] = row

    draft_rows = []
    for row in drafts:
        contract = contract_lookup[row["paragraph_id"]]
        text = row["draft_text"]
        draft_rows.append(
            {
                "section": row["section"],
                "paragraph_id": row["paragraph_id"],
                "paragraph_job": row["paragraph_job"],
                "word_count": word_count(text),
                "target_words": contract.get("target_words", ""),
                "evidence_anchor": contract.get("evidence_anchor", ""),
                "draft_text": text,
            }
        )

    full_sections: dict[str, list[str]] = {"Introduction": [], "Discussion": [], "Conclusion": []}
    for row in drafts:
        full_sections[row["section"]].append(row["draft_text"])

    risky_hits = []
    full_text = "\n\n".join(row["draft_text"] for row in drafts)
    for risk in risk_rows:
        for term in [part.strip() for part in risk["trigger_terms"].split(";")]:
            if term and term.lower() in full_text.lower():
                risky_hits.append(
                    {
                        "risk_id": risk["risk_id"],
                        "risk": risk["risk"],
                        "trigger_term": term,
                        "status": "hit",
                        "required_replacement": risk["required_replacement"],
                    }
                )

    if not risky_hits:
        risky_hits.append(
            {
                "risk_id": "none",
                "risk": "No exact trigger terms from narrative risk map were found.",
                "trigger_term": "",
                "status": "pass",
                "required_replacement": "",
            }
        )

    write_csv(OUT_DIR / "narrative_section_draft_paragraphs.csv", draft_rows)
    write_csv(OUT_DIR / "narrative_overclaim_scan.csv", risky_hits)

    intro_md = "# Introduction Draft v0\n\n" + "\n\n".join(full_sections["Introduction"]) + "\n"
    discussion_md = "# Discussion Draft v0\n\n" + "\n\n".join(full_sections["Discussion"]) + "\n"
    conclusion_md = "# Conclusion Draft v0\n\n" + "\n\n".join(full_sections["Conclusion"]) + "\n"
    combined_md = (
        "# Narrative Section Drafts v0 2026-08-10\n\n"
        "## Drafting Boundary\n\n"
        "These sections are bounded v0 prose. They contain citation placeholders and pending figure/table pointers, "
        "and they do not close blind external validation, data/code DOI, Reporting Summary, final figure or public-release gates.\n\n"
        + intro_md
        + "\n"
        + discussion_md
        + "\n"
        + conclusion_md
    )

    (OUT_DIR / "introduction_draft_v0.md").write_text(intro_md, encoding="utf-8")
    (OUT_DIR / "discussion_draft_v0.md").write_text(discussion_md, encoding="utf-8")
    (OUT_DIR / "conclusion_draft_v0.md").write_text(conclusion_md, encoding="utf-8")
    (OUT_DIR / "narrative_section_drafts_v0.md").write_text(combined_md, encoding="utf-8")

    total_words = sum(row["word_count"] for row in draft_rows)
    summary = {
        "run_id": "20260810_narrative_section_drafts_v0",
        "paragraphs": len(draft_rows),
        "sections": ["Introduction", "Discussion", "Conclusion"],
        "total_words": total_words,
        "citation_placeholders": full_text.count("[Citation needed:"),
        "figure_table_placeholders": full_text.count("[Figure/Table pointer pending"),
        "overclaim_scan_status": "PASS" if risky_hits[0]["status"] == "pass" else "REVIEW",
        "manuscript_ready": False,
        "boundary": "V0 prose only; citations, final figure calls, repository identifiers and blind external validation remain open.",
    }
    (OUT_DIR / "narrative_section_drafts_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
