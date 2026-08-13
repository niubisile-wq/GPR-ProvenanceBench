#!/usr/bin/env python3
"""Build manuscript table drafts and captions from locked source data."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manuscript_table_drafts_20260810"
TABLE1_SOURCE = BENCH_ROOT / "reports" / "figure1_table1_sources_20260810" / "table1_asset_audit.csv"
TABLE2_SOURCE = BENCH_ROOT / "reports" / "figure2_table2_sources_20260810" / "table2_model_family_support.csv"
ANCHOR_SOURCE = BENCH_ROOT / "reports" / "figure_table_anchor_lock_20260810" / "figure_table_numbering_lock.csv"


TABLE3_ROWS = [
    {
        "gate": "External blind validation",
        "current_status": "NO-GO",
        "evidence_anchor": "Fig. 6; Table 3",
        "blocking_item": "No real advisor-held or third-party-held blind external asset has passed strict-SHA intake and locked main-claim evaluation.",
        "manuscript_rule": "Do not describe the template dry run as external validation.",
    },
    {
        "gate": "TIGPR local restoration",
        "current_status": "NO-GO for core executable asset",
        "evidence_anchor": "Table 1",
        "blocking_item": "Current local TIGPR unified manifest has 0 rows and no verified five-class source tree.",
        "manuscript_rule": "Treat TIGPR as supporting prior audit context only.",
    },
    {
        "gate": "4TU confirmation layer",
        "current_status": "Stress-test only",
        "evidence_anchor": "Fig. 4; Fig. 5",
        "blocking_item": "Project count and metadata label balance weaken group-aware confirmation.",
        "manuscript_rule": "Use 4TU for failure-mode and feasibility evidence, not as main confirmation.",
    },
    {
        "gate": "Full Res-SAM replication",
        "current_status": "Lightweight asset usable; full model not replicated",
        "evidence_anchor": "Table 1; Fig. 2",
        "blocking_item": "SAM ViT-L checkpoint/runtime is not locally reproduced.",
        "manuscript_rule": "Report current lightweight model-family evidence; do not claim full Res-SAM model replication.",
    },
    {
        "gate": "Data/code public release",
        "current_status": "Not ready",
        "evidence_anchor": "Source-data and release-readiness artifacts",
        "blocking_item": "Repository DOI, code DOI, licence selection and third-party redistribution rights are unresolved.",
        "manuscript_rule": "Do not write Data Availability or Code Availability as completed.",
    },
    {
        "gate": "Final figures and Source Data",
        "current_status": "Not rendered",
        "evidence_anchor": "Fig. 1-Fig. 6; Table 1-Table 3",
        "blocking_item": "Figures are not rendered and panel-level Source Data mapping is not final.",
        "manuscript_rule": "Use planned anchors only until figure rendering and visual QA are complete.",
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


def markdown_table(rows: list[dict[str, str]], headers: list[tuple[str, str]]) -> str:
    labels = [label for _, label in headers]
    keys = [key for key, _ in headers]
    lines = [
        "| " + " | ".join(labels) + " |",
        "| " + " | ".join("---" for _ in labels) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(key, "")).replace("\n", " ") for key in keys) + " |")
    return "\n".join(lines)


def build_table1(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in source_rows:
        rows.append(
            {
                "asset": row["asset"],
                "local_executable_rows": row["local_executable_rows"],
                "current_role": row["main_role"],
                "model_matrix_use": row["can_enter_current_model_matrix"],
                "blind_external_use": row["can_count_as_blind_external"],
                "status_boundary": row["blocking_issue"],
            }
        )
    return rows


def build_table2(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in source_rows:
        rows.append(
            {
                "dataset": row["dataset"],
                "contrast": row["contrast"],
                "directional_support": row["directional_support"],
                "material_support": row["material_support"],
                "mean_delta_balanced_accuracy": row["mean_delta_balanced_accuracy"],
                "claim_status": row["claim_status"],
                "interpretation_boundary": row["manuscript_interpretation"],
            }
        )
    return rows


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    table1_rows = build_table1(read_csv(TABLE1_SOURCE))
    table2_rows = build_table2(read_csv(TABLE2_SOURCE))
    anchor_rows = read_csv(ANCHOR_SOURCE)
    table_anchor_rows = [row for row in anchor_rows if row["item_id"].startswith("Table")]

    write_csv(
        OUT_DIR / "table1_dataset_asset_audit_draft.csv",
        table1_rows,
        ["asset", "local_executable_rows", "current_role", "model_matrix_use", "blind_external_use", "status_boundary"],
    )
    write_csv(
        OUT_DIR / "table2_model_family_support_draft.csv",
        table2_rows,
        ["dataset", "contrast", "directional_support", "material_support", "mean_delta_balanced_accuracy", "claim_status", "interpretation_boundary"],
    )
    write_csv(
        OUT_DIR / "table3_open_gates_draft.csv",
        TABLE3_ROWS,
        ["gate", "current_status", "evidence_anchor", "blocking_item", "manuscript_rule"],
    )

    table1_md = [
        "# Table 1. Local executable GPR asset audit",
        "",
        "Local executable rows are counted from generated unified manifests at the 2026-08-10 checkpoint. They are not global dataset sizes.",
        "",
        markdown_table(
            table1_rows,
            [
                ("asset", "Asset"),
                ("local_executable_rows", "Rows"),
                ("current_role", "Current role"),
                ("model_matrix_use", "Model matrix"),
                ("blind_external_use", "Blind external"),
                ("status_boundary", "Boundary"),
            ],
        ),
        "",
        "Caption: Table 1 separates executable local assets from supporting-only or non-blind assets. Mojahid, 4TU and Res-SAM are locally executable at this checkpoint, whereas TIGPR is not a core executable asset until authorized source media are restored and verified.",
        "",
    ]
    table2_md = [
        "# Table 2. Model-family support for current benchmark claims",
        "",
        "Material support follows the predeclared model-family threshold used in the five-model synthesis.",
        "",
        markdown_table(
            table2_rows,
            [
                ("dataset", "Dataset"),
                ("contrast", "Contrast"),
                ("directional_support", "Directional"),
                ("material_support", "Material"),
                ("mean_delta_balanced_accuracy", "Mean delta BA"),
                ("claim_status", "Claim status"),
                ("interpretation_boundary", "Boundary"),
            ],
        ),
        "",
        "Caption: Table 2 shows that Res-SAM environment transfer currently provides the strongest cross-model evidence, whereas Mojahid split sensitivity is directional but modest and model-dependent. The table excludes 4TU and true blind external validation from the main model-family matrix.",
        "",
    ]
    table3_md = [
        "# Table 3. Open gates and remaining submission requirements",
        "",
        "Table 3 is an internal or supplementary decision table unless the manuscript is framed explicitly as a benchmark/resource paper.",
        "",
        markdown_table(
            TABLE3_ROWS,
            [
                ("gate", "Gate"),
                ("current_status", "Current status"),
                ("evidence_anchor", "Evidence anchor"),
                ("blocking_item", "Blocking item"),
                ("manuscript_rule", "Manuscript rule"),
            ],
        ),
        "",
        "Caption: Table 3 records the gates that prevent the current package from being submission-ready, including blind external validation, TIGPR restoration, full Res-SAM replication, public release identifiers and rendered figures.",
        "",
    ]
    all_tables = [
        "# Manuscript Table Drafts 2026-08-10",
        "",
        "Draft boundary: these are manuscript table drafts from locked source data. They are not typeset final tables and do not replace figure rendering, final Source Data or repository identifiers.",
        "",
        *table1_md,
        *table2_md,
        *table3_md,
    ]
    (OUT_DIR / "table1_dataset_asset_audit_draft.md").write_text("\n".join(table1_md), encoding="utf-8")
    (OUT_DIR / "table2_model_family_support_draft.md").write_text("\n".join(table2_md), encoding="utf-8")
    (OUT_DIR / "table3_open_gates_draft.md").write_text("\n".join(table3_md), encoding="utf-8")
    (OUT_DIR / "manuscript_table_drafts.md").write_text("\n".join(all_tables), encoding="utf-8")

    caption_rows = [
        {
            "table_id": "Table 1",
            "caption": "Local executable GPR asset audit.",
            "source_files": "reports/figure1_table1_sources_20260810/table1_asset_audit.csv",
            "boundary": "Counts are local executable rows, not global dataset sizes.",
        },
        {
            "table_id": "Table 2",
            "caption": "Model-family support for current benchmark claims.",
            "source_files": "reports/figure2_table2_sources_20260810/table2_model_family_support.csv",
            "boundary": "Excludes 4TU and true blind external validation from the main model-family matrix.",
        },
        {
            "table_id": "Table 3",
            "caption": "Open gates and remaining submission requirements.",
            "source_files": "checkpoints/gate_status_20260810.md; checkpoints/checkpoint_20260810.md",
            "boundary": "Internal/supplementary decision table unless the manuscript is framed as a benchmark/resource paper.",
        },
    ]
    write_csv(OUT_DIR / "table_caption_and_boundary_audit.csv", caption_rows, ["table_id", "caption", "source_files", "boundary"])

    summary = {
        "run_id": "20260810_manuscript_table_drafts",
        "tables": 3,
        "table1_rows": len(table1_rows),
        "table2_rows": len(table2_rows),
        "table3_rows": len(TABLE3_ROWS),
        "table_anchors_locked": len(table_anchor_rows),
        "table_sources_ready": all(row["rendered_artifact_status"] == "table_source_ready" for row in table_anchor_rows),
        "status": "table_drafts_ready_not_typeset_final",
        "manuscript_ready": False,
        "boundary": "Tables are drafted from locked source data; final formatting, rendered figures, source-data panel mapping and submission identifiers remain open.",
    }
    (OUT_DIR / "manuscript_table_drafts_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Manuscript table drafts report 2026-08-10",
        "",
        "Generated Table 1, Table 2 and Table 3 drafts from locked source data.",
        "",
        f"- Table 1 rows: {summary['table1_rows']}",
        f"- Table 2 rows: {summary['table2_rows']}",
        f"- Table 3 rows: {summary['table3_rows']}",
        f"- Table source anchors ready: {str(summary['table_sources_ready']).lower()}",
        "",
        "Boundary: table drafts are not final typeset submission tables. Figure rendering and repository identifiers remain open.",
        "",
    ]
    (OUT_DIR / "manuscript_table_drafts_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
