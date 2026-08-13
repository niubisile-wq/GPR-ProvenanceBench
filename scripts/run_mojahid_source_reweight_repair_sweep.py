#!/usr/bin/env python3
"""Run train-only source reweighting repair sweeps on Mojahid grouped splits."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]
WEIGHT_SCHEMES = [
    "uniform",
    "class_balanced",
    "source_balanced",
    "label_source_balanced",
]


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


def normalized_inverse_weights(keys: list[object]) -> np.ndarray:
    counts = Counter(keys)
    weights = np.asarray([1.0 / counts[key] for key in keys], dtype=np.float64)
    return weights / weights.mean()


def build_weights(labels: np.ndarray, sources: np.ndarray, scheme: str) -> np.ndarray | None:
    if scheme == "uniform":
        return None
    if scheme == "class_balanced":
        return normalized_inverse_weights(labels.tolist())
    if scheme == "source_balanced":
        return normalized_inverse_weights(sources.tolist())
    if scheme == "label_source_balanced":
        return normalized_inverse_weights(list(zip(labels.tolist(), sources.tolist())))
    raise ValueError(scheme)


def evaluate(
    train_x: np.ndarray,
    train_y: np.ndarray,
    train_source: np.ndarray,
    test_x: np.ndarray,
    test_y: np.ndarray,
    scheme: str,
    seed: int,
) -> dict[str, float]:
    scaler = StandardScaler()
    scaled_train = scaler.fit_transform(train_x)
    scaled_test = scaler.transform(test_x)
    model = SVC(C=3.0, gamma="scale", random_state=seed)
    model.fit(scaled_train, train_y, sample_weight=build_weights(train_y, train_source, scheme))
    pred = model.predict(scaled_test)
    return {
        "accuracy": float(accuracy_score(test_y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_y, pred)),
        "macro_f1": float(f1_score(test_y, pred, average="macro")),
    }


def protocol_result(
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
    test_idx = np.flatnonzero(folds == test_fold)
    result: dict[str, object] = {
        "protocol": protocol_name,
        "test_fold": test_fold,
        "val_fold": val_fold,
        "seed": seed,
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "train_source_groups": int(len(set(sources[train_idx]))),
        "test_source_groups": int(len(set(sources[test_idx]))),
        "shared_source_groups": int(len(set(sources[train_idx]).intersection(set(sources[test_idx])))),
        "train_label_counts": {str(k): int(v) for k, v in Counter(y[train_idx]).items()},
        "test_label_counts": {str(k): int(v) for k, v in Counter(y[test_idx]).items()},
    }
    for scheme in WEIGHT_SCHEMES:
        result[scheme] = evaluate(
            x[train_idx],
            y[train_idx],
            sources[train_idx],
            x[test_idx],
            y[test_idx],
            scheme,
            seed,
        )
    for scheme in WEIGHT_SCHEMES:
        if scheme != "uniform":
            result[f"delta_{scheme}_minus_uniform"] = {
                metric: float(result[scheme][metric] - result["uniform"][metric])  # type: ignore[index]
                for metric in METRICS
            }
    return result


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def summarize_runs(runs: list[dict[str, object]]) -> dict[str, object]:
    by_protocol: dict[str, list[dict[str, object]]] = defaultdict(list)
    for run in runs:
        by_protocol[str(run["protocol"])].append(run)
    protocols: dict[str, object] = {}
    for protocol, protocol_runs in by_protocol.items():
        item: dict[str, object] = {}
        for scheme in WEIGHT_SCHEMES:
            item[scheme] = {
                metric: summarize([float(run[scheme][metric]) for run in protocol_runs])  # type: ignore[index]
                for metric in METRICS
            }
        for scheme in WEIGHT_SCHEMES:
            if scheme != "uniform":
                key = f"delta_{scheme}_minus_uniform"
                item[key] = {
                    metric: summarize([float(run[key][metric]) for run in protocol_runs])  # type: ignore[index]
                    for metric in METRICS
                }
        protocols[protocol] = item
    return protocols


def flatten_runs(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    flat = []
    for run in runs:
        row = {
            "protocol": run["protocol"],
            "test_fold": run["test_fold"],
            "val_fold": run["val_fold"],
            "seed": run["seed"],
            "train_n": run["train_n"],
            "test_n": run["test_n"],
            "train_source_groups": run["train_source_groups"],
            "test_source_groups": run["test_source_groups"],
            "shared_source_groups": run["shared_source_groups"],
            "train_label_counts": json.dumps(run["train_label_counts"], ensure_ascii=False),
            "test_label_counts": json.dumps(run["test_label_counts"], ensure_ascii=False),
        }
        for scheme in WEIGHT_SCHEMES:
            for metric in METRICS:
                row[f"{scheme}_{metric}"] = run[scheme][metric]  # type: ignore[index]
        for scheme in WEIGHT_SCHEMES:
            if scheme != "uniform":
                for metric in METRICS:
                    row[f"delta_{scheme}_minus_uniform_{metric}"] = run[f"delta_{scheme}_minus_uniform"][metric]  # type: ignore[index]
        flat.append(row)
    return flat


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Mojahid Source Reweighting Repair Sweep",
        "",
        "Scope: train-only source/class reweighting on Mojahid grouped splits.",
        "No target-fold images or labels are used to compute repair parameters.",
        "",
        f"Runs: `{summary['n_runs']}`",
        f"Seeds: `{', '.join(str(seed) for seed in summary['seeds'])}`",
        "",
        "| protocol | uniform BA | class BA | source BA | label-source BA | best delta vs uniform |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for protocol, item in summary["protocols"].items():  # type: ignore[union-attr]
        best_delta = max(
            item[f"delta_{scheme}_minus_uniform"]["balanced_accuracy"]["mean"]  # type: ignore[index]
            for scheme in WEIGHT_SCHEMES
            if scheme != "uniform"
        )
        lines.append(
            f"| {protocol} | "
            f"{item['uniform']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
            f"{item['class_balanced']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
            f"{item['source_balanced']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
            f"{item['label_source_balanced']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
            f"{best_delta:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a strict train-time internal repair experiment. It can bound whether",
            "simple provenance-aware weighting helps on Mojahid, but it is not external",
            "repair validation and cannot close the blind external gate.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data_manifests/mojahid_unified_samples_20260810.csv"))
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("reports/mojahid_source_reweight_repair_20260811"))
    parser.add_argument("--image-size", type=int, default=64)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
    x, y, folds, sources = extract(rows, args.image_size, args.data_root)
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]
    protocols = [
        ("current_fold0_test_fold1_val", 0, 1),
        ("task_aware_fold0_test_fold3_val", 0, 3),
    ]
    runs = [
        protocol_result(x, y, folds, sources, protocol, test_fold, val_fold, seed)
        for seed in seeds
        for protocol, test_fold, val_fold in protocols
    ]
    summary = {
        "run_id": "20260811_E19_mojahid_source_reweight_repair",
        "manifest": str(args.manifest),
        "n_samples": len(rows),
        "n_runs": len(runs),
        "seeds": seeds,
        "weight_schemes": WEIGHT_SCHEMES,
        "protocols": summarize_runs(runs),
        "detailed_runs": runs,
        "blind_external_eligible": False,
        "repair_uses_unlabeled_target_statistics": False,
        "status": "complete_internal_train_only_reweighting_repair",
    }
    (args.output_dir / "source_reweight_repair_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(args.output_dir / "source_reweight_repair_runs.csv", flatten_runs(runs))
    write_md(args.output_dir / "source_reweight_repair_summary.md", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
