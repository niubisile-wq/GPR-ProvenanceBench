# Return evidence inbox: 02_author_replies

Route: `RTE-002`
Closeout action: `HEC-002`

Put only returned evidence for this route in this folder.

Expected evidence:
completed author reply forms, backend/scope decision, admin confirmations

Accepted extensions:
.csv;.xlsx;.docx;.pdf;.txt;.md;.zip

After evidence is copied here, run:
```powershell
py scripts/build_natcomms_author_reply_ingestion_validator.py
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`<REPO_ROOT>\final_return_evidence_inbox_20260810\02_author_replies`
