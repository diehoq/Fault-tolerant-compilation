# Concatenated Steane Memory

This repository studies memory-only error suppression in the concatenated Steane `[[7,1,3]]` code.

The project is intentionally pedagogy-first. Each module is meant to be readable on its own, tested directly, and accompanied by explanation docs that make the implementation traceable line by line.

The current milestone implements the algebraic foundations:

- phase-free Pauli operators,
- the Steane code stabilizers and logical operators,
- explicit syndrome computation,
- a transparent lookup-table decoder for all single-qubit `X`, `Y`, and `Z` errors.
- independent Pauli memory-noise channels,
- real Stim circuits for level-0 physical memory checks.
- ideal level-1 Steane memory sampling with logical `X`/`Z` failure classification.

Later phases will add noisy syndrome-extraction circuits and recursive higher-level analysis.

Run the first suppression scan with:

```bash
python scripts/run_level_scan.py
```

This writes `results/level_scan.csv` and `results/level_scan.png`.
It also writes `results/level1_pseudo_thresholds.csv`, which estimates where
the level-1 logical failure rate crosses the level-0 physical failure rate.
