# Return evidence inbox: 01_author_sendout

Route: `RTE-001`
Closeout action: `HEC-001`

Put only returned evidence for this route in this folder.

Expected evidence:
send timestamp, recipients, subject, sent email export/screenshot, handoff zip SHA256

Accepted extensions:
.md;.txt;.csv;.pdf;.png;.jpg;.zip

After evidence is copied here, run:
```powershell
py scripts/build_post_dispatch_evidence_intake_validator.py
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`<REPO_ROOT>\final_return_evidence_inbox_20260810\01_author_sendout`
