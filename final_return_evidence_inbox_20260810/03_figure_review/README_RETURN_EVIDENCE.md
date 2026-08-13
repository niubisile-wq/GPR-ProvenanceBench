# Return evidence inbox: 03_figure_review

Route: `RTE-003`
Closeout action: `HEC-003`

Put only returned evidence for this route in this folder.

Expected evidence:
completed figure review form and reviewer-marked preview approvals/revisions

Accepted extensions:
.csv;.xlsx;.pdf;.png;.jpg;.zip

After evidence is copied here, run:
```powershell
py scripts/build_python_figure_author_review_intake_validator.py
```

Then run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_m0_m2_checks.ps1
```

Do not edit generated summary JSON files by hand. Do not mark any gate closed until the corresponding validator passes on real returned evidence.

Folder:
`<REPO_ROOT>\final_return_evidence_inbox_20260810\03_figure_review`
