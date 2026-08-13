#!/usr/bin/env python3
"""Run lightweight provenance/source predictability experiments.

These tests measure whether image features carry recoverable source signals.
They are not target-recognition tests and they do not replace blind external
validation.
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
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier


SEEDS = [20260811, 20260812, 20260813, 20260814, 20260815]
METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def resolve_path(row: dict[str, str], data_root: Path | None) -> Path:
    abs_path = row.get("abs_path", "").strip()
    if abs_path:
        path = Path(abs_path)
        if path.exists():
            return path
    if data_root is not None:
        path = data_root / row["rel_path"]
        if path.exists():
            return path
    raise FileNotFoundError(row.get("sample_id", row.get("rel_path", "<unknown>")))


def load_gray(path: Path, size: int) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((size, size), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    return arr / 255.0


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


def extract_features(rows: list[dict[str, str]], data_root: Path | None, image_size: int) -> np.ndarray:
    features = [simple_hog(load_gray(resolve_path(row, data_root), image_size)) for row in rows]
    return np.stack(features)


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            class_weight="balanced",
            random_state=seed,
            max_iter=1000,
            tol=1e-3,
        ),
    )


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def stratify_key(rows: list[dict[str, str]], y: np.ndarray, include_target_label: bool) -> np.ndarray | None:
    if not include_target_label:
        return y
    keys = np.asarray([f"{target}::{source}" for target, source in zip((row["label"] for row in rows), y)])
    counts = Counter(keys)
    if min(counts.values()) < 2:
        return y
    return keys


def run_task(
    task_name: str,
    rows: list[dict[str, str]],
    x: np.ndarray,
    y: np.ndarray,
    include_target_label_in_stratify: bool,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    if len(set(y)) < 2:
        raise ValueError(f"{task_name} has fewer than two source classes")

    metric_values: dict[str, list[float]] = defaultdict(list)
    long_rows: list[dict[str, object]] = []
    detailed: list[dict[str, object]] = []
    class_counts = Counter(str(item) for item in y)
    stratify = stratify_key(rows, y, include_target_label_in_stratify)
    for seed in SEEDS:
        train_idx, test_idx = train_test_split(
            np.arange(len(y)),
            test_size=0.30,
            random_state=seed,
            stratify=stratify,
        )
        model = make_model(seed)
        model.fit(x[train_idx], y[train_idx])
        pred = model.predict(x[test_idx])
        metrics = {
            "accuracy": float(accuracy_score(y[test_idx], pred)),
            "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)),
            "macro_f1": float(f1_score(y[test_idx], pred, average="macro")),
        }
        detailed.append(
            {
                "seed": seed,
                "train_samples": int(len(train_idx)),
                "test_samples": int(len(test_idx)),
                **metrics,
            }
        )
        for metric, value in metrics.items():
            metric_values[metric].append(value)
            long_rows.append({"task": task_name, "seed": seed, "metric": metric, "value": value})

    chance_balanced = 1.0 / float(len(class_counts))
    majority_accuracy = max(class_counts.values()) / float(sum(class_counts.values()))
    summary = {
        "task": task_name,
        "samples": int(len(rows)),
        "classes": int(len(class_counts)),
        "class_count_min": int(min(class_counts.values())),
        "class_count_max": int(max(class_counts.values())),
        "chance_balanced_accuracy": chance_balanced,
        "majority_accuracy": majority_accuracy,
        "metrics": {metric: summarize(values) for metric, values in metric_values.items()},
        "detailed_runs": detailed,
    }
    return summary, long_rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Source Predictability Sweep",
        "",
        f"Runs per task: `{len(SEEDS)}`",
        "",
        "| task | samples | classes | balanced accuracy | chance BA | accuracy | majority acc | macro-F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for task in summary["tasks"]:
        metrics = task["metrics"]
        lines.append(
            f"| {task['task']} | {task['samples']} | {task['classes']} | "
            f"{metrics['balanced_accuracy']['mean']:.4f} | {task['chance_balanced_accuracy']:.4f} | "
            f"{metrics['accuracy']['mean']:.4f} | {task['majority_accuracy']:.4f} | "
            f"{metrics['macro_f1']['mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: these are internal source-signal probes. They show whether",
            "provenance or processing lineage is learnable from images, but they do",
            "not measure blind external generalization.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mojahid-manifest", type=Path, required=True)
    parser.add_argument("--ressam-manifest", type=Path, required=True)
    parser.add_argument("--mojahid-data-root", type=Path)
    parser.add_argument("--ressam-data-root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--min-lineage-samples", type=int, default=8)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    mojahid_rows_all = read_rows(args.mojahid_manifest)
    mojahid_role_rows = [row for row in mojahid_rows_all if row.get("is_augmented", "") in {"0", "1"}]
    lineage_counts = Counter(row["source_group"] for row in mojahid_rows_all if row.get("source_group", ""))
    mojahid_lineage_rows = [
        row
        for row in mojahid_rows_all
        if lineage_counts.get(row.get("source_group", ""), 0) >= args.min_lineage_samples
    ]
    ressam_rows = [row for row in read_rows(args.ressam_manifest) if row.get("source_group") in {"real_world", "synthetic"}]

    mojahid_role_x = extract_features(mojahid_role_rows, args.mojahid_data_root, args.image_size)
    mojahid_lineage_x = extract_features(mojahid_lineage_rows, args.mojahid_data_root, args.image_size)
    ressam_x = extract_features(ressam_rows, args.ressam_data_root, args.image_size)

    task_summaries: list[dict[str, object]] = []
    long_rows: list[dict[str, object]] = []
    task, rows = run_task(
        "mojahid_processing_role_is_augmented",
        mojahid_role_rows,
        mojahid_role_x,
        np.asarray([row["is_augmented"] for row in mojahid_role_rows]),
        include_target_label_in_stratify=True,
    )
    task_summaries.append(task)
    long_rows.extend(rows)

    task, rows = run_task(
        "mojahid_augmentation_lineage_source_group",
        mojahid_lineage_rows,
        mojahid_lineage_x,
        np.asarray([row["source_group"] for row in mojahid_lineage_rows]),
        include_target_label_in_stratify=False,
    )
    task_summaries.append(task)
    long_rows.extend(rows)

    task, rows = run_task(
        "ressam_environment_source_group",
        ressam_rows,
        ressam_x,
        np.asarray([row["source_group"] for row in ressam_rows]),
        include_target_label_in_stratify=True,
    )
    task_summaries.append(task)
    long_rows.extend(rows)

    summary = {
        "run_id": "20260811_E07_source_predictability_sweep",
        "seeds": SEEDS,
        "image_size": args.image_size,
        "tasks": task_summaries,
        "claim_boundary": "Internal source/provenance signal probe; not blind external validation.",
    }
    (args.output_dir / "source_predictability_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "source_predictability_long.csv", long_rows)
    write_md(args.output_dir / "source_predictability_summary.md", summary)
    print(json.dumps(task_summaries, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
