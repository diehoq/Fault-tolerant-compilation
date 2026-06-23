# `physical_memory.py`

`physical_memory.py` builds the first real Stim circuits in the repository.

Level 0 means one unencoded physical qubit. The circuit prepares a basis
eigenstate, applies one interval of memory noise, and measures in the same
basis.

- In the `Z` basis, an `X` or `Y` component flips the measurement.
- In the `X` basis, a `Z` or `Y` component flips the measurement.

This does not yet simulate encoded error correction. It is the smallest
Stim-backed baseline needed before building level-1 Steane memory cycles.
