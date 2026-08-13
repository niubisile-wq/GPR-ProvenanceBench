#!/usr/bin/env python3
"""Run local sign-flip/permutation audit over existing experimental contrasts."""

from __future__ import annotations

import csv
import itertools
import json
from math import comb
from pathlib import Path

import numpy as np


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "local_signflip_permutation_audit_20260811"


def read_json(rel_path: str) -> dict:
    return json.loads((BENCH_ROOT / rel_path).read_text(encoding="utf-8-sig"))


def exact_binomial_tail(k: int, n: int, direction: str) -> float:
    if n <= 0:
        return 1.0
    if direction == "positive":
        return float(sum(comb(n, i) for i in range(k, n + 1)) / (2**n))
    if direction == "negative":
        return float(sum(comb(n, i) for i in range(k, n + 1)) / (2**n))
    raise ValueError(direction)


def exact_signflip_mean_p(values: list[float], observed_direction: str) -> float:
    arr = np.asarray([value for value in values if value != 0.0], dtype=np.float64)
    if arr.size == 0:
        return 1.0
    observed = float(arr.mean())
    magnitudes = np.abs(arr)
    count = 0
    total = 0
    for signs in itertools.product([-1.0, 1.0], repeat=len(magnitudes)):
        total += 1
        mean_value = float((magnitudes * np.asarray(signs)).mean())
        if observed_direction == "positive" and mean_value >= observed - 1e-15:
            count += 1
        elif observed_direction == "negative" and mean_value <= observed + 1e-15:
            count += 1
    return float(count / total)


def summarize_values(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "n": int(arr.size),
        "mean": float(arr.mean()) if arr.size else 0.0,
        "min": float(arr.min()) if arr.size else 0.0,
        "max": float(arr.max()) if arr.size else 0.0,
    }


def unified_rows(effect_stats: dict) -> list[dict[str, object]]:
    rows = []
    contrasts = effect_stats["contrasts"]
    for dataset in sorted({row["dataset"] for row in contrasts}):
        values = [
            float(row["observed_delta_balanced_accuracy"])
            for row in contrasts
            if row["dataset"] == dataset
        ]
        positive = sum(value > 0 for value in values)
        nonzero = sum(value != 0 for value in values)
        rows.append(
            {
                "audit_family": "unified_split_random_minus_protocol",
                "unit": dataset,
                "n_contrasts": len(values),
                "positive_count": positive,
                "negative_count": sum(value < 0 for value in values),
                "mean_delta": summarize_values(values)["mean"],
                "exact_sign_positive_tail_p": exact_binomial_tail(positive, nonzero, "positive"),
                "exact_signflip_mean_positive_p": exact_signflip_mean_p(values, "positive"),
            }
        )
    all_values = [float(row["observed_delta_balanced_accuracy"]) for row in contrasts]
    positive = sum(value > 0 for value in all_values)
    nonzero = sum(value != 0 for value in all_values)
    rows.append(
        {
            "audit_family": "unified_split_random_minus_protocol",
            "unit": "all_assets",
            "n_contrasts": len(all_values),
            "positive_count": positive,
            "negative_count": sum(value < 0 for value in all_values),
            "mean_delta": summarize_values(all_values)["mean"],
            "exact_sign_positive_tail_p": exact_binomial_tail(positive, nonzero, "positive"),
            "exact_signflip_mean_positive_p": exact_signflip_mean_p(all_values, "positive"),
        }
    )
    return rows


def four_tu_rows(stability: dict) -> list[dict[str, object]]:
    rows = []
    for layer in stability["layers"]:
        values = [float(row["balanced_accuracy_delta_vs_original"]) for row in layer["rows"]]
        negative = sum(value < 0 for value in values)
        nonzero = sum(value != 0 for value in values)
        rows.append(
            {
                "audit_family": "4tu_log_clip_stress_delta",
                "unit": layer["layer"],
                "n_contrasts": len(values),
                "positive_count": sum(value > 0 for value in values),
                "negative_count": negative,
                "mean_delta": summarize_values(values)["mean"],
                "exact_sign_negative_tail_p": exact_binomial_tail(negative, nonzero, "negative"),
                "exact_signflip_mean_negative_p": exact_signflip_mean_p(values, "negative"),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Local Sign-Flip / Permutation Audit",
        "",
        "Exact sign and exhaustive sign-flip tests are computed from existing local",
        "experimental contrasts. No model is retrained here.",
        "",
        "## Unified Split Random-Minus-Protocol",
        "",
        "| unit | n | + | - | mean delta | sign p | mean sign-flip p |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["unified_rows"]:
        lines.append(
            f"| {row['unit']} | {row['n_contrasts']} | {row['positive_count']} | "
            f"{row['negative_count']} | {row['mean_delta']:+.4f} | "
            f"{row['exact_sign_positive_tail_p']:.4f} | "
            f"{row['exact_signflip_mean_positive_p']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## 4TU Log-Clip Stress Deltas",
            "",
            "| unit | n | + | - | mean delta | sign p | mean sign-flip p |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in result["four_tu_rows"]:
        lines.append(
            f"| {row['unit']} | {row['n_contrasts']} | {row['positive_count']} | "
            f"{row['negative_count']} | {row['mean_delta']:+.4f} | "
            f"{row['exact_sign_negative_tail_p']:.4f} | "
            f"{row['exact_signflip_mean_negative_p']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These tests strengthen the local statistical audit layer. They do not",
            "replace cluster bootstrap, deep model reruns or blind external validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    effect_stats = read_json("reports/unified_split_effect_statistics_20260811/unified_split_effect_statistics_summary.json")
    stability = read_json("reports/4tu_stress_stability_20260811/4tu_stress_stability_summary.json")
    result = {
        "run_id": "20260811_E30_local_signflip_permutation_audit",
        "unified_rows": unified_rows(effect_stats),
        "four_tu_rows": four_tu_rows(stability),
        "blind_external_eligible": False,
        "status": "complete_local_signflip_permutation_audit",
    }
    (OUT_DIR / "local_signflip_permutation_audit_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "local_signflip_permutation_audit_rows.csv", result["unified_rows"] + result["four_tu_rows"])
    write_md(OUT_DIR / "local_signflip_permutation_audit_summary.md", result)
    print(
        json.dumps(
            {
                "run_id": result["run_id"],
                "status": result["status"],
                "rows": len(result["unified_rows"]) + len(result["four_tu_rows"]),
                "blind_external_eligible": result["blind_external_eligible"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
