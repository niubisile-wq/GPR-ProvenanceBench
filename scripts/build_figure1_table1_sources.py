#!/usr/bin/env python3
"""Build frozen source data for Figure 1 and Table 1."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = BENCH_ROOT / "data_manifests"
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "figure1_table1_sources_20260810"

TIGPR_AUDIT = REPORTS / "tigpr_local_asset_audit_20260810.json"
EXTERNAL_READY = REPORTS / "external_validation_readiness_20260810" / "external_validation_readiness_summary.json"

MANIFESTS = {
    "Mojahid": DATA_DIR / "mojahid_unified_samples_20260810.csv",
    "4TU": DATA_DIR / "four_tu_unified_samples_20260810.csv",
    "Res-SAM": DATA_DIR / "res_sam_unified_samples_20260810.csv",
    "TIGPR": DATA_DIR / "tigpr_unified_samples_20260810.csv",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return max(0, sum(1 for _ in csv.reader(handle)) - 1)


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_table1(tigpr: dict) -> list[dict[str, object]]:
    rows = [
        {
            "asset": "Mojahid",
            "local_executable_rows": count_rows(MANIFESTS["Mojahid"]),
            "asset_status": "executable_local",
            "main_role": "baseline split/provenance signal",
            "can_enter_current_model_matrix": "yes",
            "can_count_as_blind_external": "no",
            "blocking_issue": "single-source exploratory asset; not sufficient alone for confirmation",
            "next_required_action": "keep grouped baseline and ancestry-aware interpretation",
        },
        {
            "asset": "4TU",
            "local_executable_rows": count_rows(MANIFESTS["4TU"]),
            "asset_status": "executable_local_with_label_limits",
            "main_role": "raw-trace counterfactual stress-test evidence",
            "can_enter_current_model_matrix": "limited",
            "can_count_as_blind_external": "no",
            "blocking_issue": "project count and metadata label balance weaken main confirmation",
            "next_required_action": "use as stress test unless stronger grouped labels or 4TU-like asset arrive",
        },
        {
            "asset": "Res-SAM",
            "local_executable_rows": count_rows(MANIFESTS["Res-SAM"]),
            "asset_status": "executable_local",
            "main_role": "environment-transfer model-matrix evidence",
            "can_enter_current_model_matrix": "yes",
            "can_count_as_blind_external": "no",
            "blocking_issue": "already used in current model-family synthesis; full Res-SAM model lacks SAM checkpoint",
            "next_required_action": "keep as core local data asset; do not relabel as blind external",
        },
        {
            "asset": "TIGPR",
            "local_executable_rows": count_rows(MANIFESTS["TIGPR"]),
            "asset_status": "supporting_only_local_no_go",
            "main_role": "supporting prior provenance evidence",
            "can_enter_current_model_matrix": "no",
            "can_count_as_blind_external": "no",
            "blocking_issue": "; ".join(tigpr["blockers"]),
            "next_required_action": "restore authorized source media and rebuild 7169-row local sample index",
        },
    ]
    return rows


def build_figure1_steps(external: dict) -> list[dict[str, object]]:
    return [
        {
            "step_id": "F1A",
            "step_label": "Asset audit",
            "evidence_status": "complete_current_checkpoint",
            "source": "data_manifests/*_unified_samples_20260810.csv",
            "key_message": "Three local executable assets are available; TIGPR remains supporting-only.",
            "open_gate": "third independent/core confirmation asset still conditional",
        },
        {
            "step_id": "F1B",
            "step_label": "Split and transfer baselines",
            "evidence_status": "partial_complete",
            "source": "reports/five_model_synthesis_20260810",
            "key_message": "Res-SAM environment transfer is the strongest current cross-model signal.",
            "open_gate": "4TU and true blind external validation absent from five-model matrix",
        },
        {
            "step_id": "F1C",
            "step_label": "Raw-trace counterfactual stress test",
            "evidence_status": "stress_test_complete",
            "source": "reports/figure4_sources_20260810",
            "key_message": "4TU fixed-split sensitivity weakens under project-level repeated splits.",
            "open_gate": "not a final causal proof or main confirmation layer",
        },
        {
            "step_id": "F1D",
            "step_label": "Blind external protocol",
            "evidence_status": "template_ready_no_go",
            "source": "protocols/blind_external_validation_protocol_20260810.md",
            "key_message": "Protocol, intake templates and locked evaluator exist.",
            "open_gate": external["gate"]["decision"],
        },
        {
            "step_id": "F1E",
            "step_label": "Manuscript claim boundary",
            "evidence_status": "active_boundary",
            "source": "reports/manuscript_figure_table_plan_20260810",
            "key_message": "Current manuscript lead should be Res-SAM environment-transfer fragility.",
            "open_gate": "do not claim completed blind external validation",
        },
    ]


def write_markdown(path: Path, table_rows: list[dict[str, object]], figure_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Figure 1 and Table 1 Source Data 2026-08-10",
        "",
        "Purpose: freeze the study-design and asset-audit source data before drawing Figure 1 and rendering Table 1.",
        "",
        "Boundary: counts are local executable manifest rows at this checkpoint, not global dataset sizes. TIGPR remains supporting-only until source media are restored.",
        "",
        "## Table 1 Asset Audit Draft",
        "",
        "| asset | rows | status | main role | current matrix | blind external | blocking issue |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in table_rows:
        lines.append(
            f"| {row['asset']} | {row['local_executable_rows']} | {row['asset_status']} | "
            f"{row['main_role']} | {row['can_enter_current_model_matrix']} | "
            f"{row['can_count_as_blind_external']} | {row['blocking_issue']} |"
        )
    lines.extend(
        [
            "",
            "## Figure 1 Flow Source",
            "",
            "| step | label | evidence status | key message | open gate |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in figure_rows:
        lines.append(
            f"| {row['step_id']} | {row['step_label']} | {row['evidence_status']} | "
            f"{row['key_message']} | {row['open_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Figure 1 Design Notes",
            "",
            "1. Use a gate-flow schematic: asset audit -> model matrix -> counterfactual stress test -> blind protocol -> manuscript boundary.",
            "2. Visually separate executable evidence from open gates.",
            "3. Mark TIGPR as supporting-only and blind external validation as NO-GO.",
            "4. Do not use Figure 1 to imply that all gates are closed.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    tigpr = read_json(TIGPR_AUDIT)
    external = read_json(EXTERNAL_READY)
    table_rows = build_table1(tigpr)
    figure_rows = build_figure1_steps(external)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUT_DIR / "table1_asset_audit.csv",
        table_rows,
        [
            "asset",
            "local_executable_rows",
            "asset_status",
            "main_role",
            "can_enter_current_model_matrix",
            "can_count_as_blind_external",
            "blocking_issue",
            "next_required_action",
        ],
    )
    write_csv(
        OUT_DIR / "figure1_flow_source.csv",
        figure_rows,
        ["step_id", "step_label", "evidence_status", "source", "key_message", "open_gate"],
    )
    write_markdown(OUT_DIR / "figure1_table1_source_summary.md", table_rows, figure_rows)
    result = {
        "run_id": "20260810_figure1_table1_sources",
        "table1_rows": len(table_rows),
        "figure1_steps": len(figure_rows),
        "asset_row_counts": {row["asset"]: row["local_executable_rows"] for row in table_rows},
        "boundary": "Local executable asset audit only; not all confirmation gates are closed.",
    }
    (OUT_DIR / "figure1_table1_source_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
