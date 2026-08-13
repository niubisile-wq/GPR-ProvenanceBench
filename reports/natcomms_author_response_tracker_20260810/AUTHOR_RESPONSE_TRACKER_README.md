# Nat Comms Author Response Tracker

This package tracks manual sendout and reply collection after the author sendout
bundle is created.

Current boundary:

1. The email has not been sent by this script.
2. No author replies have been collected by this script.
3. No figure backend has been selected by this script.
4. No final gate is closed by this script.
5. Submission remains not ready.

Use `author_response_send_log_template.csv` only after a real human sendout.
Use `author_response_return_tracker.csv` only after filled files are returned.
Then rerun the ingestion validator, gate binder, command dashboard and full
checks in the order listed in `post_reply_rerun_command_queue.csv`.
