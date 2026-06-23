# Concatenated Steane Memory

This repository studies memory-only error suppression in the concatenated Steane `[[7,1,3]]` code.

The project is intentionally pedagogy-first. Each module is meant to be readable on its own, tested directly, and accompanied by explanation docs that make the implementation traceable line by line.

The current milestone implements the algebraic foundations:

- phase-free Pauli operators,
- the Steane code stabilizers and logical operators,
- explicit syndrome computation,
- a transparent lookup-table decoder for all single-qubit `X`, `Y`, and `Z` errors.

Later phases will add real Stim circuits, level-0 physical memory simulation, level-1 encoded memory cycles, and recursive higher-level analysis.
