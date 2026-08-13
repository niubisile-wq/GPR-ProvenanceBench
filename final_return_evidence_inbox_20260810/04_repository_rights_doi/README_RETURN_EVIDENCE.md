# Return evidence inbox: 04_repository_rights_doi

Route: `RTE-004`
Closeout action: `HEC-004`

Put only returned evidence for this route in this folder.

Expected evidence:
repository DOI, code DOI, licence selection, third-party rights clearance, upload checksums

Accepted extensions:
.csv;.xlsx;.pdf;.txt;.md;.json;.zip

After evidence is copied here, run:
```powershell
py scripts/build_availability_repository_finalization_validator.py
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`<REPO_ROOT>\final_return_evidence_inbox_20260810\04_repository_rights_doi`
