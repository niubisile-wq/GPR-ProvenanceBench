# Nat Comms Author Sendout Bundle v2

This v2 bundle includes the original author reply forms plus the new fill guide,
send/return lifecycle templates and safe rerun order.

Manual use:

1. Send the files under `attachments/reply_forms/` and the guide under
   `attachments/fill_guides/`.
2. Do not mark `email_sent=true` until the message is actually sent outside this
   script.
3. After real sendout, fill `attachments/lifecycle_logs/author_response_send_log_template.csv`.
4. After returned files are received, fill
   `attachments/lifecycle_logs/author_response_return_tracker.csv`.
5. Then rerun the validators and full checks listed in
   `attachments/lifecycle_logs/manual_field_safe_rerun_order.csv`.

Boundary: this bundle does not send email, collect replies, select a backend,
render figures, create DOI records, close gates, generate final files or submit
the manuscript.
