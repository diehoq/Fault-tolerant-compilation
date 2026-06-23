# `steane_code.py` Walkthrough

## Why this file exists

`steane_code.py` is the repository's fixed definition of the Steane `[[7,1,3]]` code. It keeps the connection to the classical `[7,4,3]` Hamming code visible instead of hiding it behind generated data.

## Line-by-line intent

- The module docstring explains that the Steane code is a CSS code built from the Hamming code.
- `ParityCheckMatrix` is a readable alias for the hard-coded binary matrix type.
- `HAMMING_PARITY_CHECK_MATRIX` is the central classical object. Its three rows define both the X-type and Z-type stabilizers.
- `_row_to_pauli()` turns one binary row into an actual `Pauli` object, either X-type or Z-type.
- The `SteaneCode` dataclass stores the fixed code parameters `n=7`, `k=1`, and `d=3`.
- `__post_init__()` checks that the hard-coded matrix really matches the declared code size.
- `parity_check_matrix()` returns the classical matrix directly so other modules can refer to it plainly.
- `hamming_columns()` exposes the seven distinct nonzero columns, which are exactly the single-qubit syndromes used by the decoder.
- `x_stabilizers()` and `z_stabilizers()` build the six stabilizer generators from the same classical matrix, making the CSS structure explicit.
- `stabilizer_generators()` just concatenates those two tuples for convenience.
- `logical_x()` and `logical_z()` return one standard pair of logical operators, both acting on all seven qubits.

## Important simplification

This file defines one standard representative for each logical operator. It does not enumerate every equivalent representative related by stabilizers, because Phase 1 only needs one explicit choice.
