# Return evidence inbox: 07_submission_portal

Route: `RTE-007`
Closeout action: `HEC-007`

Put only returned evidence for this route in this folder.

Expected evidence:
final portal upload list, upload screenshots, submission receipt only after all gates close

Accepted extensions:
.csv;.xlsx;.pdf;.png;.jpg;.txt;.md;.zip

After evidence is copied here, run:
```powershell
py scripts/build_natcomms_submission_final_lock_validator.py
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`<REPO_ROOT>\final_return_evidence_inbox_20260810\07_submission_portal`
