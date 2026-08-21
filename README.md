# BCDE321 Advanced Programming: Zombies In My Pocket

This repository contains the ZIMP game created by "Just a couple of cool guys" for Assessment 2.

## Requirements

- Python 3.14 or later
- Tkinter
- pytest

## Setup

Create and activate a virtual environment, then install the project and pytest:

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

## How to Play

- The goal of the game is to disperse the corruption causing the zombies to appear
- To accomplish this the totem must be found in the house and buried in the garden
- The player must explore the house and fight zombies
- Use found items to help you survive encounters!

## Troubleshooting

- If `_tkinter` cannot be imported, use the supported campus Python installation and report the exact Python command and error.
- If tests cannot find `zimp`, run `python -m pip install -e .` from the repository root.
- Do not create Tk windows at module import time.
