#!/usr/bin/env python3
"""Run a non-blind foreground-ratio baseline for Zenodo MCG GPR."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import balanced_accuracy_score, mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


BENCH_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = BENCH_ROOT / "data_manifests" / "zenodo_mcg_gpr_manifest_20260811.csv"
OUT_DIR = BENCH_ROOT / "reports" / "zenodo_mcg_gpr_nonblind_baseline_20260811"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_gray(path: Path, size: int = 32) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(image.convert("L").resize((size, size), Image.Resampling.BILINEAR), dtype=np.float32)
    return arr.ravel() / 255.0


def image_features(rows: list[dict[str, str]]) -> np.ndarray:
    cache = OUT_DIR / "mcg_pixel32_features.npz"
    sample_ids = [row["sample_id"] for row in rows]
    if cache.exists():
        data = np.load(cache)
        if data["sample_ids"].tolist() == sample_ids:
            return data["features"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    features = np.stack([load_gray(Path(row["image_abs_path"])) for row in rows]).astype(np.float32)
    np.savez_compressed(cache, sample_ids=np.asarray(sample_ids), features=features)
    return features


def bin_targets(train_y: np.ndarray, values: np.ndarray) -> np.ndarray:
    q1, q2 = np.quantile(train_y, [1 / 3, 2 / 3])
    return np.where(values <= q1, "low", np.where(values <= q2, "mid", "high"))


def evaluate_regression(name: str, model, train_x, train_y, test_x, test_y) -> dict[str, object]:
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    return {
        "model": name,
        "task": "foreground_ratio_regression",
        "test_n": int(len(test_y)),
        "mae": float(mean_absolute_error(test_y, pred)),
        "r2": float(r2_score(test_y, pred)),
    }


def evaluate_classification(name: str, model, train_x, train_bins, test_x, test_bins) -> dict[str, object]:
    model.fit(train_x, train_bins)
    pred = model.predict(test_x)
    return {
        "model": name,
        "task": "foreground_ratio_tertile_classification",
        "test_n": int(len(test_bins)),
        "balanced_accuracy": float(balanced_accuracy_score(test_bins, pred)),
        "test_bin_counts": {label: int(np.sum(test_bins == label)) for label in sorted(set(test_bins.tolist()))},
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {key: json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value for key, value in row.items()}
            )


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Zenodo MCG GPR Non-Blind Baseline",
        "",
        f"Annotated rows: {summary['annotated_rows']}",
        f"Train/val/test: {summary['split_counts']}",
        "",
        "| task | model | metric | value |",
        "| --- | --- | --- | ---: |",
    ]
    for row in summary["runs"]:
        if row["task"] == "foreground_ratio_regression":
            lines.append(f"| regression | {row['model']} | MAE | {row['mae']:.6f} |")
            lines.append(f"| regression | {row['model']} | R2 | {row['r2']:.6f} |")
        else:
            lines.append(f"| tertile classification | {row['model']} | balanced accuracy | {row['balanced_accuracy']:.6f} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a public, non-blind segmentation-derived stress baseline. It",
            "cannot close the hard blind external validation gate.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = [row for row in read_rows(MANIFEST) if row["has_annotation"] == "true"]
    x = image_features(all_rows)
    y = np.asarray([float(row["foreground_ratio"]) for row in all_rows], dtype=np.float32)
    roles = np.asarray([row["split_role"] for row in all_rows])
    train_idx = np.flatnonzero(roles == "train")
    test_idx = np.flatnonzero(roles == "test")
    train_bins = bin_targets(y[train_idx], y[train_idx])
    test_bins = bin_targets(y[train_idx], y[test_idx])
    runs = [
        evaluate_regression(
            "ridge_pixel32",
            make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
            x[train_idx],
            y[train_idx],
            x[test_idx],
            y[test_idx],
        ),
        evaluate_regression(
            "extra_trees_pixel32",
            ExtraTreesRegressor(n_estimators=240, min_samples_leaf=2, random_state=20260811, n_jobs=-1),
            x[train_idx],
            y[train_idx],
            x[test_idx],
            y[test_idx],
        ),
        evaluate_classification(
            "extra_trees_pixel32",
            ExtraTreesClassifier(n_estimators=240, min_samples_leaf=2, random_state=20260811, n_jobs=-1),
            x[train_idx],
            train_bins,
            x[test_idx],
            test_bins,
        ),
    ]
    summary = {
        "run_id": "20260811_E39_zenodo_mcg_gpr_nonblind_baseline",
        "annotated_rows": len(all_rows),
        "split_counts": {role: int(np.sum(roles == role)) for role in sorted(set(roles.tolist()))},
        "target_foreground_ratio": {
            "train_mean": float(y[train_idx].mean()),
            "test_mean": float(y[test_idx].mean()),
            "train_min": float(y[train_idx].min()),
            "train_max": float(y[train_idx].max()),
        },
        "runs": runs,
        "blind_external_eligible": False,
        "status": "complete_public_mcg_gpr_nonblind_baseline",
    }
    (OUT_DIR / "zenodo_mcg_gpr_nonblind_baseline_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "zenodo_mcg_gpr_nonblind_baseline_runs.csv", runs)
    write_md(OUT_DIR / "zenodo_mcg_gpr_nonblind_baseline_summary.md", summary)
    print(json.dumps({"status": summary["status"], "runs": len(runs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
