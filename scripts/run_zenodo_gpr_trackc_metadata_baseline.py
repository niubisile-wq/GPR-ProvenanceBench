#!/usr/bin/env python3
"""Run a non-blind Track C baseline on Zenodo 14637589 raw GPR files."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


BENCH_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = BENCH_ROOT / "data_manifests" / "zenodo_gpr_14637589_raw_manifest_20260811.csv"
OUT_DIR = BENCH_ROOT / "reports" / "zenodo_gpr_trackc_metadata_baseline_20260811"
SEEDS = [0, 1, 2, 3, 4]
TAIL_BYTES = 4096
HEAD_BYTES = 4096


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def byte_features(path: Path) -> tuple[float, float, float, float, list[float]]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(HEAD_BYTES)
        if size > HEAD_BYTES:
            handle.seek(max(0, size - TAIL_BYTES))
            tail = handle.read(TAIL_BYTES)
        else:
            tail = b""
    data = np.frombuffer(head + tail, dtype=np.uint8)
    if data.size == 0:
        hist = np.zeros(256, dtype=float)
        zero_ratio = printable_ratio = high_byte_ratio = entropy = 0.0
    else:
        counts = np.bincount(data, minlength=256).astype(float)
        hist = counts / counts.sum()
        zero_ratio = float(hist[0])
        printable_ratio = float(hist[32:127].sum())
        high_byte_ratio = float(hist[128:].sum())
        nonzero = hist[hist > 0]
        entropy = float(-(nonzero * np.log2(nonzero)).sum())
    return zero_ratio, printable_ratio, high_byte_ratio, entropy, hist.tolist()


def build_matrix(rows: list[dict[str, str]]) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    labels = sorted({row["label"] for row in rows})
    exts = sorted({row["extension"].lower() for row in rows})
    label_index = {label: idx for idx, label in enumerate(labels)}
    ext_index = {ext: idx for idx, ext in enumerate(exts)}
    features = []
    y = []
    groups = []
    for row in rows:
        path = Path(row["absolute_path"])
        size = float(row["size_bytes"])
        zero_ratio, printable_ratio, high_byte_ratio, entropy, hist = byte_features(path)
        ext_features = [0.0] * len(exts)
        ext_features[ext_index[row["extension"].lower()]] = 1.0
        path_depth = len(Path(row["relative_path"]).parts)
        name_len = len(Path(row["relative_path"]).name)
        features.append(
            [
                math.log1p(size),
                size / 1_000_000.0,
                float(path_depth),
                float(name_len),
                zero_ratio,
                printable_ratio,
                high_byte_ratio,
                entropy,
            ]
            + ext_features
            + hist
        )
        y.append(label_index[row["label"]])
        groups.append(row["split_group"])
    return np.asarray(features, dtype=float), np.asarray(y, dtype=int), np.asarray(groups), labels


def group_split_indices(y: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    unique_groups = np.asarray(sorted(set(groups)))
    group_labels = []
    for group in unique_groups:
        group_y = y[groups == group]
        group_labels.append(Counter(group_y).most_common(1)[0][0])
    group_labels = np.asarray(group_labels, dtype=int)
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
    group_train, group_test = next(splitter.split(unique_groups, group_labels))
    train_groups = set(unique_groups[group_train])
    test_groups = set(unique_groups[group_test])
    train_idx = np.asarray([idx for idx, group in enumerate(groups) if group in train_groups], dtype=int)
    test_idx = np.asarray([idx for idx, group in enumerate(groups) if group in test_groups], dtype=int)
    return train_idx, test_idx


def random_split_indices(y: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray]:
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
    return next(splitter.split(np.zeros_like(y), y))


def evaluate_model(model_name: str, x: np.ndarray, y: np.ndarray, groups: np.ndarray, labels: list[str]) -> list[dict[str, object]]:
    rows = []
    for split_name, split_fn in [
        ("random_stratified_70_30", lambda seed: random_split_indices(y, seed)),
        ("project_group_stratified_70_30", lambda seed: group_split_indices(y, groups, seed)),
    ]:
        for seed in SEEDS:
            train_idx, test_idx = split_fn(seed)
            if model_name == "sgd_logistic":
                clf = make_pipeline(
                    StandardScaler(),
                    SGDClassifier(loss="log_loss", alpha=1e-4, max_iter=4000, tol=1e-4, random_state=seed),
                )
            elif model_name == "extra_trees":
                clf = ExtraTreesClassifier(
                    n_estimators=300,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=seed,
                    n_jobs=-1,
                )
            else:
                raise ValueError(model_name)
            clf.fit(x[train_idx], y[train_idx])
            pred = clf.predict(x[test_idx])
            cm = confusion_matrix(y[test_idx], pred, labels=list(range(len(labels))))
            rows.append(
                {
                    "model": model_name,
                    "split": split_name,
                    "seed": seed,
                    "n_train": int(len(train_idx)),
                    "n_test": int(len(test_idx)),
                    "train_groups": int(len(set(groups[train_idx]))),
                    "test_groups": int(len(set(groups[test_idx]))),
                    "shared_groups": int(len(set(groups[train_idx]).intersection(set(groups[test_idx])))),
                    "test_label_counts": {labels[idx]: int(np.sum(y[test_idx] == idx)) for idx in range(len(labels))},
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "balanced_accuracy": float(balanced_accuracy_score(y[test_idx], pred)),
                    "confusion_matrix_labels": labels,
                    "confusion_matrix": cm.tolist(),
                }
            )
    return rows


def summarize(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key, ""), ensure_ascii=False) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fieldnames})


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Zenodo Raw-GPR Track C Metadata Baseline",
        "",
        "Scope: non-blind public raw-GPR stress test on Zenodo record 14637589.",
        "Features are file-level metadata plus head/tail byte signatures, not semantic GPR interpretation.",
        "",
        "## Dataset",
        "",
        f"- Samples: {result['dataset']['n_samples']}",
        f"- Labels: {result['dataset']['label_counts']}",
        f"- Project groups: {result['dataset']['n_groups']}",
        "",
        "## Split Contrast",
        "",
        "| model | random BA | group BA | random - group BA | group shared groups |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in result["model_contrasts"]:
        lines.append(
            f"| {row['model']} | {row['random_balanced_accuracy']['mean']:.4f} | "
            f"{row['group_balanced_accuracy']['mean']:.4f} | {row['random_minus_group_balanced_accuracy']['mean']:+.4f} | "
            f"{row['group_shared_groups']['mean']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            result["interpretation"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_manifest()
    if not rows:
        raise RuntimeError("Zenodo raw-GPR manifest is empty")
    x, y, groups, labels = build_matrix(rows)
    run_rows = []
    for model_name in ["sgd_logistic", "extra_trees"]:
        run_rows.extend(evaluate_model(model_name, x, y, groups, labels))

    model_contrasts = []
    for model_name in ["sgd_logistic", "extra_trees"]:
        model_rows = [row for row in run_rows if row["model"] == model_name]
        random_rows = [row for row in model_rows if row["split"] == "random_stratified_70_30"]
        group_rows = [row for row in model_rows if row["split"] == "project_group_stratified_70_30"]
        random_ba = [float(row["balanced_accuracy"]) for row in random_rows]
        group_ba = [float(row["balanced_accuracy"]) for row in group_rows]
        deltas = [random_ba[idx] - group_ba[idx] for idx in range(len(SEEDS))]
        model_contrasts.append(
            {
                "model": model_name,
                "random_balanced_accuracy": summarize(random_ba),
                "group_balanced_accuracy": summarize(group_ba),
                "random_minus_group_balanced_accuracy": summarize(deltas),
                "random_shared_groups": summarize([float(row["shared_groups"]) for row in random_rows]),
                "group_shared_groups": summarize([float(row["shared_groups"]) for row in group_rows]),
            }
        )

    group_label_counts: dict[str, int] = defaultdict(int)
    for group in sorted(set(groups)):
        label = labels[Counter(y[groups == group]).most_common(1)[0][0]]
        group_label_counts[label] += 1

    result = {
        "run_id": "20260811_E18_zenodo_gpr_trackc_metadata_baseline",
        "manifest": MANIFEST.relative_to(BENCH_ROOT).as_posix(),
        "dataset": {
            "n_samples": len(rows),
            "label_counts": dict(Counter(row["label"] for row in rows)),
            "n_groups": int(len(set(groups))),
            "group_label_counts": dict(sorted(group_label_counts.items())),
            "extensions": dict(Counter(row["extension"] for row in rows)),
        },
        "features": {
            "description": "log file size, raw size, path depth, filename length, extension one-hot, and 4096-byte head/tail byte histogram/signature features",
            "n_features": int(x.shape[1]),
            "semantic_gpr_signal_used": False,
        },
        "split_protocols": {
            "random_stratified_70_30": "sample-level stratified split; can share project groups across train/test",
            "project_group_stratified_70_30": "project group split stratified by majority group label; zero shared split groups",
        },
        "model_contrasts": model_contrasts,
        "detailed_runs": run_rows,
        "blind_external_eligible": False,
        "interpretation": (
            "The public Zenodo raw-GPR asset is now executable as a Track C non-blind stress test. "
            "Any high accuracy from metadata/byte-signature features should be interpreted as source or format separability, "
            "not as proof that semantic GPR defect reasoning generalizes. The hard blind-external gate remains open."
        ),
        "status": "complete_nonblind_trackc_baseline",
    }
    (OUT_DIR / "zenodo_gpr_trackc_metadata_baseline_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(
        OUT_DIR / "zenodo_gpr_trackc_metadata_baseline_runs.csv",
        run_rows,
        [
            "model",
            "split",
            "seed",
            "n_train",
            "n_test",
            "train_groups",
            "test_groups",
            "shared_groups",
            "test_label_counts",
            "accuracy",
            "balanced_accuracy",
            "confusion_matrix_labels",
            "confusion_matrix",
        ],
    )
    write_md(OUT_DIR / "zenodo_gpr_trackc_metadata_baseline_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
