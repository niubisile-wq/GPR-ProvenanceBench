#!/usr/bin/env python3
"""Run duplicate-group leakage dose experiment on restored TIGPR."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


BENCH_ROOT = Path(__file__).resolve().parents[1]
SEEDS = [20260811, 20260812, 20260813, 20260814, 20260815]
DOSES = [0.0, 0.05, 0.10, 0.20, 0.40]
METRICS = ["accuracy", "balanced_accuracy", "macro_f1"]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def resolve_path(row: dict[str, str]) -> Path:
    path = BENCH_ROOT / row["rel_path"]
    if path.exists():
        return path
    abs_path = Path(row["abs_path"])
    if abs_path.exists():
        return abs_path
    raise FileNotFoundError(row["sample_id"])


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


def load_or_build_features(rows: list[dict[str, str]], cache_path: Path, image_size: int) -> np.ndarray:
    if cache_path.exists():
        cached = np.load(cache_path)
        if int(cached["image_size"]) == image_size and int(cached["n_rows"]) == len(rows):
            return cached["features"]
    features = []
    for i, row in enumerate(rows, start=1):
        features.append(simple_hog(load_gray(resolve_path(row), image_size)))
        if i % 500 == 0:
            print(f"extracted {i}/{len(rows)} TIGPR HOG features")
    x = np.stack(features).astype(np.float32)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_path, features=x, image_size=image_size, n_rows=len(rows))
    return x


def make_model(seed: int):
    return make_pipeline(
        StandardScaler(),
        SGDClassifier(
            loss="log_loss",
            alpha=1e-4,
            class_weight="balanced",
            random_state=seed,
            max_iter=1500,
            tol=1e-3,
        ),
    )


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
    }


def duplicate_group_members(groups: np.ndarray, y: np.ndarray) -> dict[str, list[int]]:
    by_group: dict[str, list[int]] = defaultdict(list)
    for idx, group in enumerate(groups.tolist()):
        by_group[str(group)].append(idx)
    return {
        group: members
        for group, members in by_group.items()
        if len(members) > 1 and len({str(y[idx]) for idx in members}) == 1
    }


def inject_duplicate_dose(
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    groups: np.ndarray,
    duplicate_groups: dict[str, list[int]],
    dose: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    if dose <= 0:
        return train_idx, test_idx, {
            "requested_dose": dose,
            "eligible_test_duplicate_groups": 0,
            "leaked_duplicate_groups": 0,
            "leaked_train_samples": 0,
            "remaining_test_samples_from_leaked_groups": 0,
        }
    rng = np.random.default_rng(seed + int(round(dose * 1000)))
    test_set = set(test_idx.tolist())
    eligible = []
    for group, members in duplicate_groups.items():
        test_members = [idx for idx in members if idx in test_set]
        if len(test_members) >= 2:
            eligible.append((group, test_members))
    n_leak = int(round(len(eligible) * dose))
    n_leak = min(max(n_leak, 0), len(eligible))
    selected = rng.choice(len(eligible), size=n_leak, replace=False).tolist() if n_leak else []
    train_additions = []
    test_removals = set()
    leaked_groups = []
    remaining_test = 0
    for selected_idx in selected:
        group, test_members = eligible[selected_idx]
        donor = int(rng.choice(test_members))
        train_additions.append(donor)
        test_removals.add(donor)
        leaked_groups.append(group)
        remaining_test += len(test_members) - 1
    new_train = np.asarray(sorted(set(train_idx.tolist()).union(train_additions)), dtype=np.int64)
    new_test = np.asarray([idx for idx in test_idx.tolist() if idx not in test_removals], dtype=np.int64)
    shared_groups = set(groups[new_train].tolist()).intersection(set(groups[new_test].tolist()))
    return new_train, new_test, {
        "requested_dose": dose,
        "eligible_test_duplicate_groups": int(len(eligible)),
        "leaked_duplicate_groups": int(len(leaked_groups)),
        "leaked_train_samples": int(len(train_additions)),
        "remaining_test_samples_from_leaked_groups": int(remaining_test),
        "shared_train_test_groups": int(len(shared_groups)),
        "shared_test_samples": int(sum(group in shared_groups for group in groups[new_test])),
    }


def run(rows: list[dict[str, str]], x: np.ndarray) -> tuple[dict[str, object], list[dict[str, object]]]:
    y = np.asarray([row["label"] for row in rows])
    groups = np.asarray([row["source_group"] for row in rows])
    duplicate_groups = duplicate_group_members(groups, y)
    detailed = []
    for seed in SEEDS:
        splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
        base_train, base_test = next(splitter.split(np.zeros(len(y)), y, groups))
        for dose in DOSES:
            train_idx, test_idx, leakage = inject_duplicate_dose(
                base_train,
                base_test,
                groups,
                duplicate_groups,
                dose,
                seed,
            )
            model = make_model(seed)
            model.fit(x[train_idx], y[train_idx])
            pred = model.predict(x[test_idx])
            item = {
                "seed": seed,
                "dose": dose,
                "train_n": int(len(train_idx)),
                "test_n": int(len(test_idx)),
                **leakage,
                **metrics(y[test_idx], pred),
            }
            detailed.append(item)
    dose_summary = {}
    base_by_seed = {row["seed"]: row for row in detailed if float(row["dose"]) == 0.0}
    for dose in DOSES:
        rows_at_dose = [row for row in detailed if float(row["dose"]) == dose]
        dose_summary[f"{dose:.2f}"] = {}
        for metric in METRICS + [
            "leaked_duplicate_groups",
            "leaked_train_samples",
            "remaining_test_samples_from_leaked_groups",
            "shared_train_test_groups",
            "shared_test_samples",
        ]:
            values = np.asarray([float(row.get(metric, 0.0)) for row in rows_at_dose], dtype=np.float64)
            dose_summary[f"{dose:.2f}"][metric] = {
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                "min": float(values.min()),
                "max": float(values.max()),
            }
        for metric in METRICS:
            deltas = np.asarray(
                [float(row[metric]) - float(base_by_seed[row["seed"]][metric]) for row in rows_at_dose],
                dtype=np.float64,
            )
            dose_summary[f"{dose:.2f}"][f"delta_vs_dose0_{metric}"] = {
                "mean": float(deltas.mean()),
                "std": float(deltas.std(ddof=1)) if len(deltas) > 1 else 0.0,
                "min": float(deltas.min()),
                "max": float(deltas.max()),
            }
    summary = {
        "run_id": "20260811_E28_tigpr_duplicate_leakage_dose",
        "n_samples": len(rows),
        "seeds": SEEDS,
        "doses": DOSES,
        "duplicate_group_count": len(duplicate_groups),
        "label_counts": {str(key): int(value) for key, value in Counter(y).items()},
        "dose_summary": dose_summary,
        "detailed_runs": detailed,
        "blind_external_eligible": False,
        "status": "complete_local_tigpr_duplicate_leakage_dose",
    }
    return summary, detailed


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# TIGPR Duplicate Leakage Dose",
        "",
        "A hash-group split is contaminated by moving one same-label duplicate",
        "from selected test duplicate groups into training while leaving at least",
        "one same-group test sample held out.",
        "",
        "| dose | leaked groups | shared test samples | BA | delta vs 0 | macro F1 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for dose in [f"{value:.2f}" for value in result["doses"]]:
        item = result["dose_summary"][dose]
        lines.append(
            f"| {dose} | {item['leaked_duplicate_groups']['mean']:.1f} | "
            f"{item['shared_test_samples']['mean']:.1f} | "
            f"{item['balanced_accuracy']['mean']:.4f} | "
            f"{item['delta_vs_dose0_balanced_accuracy']['mean']:+.4f} | "
            f"{item['macro_f1']['mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a restored-local duplicate leakage dose experiment. It strengthens",
            "cross-asset dose-response evidence, but does not create blind external",
            "validation because TIGPR labels and media are visible locally.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data_manifests/tigpr_unified_samples_20260810.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/tigpr_duplicate_leakage_dose_20260811"))
    parser.add_argument("--image-size", type=int, default=64)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.manifest)
    x = load_or_build_features(rows, args.output_dir / f"tigpr_hog_features_{args.image_size}.npz", args.image_size)
    summary, detailed = run(rows, x)
    (args.output_dir / "tigpr_duplicate_leakage_dose_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(args.output_dir / "tigpr_duplicate_leakage_dose_runs.csv", detailed)
    write_md(args.output_dir / "tigpr_duplicate_leakage_dose_summary.md", summary)
    print(
        json.dumps(
            {
                "run_id": summary["run_id"],
                "status": summary["status"],
                "runs": len(detailed),
                "duplicate_group_count": summary["duplicate_group_count"],
                "blind_external_eligible": summary["blind_external_eligible"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
