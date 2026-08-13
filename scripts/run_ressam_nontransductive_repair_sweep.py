#!/usr/bin/env python3
"""Run non-transductive Res-SAM preprocessing repair sweeps.

The repair variants are per-image transforms. They do not use target-domain
batch statistics or target labels, so they are compatible with a stricter
external-use boundary than CORAL or target mean/std alignment.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


SHARED_LABELS = {"cavity", "crack", "pipe"}
PREPROCESSORS = ["raw", "per_image_zscore", "per_image_equalized"]
METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_gray(path: Path, size: int) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((size, size), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    return arr / 255.0


def preprocess_image(image: np.ndarray, method: str) -> np.ndarray:
    if method == "raw":
        return image
    if method == "per_image_zscore":
        centered = (image - float(image.mean())) / (float(image.std()) + 1e-6)
        clipped = np.clip(centered, -3.0, 3.0)
        return ((clipped + 3.0) / 6.0).astype(np.float32)
    if method == "per_image_equalized":
        flat = image.ravel()
        order = np.argsort(flat, kind="mergesort")
        ranks = np.empty_like(order, dtype=np.float32)
        ranks[order] = np.linspace(0.0, 1.0, num=flat.size, dtype=np.float32)
        return ranks.reshape(image.shape)
    raise ValueError(f"Unknown preprocessing method: {method}")


def simple_hog(image: np.ndarray, cell_size: int = 8, bins: int = 9) -> np.ndarray:
    gy, gx = np.gradient(image)
    magnitude = np.sqrt(gx * gx + gy * gy)
    orientation = np.mod((np.arctan2(gy, gx) + np.pi) * (180.0 / np.pi), 180.0)
    bin_idx = np.minimum((orientation / (180.0 / bins)).astype(np.int32), bins - 1)
    cells_y = image.shape[0] // cell_size
    cells_x = image.shape[1] // cell_size
    features: list[float] = []
    for cy in range(cells_y):
        for cx in range(cells_x):
            y0 = cy * cell_size
            x0 = cx * cell_size
            cell_bins = bin_idx[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            cell_mag = magnitude[y0 : y0 + cell_size, x0 : x0 + cell_size].ravel()
            hist = np.bincount(cell_bins, weights=cell_mag, minlength=bins).astype(np.float32)
            features.extend((hist / (float(np.linalg.norm(hist)) + 1e-8)).tolist())
    return np.asarray(features, dtype=np.float32)


def extract(
    rows: list[dict[str, str]],
    data_root: Path,
    image_size: int,
    preprocessor: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    environments: list[str] = []
    for row in rows:
        image_path = data_root / row["rel_path"]
        if not image_path.exists():
            raise FileNotFoundError(f"Missing Res-SAM image: {image_path}")
        image = preprocess_image(load_gray(image_path, image_size), preprocessor)
        features.append(simple_hog(image))
        labels.append(row["label"])
        environments.append(row["project_id"])
    return np.stack(features), np.asarray(labels), np.asarray(environments)


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        SVC(C=3.0, gamma="scale", class_weight="balanced", random_state=seed),
    )


def evaluate(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray, seed: int) -> dict[str, float]:
    model = make_model(seed)
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    return {
        "accuracy": float(accuracy_score(test_y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_y, pred)),
        "macro_f1": float(f1_score(test_y, pred, average="macro")),
    }


def transfer(
    x: np.ndarray,
    y: np.ndarray,
    env: np.ndarray,
    train_environment: str,
    test_environment: str,
    seed: int,
) -> dict:
    shared_idx = np.flatnonzero(np.isin(y, sorted(SHARED_LABELS)))
    train_idx = shared_idx[env[shared_idx] == train_environment]
    test_idx = shared_idx[env[shared_idx] == test_environment]
    return {
        "train_environment": train_environment,
        "test_environment": test_environment,
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "train_label_counts": {str(k): int(v) for k, v in Counter(y[train_idx]).items()},
        "test_label_counts": {str(k): int(v) for k, v in Counter(y[test_idx]).items()},
        "metrics": evaluate(x[train_idx], y[train_idx], x[test_idx], y[test_idx], seed),
    }


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict) -> None:
    lines = [
        "# Res-SAM Non-Transductive Repair Sweep",
        "",
        f"Runs: `{summary['n_runs']}`",
        f"Seeds: `{', '.join(str(seed) for seed in summary['seeds'])}`",
        "",
        "| transfer | raw bal acc | zscore bal acc | equalized bal acc | best delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for direction, item in summary["transfer"].items():
        raw = item["raw"]["balanced_accuracy"]["mean"]
        zscore = item["per_image_zscore"]["balanced_accuracy"]["mean"]
        equalized = item["per_image_equalized"]["balanced_accuracy"]["mean"]
        lines.append(
            f"| {direction} | {raw:.4f} | {zscore:.4f} | {equalized:.4f} | "
            f"{max(zscore, equalized) - raw:+.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: these repairs are per-image preprocessing variants. They do not",
            "use target-domain batch statistics or labels, but this is still not a",
            "formal blind external submission because the Res-SAM asset is already part",
            "of local model development.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=64)
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]
    long_rows: list[dict[str, object]] = []
    metric_values: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    detailed: list[dict] = []

    extracted = {
        preprocessor: extract(rows, args.data_root, args.image_size, preprocessor)
        for preprocessor in PREPROCESSORS
    }
    for seed in seeds:
        for preprocessor, (x, y, env) in extracted.items():
            for train_environment, test_environment in [
                ("synthetic", "real_world"),
                ("real_world", "synthetic"),
            ]:
                result = transfer(x, y, env, train_environment, test_environment, seed)
                direction = f"{train_environment}_to_{test_environment}"
                detailed.append({"seed": seed, "preprocessor": preprocessor, **result})
                for metric in METRICS:
                    value = float(result["metrics"][metric])
                    metric_values[direction][preprocessor][metric].append(value)
                    long_rows.append(
                        {
                            "seed": seed,
                            "direction": direction,
                            "preprocessor": preprocessor,
                            "metric": metric,
                            "value": value,
                        }
                    )

    summary = {
        "run_id": "20260811_E03_ressam_nontransductive_repair_sweep",
        "n_runs": len(seeds) * len(PREPROCESSORS) * 2,
        "seeds": seeds,
        "preprocessors": PREPROCESSORS,
        "transfer": {
            direction: {
                preprocessor: {
                    metric: summarize(values)
                    for metric, values in metric_rows.items()
                }
                for preprocessor, metric_rows in preprocessor_rows.items()
            }
            for direction, preprocessor_rows in metric_values.items()
        },
        "detailed_runs": detailed,
        "claim_boundary": "Per-image non-transductive repair; not blind external validation.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "seed_sweep_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(args.output_dir / "seed_sweep_long.csv", long_rows)
    write_md(args.output_dir / "seed_sweep_summary.md", summary)
    print(json.dumps(summary["transfer"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
