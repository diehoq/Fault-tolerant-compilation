# `pauli.py` Walkthrough

## Why this file exists

`pauli.py` gives the whole repository a common language for Pauli errors. Later modules should not each invent their own ad hoc way to describe `X`, `Y`, and `Z` faults.

## Line-by-line intent

- The module docstring explains the binary symplectic representation and says up front that global phase is intentionally ignored.
- `BitTuple` and `SingleQubitPauli` make the type signatures readable.
- `_normalize_bits()` exists so invalid values such as `2` or `-1` are rejected immediately instead of quietly propagating.
- `_letter_from_bits()` is the inverse of the symplectic encoding for one qubit, which keeps string rendering explicit.
- The `Pauli` dataclass stores the actual representation: one tuple for X support and one tuple for Z support.
- `__post_init__()` enforces that both bit strings are binary and have the same length.
- `n_qubits`, `weight`, and `support` are small convenience properties that keep later code readable.
- `identity()` creates the all-zero symplectic vector.
- `from_label()` turns human-readable strings like `IXYZ` into the internal binary representation.
- `single_qubit()` is the most common constructor used in tests and decoding logic.
- `as_label()` converts the internal representation back into a readable string.
- `compose()` uses bitwise XOR because Pauli multiplication, after discarding global phase, is addition mod 2 in the symplectic representation.
- `symplectic_product()` is the core commutation rule. It returns `1` when two Paulis anticommute and `0` when they commute.
- `commutes_with()` and `anticommutes_with()` are thin wrappers that make later code easier to read.
- `_check_compatible_size()` guards against accidentally comparing operators on different numbers of qubits.
- `__str__()` makes printed objects easy to inspect in tests or notebooks.

## Important simplification

This file does not track the global phase of a Pauli operator. That is deliberate. Phase is unnecessary for the syndrome and decoder logic in Phase 1, and leaving it out keeps the implementation easier to learn.
