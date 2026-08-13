# Label-holder SOP for blind external validation

## Role

The label holder protects the true labels until the analyst freezes the prediction submission.

## Before prediction

1. Assign stable sample IDs.
2. Prepare the sealed label file with `sample_id`, `sealed_label`, `label_space_version`, `label_holder` and `sealed_timestamp`.
3. Store the label file outside the analyst workflow.
4. Optionally provide a hash of the sealed label file, but do not provide labels.

## After prediction freeze

1. Verify that the analyst has produced a frozen prediction file and hash record.
2. Record `unlock_timestamp` and `unlock_authorized_by`.
3. Release the label file.
4. Do not allow model changes before the locked main-claim evaluation.

## Non-negotiable rule

Any evaluation after labels have been seen and after model or threshold changes is exploratory only. It cannot replace the main blind external validation result.
