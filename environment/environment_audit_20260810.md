# Environment Audit 2026-08-10

## Required Runtime

Minimum runtime required for M0-M2:

1. Python 3.10 or newer.
2. PyYAML.
3. NumPy.
4. Pillow.
5. scikit-learn.
6. PyTorch and torchvision for CNN baselines.
7. A reproducible virtual environment or conda environment file.

## Verified Current State

Verified on 2026-08-10:

1. `python` resolves to the WindowsApps launcher and is not usable in this shell.
2. `py` is usable and launches `D:\学习需求\python.exe`.
3. `py --version` reports Python 3.12.5.
4. `py -m pip --version` reports pip 26.1.2.
5. `conda` is not available in PATH.
6. Core imports pass with `py`: PyYAML, NumPy 2.1.3, Pillow 12.2.0,
   scikit-learn 1.5.2.
7. Deep-learning imports pass with `py`: torch 2.8.0+cpu and torchvision
   0.23.0+cpu.
8. `py scripts/validate_manifest_consistency.py` passes for Mojahid and TIGPR.

Operational rule for the next phase: use `py` instead of `python` unless PATH is
repaired.

## Verification Commands

```powershell
where.exe python
where.exe py
py --version
py -m pip --version
py -c "import yaml, numpy, PIL, sklearn; print('core-ok')"
py -c "import torch, torchvision; print(torch.__version__, torchvision.__version__)"
where.exe conda
```

## Current Pass Criteria

1. `py --version` returns a concrete version. Passed.
2. Core packages import successfully. Passed.
3. PyTorch imports successfully or is explicitly deferred for non-deep baselines.
   Passed with CPU-only PyTorch.
4. The environment can run `scripts/validate_manifest_consistency.py`. Passed.
5. The environment state is captured in a lock file before final benchmark runs.
   Completed for the current CPU `py` runtime:
   `pip_freeze_20260810.txt` and `python_environment_20260810.json`.

## Remaining Environment Risk

The current PyTorch stack is CPU-only. It is enough for manifest checks and
lightweight baselines, but not enough to execute the full CNN/ResNet/EfficientNet/
DeiT matrix at practical speed. A GPU environment still needs to be configured
before the deep-model phase.
