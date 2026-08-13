# Return evidence inbox: 05_reporting_summary

Route: `RTE-005`
Closeout action: `HEC-005`

Put only returned evidence for this route in this folder.

Expected evidence:
completed Reporting Summary answers and author confirmation

Accepted extensions:
.csv;.xlsx;.docx;.pdf;.txt;.md;.zip

After evidence is copied here, run:
```powershell
py scripts/build_reporting_summary_final_lock_validator.py
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`<REPO_ROOT>\final_return_evidence_inbox_20260810\05_reporting_summary`
