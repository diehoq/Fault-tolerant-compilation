# `ideal_memory.py`

`ideal_memory.py` implements the first encoded memory cycle.

One level-1 shot samples Pauli memory errors on the seven Steane data qubits,
computes the ideal syndrome, applies the lookup-table recovery in a Pauli frame,
and classifies the residual operator.

The classification uses commutation with the logical operators:

- a residual logical-X component anticommutes with logical Z,
- a residual logical-Z component anticommutes with logical X.

This module still uses ideal error correction. It does not yet include a noisy
syndrome-extraction circuit or ancilla verification.

Here, "ideal" means the syndrome bits and recovery operation are computed
perfectly from the physical data error. The memory faults are noisy, but the
error-correction machinery itself cannot introduce extra faults, mismeasure a
syndrome, or fail because of a bad ancilla.
