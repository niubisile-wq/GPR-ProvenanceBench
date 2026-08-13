#!/usr/bin/env python3
"""Run train/val-only temperature calibration on Mojahid grouped splits."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import LabelEncoder, StandardScaler


METRICS = ["accuracy", "balanced_accuracy", "macro_f1", "nll", "ece_10bin", "mean_confidence"]
TEMPERATURE_GRID = np.round(np.linspace(0.5, 5.0, 91), 3)


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


def resolve_image_path(row: dict[str, str], data_root: Path | None) -> Path:
    if data_root is not None:
        path = data_root / row["rel_path"]
        if path.exists():
            return path
    path = Path(row["abs_path"])
    if path.exists():
        return path
    raise FileNotFoundError(f"Missing Mojahid image for sample {row['sample_id']}: {path}")


def extract(
    rows: list[dict[str, str]],
    image_size: int,
    data_root: Path | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    folds: list[int] = []
    sources: list[str] = []
    for row in rows:
        features.append(simple_hog(load_gray(resolve_image_path(row, data_root), image_size)))
        labels.append(row["label"])
        folds.append(int(row["fold_id"]))
        sources.append(row["source_group"])
    return np.stack(features), np.asarray(labels), np.asarray(folds), np.asarray(sources)


def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)


def ece_10bin(probs: np.ndarray, y_true: np.ndarray) -> float:
    pred = probs.argmax(axis=1)
    conf = probs.max(axis=1)
    correct = (pred == y_true).astype(float)
    ece = 0.0
    for low in np.linspace(0.0, 0.9, 10):
        high = low + 0.1
        if high >= 1.0:
            mask = (conf >= low) & (conf <= high)
        else:
            mask = (conf >= low) & (conf < high)
        if np.any(mask):
            ece += float(mask.mean() * abs(correct[mask].mean() - conf[mask].mean()))
    return ece


def metrics_from_probs(probs: np.ndarray, y_true: np.ndarray, labels: list[int]) -> dict[str, float]:
    pred = probs.argmax(axis=1)
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, average="macro")),
        "nll": float(log_loss(y_true, probs, labels=labels)),
        "ece_10bin": ece_10bin(probs, y_true),
        "mean_confidence": float(probs.max(axis=1).mean()),
    }


def tune_temperature(val_logits: np.ndarray, val_y: np.ndarray, labels: list[int]) -> tuple[float, float]:
    best_temperature = 1.0
    best_nll = float("inf")
    for temperature in TEMPERATURE_GRID:
        probs = softmax(val_logits / float(temperature))
        nll = float(log_loss(val_y, probs, labels=labels))
        if nll < best_nll:
            best_nll = nll
            best_temperature = float(temperature)
    return best_temperature, best_nll


def run_protocol(
    x: np.ndarray,
    y: np.ndarray,
    folds: np.ndarray,
    sources: np.ndarray,
    protocol_name: str,
    test_fold: int,
    val_fold: int,
    seed: int,
) -> dict[str, object]:
    train_idx = np.flatnonzero(~np.isin(folds, [test_fold, val_fold]))
    val_idx = np.flatnonzero(folds == val_fold)
    test_idx = np.flatnonzero(folds == test_fold)

    scaler = StandardScaler()
    train_x = scaler.fit_transform(x[train_idx])
    val_x = scaler.transform(x[val_idx])
    test_x = scaler.transform(x[test_idx])
    model = LogisticRegression(C=3.0, class_weight="balanced", max_iter=3000, random_state=seed)
    model.fit(train_x, y[train_idx])
    labels = sorted(set(y.tolist()))
    val_logits = model.decision_function(val_x)
    test_logits = model.decision_function(test_x)
    if val_logits.ndim == 1:
        val_logits = np.column_stack([-val_logits, val_logits])
        test_logits = np.column_stack([-test_logits, test_logits])
    temperature, val_nll = tune_temperature(val_logits, y[val_idx], labels)
    uncalibrated = metrics_from_probs(softmax(test_logits), y[test_idx], labels)
    calibrated = metrics_from_probs(softmax(test_logits / temperature), y[test_idx], labels)
    return {
        "protocol": protocol_name,
        "test_fold": test_fold,
        "val_fold": val_fold,
        "seed": seed,
        "temperature": temperature,
        "validation_nll_at_temperature": val_nll,
        "train_n": int(len(train_idx)),
        "val_n": int(len(val_idx)),
        "test_n": int(len(test_idx)),
        "train_source_groups": int(len(set(sources[train_idx]))),
        "val_source_groups": int(len(set(sources[val_idx]))),
        "test_source_groups": int(len(set(sources[test_idx]))),
        "shared_train_test_source_groups": int(len(set(sources[train_idx]).intersection(set(sources[test_idx])))),
        "test_label_counts": {str(k): int(v) for k, v in Counter(y[test_idx]).items()},
        "uncalibrated": uncalibrated,
        "temperature_calibrated": calibrated,
        "delta_temperature_calibrated_minus_uncalibrated": {
            metric: float(calibrated[metric] - uncalibrated[metric])
            for metric in METRICS
        },
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
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def flatten_runs(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for run in runs:
        row = {
            "protocol": run["protocol"],
            "test_fold": run["test_fold"],
            "val_fold": run["val_fold"],
            "seed": run["seed"],
            "temperature": run["temperature"],
            "validation_nll_at_temperature": run["validation_nll_at_temperature"],
            "train_n": run["train_n"],
            "val_n": run["val_n"],
            "test_n": run["test_n"],
            "shared_train_test_source_groups": run["shared_train_test_source_groups"],
            "test_label_counts": json.dumps(run["test_label_counts"], ensure_ascii=False),
        }
        for stage in ["uncalibrated", "temperature_calibrated", "delta_temperature_calibrated_minus_uncalibrated"]:
            for metric in METRICS:
                row[f"{stage}_{metric}"] = run[stage][metric]  # type: ignore[index]
        rows.append(row)
    return rows


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Mojahid Temperature Calibration Repair",
        "",
        "Scope: train/validation-only post-hoc calibration on Mojahid grouped splits.",
        "The test fold is used once for final evaluation after temperature selection on the validation fold.",
        "",
        "| protocol | T | uncal BA | cal BA | delta BA | uncal ECE | cal ECE | delta ECE |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for protocol, item in summary["protocols"].items():  # type: ignore[union-attr]
        lines.append(
            f"| {protocol} | "
            f"{item['temperature']['mean']:.3f} | "  # type: ignore[index]
            f"{item['uncalibrated']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
            f"{item['temperature_calibrated']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
            f"{item['delta_temperature_calibrated_minus_uncalibrated']['balanced_accuracy']['mean']:+.4f} | "  # type: ignore[index]
            f"{item['uncalibrated']['ece_10bin']['mean']:.4f} | "  # type: ignore[index]
            f"{item['temperature_calibrated']['ece_10bin']['mean']:.4f} | "  # type: ignore[index]
            f"{item['delta_temperature_calibrated_minus_uncalibrated']['ece_10bin']['mean']:+.4f} |"  # type: ignore[index]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Temperature calibration can change confidence and ECE without changing",
            "predicted classes. This is an internal grouped-split repair/calibration",
            "test, not external repair validation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data_manifests/mojahid_unified_samples_20260810.csv"))
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("reports/mojahid_temperature_calibration_repair_20260811"))
    parser.add_argument("--image-size", type=int, default=64)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
    x, labels_raw, folds, sources = extract(rows, args.image_size, args.data_root)
    encoder = LabelEncoder()
    y = encoder.fit_transform(labels_raw)
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]
    protocol_specs = [
        ("current_fold0_test_fold1_val", 0, 1),
        ("task_aware_fold0_test_fold3_val", 0, 3),
    ]
    runs = [
        run_protocol(x, y, folds, sources, protocol, test_fold, val_fold, seed)
        for seed in seeds
        for protocol, test_fold, val_fold in protocol_specs
    ]
    protocols: dict[str, object] = {}
    for protocol, _, _ in protocol_specs:
        protocol_runs = [run for run in runs if run["protocol"] == protocol]
        item: dict[str, object] = {"temperature": summarize([float(run["temperature"]) for run in protocol_runs])}
        for stage in ["uncalibrated", "temperature_calibrated", "delta_temperature_calibrated_minus_uncalibrated"]:
            item[stage] = {
                metric: summarize([float(run[stage][metric]) for run in protocol_runs])  # type: ignore[index]
                for metric in METRICS
            }
        protocols[protocol] = item
    summary = {
        "run_id": "20260811_E20_mojahid_temperature_calibration_repair",
        "manifest": str(args.manifest),
        "n_samples": len(rows),
        "labels": encoder.classes_.tolist(),
        "n_runs": len(runs),
        "seeds": seeds,
        "protocols": protocols,
        "detailed_runs": runs,
        "blind_external_eligible": False,
        "repair_uses_test_fold_for_parameter_selection": False,
        "status": "complete_internal_temperature_calibration_repair",
    }
    (args.output_dir / "temperature_calibration_repair_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(args.output_dir / "temperature_calibration_repair_runs.csv", flatten_runs(runs))
    write_md(args.output_dir / "temperature_calibration_repair_summary.md", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
