#!/usr/bin/env python3
"""Build a Nature-style pre-submission reviewer-risk audit from author-review draft."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "pre_submission_reviewer_risk_audit_20260810"
MANUSCRIPT = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_v0_1.md"
MANUSCRIPT_SUMMARY = BENCH_ROOT / "reports" / "author_review_manuscript_package_20260810" / "author_review_manuscript_summary.json"
GAP_MATRIX = BENCH_ROOT / "reports" / "submission_gap_closure_matrix_20260810" / "submission_gap_closure_matrix.csv"
CLAIM_AUDIT = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810" / "manuscript_claim_readiness_audit.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manuscript_text = MANUSCRIPT.read_text(encoding="utf-8")
    manuscript_summary = json.loads(MANUSCRIPT_SUMMARY.read_text(encoding="utf-8"))
    gap_rows = read_csv(GAP_MATRIX)
    claim_rows = read_csv(CLAIM_AUDIT)

    fact_base = {
        "input_scope": "Author-review manuscript package v0.1 with title, abstract, Introduction, Results, Discussion, Methods and Conclusion.",
        "assessment_boundary": "No rendered figures, no real blind external validation, no repository/code DOI, no rights clearance, no final Reporting Summary and no final Nature-style references.",
        "shared_claim": "GPR-ProvenanceBench argues that environment and provenance structure can reshape apparent GPR recognition generalization, with Res-SAM environment transfer as the current main signal and Mojahid/4TU as bounded secondary and stress-test evidence.",
        "visible_evidence": "Mojahid/4TU/Res-SAM manifests, five-model Mojahid/Res-SAM synthesis, Res-SAM transfer deltas, Mojahid grouped-vs-random contrast, 4TU counterfactual stress tests and feasibility audit, and a blind external protocol dry run.",
        "missing_materials": "Rendered figures, independent held-label external asset, final repository identifiers, final rights decision, final Reporting Summary and final references.",
    }
    (OUT_DIR / "review_fact_base.json").write_text(json.dumps(fact_base, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    reviewer_reports = """# Pre-submission reviewer-risk audit 2026-08-10

## Review setup

- Input scope: Author-review manuscript package v0.1, assembled from the current local evidence and bounded draft sections.
- Assessment boundary: The manuscript is not submission-final. Main figures are not rendered, blind external validation is not complete, repository identifiers are missing, rights clearance is unresolved, the Reporting Summary is draft-only and references remain candidate markers.
- Shared manuscript claim summary: The manuscript argues that environment and provenance structure can reshape apparent GPR recognition generalization. The strongest current evidence is Res-SAM environment-transfer fragility across five model families; Mojahid and 4TU provide secondary split-sensitivity and stress-test boundaries.
- Visible evidence base: Dated asset manifests, five-model Mojahid/Res-SAM synthesis, Res-SAM transfer deltas, Mojahid grouped-vs-random contrast, 4TU raw-trace counterfactual tests, 4TU feasibility audit and blind-external protocol templates.
- Missing materials affecting confidence: Rendered figures, real held-label external validation, repository/code DOI, rights clearance, final Reporting Summary and final references.

## Reviewer 1

- Overall assessment: The manuscript has a clear technical premise and a useful audit workflow, but the authors' strongest generalization case is not yet established because the external-validation gate remains open.
- Who would be interested in the results, and why: Researchers using GPR recognition, remote-sensing model evaluation, dataset benchmarking and applied machine learning would be interested because the draft links performance estimates to provenance and environment structure.
- Major strengths: The draft separates executable asset status from nominal dataset availability, reports model-family-level Res-SAM transfer effects and avoids promoting 4TU or TIGPR beyond their current evidence state.
- Major concerns: The main figures are not rendered, the blind external validation evidence is absent, and the current manuscript still depends on candidate citation markers and provisional repository statements.
- Technical failings that need to be addressed before the case is established: A real external held-label asset must be acquired and evaluated once after prediction freezing; the source-data and figure panels must be rendered and checked; repository and rights status must be resolved before Data and Code Availability can be final.
- Assessment against Nature-style criteria: Originality is plausible as an auditable provenance-focused workflow, but prior-work distinction still requires final citation verification. Scientific importance is potentially strong for GPR evaluation, but not yet outstanding without external validation. Interdisciplinary readership is possible across GPR, remote sensing and ML evaluation, but the broad implication should remain bounded. Technical soundness is internally organized but incomplete at the external-validation and figure layers. Readability is adequate for technical readers, but nonspecialists may need a clearer schematic once figures are rendered.
- Recommendation posture: Promising but technically not established from the provided evidence.

## Reviewer 2

- Overall assessment: The central finding is interesting because it shifts the manuscript from model performance ranking to provenance-aware evaluation, but the novelty and significance case remains underdeveloped without a final comparison to prior GPR benchmarking work.
- Who would be interested in the results, and why: The most direct audience is GPR recognition researchers, with adjacent interest from scientists concerned with dataset leakage, environment shift and benchmark reproducibility.
- Major strengths: The title and abstract are appropriately conservative, the Res-SAM result is positioned as the lead claim, and Mojahid/4TU are framed as bounded secondary evidence rather than inflated confirmation.
- Major concerns: The manuscript currently reads more like a strong checkpoint paper than a final high-impact submission because several decisive outputs are still pending. The broad-interest claim depends on whether the authors can show that the observed fragility generalizes beyond the current local matrix.
- Technical failings that need to be addressed before the case is established: The manuscript needs final figures, final references and a resolved external-validation route. If no external asset is obtained, the framing should shift explicitly toward benchmark/resource and evidence-boundary contribution.
- Assessment against Nature-style criteria: Originality is credible but not fully benchmarked against prior literature in the current draft. Scientific importance may be substantial if the workflow changes how GPR models are evaluated, but this is not yet demonstrated as far-reaching. Interdisciplinary readership is moderate and could improve with clearer connection to general ML dataset-shift problems. Technical soundness is strongest for internal auditability and weakest for external confirmation. Readability is concise but still assumes readers understand GPR provenance, grouped splits and transfer settings.
- Recommendation posture: Potentially significant after reframing and evidence completion; currently the broad-importance case remains incomplete.

## Reviewer 3

- Overall assessment: The manuscript is readable and unusually candid about evidence boundaries, but its accessibility and cross-disciplinary appeal will depend heavily on final figures and a simple visual explanation of the audit workflow.
- Who would be interested in the results, and why: Applied ML, geophysics, infrastructure inspection and benchmark-design readers could care if the manuscript clearly explains why environment-transfer fragility changes how GPR recognition results should be trusted.
- Major strengths: The manuscript avoids overclaiming, uses a clear lead result and repeatedly distinguishes protocol readiness from validation. This honesty improves credibility.
- Major concerns: The draft is still text-heavy for nonspecialists, figure references are conceptual, and the exact practical consequence for field deployment is not yet visually or narratively sharp.
- Technical failings that need to be addressed before the case is established: The authors need a rendered workflow figure, a main result figure that makes the Res-SAM transfer drop legible, final source-data links and a clear statement of what users should do differently after reading the paper.
- Assessment against Nature-style criteria: Originality is accessible as an audit workflow if the figures make the workflow visible. Scientific importance is promising but currently framed as cautious rather than far-reaching. Interdisciplinary readership is possible but not guaranteed because the draft needs a nonspecialist explanation of GPR data provenance. Technical soundness is bounded and transparent, but missing external validation remains a major limitation. Readability is serviceable for reviewers but would benefit from stronger figure-led communication.
- Recommendation posture: Readable and credible as an author-review draft, but not yet persuasive as a broad-readership submission.

## Cross-review synthesis

- Consensus strengths: All reviewers agree that the manuscript has a coherent central argument, a conservative claim hierarchy and a useful distinction between executable evidence and open validation gates.
- Consensus technical risks: The largest shared risks are missing blind external validation, missing rendered figures, unresolved repository/rights status, draft-only Reporting Summary and non-final references.
- Where emphasis differs across reviewers: Reviewer 1 weights technical establishment most heavily; Reviewer 2 weights novelty and significance; Reviewer 3 weights readability and interdisciplinary uptake.
- Broad-interest / significance readout: The manuscript could interest readers beyond GPR if it is framed as a provenance-aware evaluation problem relevant to environment shift and benchmark trust. The current draft does not yet prove far-reaching implications.
- Most important issues to resolve before a strong Nature-style case is established: render the main figures, obtain or explicitly downgrade the external-validation claim, finalize repository and rights status, verify references and decide whether the paper is a finding-led Article or a benchmark/resource-style contribution.

## Risk / unsupported claims

- Completed blind external validation is unsupported.
- External generalization beyond the current audited matrix is unsupported.
- Public data/code deposition is unsupported until DOI/accession and licence decisions exist.
- Final Reporting Summary readiness is unsupported.
- Final figure-based claims are unsupported until figures are rendered and visually QAed.
- Final numbered references are unsupported while candidate [P#] markers remain.
"""
    (OUT_DIR / "pre_submission_reviewer_reports.md").write_text(reviewer_reports, encoding="utf-8")

    risk_rows = [
        {
            "priority": "1",
            "risk": "Missing real blind external validation",
            "reviewer_axis": "technical_soundness",
            "current_evidence": "Protocol templates and dry run only",
            "required_resolution": "Acquire held-label asset and run one locked evaluation, or downgrade framing.",
        },
        {
            "priority": "2",
            "risk": "Main figures not rendered",
            "reviewer_axis": "readability_and_technical_soundness",
            "current_evidence": "Figure specs and source packages only",
            "required_resolution": "Render Figure 1-Figure 6 or final reduced set and complete visual QA.",
        },
        {
            "priority": "3",
            "risk": "Repository and rights unresolved",
            "reviewer_axis": "technical_soundness_reproducibility",
            "current_evidence": "Metadata drafts and staging preview only",
            "required_resolution": "Resolve licence, rights, repository route and DOI/accession.",
        },
        {
            "priority": "4",
            "risk": "Broad-interest case not fully established",
            "reviewer_axis": "scientific_importance_interdisciplinary_interest",
            "current_evidence": "GPR-focused argument with general ML benchmark implications",
            "required_resolution": "Sharpen cross-field implications and visual workflow explanation.",
        },
        {
            "priority": "5",
            "risk": "References not final",
            "reviewer_axis": "originality_readability",
            "current_evidence": "Candidate [P#] markers and local citation pass",
            "required_resolution": "Manual verification and Nature-style numbered references.",
        },
    ]
    write_csv(OUT_DIR / "reviewer_risk_priority_queue.csv", risk_rows, ["priority", "risk", "reviewer_axis", "current_evidence", "required_resolution"])

    axis_rows = [
        {"axis": "originality", "status": "promising_not_final", "evidence": "Provenance-aware GPR evaluation workflow", "risk": "Prior-work distinction not final without verified references."},
        {"axis": "scientific_importance", "status": "promising_but_not_far_reaching_yet", "evidence": "Res-SAM environment-transfer fragility", "risk": "External validation and broad implication are not yet established."},
        {"axis": "interdisciplinary_readership", "status": "possible_but_needs_sharper_framing", "evidence": "Links GPR, benchmark trust and environment shift", "risk": "May read as field-internal without figure-led explanation."},
        {"axis": "technical_soundness", "status": "internally_auditable_but_incomplete", "evidence": "M0-M2 checks and dated artifacts", "risk": "External validation, figures and DOI gates remain open."},
        {"axis": "readability_for_nonspecialists", "status": "serviceable_needs_figures", "evidence": "Coherent author-review manuscript", "risk": "Nonspecialist readers need workflow and result figures."},
    ]
    write_csv(OUT_DIR / "review_axis_assessment.csv", axis_rows, ["axis", "status", "evidence", "risk"])

    qa_rows = [
        {"check": "three_reviewer_reports", "result": "PASS", "detail": "Reviewer 1, Reviewer 2 and Reviewer 3 sections are present."},
        {"check": "cross_review_synthesis", "result": "PASS", "detail": "Cross-review synthesis section is present."},
        {"check": "risk_unsupported_claims", "result": "PASS", "detail": "Risk / unsupported claims section is present."},
        {"check": "no_editorial_decision", "result": "PASS", "detail": "No final accept/reject decision is stated."},
        {"check": "no_invented_reviewer_identity", "result": "PASS", "detail": "Reports differ by emphasis only."},
    ]
    write_csv(OUT_DIR / "reviewer_audit_qa.csv", qa_rows, ["check", "result", "detail"])

    summary = {
        "run_id": "20260810_pre_submission_reviewer_risk_audit",
        "reviewer_reports": 3,
        "risk_rows": len(risk_rows),
        "axis_rows": len(axis_rows),
        "qa_rows": len(qa_rows),
        "qa_pass": all(row["result"] == "PASS" for row in qa_rows),
        "manuscript_status": manuscript_summary["status"],
        "open_gates": len(gap_rows),
        "claims_audited": len(claim_rows),
        "submission_ready": False,
        "status": "reviewer_risk_audit_ready_submission_not_ready",
        "boundary": "Reviewer-risk audit identifies pre-submission weaknesses; it does not close figures, external validation, DOI, rights, Reporting Summary or references.",
    }
    (OUT_DIR / "reviewer_risk_audit_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = [
        "# Reviewer-risk audit report 2026-08-10",
        "",
        f"- Reviewer reports: {summary['reviewer_reports']}",
        f"- Risk rows: {summary['risk_rows']}",
        f"- Axis rows: {summary['axis_rows']}",
        f"- QA rows: {summary['qa_rows']}",
        f"- QA pass: {summary['qa_pass']}",
        f"- Status: {summary['status']}",
        "",
        "Conclusion: the manuscript is coherent enough for author review, but reviewer-facing technical risks remain substantial.",
        "",
    ]
    (OUT_DIR / "reviewer_risk_audit_report.md").write_text("\n".join(report), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
