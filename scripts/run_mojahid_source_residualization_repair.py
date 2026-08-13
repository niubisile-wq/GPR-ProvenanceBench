#!/usr/bin/env python3
"""Train-only source-direction residualization repair on Mojahid HOG features."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import LabelEncoder, StandardScaler


METRICS = ["accuracy", "balanced_accuracy", "macro_f1", "nll", "ece_10bin", "mean_confidence"]
K_VALUES = [0, 1]


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
    source_field: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    folds: list[int] = []
    sources: list[str] = []
    for row in rows:
        features.append(simple_hog(load_gray(resolve_image_path(row, data_root), image_size)))
        labels.append(row["label"])
        folds.append(int(row["fold_id"]))
        sources.append(row[source_field])
    return np.stack(features), np.asarray(labels), np.asarray(folds), np.asarray(sources)


def ece_10bin(probs: np.ndarray, y_true: np.ndarray) -> float:
    pred = probs.argmax(axis=1)
    conf = probs.max(axis=1)
    correct = (pred == y_true).astype(float)
    ece = 0.0
    for low in np.linspace(0.0, 0.9, 10):
        high = low + 0.1
        mask = (conf >= low) & (conf <= high if high >= 1.0 else conf < high)
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


def source_basis(train_x: np.ndarray, source_y: np.ndarray, max_k: int, seed: int) -> np.ndarray:
    del seed
    means = []
    global_mean = train_x.mean(axis=0, keepdims=True)
    for source in sorted(set(source_y.tolist())):
        means.append(train_x[source_y == source].mean(axis=0) - global_mean.ravel())
    coef = np.stack(means)
    _, _, vt = np.linalg.svd(coef, full_matrices=False)
    return vt[:max_k].T


def residualize(x: np.ndarray, basis: np.ndarray, k: int) -> np.ndarray:
    if k <= 0:
        return x
    selected = basis[:, :k]
    return x - (x @ selected) @ selected.T


def target_metrics(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray, seed: int) -> dict[str, float]:
    model = LogisticRegression(C=3.0, class_weight="balanced", max_iter=3000, random_state=seed)
    model.fit(train_x, train_y)
    probs = model.predict_proba(test_x)
    return metrics_from_probs(probs, test_y, sorted(set(train_y.tolist())))


def source_metrics(train_x: np.ndarray, train_source: np.ndarray, test_x: np.ndarray, test_source: np.ndarray, seed: int) -> dict[str, float]:
    del seed
    classes = np.asarray(sorted(set(train_source.tolist())))
    centroids = np.stack([train_x[train_source == cls].mean(axis=0) for cls in classes])
    train_counts = Counter(train_source.tolist())
    # Add a mild prior correction so large source groups do not dominate by density.
    priors = np.asarray([np.log(train_counts[int(cls)] + 1.0) for cls in classes])
    centroid_norm = (centroids * centroids).sum(axis=1)
    pred_chunks = []
    for start in range(0, len(test_x), 128):
        chunk = test_x[start : start + 128]
        distances = (
            (chunk * chunk).sum(axis=1, keepdims=True)
            + centroid_norm[None, :]
            - 2.0 * (chunk @ centroids.T)
            + 0.01 * priors[None, :]
        )
        pred_chunks.append(classes[np.argmin(distances, axis=1)])
    pred = np.concatenate(pred_chunks)
    return {
        "accuracy": float(accuracy_score(test_source, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(test_source, pred)),
        "macro_f1": float(f1_score(test_source, pred, average="macro", zero_division=0)),
    }


def run_protocol(
    x: np.ndarray,
    target_y: np.ndarray,
    source_y: np.ndarray,
    folds: np.ndarray,
    protocol_name: str,
    test_fold: int,
    val_fold: int,
    seed: int,
) -> list[dict[str, object]]:
    train_idx = np.flatnonzero(~np.isin(folds, [test_fold, val_fold]))
    test_idx = np.flatnonzero(folds == test_fold)
    scaler = StandardScaler()
    train_x = scaler.fit_transform(x[train_idx])
    test_x = scaler.transform(x[test_idx])
    max_k = min(max(K_VALUES), train_x.shape[1], len(set(source_y[train_idx])) - 1)
    basis = source_basis(train_x, source_y[train_idx], max_k, seed)
    rows = []
    for k in K_VALUES:
        usable_k = min(k, basis.shape[1])
        repaired_train = residualize(train_x, basis, usable_k)
        repaired_test = residualize(test_x, basis, usable_k)
        tgt = target_metrics(repaired_train, target_y[train_idx], repaired_test, target_y[test_idx], seed)
        src = source_metrics(repaired_train, source_y[train_idx], repaired_test, source_y[test_idx], seed)
        rows.append(
            {
                "protocol": protocol_name,
                "seed": seed,
                "test_fold": test_fold,
                "val_fold": val_fold,
                "removed_source_directions": usable_k,
                "train_n": int(len(train_idx)),
                "test_n": int(len(test_idx)),
        "train_source_classes": int(len(set(source_y[train_idx]))),
        "test_source_classes": int(len(set(source_y[test_idx]))),
        "shared_source_classes": int(len(set(source_y[train_idx]).intersection(set(source_y[test_idx])))),
                "train_target_counts": {str(k): int(v) for k, v in Counter(target_y[train_idx]).items()},
                "test_target_counts": {str(k): int(v) for k, v in Counter(target_y[test_idx]).items()},
                "target": tgt,
                "source_probe": src,
            }
        )
    base_target = rows[0]["target"]
    base_source = rows[0]["source_probe"]
    for row in rows:
        row["delta_target_minus_k0"] = {
            metric: float(row["target"][metric] - base_target[metric])  # type: ignore[index]
            for metric in METRICS
        }
        row["delta_source_probe_minus_k0"] = {
            metric: float(row["source_probe"][metric] - base_source[metric])  # type: ignore[index]
            for metric in ["accuracy", "balanced_accuracy", "macro_f1"]
        }
    return rows


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def summarize_runs(rows: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["protocol"]), int(row["removed_source_directions"]))].append(row)
    summary: dict[str, object] = {}
    for (protocol, k), items in sorted(grouped.items()):
        summary.setdefault(protocol, {})
        summary[protocol][str(k)] = {  # type: ignore[index]
            "target": {metric: summarize([float(item["target"][metric]) for item in items]) for metric in METRICS},  # type: ignore[index]
            "source_probe": {
                metric: summarize([float(item["source_probe"][metric]) for item in items])  # type: ignore[index]
                for metric in ["accuracy", "balanced_accuracy", "macro_f1"]
            },
            "delta_target_minus_k0": {
                metric: summarize([float(item["delta_target_minus_k0"][metric]) for item in items])  # type: ignore[index]
                for metric in METRICS
            },
            "delta_source_probe_minus_k0": {
                metric: summarize([float(item["delta_source_probe_minus_k0"][metric]) for item in items])  # type: ignore[index]
                for metric in ["accuracy", "balanced_accuracy", "macro_f1"]
            },
        }
    return summary


def choose_best_tradeoff(protocol_summary: dict[str, object]) -> dict[str, object]:
    choices = []
    for protocol, by_k in protocol_summary.items():
        for k, item in by_k.items():  # type: ignore[union-attr]
            choices.append(
                {
                    "protocol": protocol,
                    "removed_source_directions": int(k),
                    "target_ba_delta": item["delta_target_minus_k0"]["balanced_accuracy"]["mean"],  # type: ignore[index]
                    "source_ba_delta": item["delta_source_probe_minus_k0"]["balanced_accuracy"]["mean"],  # type: ignore[index]
                    "target_ba": item["target"]["balanced_accuracy"]["mean"],  # type: ignore[index]
                    "source_ba": item["source_probe"]["balanced_accuracy"]["mean"],  # type: ignore[index]
                }
            )
    feasible = [row for row in choices if row["removed_source_directions"] > 0 and row["target_ba_delta"] >= -0.01]
    if not feasible:
        feasible = [row for row in choices if row["removed_source_directions"] > 0]
    return min(feasible, key=lambda row: (row["source_ba_delta"], -row["target_ba_delta"]))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    flat = []
    for row in rows:
        out = {k: v for k, v in row.items() if k not in {"target", "source_probe", "delta_target_minus_k0", "delta_source_probe_minus_k0"}}
        for group in ["target", "source_probe", "delta_target_minus_k0", "delta_source_probe_minus_k0"]:
            for metric, value in row[group].items():  # type: ignore[index]
                out[f"{group}_{metric}"] = value
        out["train_target_counts"] = json.dumps(out["train_target_counts"], ensure_ascii=False)
        out["test_target_counts"] = json.dumps(out["test_target_counts"], ensure_ascii=False)
        flat.append(out)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(flat)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Mojahid Source-Direction Residualization Repair",
        "",
        f"Scope: train-only projection removal of `{result['source_field']}`-discriminative HOG directions.",
        "The source basis is learned on training folds only, then applied to test folds.",
        "",
        "| protocol | removed dirs | target BA | target BA delta | source BA | source BA delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for protocol, by_k in result["protocols"].items():  # type: ignore[union-attr]
        for k, item in by_k.items():  # type: ignore[union-attr]
            lines.append(
                f"| {protocol} | {k} | "
                f"{item['target']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
                f"{item['delta_target_minus_k0']['balanced_accuracy']['mean']:+.4f} | "  # type: ignore[index]
                f"{item['source_probe']['balanced_accuracy']['mean']:.4f} | "  # type: ignore[index]
                f"{item['delta_source_probe_minus_k0']['balanced_accuracy']['mean']:+.4f} |"  # type: ignore[index]
            )
    best = result["best_tradeoff"]
    lines.extend(
        [
            "",
            "## Best Tradeoff",
            "",
            f"- Protocol: `{best['protocol']}`",
            f"- Removed source directions: `{best['removed_source_directions']}`",
            f"- Target BA delta: `{best['target_ba_delta']:+.4f}`",
            f"- Source probe BA delta: `{best['source_ba_delta']:+.4f}`",
            "",
            "## Boundary",
            "",
            "This is an internal representation-repair stress test. It can show whether",
            "simple linear source residualization suppresses source information, but it",
            "does not establish external repair benefit.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data_manifests/mojahid_unified_samples_20260810.csv"))
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("reports/mojahid_source_residualization_repair_20260811"))
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--source-field", type=str, default="is_augmented")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
    if rows and args.source_field not in rows[0]:
        raise KeyError(f"source field not in manifest: {args.source_field}")
    x, labels_raw, folds, sources_raw = extract(rows, args.image_size, args.data_root, args.source_field)
    target_encoder = LabelEncoder()
    source_encoder = LabelEncoder()
    target_y = target_encoder.fit_transform(labels_raw)
    source_y = source_encoder.fit_transform(sources_raw)
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]
    protocols = [
        ("current_fold0_test_fold1_val", 0, 1),
        ("task_aware_fold0_test_fold3_val", 0, 3),
    ]
    detail_rows = []
    for seed in seeds:
        for protocol, test_fold, val_fold in protocols:
            detail_rows.extend(run_protocol(x, target_y, source_y, folds, protocol, test_fold, val_fold, seed))
    protocol_summary = summarize_runs(detail_rows)
    result = {
        "run_id": "20260811_E21_mojahid_source_residualization_repair",
        "manifest": str(args.manifest),
        "source_field": args.source_field,
        "n_samples": len(rows),
        "target_labels": target_encoder.classes_.tolist(),
        "source_classes": int(len(source_encoder.classes_)),
        "seeds": seeds,
        "removed_source_direction_grid": K_VALUES,
        "protocols": protocol_summary,
        "best_tradeoff": choose_best_tradeoff(protocol_summary),
        "detailed_runs": detail_rows,
        "blind_external_eligible": False,
        "source_basis_uses_test_fold": False,
        "status": "complete_internal_source_residualization_repair",
    }
    (args.output_dir / "source_residualization_repair_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(args.output_dir / "source_residualization_repair_runs.csv", detail_rows)
    write_md(args.output_dir / "source_residualization_repair_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
