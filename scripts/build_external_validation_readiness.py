#!/usr/bin/env python3
"""Build an external validation acquisition/readiness checklist."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCH_ROOT.parent
OUT_DIR = BENCH_ROOT / "reports" / "external_validation_readiness_20260810"


def exists_rel(path: Path) -> bool:
    return path.exists()


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def count_csv_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return max(0, sum(1 for _ in csv.reader(handle)) - 1)


def build_tracks() -> list[dict[str, object]]:
    tigpr = read_json(BENCH_ROOT / "reports" / "tigpr_local_asset_audit_20260810.json")
    tigpr_duplicate = read_json(BENCH_ROOT / "reports" / "tigpr_duplicate_aware_sweep_20260811" / "tigpr_duplicate_aware_summary.json")
    four_tu = read_json(BENCH_ROOT / "reports" / "4tu_group_feasibility_20260810" / "4tu_group_feasibility_summary.json")
    five_model = read_json(BENCH_ROOT / "reports" / "five_model_synthesis_20260810" / "five_model_synthesis_summary.json")
    tigpr_restored = tigpr.get("status") == "GO" and tigpr.get("sample_index_rows") == 7169
    tigpr_group_split_clean = (
        tigpr_duplicate.get("split_summary", {})
        .get("hash_group_stratified_80_20", {})
        .get("shared_groups", {})
        .get("mean")
        == 0.0
    )

    return [
        {
            "track_id": "A",
            "name": "TIGPR restoration",
            "role": "restored public local image dataset; not blind external validation",
            "current_status": "ready_as_restored_local_not_blind"
            if tigpr_restored and tigpr_group_split_clean
            else "not_ready",
            "blocking_facts": []
            if tigpr_restored and tigpr_group_split_clean
            else tigpr.get(
                "blockers",
                ["TIGPR local executable media have not been verified"],
            ),
            "minimum_entry_requirements": [
                "authorized source download",
                "local source image tree under external_assets/tigpr",
                "7169-row sample index",
                "class counts verified against prior audit",
                "duplicate-aware grouped split with duplicate groups locked within folds",
            ],
            "next_action": "Use TIGPR only as restored-local duplicate-aware evidence; do not count it as blind external validation because labels and media are visible."
            if tigpr_restored and tigpr_group_split_clean
            else "Recover source media from the Mendeley dataset page with authorized access; otherwise keep TIGPR as supporting evidence only.",
        },
        {
            "track_id": "B",
            "name": "New third-party blind GPR image set",
            "role": "primary blind external validation",
            "current_status": "not_started",
            "blocking_facts": [
                "no advisor-held or third-party blind manifest exists locally",
                "no encrypted label file or label-holder protocol exists",
                "no one-shot submission package exists",
            ],
            "minimum_entry_requirements": [
                "data not used in model selection or threshold tuning",
                "labels held by advisor or third party until predictions are frozen",
                "sample IDs and hashes frozen before prediction",
                "single allowed submission for main claims",
                "label space harmonized to a predeclared target before model execution",
            ],
            "next_action": "Create a blind intake template and ask the label holder to provide sample IDs, raw files or images, and sealed labels.",
        },
        {
            "track_id": "C",
            "name": "4TU-like raw-trace external asset",
            "role": "external raw-trace counterfactual confirmation",
            "current_status": "not_ready",
            "blocking_facts": [
                "current 4TU metadata labels are not strong enough for main cross-model confirmation",
                "existing 4TU group-aware evidence remains a stress test",
            ],
            "minimum_entry_requirements": [
                "at least 10 independent projects or collection groups",
                "at least 2 labels in every train/validation/test grouped split",
                "held-out labels covered by training labels",
                "raw traces available for deterministic counterfactual rendering",
                "project-level split frozen before model execution",
            ],
            "next_action": "Search for or request a 4TU-like raw-trace dataset with better project and label balance before expanding the full five-model matrix.",
            "current_4tu_summary": [
                {
                    "target": item.get("target"),
                    "status": item.get("status"),
                    "test2_val2_feasible": item.get("split_grid", {}).get("test2_val2", {}).get("feasible"),
                }
                for item in four_tu.get("targets", [])
            ],
        },
        {
            "track_id": "D",
            "name": "Current Res-SAM as external-looking heldout",
            "role": "not acceptable as blind external validation",
            "current_status": "already_used_in_model_matrix",
            "blocking_facts": [
                "Res-SAM has already been used for model-family synthesis",
                "using it again as blind external validation would contaminate main claims",
            ],
            "minimum_entry_requirements": [
                "can remain a core local data asset",
                "cannot be relabeled as blind external after current analyses",
            ],
            "next_action": "Use Res-SAM for cross-model evidence and methods development only; acquire a separate blind asset for final validation.",
            "current_claim_summary": five_model.get("claim_summary", []),
        },
    ]


def build_gate(tracks: list[dict[str, object]]) -> dict[str, object]:
    hard_requirements = [
        "external asset is not used in model development",
        "manifest includes stable sample_id, rel_path or abs_path, file_sha256, label field placeholder, and source_group",
        "labels are unavailable to the analyst until predictions are frozen",
        "one prediction submission is allowed for main claims",
        "evaluation script, model versions, seeds, preprocessing, and thresholds are frozen before labels are opened",
        "post-hoc reruns are excluded from main claims and reported as exploratory only",
    ]
    current_ready_tracks = [
        track["track_id"]
        for track in tracks
        if track["current_status"] in {"ready", "ready_with_caution"}
    ]
    return {
        "gate_id": "external_validation_readiness_20260810",
        "status": "NO-GO",
        "hard_requirements": hard_requirements,
        "current_ready_tracks": current_ready_tracks,
        "decision": "No current track satisfies blind external validation readiness. TIGPR restoration is complete as local evidence, but a separate label-held blind asset is still required.",
    }


def write_csv(path: Path, tracks: list[dict[str, object]]) -> None:
    fields = ["track_id", "name", "role", "current_status", "blocking_facts", "next_action"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for track in tracks:
            writer.writerow(
                {
                    "track_id": track["track_id"],
                    "name": track["name"],
                    "role": track["role"],
                    "current_status": track["current_status"],
                    "blocking_facts": "; ".join(track["blocking_facts"]),
                    "next_action": track["next_action"],
                }
            )


def write_md(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# External Validation Readiness 2026-08-10",
        "",
        "Purpose: freeze what must be true before any result can be called blind external validation.",
        "",
        f"Gate status: **{result['gate']['status']}**.",
        "",
        "Decision: no current track satisfies blind external validation readiness. TIGPR restoration is now complete as local evidence, but it cannot be relabeled as blind external validation.",
        "",
        "## Track Summary",
        "",
        "| track | name | role | status | next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for track in result["tracks"]:
        lines.append(
            f"| {track['track_id']} | {track['name']} | {track['role']} | "
            f"{track['current_status']} | {track['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Hard Requirements",
            "",
        ]
    )
    for item in result["gate"]["hard_requirements"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Track Details", ""])
    for track in result["tracks"]:
        lines.extend(
            [
                f"### Track {track['track_id']}: {track['name']}",
                "",
                f"Status: `{track['current_status']}`",
                "",
                "Blocking facts:",
            ]
        )
        for fact in track["blocking_facts"]:
            lines.append(f"- {fact}")
        lines.extend(["", "Minimum entry requirements:"])
        for req in track["minimum_entry_requirements"]:
            lines.append(f"- {req}")
        lines.extend(["", f"Next action: {track['next_action']}", ""])
    lines.extend(
        [
            "## Protocol Consequence",
            "",
            "1. Res-SAM remains the strongest current cross-model evidence but cannot be reused as blind external validation.",
            "2. 4TU remains a raw-trace counterfactual stress-test asset, not the main confirmation layer.",
            "3. TIGPR restoration is complete as local duplicate-aware evidence, but not as blind external validation.",
            "4. Final Nature Communications-level claims still require a separate blind external asset or an equivalent advisor-held validation protocol.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tracks = build_tracks()
    result = {
        "run_id": "20260810_E00_external_validation_readiness",
        "local_state": {
            "external_assets_exists": exists_rel(ROOT / "external_assets"),
            "tigpr_sample_rows": count_csv_rows(ROOT / "manifest" / "tigpr_sample_index_v1.csv"),
            "blind_manifest_exists": exists_rel(BENCH_ROOT / "data_manifests" / "external_blind_manifest_20260810.csv"),
        },
        "tracks": tracks,
        "gate": build_gate(tracks),
    }
    (OUT_DIR / "external_validation_readiness_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "external_validation_readiness_tracks.csv", tracks)
    write_md(OUT_DIR / "external_validation_readiness_summary.md", result)
    print(json.dumps({"gate": result["gate"], "tracks": [(t["track_id"], t["current_status"]) for t in tracks]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
