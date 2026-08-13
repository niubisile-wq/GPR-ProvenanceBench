#!/usr/bin/env python3
"""Run Mojahid lineage leakage-dose experiments.

The clean baseline keeps source groups separated by the frozen grouped fold.
Dose runs intentionally break that boundary for a controlled fraction of test
source groups by moving part of each selected group into training while leaving
the rest in test. This quantifies how augmentation-lineage leakage changes
apparent performance.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


DOSES = [0.0, 0.05, 0.10, 0.20, 0.40]
METRICS = [
    "accuracy",
    "balanced_accuracy",
    "macro_f1",
    "mean_confidence",
    "correct_mean_confidence",
    "incorrect_mean_confidence",
    "ece_10bin",
    "worst_class_recall",
    "class_recall_spread",
    "prediction_entropy",
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


def extract(rows: list[dict[str, str]], data_root: Path, image_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    folds: list[int] = []
    groups: list[str] = []
    for row in rows:
        image_path = data_root / row["rel_path"]
        if not image_path.exists():
            raise FileNotFoundError(f"Missing Mojahid image: {image_path}")
        features.append(simple_hog(load_gray(image_path, image_size)))
        labels.append(row["label"])
        folds.append(int(row["fold_id"]))
        groups.append(row["source_group"])
    return np.stack(features), np.asarray(labels), np.asarray(folds), np.asarray(groups)


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        SVC(C=3.0, gamma="scale", class_weight="balanced", probability=True, random_state=seed),
    )


def expected_calibration_error(correct: np.ndarray, confidence: np.ndarray, n_bins: int = 10) -> float:
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total = len(confidence)
    ece = 0.0
    for low, high in zip(edges[:-1], edges[1:]):
        if high == 1.0:
            mask = (confidence >= low) & (confidence <= high)
        else:
            mask = (confidence >= low) & (confidence < high)
        if not np.any(mask):
            continue
        bin_acc = float(correct[mask].mean())
        bin_conf = float(confidence[mask].mean())
        ece += float(mask.mean()) * abs(bin_acc - bin_conf)
    return float(ece)


def normalized_entropy(values: np.ndarray, labels: list[str]) -> float:
    counts = np.asarray([np.sum(values == label) for label in labels], dtype=np.float64)
    probs = counts / max(1.0, counts.sum())
    probs = probs[probs > 0]
    if len(labels) <= 1:
        return 0.0
    return float(-(probs * np.log(probs)).sum() / np.log(float(len(labels))))


def evaluate(x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, seed: int) -> dict[str, object]:
    model = make_model(seed)
    model.fit(x[train_idx], y[train_idx])
    pred = model.predict(x[test_idx])
    proba = model.predict_proba(x[test_idx])
    confidence = np.max(proba, axis=1)
    correct = pred == y[test_idx]
    incorrect_confidence = confidence[~correct]
    class_labels = sorted(set(y[train_idx]) | set(y[test_idx]))
    per_class_recall: dict[str, float] = {}
    for label in class_labels:
        mask = y[test_idx] == label
        per_class_recall[str(label)] = float(np.mean(pred[mask] == label)) if np.any(mask) else 0.0
    recalls = np.asarray(list(per_class_recall.values()), dtype=np.float64)
    return {
        "accuracy": float(accuracy_score(y[test_idx], pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)),
        "macro_f1": float(f1_score(y[test_idx], pred, average="macro")),
        "mean_confidence": float(confidence.mean()),
        "correct_mean_confidence": float(confidence[correct].mean()) if np.any(correct) else 0.0,
        "incorrect_mean_confidence": float(incorrect_confidence.mean()) if len(incorrect_confidence) else 0.0,
        "ece_10bin": expected_calibration_error(correct.astype(np.float32), confidence, n_bins=10),
        "worst_class_recall": float(recalls.min()),
        "class_recall_spread": float(recalls.max() - recalls.min()),
        "prediction_entropy": normalized_entropy(pred, class_labels),
        "per_class_recall": per_class_recall,
    }


def group_label(labels: np.ndarray, idx: np.ndarray) -> str:
    counts = Counter(labels[idx])
    return str(counts.most_common(1)[0][0])


def choose_leaked_groups(
    labels: np.ndarray,
    groups: np.ndarray,
    test_idx: np.ndarray,
    dose: float,
    rng: np.random.Generator,
) -> list[str]:
    by_label: dict[str, list[str]] = defaultdict(list)
    for group in sorted(set(groups[test_idx])):
        idx = test_idx[groups[test_idx] == group]
        if len(idx) < 2:
            continue
        by_label[group_label(labels, idx)].append(str(group))

    selected: list[str] = []
    for label, label_groups in by_label.items():
        shuffled = list(label_groups)
        rng.shuffle(shuffled)
        n_pick = int(math.floor(len(shuffled) * dose))
        if dose > 0.0 and n_pick == 0 and shuffled:
            n_pick = 1
        selected.extend(shuffled[:n_pick])
    return sorted(selected)


def split_for_dose(
    labels: np.ndarray,
    folds: np.ndarray,
    groups: np.ndarray,
    seed: int,
    dose: float,
    test_fold: int,
    val_fold: int,
    leak_fraction_within_group: float,
) -> dict[str, object]:
    rng = np.random.default_rng(seed + int(dose * 1000))
    base_train_idx = np.flatnonzero(~np.isin(folds, [test_fold, val_fold]))
    base_test_idx = np.flatnonzero(folds == test_fold)
    leaked_groups = choose_leaked_groups(labels, groups, base_test_idx, dose, rng)

    leaked_train_parts: list[np.ndarray] = []
    kept_test_parts: list[np.ndarray] = []
    leaked_group_set = set(leaked_groups)
    for group in sorted(set(groups[base_test_idx])):
        group_idx = base_test_idx[groups[base_test_idx] == group]
        if group not in leaked_group_set:
            kept_test_parts.append(group_idx)
            continue
        shuffled = np.array(group_idx, copy=True)
        rng.shuffle(shuffled)
        n_train = max(1, int(math.floor(len(shuffled) * leak_fraction_within_group)))
        n_train = min(n_train, len(shuffled) - 1)
        leaked_train_parts.append(shuffled[:n_train])
        kept_test_parts.append(shuffled[n_train:])

    train_idx = base_train_idx
    if leaked_train_parts:
        train_idx = np.concatenate([base_train_idx, *leaked_train_parts])
    test_idx = np.concatenate(kept_test_parts) if kept_test_parts else np.asarray([], dtype=int)
    return {
        "train_idx": np.asarray(sorted(set(int(i) for i in train_idx)), dtype=int),
        "test_idx": np.asarray(sorted(set(int(i) for i in test_idx)), dtype=int),
        "leaked_groups": leaked_groups,
        "leaked_train_samples": int(sum(len(part) for part in leaked_train_parts)),
        "remaining_test_samples": int(len(test_idx)),
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
    clean = summary["dose_summary"]["0.00"]["balanced_accuracy"]["mean"]
    lines = [
        "# Mojahid Lineage Leakage-Dose Sweep",
        "",
        f"Runs: `{summary['n_runs']}`",
        f"Test fold: `{summary['test_fold']}`",
        f"Val fold excluded: `{summary['val_fold']}`",
        "",
        "| dose | leaked groups mean | leaked train samples mean | test samples mean | balanced accuracy | delta vs 0 | macro-F1 | mean confidence | ECE | worst recall | recall spread | pred entropy |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for dose_key, item in summary["dose_summary"].items():
        ba = item["balanced_accuracy"]["mean"]
        lines.append(
            f"| {float(dose_key):.2f} | {item['leaked_groups']['mean']:.1f} | "
            f"{item['leaked_train_samples']['mean']:.1f} | {item['remaining_test_samples']['mean']:.1f} | "
            f"{ba:.4f} | {ba - clean:+.4f} | {item['macro_f1']['mean']:.4f} | "
            f"{item['mean_confidence']['mean']:.4f} | {item['ece_10bin']['mean']:.4f} | "
            f"{item['worst_class_recall']['mean']:.4f} | {item['class_recall_spread']['mean']:.4f} | "
            f"{item['prediction_entropy']['mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Boundary: this intentionally injects augmentation-lineage leakage into",
            "the training set. It quantifies leakage sensitivity and is not a valid",
            "generalization protocol.",
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
    parser.add_argument("--test-fold", type=int, default=0)
    parser.add_argument("--val-fold", type=int, default=1)
    parser.add_argument("--leak-fraction-within-group", type=float, default=0.5)
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    x, y, folds, groups = extract(rows, args.data_root, args.image_size)
    seeds = [20260811, 20260812, 20260813, 20260814, 20260815]

    long_rows: list[dict[str, object]] = []
    dose_values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    detailed: list[dict[str, object]] = []
    for seed in seeds:
        for dose in DOSES:
            split = split_for_dose(
                y,
                folds,
                groups,
                seed,
                dose,
                args.test_fold,
                args.val_fold,
                args.leak_fraction_within_group,
            )
            metrics = evaluate(x, y, split["train_idx"], split["test_idx"], seed)
            dose_key = f"{dose:.2f}"
            for metric in METRICS:
                value = float(metrics[metric])
                dose_values[dose_key][metric].append(value)
                long_rows.append({"seed": seed, "dose": dose_key, "metric": metric, "value": value})
            for count_key in ["leaked_groups", "leaked_train_samples", "remaining_test_samples"]:
                value = len(split[count_key]) if count_key == "leaked_groups" else split[count_key]
                dose_values[dose_key][count_key].append(float(value))
            detailed.append(
                {
                    "seed": seed,
                    "dose": dose,
                    "train_n": int(len(split["train_idx"])),
                    "test_n": int(len(split["test_idx"])),
                    "leaked_group_count": int(len(split["leaked_groups"])),
                    "leaked_train_samples": int(split["leaked_train_samples"]),
                    "remaining_test_samples": int(split["remaining_test_samples"]),
                    "metrics": {metric: float(metrics[metric]) for metric in METRICS},
                    "per_class_recall": metrics["per_class_recall"],
                }
            )

    summary = {
        "run_id": "20260811_E06_mojahid_lineage_leakage_dose_sweep",
        "n_runs": len(seeds) * len(DOSES),
        "seeds": seeds,
        "doses": DOSES,
        "test_fold": args.test_fold,
        "val_fold": args.val_fold,
        "leak_fraction_within_group": args.leak_fraction_within_group,
        "dose_summary": {
            dose: {
                metric: summarize(values)
                for metric, values in metric_rows.items()
            }
            for dose, metric_rows in dose_values.items()
        },
        "detailed_runs": detailed,
        "claim_boundary": "Intentional lineage leakage injection; not a valid generalization protocol.",
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "dose_sweep_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_csv(args.output_dir / "dose_sweep_long.csv", long_rows)
    write_md(args.output_dir / "dose_sweep_summary.md", summary)
    print(json.dumps(summary["dose_summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
