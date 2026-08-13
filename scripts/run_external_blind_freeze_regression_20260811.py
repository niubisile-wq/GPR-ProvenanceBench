#!/usr/bin/env python3
"""Run a synthetic blind-freeze regression for the external validation pipeline."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

from run_unified_split_baseline_20260811 import BENCH_ROOT, read_rows, simple_hog


OUT_DIR = BENCH_ROOT / "reports" / "external_blind_freeze_regression_20260811"
MANIFEST = BENCH_ROOT / "data_manifests" / "tigpr_unified_samples_20260810.csv"
SPLIT = BENCH_ROOT / "splits" / "tigpr" / "source_group_holdout_70_15_15_split_manifest_20260811.csv"
N_SYNTHETIC_BLIND = 240
SEED = 20260811

MANIFEST_COLUMNS = [
    "sample_id",
    "rel_path",
    "abs_path",
    "file_sha256",
    "label_placeholder",
    "source_group",
    "asset_track",
    "modality",
    "target_task",
    "notes",
]
LABEL_COLUMNS = [
    "sample_id",
    "sealed_label",
    "label_space_version",
    "label_holder",
    "sealed_timestamp",
    "unlock_timestamp",
    "unlock_authorized_by",
]
PREDICTION_COLUMNS = [
    "sample_id",
    "predicted_label",
    "prediction_score",
    "model_family",
    "model_version",
    "preprocessing_version",
    "seed",
    "submission_id",
    "prediction_timestamp",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_feature(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        image.load()
        arr = np.asarray(
            image.convert("L").resize((64, 64), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
    return simple_hog(arr / 255.0)


def evaluate(y_true: list[str], y_pred: list[str]) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
    }


def rel_posix(path: Path) -> str:
    return path.relative_to(BENCH_ROOT).as_posix()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows = {row["sample_id"]: row for row in read_rows(MANIFEST)}
    split_rows = read_rows(SPLIT)
    train_ids = [row["sample_id"] for row in split_rows if row["split_role"] == "train"]
    test_ids = [row["sample_id"] for row in split_rows if row["split_role"] == "test"]
    rng = np.random.default_rng(SEED)
    synthetic_ids = sorted(rng.choice(test_ids, size=min(N_SYNTHETIC_BLIND, len(test_ids)), replace=False).tolist())

    train_x = np.stack([load_feature(Path(manifest_rows[sample_id]["abs_path"])) for sample_id in train_ids])
    synthetic_x = np.stack([load_feature(Path(manifest_rows[sample_id]["abs_path"])) for sample_id in synthetic_ids])
    encoder = LabelEncoder()
    train_y = encoder.fit_transform([manifest_rows[sample_id]["label"] for sample_id in train_ids])
    model = make_pipeline(
        StandardScaler(),
        SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            max_iter=3000,
            tol=1e-4,
            class_weight="balanced",
            random_state=SEED,
        ),
    )
    model.fit(train_x, train_y)
    probs = model.predict_proba(synthetic_x)
    pred_idx = probs.argmax(axis=1)
    pred_labels = encoder.inverse_transform(pred_idx)
    pred_scores = probs.max(axis=1)

    prediction_time = datetime(2026, 8, 11, 9, 30, tzinfo=timezone.utc)
    unlock_time = prediction_time + timedelta(minutes=10)
    sealed_time = prediction_time - timedelta(days=1)
    submission_id = "synthetic_blind_freeze_regression_20260811"

    blind_manifest_rows = []
    label_rows = []
    prediction_rows = []
    y_true = []
    y_pred = []
    for sample_id, pred_label, score in zip(synthetic_ids, pred_labels.tolist(), pred_scores.tolist()):
        row = manifest_rows[sample_id]
        payload = Path(row["abs_path"])
        blind_manifest_rows.append(
            {
                "sample_id": sample_id,
                "rel_path": row["rel_path"],
                "abs_path": row["abs_path"],
                "file_sha256": sha256_file(payload),
                "label_placeholder": "HELD_OUT",
                "source_group": row["source_group"],
                "asset_track": "other_external",
                "modality": "image",
                "target_task": "tigpr_damage_classification",
                "notes": "synthetic blind-freeze regression row; not real blind external evidence",
            }
        )
        label_rows.append(
            {
                "sample_id": sample_id,
                "sealed_label": row["label"],
                "label_space_version": "tigpr_damage_v1",
                "label_holder": "synthetic_regression_fixture",
                "sealed_timestamp": sealed_time.isoformat(),
                "unlock_timestamp": unlock_time.isoformat(),
                "unlock_authorized_by": "synthetic_regression_fixture",
            }
        )
        prediction_rows.append(
            {
                "sample_id": sample_id,
                "predicted_label": pred_label,
                "prediction_score": f"{score:.8f}",
                "model_family": "hog_sgd_logistic",
                "model_version": "tigpr_source_group_holdout_frozen_20260811",
                "preprocessing_version": "gray64_hog_v1",
                "seed": SEED,
                "submission_id": submission_id,
                "prediction_timestamp": prediction_time.isoformat(),
            }
        )
        y_true.append(row["label"])
        y_pred.append(pred_label)

    blind_manifest = OUT_DIR / "synthetic_blind_manifest.csv"
    labels = OUT_DIR / "synthetic_label_holdout.csv"
    predictions = OUT_DIR / "synthetic_frozen_predictions.csv"
    write_csv(blind_manifest, MANIFEST_COLUMNS, blind_manifest_rows)
    write_csv(labels, LABEL_COLUMNS, label_rows)
    write_csv(predictions, PREDICTION_COLUMNS, prediction_rows)

    prediction_sha = sha256_file(predictions)
    label_sha = sha256_file(labels)
    manifest_sha = sha256_file(blind_manifest)
    metrics = evaluate(y_true, y_pred)
    train_groups = {manifest_rows[sample_id]["source_group"] for sample_id in train_ids}
    synthetic_groups = {manifest_rows[sample_id]["source_group"] for sample_id in synthetic_ids}
    result = {
        "run_id": "20260811_E31_external_blind_freeze_regression",
        "fixture_type": "synthetic_regression_not_real_blind_external",
        "manifest": rel_posix(blind_manifest),
        "labels": rel_posix(labels),
        "predictions": rel_posix(predictions),
        "manifest_sha256": manifest_sha,
        "label_holdout_sha256": label_sha,
        "prediction_sha256_at_freeze": prediction_sha,
        "prediction_timestamp": prediction_time.isoformat(),
        "label_unlock_timestamp": unlock_time.isoformat(),
        "prediction_precedes_unlock": prediction_time < unlock_time,
        "n_train": len(train_ids),
        "n_synthetic_blind": len(synthetic_ids),
        "shared_train_synthetic_source_groups": len(train_groups.intersection(synthetic_groups)),
        "metrics_after_unlock": metrics,
        "blind_external_eligible": False,
        "status": "complete_synthetic_blind_freeze_regression",
    }
    (OUT_DIR / "external_blind_freeze_regression_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    lines = [
        "# External Blind Freeze Regression",
        "",
        "Synthetic regression fixture for the blind external intake/freeze/unlock path.",
        "This is not real blind external evidence.",
        "",
        f"- synthetic rows: {result['n_synthetic_blind']}",
        f"- prediction precedes unlock: {result['prediction_precedes_unlock']}",
        f"- prediction SHA-256 at freeze: `{prediction_sha}`",
        f"- balanced accuracy after synthetic unlock: {metrics['balanced_accuracy']:.4f}",
        f"- shared train/synthetic source groups: {result['shared_train_synthetic_source_groups']}",
        "",
        "Boundary: TIGPR rows are visible local data. This proves the one-shot",
        "prediction-freeze regression path, not the external validation result.",
        "",
    ]
    (OUT_DIR / "external_blind_freeze_regression_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "run_id": result["run_id"],
                "status": result["status"],
                "n_synthetic_blind": result["n_synthetic_blind"],
                "balanced_accuracy": metrics["balanced_accuracy"],
                "prediction_precedes_unlock": result["prediction_precedes_unlock"],
                "blind_external_eligible": result["blind_external_eligible"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
