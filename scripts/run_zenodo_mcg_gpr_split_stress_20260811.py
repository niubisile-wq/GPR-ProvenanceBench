#!/usr/bin/env python3
"""Compare official MCG downstream split with random foreground-ratio splits."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.metrics import balanced_accuracy_score, mean_absolute_error, r2_score
from sklearn.model_selection import StratifiedShuffleSplit

from run_zenodo_mcg_gpr_nonblind_baseline_20260811 import BENCH_ROOT, MANIFEST, OUT_DIR as BASE_OUT, image_features, read_rows


OUT_DIR = BENCH_ROOT / "reports" / "zenodo_mcg_gpr_split_stress_20260811"
SEEDS = [20260811, 20260812, 20260813, 20260814, 20260815]


def target_bins(reference_y: np.ndarray, values: np.ndarray) -> np.ndarray:
    q1, q2 = np.quantile(reference_y, [1 / 3, 2 / 3])
    return np.where(values <= q1, "low", np.where(values <= q2, "mid", "high"))


def evaluate_split(name: str, split_family: str, seed: int | str, x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray) -> dict[str, object]:
    reg = ExtraTreesRegressor(n_estimators=240, min_samples_leaf=2, random_state=20260811 if seed == "official" else int(seed), n_jobs=-1)
    reg.fit(x[train_idx], y[train_idx])
    pred_y = reg.predict(x[test_idx])
    train_bins = target_bins(y[train_idx], y[train_idx])
    test_bins = target_bins(y[train_idx], y[test_idx])
    clf = ExtraTreesClassifier(n_estimators=240, min_samples_leaf=2, random_state=20260811 if seed == "official" else int(seed), n_jobs=-1)
    clf.fit(x[train_idx], train_bins)
    pred_bins = clf.predict(x[test_idx])
    return {
        "split_name": name,
        "split_family": split_family,
        "seed": seed,
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "train_foreground_mean": float(y[train_idx].mean()),
        "test_foreground_mean": float(y[test_idx].mean()),
        "foreground_mean_shift_test_minus_train": float(y[test_idx].mean() - y[train_idx].mean()),
        "regression_mae": float(mean_absolute_error(y[test_idx], pred_y)),
        "regression_r2": float(r2_score(y[test_idx], pred_y)),
        "tertile_balanced_accuracy": float(balanced_accuracy_score(test_bins, pred_bins)),
    }


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Zenodo MCG GPR Split Stress",
        "",
        "| split | train n | test n | mean shift | MAE | R2 | tertile BA |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["runs"]:
        lines.append(
            f"| {row['split_name']} | {row['train_n']} | {row['test_n']} | "
            f"{row['foreground_mean_shift_test_minus_train']:+.4f} | {row['regression_mae']:.4f} | "
            f"{row['regression_r2']:.4f} | {row['tertile_balanced_accuracy']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a public non-blind split-stress audit over a segmentation-derived",
            "foreground-ratio task. It cannot close blind external validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [row for row in read_rows(MANIFEST) if row["has_annotation"] == "true"]
    x = image_features(rows)
    y = np.asarray([float(row["foreground_ratio"]) for row in rows], dtype=np.float32)
    roles = np.asarray([row["split_role"] for row in rows])

    runs: list[dict[str, object]] = []
    official_train = np.flatnonzero(roles == "train")
    for role in ["val", "test"]:
        runs.append(evaluate_split(f"official_train_to_{role}", "official", "official", x, y, official_train, np.flatnonzero(roles == role)))

    global_bins = target_bins(y, y)
    for seed in SEEDS:
        split = StratifiedShuffleSplit(n_splits=1, train_size=0.70, test_size=0.15, random_state=seed)
        train_idx, test_idx = next(split.split(np.zeros(len(y)), global_bins))
        runs.append(evaluate_split("random_stratified_70_15", "random", seed, x, y, train_idx, test_idx))

    random_runs = [row for row in runs if row["split_family"] == "random"]
    official_test = next(row for row in runs if row["split_name"] == "official_train_to_test")
    random_mae = summarize([float(row["regression_mae"]) for row in random_runs])
    random_ba = summarize([float(row["tertile_balanced_accuracy"]) for row in random_runs])
    summary = {
        "run_id": "20260811_E40_zenodo_mcg_gpr_split_stress",
        "annotated_rows": len(rows),
        "seeds": SEEDS,
        "runs": runs,
        "random_regression_mae": random_mae,
        "random_tertile_balanced_accuracy": random_ba,
        "official_test_regression_mae": official_test["regression_mae"],
        "official_test_tertile_balanced_accuracy": official_test["tertile_balanced_accuracy"],
        "official_minus_random_mae": float(official_test["regression_mae"] - random_mae["mean"]),
        "official_minus_random_tertile_ba": float(official_test["tertile_balanced_accuracy"] - random_ba["mean"]),
        "blind_external_eligible": False,
        "status": "complete_public_mcg_gpr_split_stress",
    }
    (OUT_DIR / "zenodo_mcg_gpr_split_stress_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "zenodo_mcg_gpr_split_stress_runs.csv", runs)
    write_md(OUT_DIR / "zenodo_mcg_gpr_split_stress_summary.md", summary)
    print(json.dumps({"status": summary["status"], "runs": len(runs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
