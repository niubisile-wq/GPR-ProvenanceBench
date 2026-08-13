# External blind GPR validation asset request

We are preparing a provenance-aware GPR recognition benchmark and need one genuinely blind external validation asset. The asset must not have been used for model development, model selection, threshold tuning or figure selection.

Please provide only unlabeled files or images plus an analyst-facing manifest. Labels should be held by an advisor, collaborator or third-party label holder until the prediction submission is frozen and hashed.

## What the analyst can receive before prediction

1. Unlabeled GPR files or exported B-scan images.
2. A manifest with stable sample IDs, file paths, SHA256 hashes, source group, modality and predeclared target task.
3. Non-label metadata needed for grouped error analysis.
4. A rights statement describing what can be used in manuscript figures, aggregate metrics, Source Data and public release.

## What must not be sent before prediction

1. Class labels or diagnostic labels.
2. Folder names, filenames or notes that reveal labels.
3. Label-derived train/test split information.
4. Any informal hint about expected class balance or sample difficulty if it reveals outcome information.

## Required sequence

The analyst validates the unlabeled manifest with strict SHA checks, freezes models and predictions, stores one prediction submission, and only then receives the sealed label file for a single locked evaluation.

Current project status: blind external validation is NO-GO until this sequence is completed with a real asset.
