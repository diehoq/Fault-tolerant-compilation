# `decoder.py` Walkthrough

## Why this file exists

`decoder.py` takes the syndrome and turns it into a correction. The goal in Phase 1 is not to build the strongest possible decoder. The goal is to build the most inspectable decoder that is obviously correct for all single-qubit errors.

## Line-by-line intent

- The module docstring explains the key Hamming-code fact used by the decoder: the seven columns of the parity-check matrix are the seven nonzero three-bit syndromes.
- `_normalize_syndrome()` rejects malformed inputs early so the lookup logic stays trustworthy.
- `SteaneLookupDecoder` stores the code object it decodes.
- `syndrome_lookup_table()` constructs the transparent mapping from three-bit syndrome to qubit index, with `(0, 0, 0)` mapped to `None`.
- `decode_x_syndrome()` turns an X-error syndrome into an X correction on the identified qubit.
- `decode_z_syndrome()` does the same for Z-error syndromes.
- `decode()` combines the two CSS halves. If both halves point to the same qubit, the composed phase-free correction is `Y` on that qubit.
- `correction_for_error()` is a convenience wrapper used in tests and later simulations.
- `_lookup_qubit_index()` is the internal validation layer that normalizes the syndrome bits and checks that they appear in the lookup table.

## Important simplification

This decoder is a lookup-table decoder specialized to the Steane code and to the pedagogical Phase 1 goal. It is not a general maximum-likelihood decoder and it does not yet model degeneracy beyond the simplest single-qubit setting.
