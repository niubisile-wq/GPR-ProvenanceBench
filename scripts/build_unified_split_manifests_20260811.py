#!/usr/bin/env python3
"""Build unified local split manifests for executable GPR assets."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = BENCH_ROOT / "splits"
REPORT_DIR = BENCH_ROOT / "reports" / "unified_split_manifest_audit_20260811"
SEED = "20260811"

DATASETS = [
    {
        "dataset": "mojahid",
        "manifest": BENCH_ROOT / "data_manifests" / "mojahid_unified_samples_20260810.csv",
        "hash_col": "file_sha256",
        "group_col": "source_group",
        "fold_col": "fold_id",
    },
    {
        "dataset": "tigpr",
        "manifest": BENCH_ROOT / "data_manifests" / "tigpr_unified_samples_20260810.csv",
        "hash_col": "file_sha256",
        "group_col": "source_group",
        "fold_col": "fold_id",
    },
    {
        "dataset": "zenodo_14637589",
        "manifest": BENCH_ROOT / "data_manifests" / "zenodo_gpr_14637589_raw_manifest_20260811.csv",
        "hash_col": "sha256",
        "group_col": "split_group",
        "fold_col": "",
    },
    {
        "dataset": "deepmask_gpr",
        "manifest": BENCH_ROOT / "data_manifests" / "deepmask_gpr_unified_samples_20260811.csv",
        "hash_col": "file_sha256",
        "group_col": "base_source_group",
        "fold_col": "",
    },
]


FIELDNAMES = [
    "dataset",
    "protocol",
    "sample_id",
    "label",
    "source_group",
    "split_role",
    "file_sha256",
    "source_manifest",
    "protocol_seed",
    "notes",
]


def stable_hash(value: str) -> str:
    return hashlib.sha256(f"{SEED}|{value}".encode("utf-8")).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_group(row: dict[str, str], group_col: str) -> str:
    value = row.get(group_col, "")
    if value:
        return value
    return row.get("sample_id", "")


def normalize_hash(row: dict[str, str], hash_col: str) -> str:
    return row.get(hash_col, "") or row.get("file_sha256", "") or row.get("sha256", "")


def emit_rows(
    dataset: str,
    protocol: str,
    rows: list[dict[str, str]],
    roles: dict[str, str],
    group_col: str,
    hash_col: str,
    source_manifest: Path,
    notes: str,
) -> list[dict[str, str]]:
    emitted = []
    for row in rows:
        sample_id = row["sample_id"]
        emitted.append(
            {
                "dataset": dataset,
                "protocol": protocol,
                "sample_id": sample_id,
                "label": row["label"],
                "source_group": normalize_group(row, group_col),
                "split_role": roles[sample_id],
                "file_sha256": normalize_hash(row, hash_col),
                "source_manifest": source_manifest.relative_to(BENCH_ROOT).as_posix(),
                "protocol_seed": SEED,
                "notes": notes,
            }
        )
    return emitted


def random_stratified_roles(rows: list[dict[str, str]]) -> dict[str, str]:
    roles = {}
    by_label: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_label[row["label"]].append(row)
    for label_rows in by_label.values():
        ordered = sorted(label_rows, key=lambda row: stable_hash(row["sample_id"]))
        n = len(ordered)
        n_test = max(1, round(n * 0.15))
        n_val = max(1, round(n * 0.15))
        for idx, row in enumerate(ordered):
            if idx < n_test:
                role = "test"
            elif idx < n_test + n_val:
                role = "val"
            else:
                role = "train"
            roles[row["sample_id"]] = role
    return roles


def group_majority_labels(rows: list[dict[str, str]], group_col: str) -> dict[str, str]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        counts[normalize_group(row, group_col)][row["label"]] += 1
    return {group: counter.most_common(1)[0][0] for group, counter in counts.items()}


def group_roles_by_label(
    rows: list[dict[str, str]],
    group_col: str,
    test_frac: float,
    val_frac: float,
    largest_first: bool,
) -> dict[str, str]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[normalize_group(row, group_col)].append(row)
    majority = group_majority_labels(rows, group_col)
    groups_by_label: dict[str, list[str]] = defaultdict(list)
    for group, label in majority.items():
        groups_by_label[label].append(group)

    group_roles: dict[str, str] = {}
    for label, label_groups in groups_by_label.items():
        label_total = sum(len(groups[group]) for group in label_groups)
        if largest_first:
            ordered = sorted(label_groups, key=lambda group: (-len(groups[group]), stable_hash(group)))
        else:
            ordered = sorted(label_groups, key=stable_hash)
        test_target = max(1, round(label_total * test_frac))
        val_target = max(1, round(label_total * val_frac))
        test_seen = 0
        val_seen = 0
        for group in ordered:
            if test_seen < test_target:
                role = "test"
                test_seen += len(groups[group])
            elif val_seen < val_target:
                role = "val"
                val_seen += len(groups[group])
            else:
                role = "train"
            group_roles[group] = role

    return {
        row["sample_id"]: group_roles[normalize_group(row, group_col)]
        for row in rows
    }


def existing_fold_p2_roles(rows: list[dict[str, str]], fold_col: str, group_col: str) -> dict[str, str]:
    if not fold_col or fold_col not in rows[0] or not any(row.get(fold_col, "") != "" for row in rows):
        return group_roles_by_label(rows, group_col, test_frac=0.20, val_frac=0.10, largest_first=False)
    roles = {}
    for row in rows:
        fold = row.get(fold_col, "")
        if fold == "0":
            role = "test"
        elif fold == "1":
            role = "val"
        else:
            role = "train"
        roles[row["sample_id"]] = role
    return roles


def audit_split(rows: list[dict[str, str]]) -> dict[str, object]:
    by_role = Counter(row["split_role"] for row in rows)
    labels_by_role: dict[str, Counter[str]] = defaultdict(Counter)
    groups_by_role: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        labels_by_role[row["split_role"]][row["label"]] += 1
        groups_by_role[row["split_role"]].add(row["source_group"])
    labels = sorted({row["label"] for row in rows})
    shared_train_test = groups_by_role["train"].intersection(groups_by_role["test"])
    shared_train_val = groups_by_role["train"].intersection(groups_by_role["val"])
    shared_val_test = groups_by_role["val"].intersection(groups_by_role["test"])
    return {
        "rows": len(rows),
        "role_counts": dict(by_role),
        "label_counts_by_role": {role: dict(counter) for role, counter in labels_by_role.items()},
        "group_counts_by_role": {role: len(groups) for role, groups in groups_by_role.items()},
        "missing_labels_by_role": {
            role: sorted(set(labels).difference(labels_by_role[role]))
            for role in ["train", "val", "test"]
        },
        "shared_train_test_groups": len(shared_train_test),
        "shared_train_val_groups": len(shared_train_val),
        "shared_val_test_groups": len(shared_val_test),
        "group_leakage_free_train_test": len(shared_train_test) == 0,
    }


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Unified Split Manifest Audit",
        "",
        "This report creates local executable split manifests for current usable assets.",
        "DataSAIL is represented only by a deterministic source-group balancing proxy, not the external solver.",
        "",
        "| dataset | protocol | rows | train | val | test | shared train-test groups | missing test labels |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary["split_rows"]:
        audit = row["audit"]
        role_counts = audit["role_counts"]
        lines.append(
            f"| {row['dataset']} | {row['protocol']} | {audit['rows']} | "
            f"{role_counts.get('train', 0)} | {role_counts.get('val', 0)} | {role_counts.get('test', 0)} | "
            f"{audit['shared_train_test_groups']} | {audit['missing_labels_by_role'].get('test', [])} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These split manifests strengthen local reproducibility and leakage auditing.",
            "They do not create blind external validation and do not replace a true DataSAIL run.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    split_rows = []
    for cfg in DATASETS:
        rows = read_rows(cfg["manifest"])
        protocol_specs = [
            ("random_stratified_70_15_15", random_stratified_roles(rows), "sample-level random stratified; leakage-prone reference"),
            ("existing_fold_p2", existing_fold_p2_roles(rows, cfg["fold_col"], cfg["group_col"]), "existing fold_id P2-style split when available; group fallback otherwise"),
            ("source_group_holdout_70_15_15", group_roles_by_label(rows, cfg["group_col"], 0.15, 0.15, False), "source-group disjoint stratified holdout"),
            ("provenance_size_holdout_p4", group_roles_by_label(rows, cfg["group_col"], 0.20, 0.10, True), "largest-source provenance stress holdout"),
            ("datasail_like_group_balance", group_roles_by_label(rows, cfg["group_col"], 0.15, 0.15, False), "deterministic source-group balancing proxy; not external DataSAIL solver"),
        ]
        for protocol, roles, notes in protocol_specs:
            emitted = emit_rows(
                cfg["dataset"],
                protocol,
                rows,
                roles,
                cfg["group_col"],
                cfg["hash_col"],
                cfg["manifest"],
                notes,
            )
            out_path = OUT_ROOT / cfg["dataset"] / f"{protocol}_split_manifest_20260811.csv"
            write_csv(out_path, emitted)
            split_rows.append(
                {
                    "dataset": cfg["dataset"],
                    "protocol": protocol,
                    "path": out_path.relative_to(BENCH_ROOT).as_posix(),
                    "audit": audit_split(emitted),
                }
            )

    summary = {
        "run_id": "20260811_E22_unified_split_manifest_audit",
        "datasets": [cfg["dataset"] for cfg in DATASETS],
        "protocols_per_dataset": 5,
        "split_manifest_rows": len(split_rows),
        "split_rows": split_rows,
        "all_split_files_exist": all((BENCH_ROOT / row["path"]).exists() for row in split_rows),
        "group_disjoint_protocols": [
            "source_group_holdout_70_15_15",
            "provenance_size_holdout_p4",
            "datasail_like_group_balance",
        ],
        "blind_external_eligible": False,
        "status": "complete_local_unified_split_manifests",
    }
    (REPORT_DIR / "unified_split_manifest_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_md(REPORT_DIR / "unified_split_manifest_audit_summary.md", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
