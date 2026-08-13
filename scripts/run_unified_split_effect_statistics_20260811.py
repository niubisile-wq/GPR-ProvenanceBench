#!/usr/bin/env python3
"""Bootstrap uncertainty for random-minus-protocol split effects."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

from run_unified_split_baseline_20260811 import (
    BENCH_ROOT,
    DATASETS,
    PROTOCOLS,
    build_feature_table,
    read_rows,
)


OUT_DIR = BENCH_ROOT / "reports" / "unified_split_effect_statistics_20260811"
N_BOOT = 2000
RNG = np.random.default_rng(20260811)


def balanced_accuracy_from_arrays(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    recalls = []
    for label in sorted(set(y_true.tolist())):
        mask = y_true == label
        if np.any(mask):
            recalls.append(float(np.mean(y_pred[mask] == label)))
    return float(np.mean(recalls)) if recalls else 0.0


def bootstrap_balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray, n_boot: int) -> np.ndarray:
    labels = sorted(set(y_true.tolist()))
    by_label = {label: np.flatnonzero(y_true == label) for label in labels}
    values = np.zeros(n_boot, dtype=np.float64)
    for boot_idx in range(n_boot):
        recalls = []
        for label, idx in by_label.items():
            sampled = RNG.choice(idx, size=len(idx), replace=True)
            recalls.append(float(np.mean(y_pred[sampled] == label)))
        values[boot_idx] = float(np.mean(recalls))
    return values


def run_predictions(
    dataset: str,
    protocol: str,
    features: dict[str, np.ndarray],
    label_by_sample: dict[str, str],
) -> dict[str, object]:
    split_path = BENCH_ROOT / "splits" / dataset / f"{protocol}_split_manifest_20260811.csv"
    split_rows = read_rows(split_path)
    train_ids = [row["sample_id"] for row in split_rows if row["split_role"] == "train"]
    test_rows = [row for row in split_rows if row["split_role"] == "test"]
    test_ids = [row["sample_id"] for row in test_rows]
    train_x = np.stack([features[sample_id] for sample_id in train_ids])
    test_x = np.stack([features[sample_id] for sample_id in test_ids])
    encoder = LabelEncoder()
    train_y = encoder.fit_transform([label_by_sample[sample_id] for sample_id in train_ids])
    test_y = encoder.transform([label_by_sample[sample_id] for sample_id in test_ids])
    model = make_pipeline(
        StandardScaler(),
        SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            max_iter=3000,
            tol=1e-4,
            class_weight="balanced",
            random_state=20260811,
        ),
    )
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    train_groups = {row["source_group"] for row in split_rows if row["split_role"] == "train"}
    test_groups = {row["source_group"] for row in test_rows}
    return {
        "dataset": dataset,
        "protocol": protocol,
        "test_ids": test_ids,
        "test_labels": encoder.inverse_transform(test_y).tolist(),
        "pred_labels": encoder.inverse_transform(pred).tolist(),
        "test_y": test_y,
        "pred": pred,
        "balanced_accuracy": balanced_accuracy_from_arrays(test_y, pred),
        "shared_train_test_groups": len(train_groups.intersection(test_groups)),
    }


def ci(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(values.mean()),
        "ci95_low": float(np.quantile(values, 0.025)),
        "ci95_high": float(np.quantile(values, 0.975)),
    }


def contrast_stats(random_pred: dict[str, object], other_pred: dict[str, object]) -> dict[str, object]:
    random_boot = bootstrap_balanced_accuracy(random_pred["test_y"], random_pred["pred"], N_BOOT)  # type: ignore[arg-type]
    other_boot = bootstrap_balanced_accuracy(other_pred["test_y"], other_pred["pred"], N_BOOT)  # type: ignore[arg-type]
    delta = random_boot - other_boot
    observed_delta = float(random_pred["balanced_accuracy"] - other_pred["balanced_accuracy"])
    p_directional = float((np.sum(delta <= 0.0) + 1.0) / (len(delta) + 1.0))
    return {
        "dataset": other_pred["dataset"],
        "contrast": f"random_minus_{other_pred['protocol']}",
        "random_protocol": random_pred["protocol"],
        "comparison_protocol": other_pred["protocol"],
        "random_balanced_accuracy": random_pred["balanced_accuracy"],
        "comparison_balanced_accuracy": other_pred["balanced_accuracy"],
        "observed_delta_balanced_accuracy": observed_delta,
        "bootstrap_delta": ci(delta),
        "bootstrap_random": ci(random_boot),
        "bootstrap_comparison": ci(other_boot),
        "p_bootstrap_delta_le_zero": p_directional,
        "random_shared_train_test_groups": random_pred["shared_train_test_groups"],
        "comparison_shared_train_test_groups": other_pred["shared_train_test_groups"],
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items()}
            )


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# Unified Split Effect Statistics",
        "",
        "Bootstrap uncertainty for random-minus-protocol balanced-accuracy gaps.",
        "",
        "| dataset | contrast | delta BA | 95% CI | p(delta <= 0) | random shared groups | comparison shared groups |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in result["contrasts"]:
        boot = row["bootstrap_delta"]
        lines.append(
            f"| {row['dataset']} | {row['contrast']} | {row['observed_delta_balanced_accuracy']:+.4f} | "
            f"[{boot['ci95_low']:+.4f}, {boot['ci95_high']:+.4f}] | {row['p_bootstrap_delta_le_zero']:.4f} | "
            f"{row['random_shared_train_test_groups']} | {row['comparison_shared_train_test_groups']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is local bootstrap uncertainty over fixed split baselines. It is not",
            "a replacement for external validation or a full multi-seed training study.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    contrasts = []
    predictions_export = []
    for dataset, manifest_path in DATASETS.items():
        manifest_rows = read_rows(manifest_path)
        features, labels = build_feature_table(dataset, manifest_rows)
        protocol_predictions = {
            protocol: run_predictions(dataset, protocol, features, labels)
            for protocol in PROTOCOLS
        }
        random_pred = protocol_predictions["random_stratified_70_15_15"]
        for protocol in PROTOCOLS:
            pred = protocol_predictions[protocol]
            for sample_id, true_label, pred_label in zip(pred["test_ids"], pred["test_labels"], pred["pred_labels"]):
                predictions_export.append(
                    {
                        "dataset": dataset,
                        "protocol": protocol,
                        "sample_id": sample_id,
                        "true_label": true_label,
                        "pred_label": pred_label,
                        "correct": int(true_label == pred_label),
                    }
                )
            if protocol != "random_stratified_70_15_15":
                contrasts.append(contrast_stats(random_pred, pred))

    result = {
        "run_id": "20260811_E25_unified_split_effect_statistics",
        "n_bootstrap": N_BOOT,
        "datasets": list(DATASETS),
        "contrasts": contrasts,
        "prediction_rows": len(predictions_export),
        "blind_external_eligible": False,
        "status": "complete_local_unified_split_effect_statistics",
    }
    (OUT_DIR / "unified_split_effect_statistics_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_csv(OUT_DIR / "unified_split_effect_statistics_contrasts.csv", contrasts)
    write_csv(OUT_DIR / "unified_split_effect_statistics_predictions.csv", predictions_export)
    write_md(OUT_DIR / "unified_split_effect_statistics_summary.md", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
