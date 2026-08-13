#!/usr/bin/env python3
"""Train-only source-confusion feature-selection repair on Mojahid HOG features."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.feature_selection import f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import LabelEncoder, StandardScaler


METRICS = ["accuracy", "balanced_accuracy", "macro_f1", "nll", "ece_10bin", "mean_confidence"]
ALPHAS = [0.0, 0.5, 1.0, 2.0]
TOP_K_VALUES = [64, 128, 256]


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


def finite_f_score(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    score, _ = f_classif(x, y)
    return np.nan_to_num(score, nan=0.0, posinf=0.0, neginf=0.0)


def select_features(train_x: np.ndarray, train_y: np.ndarray, train_source: np.ndarray, alpha: float, top_k: int) -> np.ndarray:
    target_score = finite_f_score(train_x, train_y)
    source_score = finite_f_score(train_x, train_source)
    if alpha == 0.0:
        score = target_score
    else:
        score = target_score / np.power(source_score + 1e-6, alpha)
    usable_k = min(top_k, train_x.shape[1])
    return np.argsort(score)[::-1][:usable_k]


def fit_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, seed: int) -> np.ndarray:
    model = LogisticRegression(C=3.0, class_weight="balanced", max_iter=3000, random_state=seed)
    model.fit(train_x, train_y)
    return model.predict_proba(test_x)


def run_protocol(
    x: np.ndarray,
    target_y: np.ndarray,
    source_y: np.ndarray,
    folds: np.ndarray,
    protocol: str,
    test_fold: int,
    val_fold: int,
    seed: int,
) -> list[dict[str, object]]:
    train_idx = np.flatnonzero(~np.isin(folds, [test_fold, val_fold]))
    test_idx = np.flatnonzero(folds == test_fold)
    scaler = StandardScaler()
    train_x = scaler.fit_transform(x[train_idx])
    test_x = scaler.transform(x[test_idx])
    labels = sorted(set(target_y.tolist()))
    source_labels = sorted(set(source_y.tolist()))

    rows: list[dict[str, object]] = []
    for alpha in ALPHAS:
        for top_k in TOP_K_VALUES:
            selected = select_features(train_x, target_y[train_idx], source_y[train_idx], alpha, top_k)
            target_probs = fit_predict(train_x[:, selected], target_y[train_idx], test_x[:, selected], seed)
            source_probs = fit_predict(train_x[:, selected], source_y[train_idx], test_x[:, selected], seed)
            rows.append(
                {
                    "protocol": protocol,
                    "seed": seed,
                    "test_fold": test_fold,
                    "val_fold": val_fold,
                    "alpha_source_penalty": alpha,
                    "top_k": int(len(selected)),
                    "strategy": f"target_over_source_alpha_{alpha:g}_top_{len(selected)}",
                    "train_n": int(len(train_idx)),
                    "test_n": int(len(test_idx)),
                    "train_source_counts": {str(k): int(v) for k, v in Counter(source_y[train_idx]).items()},
                    "test_source_counts": {str(k): int(v) for k, v in Counter(source_y[test_idx]).items()},
                    "target": metrics_from_probs(target_probs, target_y[test_idx], labels),
                    "source_probe": metrics_from_probs(source_probs, source_y[test_idx], source_labels),
                }
            )
    baseline = next(row for row in rows if row["alpha_source_penalty"] == 0.0 and row["top_k"] == 256)
    for row in rows:
        row["delta_target_minus_target_top256"] = {
            metric: float(row["target"][metric] - baseline["target"][metric])  # type: ignore[index]
            for metric in METRICS
        }
        row["delta_source_probe_minus_target_top256"] = {
            metric: float(row["source_probe"][metric] - baseline["source_probe"][metric])  # type: ignore[index]
            for metric in METRICS
        }
    return rows


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {"mean": float(arr.mean()), "std": float(arr.std(ddof=0)), "min": float(arr.min()), "max": float(arr.max())}


def summarize_runs(rows: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["protocol"]), str(row["strategy"]))].append(row)
    out: dict[str, object] = {}
    for (protocol, strategy), items in sorted(grouped.items()):
        out.setdefault(protocol, {})
        out[protocol][strategy] = {  # type: ignore[index]
            "alpha_source_penalty": items[0]["alpha_source_penalty"],
            "top_k": items[0]["top_k"],
            "target": {metric: summarize([float(row["target"][metric]) for row in items]) for metric in METRICS},  # type: ignore[index]
            "source_probe": {metric: summarize([float(row["source_probe"][metric]) for row in items]) for metric in METRICS},  # type: ignore[index]
            "delta_target_minus_target_top256": {
                metric: summarize([float(row["delta_target_minus_target_top256"][metric]) for row in items])  # type: ignore[index]
                for metric in METRICS
            },
            "delta_source_probe_minus_target_top256": {
                metric: summarize([float(row["delta_source_probe_minus_target_top256"][metric]) for row in items])  # type: ignore[index]
                for metric in METRICS
            },
        }
    return out


def best_tradeoff(protocol_summary: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for protocol, by_strategy in protocol_summary.items():
        candidates = []
        for strategy, item in by_strategy.items():  # type: ignore[union-attr]
            candidates.append(
                {
                    "protocol": protocol,
                    "strategy": strategy,
                    "alpha_source_penalty": item["alpha_source_penalty"],
                    "top_k": item["top_k"],
                    "target_ba_delta": item["delta_target_minus_target_top256"]["balanced_accuracy"]["mean"],
                    "source_probe_ba_delta": item["delta_source_probe_minus_target_top256"]["balanced_accuracy"]["mean"],
                    "tradeoff_score": item["delta_target_minus_target_top256"]["balanced_accuracy"]["mean"]
                    - max(0.0, item["delta_source_probe_minus_target_top256"]["balanced_accuracy"]["mean"]),
                }
            )
        rows.append(max(candidates, key=lambda row: row["tradeoff_score"]))
    return rows


def flatten_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    flat = []
    for row in rows:
        out = {
            "protocol": row["protocol"],
            "seed": row["seed"],
            "strategy": row["strategy"],
            "alpha_source_penalty": row["alpha_source_penalty"],
            "top_k": row["top_k"],
            "train_n": row["train_n"],
            "test_n": row["test_n"],
        }
        for prefix in ["target", "source_probe", "delta_target_minus_target_top256", "delta_source_probe_minus_target_top256"]:
            for metric in METRICS:
                out[f"{prefix}_{metric}"] = row[prefix][metric]  # type: ignore[index]
        flat.append(out)
    return flat


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Mojahid Source-Confusion Feature Repair",
        "",
        "Scope: train-only HOG feature selection penalizing source-predictive dimensions.",
        "",
        "| protocol | best strategy | target BA delta | source-probe BA delta | tradeoff score |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in result["best_tradeoff_rows"]:
        lines.append(
            f"| {row['protocol']} | {row['strategy']} | {row['target_ba_delta']:+.4f} | "
            f"{row['source_probe_ba_delta']:+.4f} | {row['tradeoff_score']:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Feature selection scores are learned on train folds only. This is an",
            "internal source-confusion repair stress test, not blind external repair",
            "evidence and not a final mitigation claim.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data_manifests/mojahid_unified_samples_20260810.csv"))
    parser.add_argument("--data-root", type=Path, default=Path(r"D:\鐧惧害缃戠洏鎷夊彇鍖匼CNS1\gpr_leakage_research\dataset_inspect\GPR_data"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/mojahid_source_confusion_feature_repair_20260811"))
    parser.add_argument("--image-size", type=int, default=64)
    parser.add_argument("--source-field", default="is_augmented")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
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
    detailed_rows: list[dict[str, object]] = []
    for seed in seeds:
        for protocol, test_fold, val_fold in protocols:
            detailed_rows.extend(run_protocol(x, target_y, source_y, folds, protocol, test_fold, val_fold, seed))
    protocol_summary = summarize_runs(detailed_rows)
    result = {
        "run_id": "20260811_E41_mojahid_source_confusion_feature_repair",
        "manifest": str(args.manifest),
        "n_samples": len(rows),
        "source_field": args.source_field,
        "target_labels": target_encoder.classes_.tolist(),
        "source_labels": source_encoder.classes_.tolist(),
        "seeds": seeds,
        "alphas": ALPHAS,
        "top_k_values": TOP_K_VALUES,
        "protocols": protocol_summary,
        "best_tradeoff_rows": best_tradeoff(protocol_summary),
        "detailed_runs": detailed_rows,
        "repair_uses_test_fold_for_feature_selection": False,
        "repair_uses_unlabeled_target_statistics": False,
        "blind_external_eligible": False,
        "status": "complete_internal_source_confusion_feature_repair",
    }
    (args.output_dir / "source_confusion_feature_repair_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(args.output_dir / "source_confusion_feature_repair_runs.csv", flatten_rows(detailed_rows))
    write_md(args.output_dir / "source_confusion_feature_repair_summary.md", result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "detailed_runs": len(detailed_rows),
                "best_tradeoff_rows": result["best_tradeoff_rows"],
                "blind_external_eligible": result["blind_external_eligible"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
