# Code Availability Skeleton 2026-08-10

Ready-to-paste status: not ready. Public repository URL, release tag, archive DOI and licence are missing.

## Draft Statement

The analysis code and reproducibility scripts used to generate the current benchmark manifests, source-data packages, Results/Methods skeletons and submission-package skeleton will be made available in [CODE_REPOSITORY_URL] and archived at [ZENODO_OR_OTHER_ARCHIVE_DOI] before submission. The archived release should include the PowerShell runbook, Python scripts, environment files, protocol templates and instructions needed to reproduce the M0-M2 artifacts from locally available or properly obtained input data. Third-party datasets are not redistributed with the code unless their licences permit redistribution.

## Required Actions

1. Create a clean public repository or release branch.
2. Add a software licence after institutional approval.
3. Add a README with setup, `py` launcher usage, expected input locations and `run_m0_m2_checks.ps1` instructions.
4. Archive a release in Zenodo, Figshare, OSF or an institutional repository to obtain a DOI.
5. Remove or parameterize local absolute paths before public release.
6. Add checksums or manifest hashes for critical input and output files where appropriate.

## Boundary

The current code availability statement covers M0-M2 artifacts only. It does not cover future final figures, real blind external validation, full Res-SAM model replication or any GPU training environment that has not yet been frozen.
