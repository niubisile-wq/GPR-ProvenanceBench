# Return evidence inbox: 06_references

Route: `RTE-006`
Closeout action: `HEC-006`

Put only returned evidence for this route in this folder.

Expected evidence:
manual citation verification sheet, final reference export evidence

Accepted extensions:
.csv;.xlsx;.ris;.bib;.enw;.pdf;.txt;.zip

After evidence is copied here, run:
```powershell
py scripts/build_reference_final_lock_validator.py
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`<REPO_ROOT>\final_return_evidence_inbox_20260810\06_references`
