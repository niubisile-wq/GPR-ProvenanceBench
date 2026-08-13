#!/usr/bin/env python3
"""Summarize a directory of 4TU task baseline results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_results(result_dir: Path) -> list[dict]:
    paths = sorted(result_dir.glob("*_result_seed_*.json"))
    if not paths:
        raise FileNotFoundError(f"No 4TU task result JSON files found in {result_dir}")
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def best_row(result: dict) -> dict:
    return max(result["rows"], key=lambda row: (row["val_balanced_accuracy"], row["val_macro_f1"]))


def write_markdown(path: Path, results: list[dict]) -> None:
    lines = [
        "# 4TU P4 v2 Multi-Target Baseline Matrix 2026-08-10",
        "",
        "This table summarizes task-metadata smoke baselines from the same P4 v2",
        "package and activity-level metadata join.",
        "",
        "| target | records | selected_model | val_balanced_accuracy | test_balanced_accuracy | val_macro_f1 | test_macro_f1 |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        row = best_row(result)
        lines.append(
            f"| {result['target_field']} | {result['records']} | {row['model']} | "
            f"{row['val_balanced_accuracy']:.3f} | {row['test_balanced_accuracy']:.3f} | "
            f"{row['val_macro_f1']:.3f} | {row['test_macro_f1']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Target Viability",
            "",
            "| target | viable | train_classes | val_classes | test_classes | reason |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for result in results:
        viability = result.get("viability", {})
        n_classes = viability.get("n_classes_by_split", {})
        lines.append(
            f"| {result['target_field']} | {viability.get('is_viable_smoke_target', 'unknown')} | "
            f"{n_classes.get('train', 'na')} | {n_classes.get('val', 'na')} | {n_classes.get('test', 'na')} | "
            f"{viability.get('reason', 'not_recorded')} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These are task-metadata smoke baselines. They are useful for selecting",
            "which 4TU target fields are viable for controlled experiments, but they",
            "do not complete the strict raw-trace counterfactual requirement.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    results = load_results(args.result_dir)
    summary = []
    for result in results:
        row = best_row(result)
        summary.append(
            {
                "target_field": result["target_field"],
                "records": result["records"],
                "selected_model": row["model"],
                "val_balanced_accuracy": row["val_balanced_accuracy"],
                "test_balanced_accuracy": row["test_balanced_accuracy"],
                "val_macro_f1": row["val_macro_f1"],
                "test_macro_f1": row["test_macro_f1"],
                "viability": result.get("viability", {}),
                "label_counts": result["label_counts"],
                "split_counts": result["split_counts"],
            }
        )

    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.output_md, results)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
