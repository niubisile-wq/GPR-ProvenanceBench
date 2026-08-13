# External blind GPR asset request email draft

Subject: Request for advisor-held blind GPR validation asset

Dear [Name],

We are preparing a manuscript on ground-penetrating-radar recognition and provenance-aware generalization. The current internal evidence indicates that model performance can change substantially under environment/provenance shifts. To avoid overclaiming, we need one independent blind validation asset held outside the model-development workflow.

Requested asset:

1. GPR images/traces or derived examples from one or more sites/projects not used in our current model development.
2. Stable sample identifiers and file checksums.
3. Labels held by you or a delegated label holder until our predictions are frozen.
4. Permission status for using aggregate metrics in a manuscript.
5. Clear indication of whether raw data may be redistributed, or whether only derived metrics/source-data tables may be shared.

Proposed blind protocol:

1. We receive files and a manifest without labels.
2. We freeze preprocessing, model version, seeds and prediction files before seeing labels.
3. You release labels only after the prediction submission is timestamped.
4. We run one locked evaluation for main claims; any reruns are reported as exploratory only.

If this is feasible, please confirm the available modality, approximate sample count, label type and rights constraints.

Best regards,
[Author]
