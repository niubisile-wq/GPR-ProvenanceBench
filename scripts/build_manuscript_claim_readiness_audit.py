#!/usr/bin/env python3
"""Audit manuscript claims against current evidence and open submission gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "reports" / "manuscript_claim_readiness_audit_20260810"
CLAIMS = BENCH_ROOT / "reports" / "submission_package_skeleton_20260810" / "submission_claim_evidence_map.csv"
GAPS = BENCH_ROOT / "reports" / "submission_gap_closure_matrix_20260810" / "submission_gap_closure_matrix.csv"
NARRATIVE = BENCH_ROOT / "reports" / "narrative_cited_drafts_20260810" / "narrative_section_drafts_v1_cited.md"


STATUS_POLICY = {
    "supported_current_main": {
        "readiness": "allowed_as_current_main",
        "allowed_strength": "current executable evidence supports this as the lead result",
        "required_wording": "Res-SAM environment-transfer fragility across five model families",
        "forbidden_upgrade": "do not describe this as blind external validation or universal GPR generalization",
    },
    "supported_for_checkpoint": {
        "readiness": "allowed_as_context",
        "allowed_strength": "asset/protocol boundary only",
        "required_wording": "current executable evidence boundary",
        "forbidden_upgrade": "do not treat asset counts as performance evidence",
    },
    "directional_only": {
        "readiness": "allowed_with_downgrade",
        "allowed_strength": "directional secondary support only",
        "required_wording": "directionally consistent but modest/model-dependent",
        "forbidden_upgrade": "do not call this universal leakage or a lead claim",
    },
    "stress_test_supported": {
        "readiness": "allowed_as_stress_test",
        "allowed_strength": "stress-test/feasibility-boundary support",
        "required_wording": "multi-layer 4TU counterfactual stress test remains a feasibility boundary",
        "forbidden_upgrade": "do not present as causal proof, main confirmation or blind external validation",
    },
    "gate_supported": {
        "readiness": "allowed_as_gate_boundary",
        "allowed_strength": "feasibility/gate explanation",
        "required_wording": "target-level feasibility boundary",
        "forbidden_upgrade": "do not present as model superiority or confirmation-matrix evidence",
    },
    "not_yet_supported": {
        "readiness": "open_gate_only",
        "allowed_strength": "negative/readiness boundary only",
        "required_wording": "blind external validation remains open/NO-GO",
        "forbidden_upgrade": "do not claim completed external validation or external generalization",
    },
}


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

    claim_rows = read_csv(CLAIMS)
    gap_rows = read_csv(GAPS)
    narrative_text = NARRATIVE.read_text(encoding="utf-8")

    audit_rows: list[dict[str, str]] = []
    for row in claim_rows:
        policy = STATUS_POLICY[row["status"]]
        text_present = "yes" if row["claim"] in narrative_text else "no"
        audit_rows.append(
            {
                "claim_id": row["claim_id"],
                "claim": row["claim"],
                "current_status": row["status"],
                "readiness": policy["readiness"],
                "allowed_strength": policy["allowed_strength"],
                "required_wording": policy["required_wording"],
                "forbidden_upgrade": policy["forbidden_upgrade"],
                "evidence_anchor": row["evidence"],
                "figure_or_table": row["figure_or_table"],
                "allowed_in_abstract": row["allowed_in_abstract"],
                "exact_claim_present_in_narrative": text_present,
            }
        )

    write_csv(
        OUT_DIR / "manuscript_claim_readiness_audit.csv",
        audit_rows,
        [
            "claim_id",
            "claim",
            "current_status",
            "readiness",
            "allowed_strength",
            "required_wording",
            "forbidden_upgrade",
            "evidence_anchor",
            "figure_or_table",
            "allowed_in_abstract",
            "exact_claim_present_in_narrative",
        ],
    )

    forbidden_rows = [
        {
            "risk_id": f"F{i + 1:02d}",
            "forbidden_claim": row["blocked_claim_until_closed"],
            "gate": row["gate"],
            "required_evidence_before_upgrade": row["minimum_evidence_to_close"],
        }
        for i, row in enumerate(gap_rows)
    ]
    for row in audit_rows:
        forbidden_rows.append(
            {
                "risk_id": f"F{len(forbidden_rows) + 1:02d}",
                "forbidden_claim": row["forbidden_upgrade"],
                "gate": f"claim_{row['claim_id']}",
                "required_evidence_before_upgrade": row["evidence_anchor"],
            }
        )
    write_csv(
        OUT_DIR / "forbidden_claims_ledger.csv",
        forbidden_rows,
        ["risk_id", "forbidden_claim", "gate", "required_evidence_before_upgrade"],
    )

    abstract_rows = [
        {
            "slot": "lead_problem",
            "allowed_content": "GPR recognition needs evaluation beyond single curated collections.",
            "must_avoid": "stating that the benchmark already proves field deployment robustness.",
        },
        {
            "slot": "main_result",
            "allowed_content": "Res-SAM environment-transfer tests show the strongest reproducible drop across five model families.",
            "must_avoid": "calling the result blind external validation.",
        },
        {
            "slot": "secondary_result",
            "allowed_content": "Mojahid is directional/modest and 4TU is stress-test/failure-mode evidence.",
            "must_avoid": "presenting Mojahid or 4TU as full independent confirmation.",
        },
        {
            "slot": "limitation",
            "allowed_content": "Blind external validation, rendered figures and repository identifiers remain open gates.",
            "must_avoid": "omitting open gates from the current checkpoint framing.",
        },
    ]
    write_csv(OUT_DIR / "abstract_claim_guardrails.csv", abstract_rows, ["slot", "allowed_content", "must_avoid"])

    allowed_md = [
        "# Allowed manuscript claims 2026-08-10",
        "",
        "These claims are permitted only at the stated strength.",
        "",
        "| Claim | Allowed strength | Required wording | Evidence anchor |",
        "| --- | --- | --- | --- |",
    ]
    for row in audit_rows:
        allowed_md.append(
            f"| {row['claim_id']} | {row['allowed_strength']} | {row['required_wording']} | {row['evidence_anchor']} |"
        )
    allowed_md.extend(
        [
            "",
            "## Abstract guardrail",
            "",
            "The abstract may foreground Res-SAM environment-transfer fragility, but must explicitly avoid blind-external-validation language until a real held-label asset is evaluated.",
            "",
        ]
    )
    (OUT_DIR / "allowed_manuscript_claims.md").write_text("\n".join(allowed_md), encoding="utf-8")

    report = [
        "# Manuscript claim readiness audit 2026-08-10",
        "",
        f"- Claims audited: {len(audit_rows)}",
        f"- Forbidden claim rows: {len(forbidden_rows)}",
        f"- Abstract guardrail rows: {len(abstract_rows)}",
        f"- Claims allowed as current main: {sum(1 for row in audit_rows if row['readiness'] == 'allowed_as_current_main')}",
        f"- Claims requiring downgrade/boundary framing: {sum(1 for row in audit_rows if row['readiness'] != 'allowed_as_current_main')}",
        "",
        "Conclusion: the current manuscript can be drafted conservatively around Res-SAM environment-transfer fragility, but cannot be framed as complete external generalization validation.",
        "",
    ]
    (OUT_DIR / "manuscript_claim_readiness_report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "run_id": "20260810_manuscript_claim_readiness_audit",
        "claims_audited": len(audit_rows),
        "forbidden_claim_rows": len(forbidden_rows),
        "abstract_guardrail_rows": len(abstract_rows),
        "allowed_as_current_main": sum(1 for row in audit_rows if row["readiness"] == "allowed_as_current_main"),
        "requires_downgrade_or_boundary": sum(1 for row in audit_rows if row["readiness"] != "allowed_as_current_main"),
        "submission_ready": False,
        "status": "claim_readiness_audit_ready_submission_not_ready",
        "boundary": "Claim audit defines permitted wording strength; it does not close external validation, figure rendering, DOI, rights or Reporting Summary gates.",
    }
    (OUT_DIR / "manuscript_claim_readiness_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
