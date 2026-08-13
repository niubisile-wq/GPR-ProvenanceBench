#!/usr/bin/env python3
"""Lock planned figure/table/source-data anchors before rendering figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAPPING = BENCH_ROOT / "reports" / "source_data_deposit_package_20260810" / "figure_table_source_mapping.csv"
FIGURE_PLAN = BENCH_ROOT / "reports" / "manuscript_figure_table_plan_20260810" / "figure_table_claim_evidence_map.csv"
CITED_DIR = BENCH_ROOT / "reports" / "narrative_cited_drafts_20260810"
OUT_DIR = BENCH_ROOT / "reports" / "figure_table_anchor_lock_20260810"


DISPLAY_ORDER = [
    ("Figure 1", "Fig. 1", "main_figure"),
    ("Table 1", "Table 1", "main_table"),
    ("Figure 2", "Fig. 2", "main_figure"),
    ("Table 2", "Table 2", "main_table"),
    ("Figure 3", "Fig. 3", "secondary_or_extended_figure"),
    ("Figure 4", "Fig. 4", "stress_test_figure"),
    ("Figure 5", "Fig. 5", "feasibility_or_extended_figure"),
    ("Figure 6", "Fig. 6", "open_gate_placeholder"),
    ("Table 3", "Table 3", "internal_or_supplement_table"),
]


NARRATIVE_POINTERS = [
    {
        "pointer_id": "NP001",
        "section": "Introduction",
        "old_text": "[Figure/Table pointer pending: Figure 1, Figure 2, Table 1 and Table 2.]",
        "new_text": "[planned Fig. 1, planned Fig. 2, Table 1 and Table 2; final numbering pending rendering].",
        "resolved_to": "Figure 1;Figure 2;Table 1;Table 2",
        "status": "placeholder_resolved_to_planned_anchor",
        "boundary": "Planned anchors only; final numbering remains pending until rendered figures are locked.",
    },
    {
        "pointer_id": "NP002",
        "section": "Discussion",
        "old_text": "[internal Figure 2/Table 2; P1 for GPR context only]",
        "new_text": "[planned Fig. 2 and Table 2 source data; P1 for GPR context only]",
        "resolved_to": "Figure 2;Table 2",
        "status": "internal_metric_anchor_refined",
        "boundary": "Internal metrics must be supported by source-data files, not by P1.",
    },
    {
        "pointer_id": "NP003",
        "section": "Discussion",
        "old_text": "[internal source-data deposit and release-readiness artifacts]",
        "new_text": "[source-data deposit and release-readiness artifacts; not a public repository]",
        "resolved_to": "Source data deposit package;Release readiness audit",
        "status": "internal_release_anchor_refined",
        "boundary": "Release-readiness statements remain internal until DOI, licence and rights checks close.",
    },
]


INTERNAL_METRIC_CITATIONS = [
    {
        "claim_id": "IM001",
        "claim": "Res-SAM environment-transfer drop is the strongest current cross-model signal.",
        "planned_anchor": "Figure 2;Table 2",
        "source_data_files": "reports/figure2_table2_sources_20260810/figure2_source_data.csv; reports/figure2_table2_sources_20260810/table2_model_family_support.csv",
        "citation_rule": "Use source-data anchor for measured deltas; cite P1 only for GPR/Res-SAM context.",
        "status": "source_data_anchor_ready_not_rendered",
    },
    {
        "claim_id": "IM002",
        "claim": "Mojahid split sensitivity is directional only and model-dependent.",
        "planned_anchor": "Figure 3;Table 2",
        "source_data_files": "reports/figure3_sources_20260810/figure3_model_delta_source_data.csv; reports/figure2_table2_sources_20260810/table2_model_family_support.csv",
        "citation_rule": "Use Figure 3/Table 2 anchors; do not cite as universal leakage.",
        "status": "source_data_anchor_ready_not_rendered",
    },
    {
        "claim_id": "IM003",
        "claim": "4TU multi-layer counterfactual stress-test evidence remains a feasibility-boundary layer rather than main confirmation.",
        "planned_anchor": "Figure 4;Figure 5",
        "source_data_files": "reports/figure4_sources_20260810/figure4_counterfactual_source_data.csv; reports/figure4_sources_20260810/figure4_evidence_layer_boundary.csv; reports/figure5_figure6_sources_20260810/figure5_4tu_feasibility_source_data.csv",
        "citation_rule": "Use stress-test and feasibility anchors; do not frame as causal proof, main confirmation or blind external validation.",
        "status": "source_data_anchor_ready_not_rendered",
    },
    {
        "claim_id": "IM004",
        "claim": "Blind external validation remains unavailable under the frozen protocol.",
        "planned_anchor": "Figure 6;Table 3",
        "source_data_files": "reports/figure5_figure6_sources_20260810/figure6_external_gate_source_data.csv; reports/external_validation_readiness_20260810/external_validation_readiness_tracks.csv",
        "citation_rule": "Use open-gate anchor only; do not report template dry-run as a real external result.",
        "status": "gate_anchor_ready_not_result",
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


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_rows = read_csv(SOURCE_MAPPING)
    plan_rows = read_csv(FIGURE_PLAN)
    source_lookup = {row["item_id"]: row for row in source_rows}
    plan_lookup = {row["item_id"]: row for row in plan_rows}

    numbering_rows: list[dict[str, str]] = []
    source_anchor_rows: list[dict[str, str]] = []
    for order, (item_id, citation_label, anchor_class) in enumerate(DISPLAY_ORDER, start=1):
        plan = plan_lookup[item_id]
        source = source_lookup[item_id]
        numbering_rows.append(
            {
                "display_order": str(order),
                "item_id": item_id,
                "citation_label": citation_label,
                "anchor_class": anchor_class,
                "role": plan["role"],
                "status": source["status"],
                "rendered_artifact_status": source["rendered_artifact_status"],
                "manuscript_use": "main_text" if item_id in {"Figure 1", "Figure 2", "Table 1", "Table 2"} else "secondary_or_supplement_pending",
                "boundary": source["boundary"],
            }
        )
        source_anchor_rows.append(
            {
                "item_id": item_id,
                "citation_label": citation_label,
                "claim": source["claim"],
                "source_files": source["source_files"],
                "rendered_artifact_status": source["rendered_artifact_status"],
                "source_data_anchor_status": "locked_to_source_files_not_rendered",
                "boundary": source["boundary"],
            }
        )

    combined_path = CITED_DIR / "narrative_section_drafts_v1_cited.md"
    combined = read_text(combined_path)
    pointer_rows: list[dict[str, str]] = []
    for pointer in NARRATIVE_POINTERS:
        hits = combined.count(pointer["old_text"])
        if hits != 1:
            raise ValueError(f"{pointer['pointer_id']} expected one match, found {hits}")
        combined = combined.replace(pointer["old_text"], pointer["new_text"])
        pointer_rows.append(pointer)

    anchored_path = OUT_DIR / "narrative_section_drafts_v1_anchored.md"
    anchored_path.write_text(combined, encoding="utf-8")

    write_csv(
        OUT_DIR / "figure_table_numbering_lock.csv",
        numbering_rows,
        ["display_order", "item_id", "citation_label", "anchor_class", "role", "status", "rendered_artifact_status", "manuscript_use", "boundary"],
    )
    write_csv(
        OUT_DIR / "source_data_anchor_map.csv",
        source_anchor_rows,
        ["item_id", "citation_label", "claim", "source_files", "rendered_artifact_status", "source_data_anchor_status", "boundary"],
    )
    write_csv(
        OUT_DIR / "narrative_pointer_resolution.csv",
        pointer_rows,
        ["pointer_id", "section", "old_text", "new_text", "resolved_to", "status", "boundary"],
    )
    write_csv(
        OUT_DIR / "internal_metric_citation_map.csv",
        INTERNAL_METRIC_CITATIONS,
        ["claim_id", "claim", "planned_anchor", "source_data_files", "citation_rule", "status"],
    )

    placeholders_remaining = combined.count("[Figure/Table pointer pending:")
    final_numbering_ready = all(row["rendered_artifact_status"] != "not_rendered_yet" for row in source_rows)
    summary = {
        "run_id": "20260810_figure_table_anchor_lock",
        "numbered_items": len(numbering_rows),
        "source_anchor_rows": len(source_anchor_rows),
        "narrative_pointer_resolutions": len(pointer_rows),
        "internal_metric_citation_rows": len(INTERNAL_METRIC_CITATIONS),
        "figure_table_placeholders_remaining": placeholders_remaining,
        "final_numbering_ready": final_numbering_ready,
        "status": "planned_anchors_locked_not_rendered",
        "manuscript_ready": False,
        "boundary": "Planned figure/table/source-data anchors are locked to current source files, but figures are not rendered and final numbering is not submission-ready.",
    }
    (OUT_DIR / "figure_table_anchor_lock_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Figure/table/source-data anchor lock 2026-08-10",
        "",
        "This package resolves narrative figure/table placeholders into planned anchors and maps internal metric claims to source-data files before figure rendering.",
        "",
        "## Outputs",
        "",
        "1. `figure_table_numbering_lock.csv`",
        "2. `source_data_anchor_map.csv`",
        "3. `narrative_pointer_resolution.csv`",
        "4. `internal_metric_citation_map.csv`",
        "5. `narrative_section_drafts_v1_anchored.md`",
        "6. `figure_table_anchor_lock_summary.json`",
        "",
        "## Current Status",
        "",
        f"- Numbered items: {summary['numbered_items']}",
        f"- Narrative pointer resolutions: {summary['narrative_pointer_resolutions']}",
        f"- Figure/table placeholders remaining: {summary['figure_table_placeholders_remaining']}",
        f"- Final numbering ready: {str(summary['final_numbering_ready']).lower()}",
        "",
        "## Guardrail",
        "",
        "These are planned anchors, not rendered final figures. Do not cite Fig. 6 as an external validation result and do not call release-staging artifacts a public repository.",
        "",
    ]
    (OUT_DIR / "figure_table_anchor_lock_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
