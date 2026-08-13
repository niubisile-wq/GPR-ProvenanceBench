# NatComms final operator execution bundle v2

Use this bundle after real human-returned evidence is available.

Current state: all post-return commands are guarded and refused because no returned evidence, protected writeback, gate transition, or submission readiness condition is met.

Execution order:
1. Put real returned files into the canonical folders under `final_return_evidence_inbox_20260810`.
2. Regenerate the final return evidence intake scanner.
3. Run the writeback preflight and manually inspect allowed protected fields.
4. Only after protected writeback is documented, regenerate the gate transition validator.
5. Use the guarded runner; it must refuse execution until guard conditions pass.

Do not upload portal files or submit the manuscript from this bundle.
