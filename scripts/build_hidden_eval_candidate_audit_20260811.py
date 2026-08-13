#!/usr/bin/env python3
"""Audit currently known GPR hidden-evaluation candidates for the blind gate."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "hidden_eval_candidate_audit_20260811"


CRITERIA = [
    "gpr_domain",
    "labels_hidden_until_prediction_freeze",
    "real_field_or_third_party_asset",
    "task_compatible_with_current_claim",
    "submission_or_oracle_available_now",
    "licence_and_rights_usable",
]


def read_json(rel_path: str) -> dict:
    path = BENCH_ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def candidate_rows() -> list[dict[str, object]]:
    mcg_download = read_json("reports/zenodo_mcg_gpr_download_20260811/zenodo_mcg_gpr_download_summary.json")
    mcg_manifest = read_json("reports/zenodo_mcg_gpr_manifest_20260811/zenodo_mcg_gpr_manifest_summary.json")
    mcg_baseline = read_json("reports/zenodo_mcg_gpr_nonblind_baseline_20260811/zenodo_mcg_gpr_nonblind_baseline_summary.json")
    mcg_split_stress = read_json("reports/zenodo_mcg_gpr_split_stress_20260811/zenodo_mcg_gpr_split_stress_summary.json")
    mcg_local_executed = (
        mcg_download.get("status") == "complete_public_mcg_gpr_download_verified_extracted"
        and mcg_download.get("md5_verified") is True
        and mcg_manifest.get("status") == "complete_public_mcg_gpr_manifest"
        and mcg_baseline.get("status") == "complete_public_mcg_gpr_nonblind_baseline"
        and mcg_split_stress.get("status") == "complete_public_mcg_gpr_split_stress"
    )
    return [
        {
            "candidate_id": "HEC-001",
            "name": "GprMax Deep Learning Challenge 1 (GDLC-1)",
            "source_url": "https://www.kaggle.com/competitions/gpr-max-deep-learning-challenge-1-gdlc-1",
            "evidence_url": "https://www.kaggle.com/competitions/gpr-max-deep-learning-challenge-1-gdlc-1/overview/evaluation",
            "gpr_domain": True,
            "labels_hidden_until_prediction_freeze": True,
            "real_field_or_third_party_asset": False,
            "task_compatible_with_current_claim": False,
            "submission_or_oracle_available_now": False,
            "licence_and_rights_usable": "unknown_requires_kaggle_terms_and_account",
            "decision": "NO-GO",
            "reason": (
                "Hidden-evaluation style candidate, but it is a synthetic gprMax multi-offset full-waveform "
                "inversion challenge rather than the current real-field defect/provenance validation task; no "
                "local one-shot submission receipt is available."
            ),
        },
        {
            "candidate_id": "HEC-002",
            "name": "Mendeley GPR dataset for deep learning applications / Mojahid",
            "source_url": "https://data.mendeley.com/datasets/ww7fd9t325/1",
            "evidence_url": "https://data.mendeley.com/datasets/ww7fd9t325/1",
            "gpr_domain": True,
            "labels_hidden_until_prediction_freeze": False,
            "real_field_or_third_party_asset": True,
            "task_compatible_with_current_claim": True,
            "submission_or_oracle_available_now": False,
            "licence_and_rights_usable": "CC_BY_4_0",
            "decision": "NO-GO",
            "reason": "Public labelled data already used locally; it cannot be a label-held external blind asset.",
        },
        {
            "candidate_id": "HEC-003",
            "name": "Zenodo GPR DATASET record 14637589",
            "source_url": "https://zenodo.org/records/14637589",
            "evidence_url": "https://zenodo.org/records/14637589",
            "gpr_domain": True,
            "labels_hidden_until_prediction_freeze": False,
            "real_field_or_third_party_asset": True,
            "task_compatible_with_current_claim": "partial_track_c_stress_only",
            "submission_or_oracle_available_now": False,
            "licence_and_rights_usable": "CC_BY_4_0",
            "decision": "NO-GO",
            "reason": "Public labelled/organized raw-GPR asset; useful for Track C stress tests but not blind external validation.",
        },
        {
            "candidate_id": "HEC-004",
            "name": "Zenodo MCG GPR dataset",
            "source_url": "https://zenodo.org/records/14270869",
            "evidence_url": "https://zenodo.org/records/14270869",
            "gpr_domain": True,
            "labels_hidden_until_prediction_freeze": False,
            "real_field_or_third_party_asset": False,
            "task_compatible_with_current_claim": False,
            "submission_or_oracle_available_now": False,
            "licence_and_rights_usable": "open_record_but_public_processed_labels",
            "local_status": (
                "downloaded_md5_verified_manifested_nonblind_baseline_and_split_stress"
                if mcg_local_executed
                else "remote_candidate_only"
            ),
            "local_manifest_rows": mcg_manifest.get("rows", 0),
            "local_annotated_rows": mcg_manifest.get("annotated_rows", 0),
            "local_nonblind_baseline_runs": len(mcg_baseline.get("runs", [])),
            "local_split_stress_runs": len(mcg_split_stress.get("runs", [])),
            "local_blind_gate_effect": "NO-GO_public_nonblind_segmentation_asset",
            "decision": "NO-GO",
            "reason": (
                "Local download, manifest, non-blind baseline, and split-stress execution are complete when "
                "available, but this remains a public processed/cropped segmentation dataset sourced from "
                "public data; not a hidden real external validation service."
            ),
        },
        {
            "candidate_id": "HEC-005",
            "name": "CMU-GPR-Dataset",
            "source_url": "https://github.com/rpl-cmu/CMU-GPR-Dataset",
            "evidence_url": "https://github.com/rpl-cmu/CMU-GPR-Dataset",
            "gpr_domain": True,
            "labels_hidden_until_prediction_freeze": False,
            "real_field_or_third_party_asset": True,
            "task_compatible_with_current_claim": False,
            "submission_or_oracle_available_now": False,
            "licence_and_rights_usable": "CC_BY_NC_SA_4_0_noncommercial",
            "decision": "NO-GO",
            "reason": "Open localization/mapping data with ground truth, not a hidden defect/provenance validation server.",
        },
        {
            "candidate_id": "HEC-006",
            "name": "GROUNDED / Localizing Ground Penetrating Radar Evaluation Dataset",
            "source_url": "https://www.roboticsproceedings.org/rss17/p080.pdf",
            "evidence_url": "http://lgprdata.com",
            "gpr_domain": True,
            "labels_hidden_until_prediction_freeze": False,
            "real_field_or_third_party_asset": True,
            "task_compatible_with_current_claim": False,
            "submission_or_oracle_available_now": False,
            "licence_and_rights_usable": "unknown_from_local_audit",
            "decision": "NO-GO",
            "reason": "Open LGPR localization benchmark proposal with ground-truth localization labels; task mismatch and no current hidden oracle receipt.",
        },
    ]


def eligible(row: dict[str, object]) -> bool:
    return all(row.get(key) is True for key in CRITERIA)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Hidden Evaluation Candidate Audit",
        "",
        "Current external candidates were audited against the hard blind-validation gate.",
        "",
        "| id | candidate | hidden labels | real/third-party | task compatible | submission now | decision |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in summary["candidates"]:
        lines.append(
            f"| {row['candidate_id']} | {row['name']} | {row['labels_hidden_until_prediction_freeze']} | "
            f"{row['real_field_or_third_party_asset']} | {row['task_compatible_with_current_claim']} | "
            f"{row['submission_or_oracle_available_now']} | {row['decision']} |"
        )
    lines.extend(
        [
            "",
            f"Eligible candidates: {summary['eligible_candidate_count']}",
            f"Gate decision: {summary['gate_decision']}",
            "",
            "## Boundary",
            "",
            "This audit can identify a candidate route, but it does not create a",
            "third-party label-held evaluation result. The blind external gate remains",
            "closed until a one-shot submission receipt and label-unlock/evaluation",
            "artifact exist for a task-compatible real external asset.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = candidate_rows()
    for row in rows:
        row["passes_all_gate_criteria"] = eligible(row)
    eligible_rows = [row for row in rows if row["passes_all_gate_criteria"]]
    mcg_row = next(row for row in rows if row["candidate_id"] == "HEC-004")
    summary = {
        "run_id": "20260811_E35_hidden_eval_candidate_audit",
        "criteria": CRITERIA,
        "candidates": rows,
        "candidate_count": len(rows),
        "eligible_candidate_count": len(eligible_rows),
        "eligible_candidate_ids": [row["candidate_id"] for row in eligible_rows],
        "hidden_eval_candidate_exists_but_not_usable": any(
            row["labels_hidden_until_prediction_freeze"] is True for row in rows
        )
        and not eligible_rows,
        "local_public_mcg_executed": mcg_row.get("local_status")
        == "downloaded_md5_verified_manifested_nonblind_baseline_and_split_stress",
        "mcg_local_manifest_rows": mcg_row.get("local_manifest_rows"),
        "mcg_local_annotated_rows": mcg_row.get("local_annotated_rows"),
        "mcg_local_nonblind_baseline_runs": mcg_row.get("local_nonblind_baseline_runs"),
        "mcg_local_split_stress_runs": mcg_row.get("local_split_stress_runs"),
        "gate_decision": "NO-GO",
        "blind_external_eligible": False,
        "status": "complete_hidden_eval_candidate_audit_no_eligible_candidate",
    }
    (OUT_DIR / "hidden_eval_candidate_audit_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "hidden_eval_candidate_rows.csv", rows)
    write_md(OUT_DIR / "hidden_eval_candidate_audit_summary.md", summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_count": summary["candidate_count"],
                "eligible_candidate_count": summary["eligible_candidate_count"],
                "gate_decision": summary["gate_decision"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
