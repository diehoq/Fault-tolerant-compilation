# `syndromes.py` Walkthrough

## Why this file exists

`syndromes.py` translates a Pauli error into the syndrome information that the decoder uses. Separating this file from `decoder.py` helps show that “compute syndrome” and “choose a correction” are different steps.

## Line-by-line intent

- The module docstring states the CSS rule: Z stabilizers detect X errors, and X stabilizers detect Z errors.
- `SyndromeBits` is just a readable name for a small tuple of bits.
- `CSSSyndrome` stores the two syndrome halves explicitly, one for X components and one for Z components.
- `as_tuple()` is a convenience method for flattening the pair into six bits when needed.
- `is_trivial()` checks whether both halves are zero.
- `_commutation_syndrome()` is the core calculation. For each check operator, it asks whether the error commutes or anticommutes with that check.
- `x_error_syndrome()` measures the error against the Z-type stabilizers because that is the syndrome that locates X components.
- `z_error_syndrome()` does the opposite half of the CSS logic.
- `full_syndrome()` bundles both halves together into one `CSSSyndrome`.
- `trivial_syndrome()` creates the all-zero reference value used in tests and later simulations.

## Important simplification

This file computes the syndrome algebraically from commutation relations. It does not yet simulate the physical circuit that would measure those stabilizers. That literal measurement circuit will appear in the Stim phase.
