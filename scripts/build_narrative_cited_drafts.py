#!/usr/bin/env python3
"""Build citation-tagged v1 narrative drafts from v0 drafts and citation mapping."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
V0_DIR = BENCH_ROOT / "reports" / "narrative_section_drafts_20260810"
CITATION_DIR = BENCH_ROOT / "reports" / "narrative_citation_pass_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "narrative_cited_drafts_20260810"


SECTION_FILES = {
    "Introduction": "introduction_draft_v0.md",
    "Discussion": "discussion_draft_v0.md",
    "Conclusion": "conclusion_draft_v0.md",
}


CITATION_INSERTIONS = [
    {
        "insertion_id": "CI001",
        "section": "Introduction",
        "segment_ids": "S001",
        "candidate_ids": "P1",
        "support_grade": "strong background support",
        "find": "Ground-penetrating radar (GPR) is increasingly used to support non-destructive inspection, subsurface mapping and infrastructure assessment, where recognition models are expected to work beyond a single curated image collection.",
        "replace": "Ground-penetrating radar (GPR) is increasingly used to support non-destructive inspection, subsurface mapping and infrastructure assessment, where recognition models are expected to work beyond a single curated image collection [P1].",
        "status": "inserted_candidate_marker",
        "boundary": "P1 supports GPR/Res-SAM context; broader application scope may still need field-specific non-CNS citations.",
    },
    {
        "insertion_id": "CI002",
        "section": "Introduction",
        "segment_ids": "S001",
        "candidate_ids": "P1",
        "support_grade": "strong background support",
        "find": "This distinction is especially important for GPR B-scan recognition, because nominally similar images can be shaped by site conditions, instrument settings, rendering choices and dataset construction. [Citation needed: broad GPR recognition and non-destructive inspection context.]",
        "replace": "This distinction is especially important for GPR B-scan recognition, because nominally similar images can be shaped by site conditions, instrument settings, rendering choices and dataset construction [P1].",
        "status": "placeholder_resolved_to_candidate_marker",
        "boundary": "The marker is candidate placement, not final formatted citation.",
    },
    {
        "insertion_id": "CI003",
        "section": "Introduction",
        "segment_ids": "S002;S003",
        "candidate_ids": "P4;P5;P6",
        "support_grade": "partial to strong support",
        "find": "A central evaluation bottleneck is that common random or weakly structured splits can mix samples that share provenance structure across training and test partitions.",
        "replace": "A central evaluation bottleneck is that common random or weakly structured splits can mix samples that share provenance structure across training and test partitions [P4,P5].",
        "status": "inserted_candidate_marker",
        "boundary": "P4/P5 support leakage and splitting risks; P6 is not inserted here because it is only acquisition-shift background.",
    },
    {
        "insertion_id": "CI004",
        "section": "Introduction",
        "segment_ids": "S003;S004",
        "candidate_ids": "P4;P5;P2",
        "support_grade": "partial to strong support",
        "find": "A benchmark intended to support generalization claims therefore needs to audit executable assets, split construction and environment transfer explicitly. [Citation needed: evaluation leakage, grouped split and dataset provenance literature.]",
        "replace": "A benchmark intended to support generalization claims therefore needs to audit executable assets, split construction and environment transfer explicitly [P2,P4,P5].",
        "status": "placeholder_resolved_to_candidate_marker",
        "boundary": "External blind validation remains an internal protocol gate; this citation cluster supports evaluation rationale only.",
    },
    {
        "insertion_id": "CI005",
        "section": "Discussion",
        "segment_ids": "S005;S007",
        "candidate_ids": "P1",
        "support_grade": "background support",
        "find": "This result shows a reproducible performance collapse under a specific environment shift and suggests that internal accuracy alone is an incomplete proxy for field-facing generalization.",
        "replace": "This result shows a reproducible performance collapse under a specific environment shift and suggests that internal accuracy alone is an incomplete proxy for field-facing generalization [internal Figure 2/Table 2; P1 for GPR context only].",
        "status": "inserted_internal_plus_context_marker",
        "boundary": "The measured deltas must cite internal source data, not P1.",
    },
    {
        "insertion_id": "CI006",
        "section": "Discussion",
        "segment_ids": "S006",
        "candidate_ids": "P2;P3;P5",
        "support_grade": "partial support",
        "find": "These constraints are not incidental limitations; they are part of the evidence for why provenance-aware GPR evaluation must report asset feasibility alongside performance.",
        "replace": "These constraints are not incidental limitations; they are part of the evidence for why provenance-aware GPR evaluation must report asset feasibility alongside performance [P2,P3,P5].",
        "status": "inserted_candidate_marker",
        "boundary": "Conceptual support only; P3 is non-GPR medical-AI shortcut-testing context.",
    },
    {
        "insertion_id": "CI007",
        "section": "Discussion",
        "segment_ids": "S008",
        "candidate_ids": "internal_artifacts",
        "support_grade": "internal evidence needed",
        "find": "The source-data deposit and sanitized release staging previews also make the future public-release work explicit.",
        "replace": "The source-data deposit and sanitized release staging previews also make the future public-release work explicit [internal source-data deposit and release-readiness artifacts].",
        "status": "inserted_internal_marker",
        "boundary": "Do not cite literature for a repository/release claim before DOI and rights are closed.",
    },
    {
        "insertion_id": "CI008",
        "section": "Conclusion",
        "segment_ids": "S009",
        "candidate_ids": "P1;P4;P5",
        "support_grade": "partial support",
        "find": "The narrow implication is that provenance-aware evaluation should precede broad claims of GPR model generalization; the final submission case still depends on blind external validation, rendered figures, repository identifiers and public-release rights being closed.",
        "replace": "The narrow implication is that provenance-aware evaluation should precede broad claims of GPR model generalization [P1,P4,P5]; the final submission case still depends on blind external validation, rendered figures, repository identifiers and public-release rights being closed.",
        "status": "inserted_candidate_marker",
        "boundary": "Conclusion still preserves the NO-GO external-validation gate.",
    },
]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def count_words(text: str) -> int:
    return len([token for token in text.replace("\n", " ").split(" ") if token.strip()])


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    citation_mapping = CITATION_DIR / "narrative_citation_mapping.csv"
    if not citation_mapping.exists():
        raise FileNotFoundError(citation_mapping)

    section_texts = {section: read_text(V0_DIR / filename) for section, filename in SECTION_FILES.items()}
    audit_rows: list[dict[str, str]] = []
    for insertion in CITATION_INSERTIONS:
        section = insertion["section"]
        source = insertion["find"]
        target = insertion["replace"]
        before = section_texts[section]
        hits = before.count(source)
        if hits != 1:
            raise ValueError(f"{insertion['insertion_id']} expected one match in {section}, found {hits}")
        section_texts[section] = before.replace(source, target)
        audit_rows.append(
            {
                "insertion_id": insertion["insertion_id"],
                "section": section,
                "segment_ids": insertion["segment_ids"],
                "candidate_ids": insertion["candidate_ids"],
                "support_grade": insertion["support_grade"],
                "status": insertion["status"],
                "boundary": insertion["boundary"],
            }
        )

    output_files = {
        "Introduction": OUT_DIR / "introduction_draft_v1_cited.md",
        "Discussion": OUT_DIR / "discussion_draft_v1_cited.md",
        "Conclusion": OUT_DIR / "conclusion_draft_v1_cited.md",
    }
    for section, path in output_files.items():
        section_texts[section] = section_texts[section].replace(f"# {section} Draft v0", f"# {section} Draft v1 cited")
        path.write_text(section_texts[section], encoding="utf-8")

    combined_parts = [
        "# Narrative Section Drafts v1 with Candidate Citation Markers 2026-08-10",
        "",
        "## Drafting Boundary",
        "",
        "These sections use candidate citation markers such as `[P1]` and internal source-data markers. They are not final Nature Communications numbered references, and they do not close blind external validation, repository DOI, Reporting Summary, figure numbering or public-release gates.",
        "",
    ]
    for section in ["Introduction", "Discussion", "Conclusion"]:
        combined_parts.append(section_texts[section])
        combined_parts.append("")
    combined = "\n".join(combined_parts)
    (OUT_DIR / "narrative_section_drafts_v1_cited.md").write_text(combined, encoding="utf-8")

    write_csv(
        OUT_DIR / "citation_insertion_audit.csv",
        audit_rows,
        ["insertion_id", "section", "segment_ids", "candidate_ids", "support_grade", "status", "boundary"],
    )

    unresolved_rows = [
        {
            "unresolved_id": "U001",
            "item": "final_reference_numbering",
            "status": "open",
            "required_action": "Convert candidate markers to final numbered references after final prose and journal style are locked.",
        },
        {
            "unresolved_id": "U002",
            "item": "figure_table_pointer",
            "status": "open",
            "required_action": "Replace pending figure/table pointer after rendered figures, table order and Source Data mapping are locked.",
        },
        {
            "unresolved_id": "U003",
            "item": "internal_metric_citations",
            "status": "open",
            "required_action": "Attach internal source-data citations for Res-SAM, Mojahid and 4TU metrics; do not use literature papers as metric evidence.",
        },
        {
            "unresolved_id": "U004",
            "item": "repository_and_release_claims",
            "status": "open",
            "required_action": "Wait for repository DOI/accession, code release DOI, licence and rights review before writing release claims as completed.",
        },
    ]
    write_csv(OUT_DIR / "unresolved_citation_and_pointer_items.csv", unresolved_rows, ["unresolved_id", "item", "status", "required_action"])

    placeholders_remaining = combined.count("[Citation needed:")
    figure_pointer_placeholders = combined.count("[Figure/Table pointer pending:")
    candidate_markers = sum(combined.count(marker) for marker in ["[P1]", "[P2", "[P4", "[P1,P4", "[P2,P4", "[P4,P5", "[P1,P4,P5]"])
    internal_markers = combined.count("[internal")
    summary = {
        "run_id": "20260810_narrative_cited_drafts_v1",
        "sections": list(SECTION_FILES.keys()),
        "insertions": len(audit_rows),
        "citation_placeholders_remaining": placeholders_remaining,
        "figure_table_placeholders_remaining": figure_pointer_placeholders,
        "internal_markers": internal_markers,
        "combined_words": count_words(combined),
        "status": "candidate_citation_markers_inserted_not_final_references",
        "manuscript_ready": False,
        "boundary": "Candidate citation markers only; final prose, numbered references, figure/table pointers and repository identifiers remain open.",
    }
    (OUT_DIR / "narrative_cited_drafts_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Narrative cited drafts v1 2026-08-10",
        "",
        "This package converts the v0 citation placeholders into conservative candidate citation markers while preserving internal-evidence and open-gate boundaries.",
        "",
        "## Outputs",
        "",
        "1. `introduction_draft_v1_cited.md`",
        "2. `discussion_draft_v1_cited.md`",
        "3. `conclusion_draft_v1_cited.md`",
        "4. `narrative_section_drafts_v1_cited.md`",
        "5. `citation_insertion_audit.csv`",
        "6. `unresolved_citation_and_pointer_items.csv`",
        "7. `narrative_cited_drafts_summary.json`",
        "",
        "## Current Status",
        "",
        f"- Citation insertions: {summary['insertions']}",
        f"- Citation placeholders remaining: {summary['citation_placeholders_remaining']}",
        f"- Figure/table placeholders remaining: {summary['figure_table_placeholders_remaining']}",
        f"- Internal source-data markers: {summary['internal_markers']}",
        "",
        "## Guardrail",
        "",
        "The `[P#]` markers are candidate citation anchors, not final Nature Communications numbered references. Internal experimental metrics still require figure/table source-data citations.",
        "",
    ]
    (OUT_DIR / "narrative_cited_drafts_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
