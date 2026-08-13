#!/usr/bin/env python3
"""Validate consistency of experiment-only gates and blind-external evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "experiment_gate_consistency_20260811"


def read_json(rel_path: str) -> dict:
    path = BENCH_ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["check", "result", "detail"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pass_row(check: str, condition: bool, detail: str) -> dict[str, object]:
    return {"check": check, "result": "PASS" if condition else "FAIL", "detail": detail}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = read_json("reports/experiment_only_progress_20260811/experiment_only_progress_summary.json")
    readiness = read_json("reports/external_validation_readiness_20260810/external_validation_readiness_summary.json")
    candidate = read_json("reports/hidden_eval_candidate_audit_20260811/hidden_eval_candidate_audit_summary.json")
    freeze = read_json("reports/external_blind_freeze_regression_20260811/external_blind_freeze_regression_summary.json")
    intake = read_json("reports/external_blind_intake_20260810/external_blind_intake_validation_summary.json")
    locked = read_json("reports/external_blind_locked_evaluation_20260810/external_blind_locked_evaluation_summary.json")
    collision = read_json("reports/cross_asset_collision_audit_20260811/cross_asset_collision_audit_summary.json")
    raw_candidate = read_json("reports/external_raw_gpr_candidate_probe_20260811/external_raw_gpr_candidate_probe_summary.json")
    mcg_download = read_json("reports/zenodo_mcg_gpr_download_20260811/zenodo_mcg_gpr_download_summary.json")
    mcg_manifest = read_json("reports/zenodo_mcg_gpr_manifest_20260811/zenodo_mcg_gpr_manifest_summary.json")
    mcg_baseline = read_json("reports/zenodo_mcg_gpr_nonblind_baseline_20260811/zenodo_mcg_gpr_nonblind_baseline_summary.json")
    mcg_split_stress = read_json("reports/zenodo_mcg_gpr_split_stress_20260811/zenodo_mcg_gpr_split_stress_summary.json")

    readiness_gate = readiness.get("gate", {})
    checks = [
        pass_row(
            "progress blind gate remains no-go",
            progress.get("blind_external_status") == "NO-GO" and progress.get("submission_ready") is False,
            f"blind={progress.get('blind_external_status')}; submission_ready={progress.get('submission_ready')}",
        ),
        pass_row(
            "readiness gate remains no-go with zero ready tracks",
            readiness_gate.get("status") == "NO-GO" and readiness_gate.get("current_ready_tracks") == [],
            f"gate={readiness_gate.get('status')}; ready_tracks={readiness_gate.get('current_ready_tracks')}",
        ),
        pass_row(
            "hidden-eval candidate audit has no eligible candidate",
            candidate.get("status") == "complete_hidden_eval_candidate_audit_no_eligible_candidate"
            and candidate.get("eligible_candidate_count") == 0
            and candidate.get("gate_decision") == "NO-GO",
            f"status={candidate.get('status')}; eligible={candidate.get('eligible_candidate_count')}; gate={candidate.get('gate_decision')}",
        ),
        pass_row(
            "synthetic freeze regression stays non-eligible despite passing",
            freeze.get("status") == "complete_synthetic_blind_freeze_regression"
            and freeze.get("prediction_precedes_unlock") is True
            and freeze.get("blind_external_eligible") is False
            and intake.get("status") == "PASS"
            and locked.get("status") == "PASS",
            (
                f"freeze={freeze.get('status')}; precedes={freeze.get('prediction_precedes_unlock')}; "
                f"eligible={freeze.get('blind_external_eligible')}; intake={intake.get('status')}; locked={locked.get('status')}"
            ),
        ),
        pass_row(
            "deepmask collision prevents independent evidence promotion",
            collision.get("status") == "complete_local_cross_asset_collision_audit"
            and collision.get("independent_asset_clusters_by_hash", 0) >= 4
            and collision.get("mojahid_deepmask_complete_sha_overlap") is True
            and collision.get("deepmask_independent_external_evidence_eligible") is False,
            (
                f"collision={collision.get('status')}; clusters={collision.get('independent_asset_clusters_by_hash')}; "
                f"overlap={collision.get('mojahid_deepmask_complete_sha_overlap')}; "
                f"eligible={collision.get('deepmask_independent_external_evidence_eligible')}"
            ),
        ),
        pass_row(
            "public raw candidate cannot close blind gate",
            raw_candidate.get("decision", "").startswith("A public raw-GPR candidate")
            and raw_candidate.get("candidates", [{}])[0].get("blind_external_eligible") is False,
            f"decision={raw_candidate.get('decision')}; candidate_eligible={raw_candidate.get('candidates', [{}])[0].get('blind_external_eligible')}",
        ),
        pass_row(
            "public MCG candidate cannot close blind gate",
            mcg_download.get("status") == "complete_public_mcg_gpr_download_verified_extracted"
            and mcg_download.get("md5_verified") is True
            and mcg_manifest.get("status") == "complete_public_mcg_gpr_manifest"
            and mcg_manifest.get("rows") == 8100
            and mcg_manifest.get("annotated_rows") == 966
            and mcg_baseline.get("status") == "complete_public_mcg_gpr_nonblind_baseline"
            and mcg_split_stress.get("status") == "complete_public_mcg_gpr_split_stress"
            and mcg_download.get("blind_external_eligible") is False
            and mcg_manifest.get("blind_external_eligible") is False
            and mcg_baseline.get("blind_external_eligible") is False
            and mcg_split_stress.get("blind_external_eligible") is False,
            (
                f"download={mcg_download.get('status')}; rows={mcg_manifest.get('rows')}; "
                f"annotated={mcg_manifest.get('annotated_rows')}; baseline={mcg_baseline.get('status')}; "
                f"split_stress={mcg_split_stress.get('status')}; eligible={mcg_split_stress.get('blind_external_eligible')}"
            ),
        ),
    ]
    status = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    summary = {
        "run_id": "20260811_E36_experiment_gate_consistency",
        "status": status,
        "checks": checks,
        "pass_count": sum(row["result"] == "PASS" for row in checks),
        "fail_count": sum(row["result"] != "PASS" for row in checks),
        "blind_external_gate_consistent_no_go": status == "PASS",
        "submission_ready": False,
        "blind_external_eligible": False,
    }
    (OUT_DIR / "experiment_gate_consistency_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "experiment_gate_consistency_qa.csv", checks)
    lines = [
        "# Experiment Gate Consistency",
        "",
        f"Status: {status}",
        "",
        "| check | result | detail |",
        "| --- | --- | --- |",
    ]
    for row in checks:
        lines.append(f"| {row['check']} | {row['result']} | {row['detail']} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This validates gate consistency only. It cannot close the blind external",
            "validation gate without a real label-held one-shot evaluation artifact.",
            "",
        ]
    )
    (OUT_DIR / "experiment_gate_consistency_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": status, "pass_count": summary["pass_count"], "fail_count": summary["fail_count"]}, ensure_ascii=False))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
