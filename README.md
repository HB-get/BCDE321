
# BCDE321 Advanced Programming: A2 Walking Skeleton

This repository provides one common Tkinter and pytest baseline for Assessment 2. It demonstrates a small framework-to-domain seam without completing the Zombie in My Pocket solution.

## Requirements

- Python 3.14 or later
- Tkinter included with the supported campus Python installation
- pytest

## Setup

Create and activate a virtual environment if directed by your tutor, then install the project and pytest:

```powershell
python -m pip install -e .
python -m pip install pytest
```

## Run the objective smoke checker

```powershell
python scripts/smoke_check.py
```

The smoke checker verifies required paths, non-GUI imports, pytest collection, and the baseline tests. It does not calculate marks.

## Run the tests

```powershell
python -m pytest
```

## Run the application

```powershell
python -m zimp.main
```

## Definition of the supplied baseline

- a minimal Tkinter shell;
- a small domain state object;
- one illustrative movement contract and implementation;
- one thin controller boundary;
- one controllable fake;
- normal, failure-path, contract, and architecture tests;
- templates for ownership, evidence, and material AI use.

## Your assessed work

Your team must not treat the supplied movement example as the complete product. Each learner must implement a substantial component or vertical feature, integrate it across an explicit boundary, and verify expected and failure behaviour using pytest.

Read:

- `docs/architecture-map.md`
- `docs/student-work-boundaries.md`
- `docs/accessibility-checklist.md`
- `CONTRIBUTING.md`

## Troubleshooting

- If `_tkinter` cannot be imported, use the supported campus Python installation and report the exact Python command and error.
- If tests cannot find `zimp`, run `python -m pip install -e .` from the repository root.
- Do not create Tk windows at module import time.
