#!/usr/bin/env python3
"""Build frozen source data for Figure 5 and Figure 6."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
REPORTS = BENCH_ROOT / "reports"
OUT_DIR = REPORTS / "figure5_figure6_sources_20260810"

FOUR_TU_TARGETS = REPORTS / "4tu_group_feasibility_20260810" / "4tu_group_feasibility_targets.csv"
EXTERNAL_TRACKS = REPORTS / "external_validation_readiness_20260810" / "external_validation_readiness_tracks.csv"
EXTERNAL_READY_JSON = REPORTS / "external_validation_readiness_20260810" / "external_validation_readiness_summary.json"
INTAKE_JSON = REPORTS / "external_blind_intake_20260810" / "external_blind_intake_validation_summary.json"
LOCKED_EVAL_JSON = REPORTS / "external_blind_locked_evaluation_20260810" / "external_blind_locked_evaluation_summary.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def feasibility_fraction(row: dict[str, str]) -> float:
    attempted = int(row["test2_val2_attempted"])
    feasible = int(row["test2_val2_feasible"])
    return feasible / attempted if attempted else 0.0


def build_figure5_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        frac = feasibility_fraction(row)
        if row["status"] == "usable_with_caution":
            interpretation = "usable with caution; still not main confirmation alone"
        elif row["status"] == "not_viable_for_group_holdout":
            interpretation = "not viable for grouped holdout"
        else:
            interpretation = "weak because labels are concentrated in too few projects"
        out.append(
            {
                "panel": "Figure 5",
                "target": row["target"],
                "status": row["status"],
                "sample_count": int(row["sample_count"]),
                "project_count": int(row["project_count"]),
                "n_labels": int(row["n_labels"]),
                "test2_val2_attempted": int(row["test2_val2_attempted"]),
                "test2_val2_feasible": int(row["test2_val2_feasible"]),
                "test2_val2_feasible_fraction": round(frac, 4),
                "singleton_labels": row["singleton_labels"],
                "rare_labels_project_support_lt3": row["rare_labels_project_support_lt3"],
                "interpretation": interpretation,
            }
        )
    return out


def build_figure6_rows(track_rows: list[dict[str, str]], external: dict, intake: dict, locked: dict) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in track_rows:
        out.append(
            {
                "panel": "Figure 6",
                "gate_component": f"Track {row['track_id']}: {row['name']}",
                "component_type": "external_asset_track",
                "status": row["current_status"],
                "role": row["role"],
                "blocking_or_boundary": row["blocking_facts"],
                "next_action": row["next_action"],
                "is_main_result": "no",
            }
        )
    out.extend(
        [
            {
                "panel": "Figure 6",
                "gate_component": "Blind intake template validation",
                "component_type": "protocol_template",
                "status": intake["status"],
                "role": "structure and blinding-contract dry run",
                "blocking_or_boundary": intake["note"],
                "next_action": "Replace template with a filled strict-SHA manifest when a real external asset arrives.",
                "is_main_result": "no",
            },
            {
                "panel": "Figure 6",
                "gate_component": "Locked evaluation dry run",
                "component_type": "evaluation_template",
                "status": locked["evaluation_mode"],
                "role": "post-unlock metric pipeline dry run",
                "blocking_or_boundary": locked["boundary"],
                "next_action": "Run once with --main-claim only after frozen predictions and legitimate label unlock.",
                "is_main_result": "no",
            },
            {
                "panel": "Figure 6",
                "gate_component": "External validation readiness gate",
                "component_type": "overall_gate",
                "status": external["gate"]["status"],
                "role": "blind external validation gate",
                "blocking_or_boundary": external["gate"]["decision"],
                "next_action": "Acquire or restore a real external asset; do not add more internal modeling as a substitute.",
                "is_main_result": "no",
            },
        ]
    )
    return out


def write_markdown(path: Path, figure5: list[dict[str, object]], figure6: list[dict[str, object]]) -> None:
    lines = [
        "# Figure 5 and Figure 6 Source Data 2026-08-10",
        "",
        "Purpose: freeze remaining gate/failure-mode source data before plotting.",
        "",
        "Boundary: Figure 5 is a 4TU feasibility/failure-mode map. Figure 6 is an external blind-validation gate map. Neither should be written as a completed confirmation result.",
        "",
        "## Figure 5: 4TU Feasibility Map",
        "",
        "| target | status | samples | projects | labels | feasible/attempted | feasible fraction | interpretation |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in figure5:
        lines.append(
            f"| {row['target']} | {row['status']} | {row['sample_count']} | "
            f"{row['project_count']} | {row['n_labels']} | {row['test2_val2_feasible']}/{row['test2_val2_attempted']} | "
            f"{row['test2_val2_feasible_fraction']:.4f} | {row['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Figure 6: External Blind Gate Map",
            "",
            "| component | type | status | boundary | main result? |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in figure6:
        lines.append(
            f"| {row['gate_component']} | {row['component_type']} | {row['status']} | "
            f"{row['blocking_or_boundary']} | {row['is_main_result']} |"
        )
    lines.extend(
        [
            "",
            "## Plotting Notes",
            "",
            "1. Figure 5 should use target-level feasibility fractions plus status colors.",
            "2. Figure 6 should use a gate diagram, not a performance chart.",
            "3. Mark all Figure 6 components as not main results until a real strict-SHA external asset is evaluated.",
            "4. Keep the text explicit that protocol readiness does not equal blind external validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    figure5 = build_figure5_rows(read_csv(FOUR_TU_TARGETS))
    figure6 = build_figure6_rows(
        read_csv(EXTERNAL_TRACKS),
        read_json(EXTERNAL_READY_JSON),
        read_json(INTAKE_JSON),
        read_json(LOCKED_EVAL_JSON),
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUT_DIR / "figure5_4tu_feasibility_source_data.csv",
        figure5,
        [
            "panel",
            "target",
            "status",
            "sample_count",
            "project_count",
            "n_labels",
            "test2_val2_attempted",
            "test2_val2_feasible",
            "test2_val2_feasible_fraction",
            "singleton_labels",
            "rare_labels_project_support_lt3",
            "interpretation",
        ],
    )
    write_csv(
        OUT_DIR / "figure6_external_gate_source_data.csv",
        figure6,
        [
            "panel",
            "gate_component",
            "component_type",
            "status",
            "role",
            "blocking_or_boundary",
            "next_action",
            "is_main_result",
        ],
    )
    write_markdown(OUT_DIR / "figure5_figure6_source_summary.md", figure5, figure6)
    result = {
        "run_id": "20260810_figure5_figure6_sources",
        "figure5_rows": len(figure5),
        "figure6_rows": len(figure6),
        "boundary": "Gate/failure-mode source data only; no completed blind external validation.",
    }
    (OUT_DIR / "figure5_figure6_source_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
