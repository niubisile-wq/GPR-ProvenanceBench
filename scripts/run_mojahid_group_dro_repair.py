#!/usr/bin/env python3
"""Run train-only group-DRO repair stress test on Mojahid HOG features."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import LabelEncoder, StandardScaler


METRICS = [
    "accuracy",
    "balanced_accuracy",
    "macro_f1",
    "nll",
    "ece_10bin",
    "mean_confidence",
    "worst_source_accuracy",
    "source_accuracy_spread",
]
STRATEGIES = ["erm", "source_group_dro", "label_source_group_dro", "processing_role_dro"]


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
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    folds: list[int] = []
    sources: list[str] = []
    processing_roles: list[str] = []
    for row in rows:
        features.append(simple_hog(load_gray(resolve_image_path(row, data_root), image_size)))
        labels.append(row["label"])
        folds.append(int(row["fold_id"]))
        sources.append(row["source_group"])
        processing_roles.append(row["is_augmented"])
    return (
        np.stack(features),
        np.asarray(labels),
        np.asarray(folds),
        np.asarray(sources),
        np.asarray(processing_roles),
    )


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
        mask = (conf >= low) & (conf <= high if high >= 1.0 else conf < high)
        if np.any(mask):
            ece += float(mask.mean() * abs(correct[mask].mean() - conf[mask].mean()))
    return ece


def source_accuracy_stats(pred: np.ndarray, y_true: np.ndarray, sources: np.ndarray) -> dict[str, float]:
    values = []
    for source in sorted(set(sources.tolist())):
        mask = sources == source
        if int(mask.sum()) >= 3:
            values.append(float((pred[mask] == y_true[mask]).mean()))
    if not values:
        return {"worst_source_accuracy": float("nan"), "source_accuracy_spread": float("nan")}
    arr = np.asarray(values, dtype=np.float64)
    return {
        "worst_source_accuracy": float(arr.min()),
        "source_accuracy_spread": float(arr.max() - arr.min()),
    }


def metrics_from_probs(probs: np.ndarray, y_true: np.ndarray, labels: list[int], sources: np.ndarray) -> dict[str, float]:
    pred = probs.argmax(axis=1)
    out = {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "macro_f1": float(f1_score(y_true, pred, average="macro")),
        "nll": float(log_loss(y_true, probs, labels=labels)),
        "ece_10bin": ece_10bin(probs, y_true),
        "mean_confidence": float(probs.max(axis=1).mean()),
    }
    out.update(source_accuracy_stats(pred, y_true, sources))
    return out


def one_hot(y: np.ndarray, n_classes: int) -> np.ndarray:
    out = np.zeros((len(y), n_classes), dtype=np.float64)
    out[np.arange(len(y)), y] = 1.0
    return out


def group_keys(strategy: str, y: np.ndarray, sources: np.ndarray, processing_roles: np.ndarray) -> np.ndarray:
    if strategy == "erm":
        return np.asarray(["all"] * len(y), dtype=object)
    if strategy == "source_group_dro":
        return sources.astype(object)
    if strategy == "label_source_group_dro":
        return np.asarray([f"{label}|{source}" for label, source in zip(y.tolist(), sources.tolist())], dtype=object)
    if strategy == "processing_role_dro":
        return processing_roles.astype(object)
    raise ValueError(strategy)


def train_softmax(
    train_x: np.ndarray,
    train_y: np.ndarray,
    group: np.ndarray,
    seed: int,
    strategy: str,
    epochs: int,
    lr: float,
    dro_eta: float,
    l2: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    rng = np.random.default_rng(seed)
    n_samples, n_features = train_x.shape
    n_classes = int(train_y.max()) + 1
    weight = rng.normal(0.0, 0.01, size=(n_features, n_classes))
    bias = np.zeros(n_classes, dtype=np.float64)
    y_oh = one_hot(train_y, n_classes)
    group_names = np.asarray(sorted(set(group.tolist())), dtype=object)
    group_masks = [np.flatnonzero(group == name) for name in group_names]
    q = np.ones(len(group_names), dtype=np.float64) / max(len(group_names), 1)
    trace = []
    for epoch in range(epochs):
        probs = softmax(train_x @ weight + bias)
        diff = probs - y_oh
        losses = -np.log(np.clip(probs[np.arange(n_samples), train_y], 1e-12, 1.0))
        if strategy == "erm":
            grad_w = (train_x.T @ diff) / n_samples + l2 * weight
            grad_b = diff.mean(axis=0)
            mean_loss = float(losses.mean())
            worst_loss = mean_loss
        else:
            group_losses = np.asarray([float(losses[mask].mean()) for mask in group_masks], dtype=np.float64)
            q *= np.exp(dro_eta * (group_losses - group_losses.max()))
            q /= q.sum()
            grad_w = np.zeros_like(weight)
            grad_b = np.zeros_like(bias)
            for q_value, mask in zip(q, group_masks):
                grad_w += q_value * (train_x[mask].T @ diff[mask]) / len(mask)
                grad_b += q_value * diff[mask].mean(axis=0)
            grad_w += l2 * weight
            mean_loss = float(losses.mean())
            worst_loss = float(group_losses.max())
        weight -= lr * grad_w
        bias -= lr * grad_b
        if epoch in {0, epochs - 1} or (epoch + 1) % 100 == 0:
            trace.append(
                {
                    "epoch": epoch + 1,
                    "mean_train_loss": mean_loss,
                    "worst_group_train_loss": worst_loss,
                    "max_group_weight": float(q.max()),
                }
            )
    return weight, bias, {
        "train_group_count": int(len(group_names)),
        "train_group_min_n": int(min(len(mask) for mask in group_masks)),
        "train_group_max_n": int(max(len(mask) for mask in group_masks)),
        "max_final_group_weight": float(q.max()),
        "trace": trace,
    }


def run_protocol(
    x: np.ndarray,
    y: np.ndarray,
    folds: np.ndarray,
    sources: np.ndarray,
    processing_roles: np.ndarray,
    protocol: str,
    test_fold: int,
    val_fold: int,
    seed: int,
    epochs: int,
    lr: float,
    dro_eta: float,
    l2: float,
) -> dict[str, object]:
    train_idx = np.flatnonzero(~np.isin(folds, [test_fold, val_fold]))
    test_idx = np.flatnonzero(folds == test_fold)
    scaler = StandardScaler()
    train_x = scaler.fit_transform(x[train_idx]).astype(np.float64)
    test_x = scaler.transform(x[test_idx]).astype(np.float64)
    result: dict[str, object] = {
        "protocol": protocol,
        "test_fold": test_fold,
        "val_fold": val_fold,
        "seed": seed,
        "train_n": int(len(train_idx)),
        "test_n": int(len(test_idx)),
        "shared_source_groups": int(len(set(sources[train_idx]).intersection(set(sources[test_idx])))),
    }
    labels = sorted(set(y.tolist()))
    for strategy in STRATEGIES:
        keys = group_keys(strategy, y[train_idx], sources[train_idx], processing_roles[train_idx])
        weight, bias, train_info = train_softmax(train_x, y[train_idx], keys, seed, strategy, epochs, lr, dro_eta, l2)
        probs = softmax(test_x @ weight + bias)
        result[strategy] = metrics_from_probs(probs, y[test_idx], labels, sources[test_idx])
        result[f"{strategy}_train_info"] = train_info
    for strategy in STRATEGIES:
        if strategy != "erm":
            result[f"delta_{strategy}_minus_erm"] = {
                metric: float(result[strategy][metric] - result["erm"][metric])  # type: ignore[index]
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
    out: dict[str, object] = {}
    for protocol, items in by_protocol.items():
        out[protocol] = {}
        for strategy in STRATEGIES:
            out[protocol][strategy] = {  # type: ignore[index]
                metric: summarize([float(row[strategy][metric]) for row in items])  # type: ignore[index]
                for metric in METRICS
            }
        for strategy in STRATEGIES:
            if strategy != "erm":
                key = f"delta_{strategy}_minus_erm"
                out[protocol][key] = {  # type: ignore[index]
                    metric: summarize([float(row[key][metric]) for row in items])  # type: ignore[index]
                    for metric in METRICS
                }
    return out


def flatten_runs(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for run in runs:
        row = {
            "protocol": run["protocol"],
            "test_fold": run["test_fold"],
            "val_fold": run["val_fold"],
            "seed": run["seed"],
            "train_n": run["train_n"],
            "test_n": run["test_n"],
            "shared_source_groups": run["shared_source_groups"],
        }
        for strategy in STRATEGIES:
            for metric in METRICS:
                row[f"{strategy}_{metric}"] = run[strategy][metric]  # type: ignore[index]
            info = run[f"{strategy}_train_info"]
            row[f"{strategy}_train_group_count"] = info["train_group_count"]  # type: ignore[index]
            row[f"{strategy}_max_final_group_weight"] = info["max_final_group_weight"]  # type: ignore[index]
        for strategy in STRATEGIES:
            if strategy != "erm":
                for metric in METRICS:
                    row[f"delta_{strategy}_minus_erm_{metric}"] = run[f"delta_{strategy}_minus_erm"][metric]  # type: ignore[index]
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Mojahid Group-DRO Repair",
        "",
        "Scope: train-only source-robust optimization on Mojahid HOG features.",
        "No test-fold labels or target-fold statistics are used to choose repair parameters.",
        "",
        "| protocol | strategy | BA | BA delta | worst-source acc | worst-source delta | ECE | ECE delta |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for protocol, item in result["protocols"].items():  # type: ignore[union-attr]
        erm = item["erm"]  # type: ignore[index]
        for strategy in STRATEGIES:
            metrics = item[strategy]  # type: ignore[index]
            if strategy == "erm":
                delta_ba = 0.0
                delta_worst = 0.0
                delta_ece = 0.0
            else:
                delta = item[f"delta_{strategy}_minus_erm"]  # type: ignore[index]
                delta_ba = delta["balanced_accuracy"]["mean"]
                delta_worst = delta["worst_source_accuracy"]["mean"]
                delta_ece = delta["ece_10bin"]["mean"]
            lines.append(
                f"| {protocol} | {strategy} | "
                f"{metrics['balanced_accuracy']['mean']:.4f} | {delta_ba:+.4f} | "
                f"{metrics['worst_source_accuracy']['mean']:.4f} | {delta_worst:+.4f} | "
                f"{metrics['ece_10bin']['mean']:.4f} | {delta_ece:+.4f} |"
            )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is an internal train-time repair stress test. It can indicate whether",
            "source-robust optimization helps the Mojahid grouped protocols, but it",
            "does not establish blind external repair benefit.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data_manifests/mojahid_unified_samples_20260810.csv"))
    parser.add_argument("--data-root", type=Path, default=Path(r"<LOCAL_DATA_ROOT>\gpr_leakage_research\dataset_inspect\GPR_data"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/mojahid_group_dro_repair_20260811"))
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=600)
    parser.add_argument("--lr", type=float, default=0.08)
    parser.add_argument("--dro-eta", type=float, default=0.08)
    parser.add_argument("--l2", type=float, default=1e-4)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
    x, labels_raw, folds, sources, processing_roles = extract(rows, args.image_size, args.data_root)
    encoder = LabelEncoder()
    y = encoder.fit_transform(labels_raw)
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]
    protocols = [
        ("current_fold0_test_fold1_val", 0, 1),
        ("task_aware_fold0_test_fold3_val", 0, 3),
    ]
    runs = []
    for seed in seeds:
        for protocol, test_fold, val_fold in protocols:
            runs.append(
                run_protocol(
                    x,
                    y,
                    folds,
                    sources,
                    processing_roles,
                    protocol,
                    test_fold,
                    val_fold,
                    seed,
                    args.epochs,
                    args.lr,
                    args.dro_eta,
                    args.l2,
                )
            )
    protocol_summary = summarize_runs(runs)
    result = {
        "run_id": "20260811_E27_mojahid_group_dro_repair",
        "manifest": str(args.manifest),
        "n_samples": len(rows),
        "target_labels": encoder.classes_.tolist(),
        "seeds": seeds,
        "strategies": STRATEGIES,
        "protocols": protocol_summary,
        "detailed_runs": runs,
        "blind_external_eligible": False,
        "repair_uses_unlabeled_target_statistics": False,
        "repair_uses_test_fold_for_parameter_selection": False,
        "status": "complete_internal_group_dro_repair",
    }
    (args.output_dir / "group_dro_repair_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(args.output_dir / "group_dro_repair_runs.csv", flatten_runs(runs))
    write_md(args.output_dir / "group_dro_repair_summary.md", result)
    print(
        json.dumps(
            {
                "run_id": result["run_id"],
                "status": result["status"],
                "n_runs": len(runs),
                "strategies": STRATEGIES,
                "blind_external_eligible": result["blind_external_eligible"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
