$ErrorActionPreference = "Stop"
Write-Host "POST-RETURN GUARDED EXECUTION REFUSED"
Write-Host "No commands are allowed because real returned evidence/writeback/gate transitions are not ready."
Write-Host "Run build_post_return_guarded_execution_runner.py after real evidence writeback to regenerate guard state."
exit 2
