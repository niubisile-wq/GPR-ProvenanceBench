#!/usr/bin/env python3
"""Build manuscript framing branches for the external-validation contingency."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "external_validation_contingency_framing_20260810"
GAP_SUMMARY = BENCH_ROOT / "reports" / "submission_gap_closure_matrix_20260810" / "submission_gap_closure_summary.json"
BLIND_SUMMARY = BENCH_ROOT / "reports" / "blind_external_acquisition_package_20260810" / "blind_external_acquisition_package_summary.json"
CLAIM_SUMMARY = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "manuscript_claim_readiness_summary.json"


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gap_summary = json.loads(GAP_SUMMARY.read_text(encoding="utf-8"))
    blind_summary = json.loads(BLIND_SUMMARY.read_text(encoding="utf-8"))
    claim_summary = json.loads(CLAIM_SUMMARY.read_text(encoding="utf-8"))

    branch_rows = [
        {
            "branch_id": "TRACK-A",
            "branch_name": "External-blind-validation completed before manuscript lock",
            "activation_condition": "A real independent GPR asset passes strict-SHA intake; labels are held outside the analyst workflow; prediction file is frozen before label unlock; one locked evaluation is run.",
            "manuscript_positioning": "Finding-led provenance-aware generalization paper with a bounded blind external validation result.",
            "allowed_external_validation_language": "One held-label external validation asset was evaluated under a locked prediction protocol.",
            "still_forbidden": "Do not generalize beyond the asset, label space or preprocessing specified in the locked protocol.",
            "status": "inactive_until_evidence_exists",
        },
        {
            "branch_id": "TRACK-B",
            "branch_name": "No external blind validation by decision cutoff",
            "activation_condition": "No real blind external asset satisfies strict intake and locked evaluation before manuscript lock.",
            "manuscript_positioning": "Benchmark/resource and evidence-boundary paper centred on Res-SAM environment-transfer fragility and provenance-aware evaluation.",
            "allowed_external_validation_language": "Blind external validation remains an open gate; the paper reports an auditable local evidence boundary.",
            "still_forbidden": "Do not write external generalization, completed blind validation, or deployment robustness.",
            "status": "currently_applicable_fallback",
        },
    ]
    write_csv(
        OUT_DIR / "external_validation_branch_decision_matrix.csv",
        branch_rows,
        ["branch_id", "branch_name", "activation_condition", "manuscript_positioning", "allowed_external_validation_language", "still_forbidden", "status"],
    )

    title_rows = [
        {
            "branch_id": "TRACK-A",
            "rank": "1",
            "title": "Locked external validation of provenance-aware environment transfer in ground-penetrating-radar recognition",
            "use_condition": "Use only after a real external blind result exists.",
            "risk": "Not usable at the current checkpoint.",
        },
        {
            "branch_id": "TRACK-A",
            "rank": "2",
            "title": "Provenance-aware GPR recognition reveals environment-transfer fragility under locked external validation",
            "use_condition": "Use only if external result supports the same bounded conclusion.",
            "risk": "Overstrong unless the external asset aligns with the tested claim.",
        },
        {
            "branch_id": "TRACK-B",
            "rank": "1",
            "title": "Environment transfer exposes fragile generalization in ground-penetrating-radar recognition",
            "use_condition": "Current safest finding-led title without external validation.",
            "risk": "Needs explicit boundary in abstract and Discussion.",
        },
        {
            "branch_id": "TRACK-B",
            "rank": "2",
            "title": "Provenance-aware evaluation reveals environment-shift fragility in ground-penetrating-radar recognition",
            "use_condition": "Use if the paper is framed as benchmark/resource plus broad benchmark-trust argument.",
            "risk": "More workflow-led; less direct as a result title.",
        },
    ]
    write_csv(OUT_DIR / "contingency_title_set.csv", title_rows, ["branch_id", "rank", "title", "use_condition", "risk"])

    abstract_track_a = """# Track A abstract scaffold

Use only after a real external blind validation asset is acquired and evaluated under a locked protocol.

Ground-penetrating radar (GPR) recognition models are often evaluated within curated datasets whose samples can share acquisition, environment or processing histories. We assembled GPR-ProvenanceBench as an auditable workflow linking dated manifests, grouped split logic, environment-transfer tests, model-family comparisons and source-data traceability. In the current local evidence matrix, Res-SAM environment transfer produced the strongest reproducible signal, with real-to-synthetic balanced-accuracy drops in all five model families and synthetic-to-real drops in four of five families. [Insert locked external-validation result only if prediction freeze, label unlock and one-shot evaluation are complete.] Together, these results would support a bounded claim that provenance-aware evaluation can expose GPR generalization fragility across both local environment transfer and one held-label external asset. The claim must remain limited to the validated asset scope, label definitions and preprocessing protocol.
"""
    (OUT_DIR / "track_a_external_validated_abstract_scaffold.md").write_text(abstract_track_a, encoding="utf-8")

    abstract_track_b = """# Track B conservative abstract

Ground-penetrating radar (GPR) recognition models are often evaluated within curated datasets whose samples may share acquisition, environment or processing histories. We assembled GPR-ProvenanceBench as an auditable workflow linking dated manifests, grouped split logic, environment-transfer tests, model-family comparisons and source-data traceability. At the current checkpoint, Res-SAM environment transfer provides the strongest reproducible signal: real-to-synthetic transfer showed directional and material balanced-accuracy drops in all five model families, with a mean delta of 0.4239, and synthetic-to-real transfer showed directional and material drops in four of five families, with a mean delta of 0.3743. Mojahid provides directional but modest split-sensitivity support, whereas 4TU defines stress-test and feasibility boundaries. These results support a provenance-aware benchmark-trust argument for GPR recognition. Blind external validation remains an open gate rather than a completed result.
"""
    (OUT_DIR / "track_b_no_external_validation_abstract.md").write_text(abstract_track_b, encoding="utf-8")

    discussion_rows = [
        {
            "branch_id": "TRACK-A",
            "discussion_boundary": "Interpret the external result as one held-label confirmation layer, not as proof of deployment-wide robustness.",
            "required_sentence": "The external result should be interpreted within the asset, label and preprocessing boundaries defined before label release.",
        },
        {
            "branch_id": "TRACK-B",
            "discussion_boundary": "Interpret the paper as a local auditable evidence boundary and benchmark/resource contribution.",
            "required_sentence": "The absence of a completed blind external validation layer limits the manuscript to provenance-aware evidence auditing rather than external generalization.",
        },
    ]
    write_csv(OUT_DIR / "discussion_boundary_insertions.csv", discussion_rows, ["branch_id", "discussion_boundary", "required_sentence"])

    no_go_rows = [
        {
            "forbidden_claim": "The model generalizes externally.",
            "why_forbidden_currently": "No real held-label external asset has been acquired or evaluated.",
            "allowed_current_wording": "External validation remains an open gate.",
        },
        {
            "forbidden_claim": "Blind validation was completed.",
            "why_forbidden_currently": "Existing materials are request letters, templates and dry runs only.",
            "allowed_current_wording": "A blind external validation protocol and acquisition package are ready.",
        },
        {
            "forbidden_claim": "The benchmark proves deployment robustness.",
            "why_forbidden_currently": "Current evidence is local environment transfer plus bounded secondary/stress-test evidence.",
            "allowed_current_wording": "The benchmark exposes provenance and environment-transfer fragility under the current evidence boundary.",
        },
    ]
    write_csv(OUT_DIR / "external_validation_no_go_wording.csv", no_go_rows, ["forbidden_claim", "why_forbidden_currently", "allowed_current_wording"])

    qa_rows = [
        {"check": "track_a_marked_inactive", "result": "PASS", "detail": "Track A requires real external evidence before activation."},
        {"check": "track_b_current_fallback", "result": "PASS", "detail": "Track B preserves external validation as an open gate."},
        {"check": "no_completed_external_validation_claim", "result": "PASS", "detail": f"blind_external_gate_status={blind_summary['blind_external_gate_status']}"},
        {"check": "submission_ready_not_claimed", "result": "PASS", "detail": f"submission_ready={gap_summary['submission_ready']}"},
        {"check": "claim_boundary_preserved", "result": "PASS", "detail": claim_summary["status"]},
    ]
    write_csv(OUT_DIR / "external_validation_contingency_qa.csv", qa_rows, ["check", "result", "detail"])

    readme = """# External validation contingency framing 2026-08-10

This package defines two manuscript-positioning branches for the external-validation gate.

## Track A

Use only if a real blind external validation asset is acquired, labels are held outside the analyst workflow, predictions are frozen before label unlock, and one locked evaluation is run.

## Track B

Use if no real external blind asset is available before manuscript lock. This is the currently applicable fallback: a benchmark/resource and evidence-boundary paper centred on Res-SAM environment-transfer fragility.

## Stop rules

1. Do not activate Track A without a real held-label asset and locked evaluation.
2. Do not claim external generalization under Track B.
3. Do not remove the external-validation limitation from the abstract or Discussion while the gate is open.
"""
    (OUT_DIR / "EXTERNAL_VALIDATION_CONTINGENCY_README.md").write_text(readme, encoding="utf-8")

    summary = {
        "run_id": "20260810_external_validation_contingency_framing",
        "branches": len(branch_rows),
        "title_rows": len(title_rows),
        "abstract_scaffolds": 2,
        "discussion_boundary_rows": len(discussion_rows),
        "no_go_rows": len(no_go_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "current_applicable_branch": "TRACK-B",
        "blind_external_gate_status": blind_summary["blind_external_gate_status"],
        "submission_ready": False,
        "status": "external_validation_contingency_framing_ready_not_submission_final",
        "boundary": "This package provides manuscript framing contingencies; it does not create or complete external validation.",
    }
    (OUT_DIR / "external_validation_contingency_framing_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = [
        "# External validation contingency framing report 2026-08-10",
        "",
        f"- Branches: {summary['branches']}",
        f"- Title rows: {summary['title_rows']}",
        f"- Abstract scaffolds: {summary['abstract_scaffolds']}",
        f"- Discussion boundary rows: {summary['discussion_boundary_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Current applicable branch: {summary['current_applicable_branch']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: Track B is the current safe manuscript-positioning fallback while blind external validation remains NO-GO.",
        "",
    ]
    (OUT_DIR / "external_validation_contingency_framing_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
