# `noise.py`

`noise.py` defines the first physical noise model used by the repository:
independent single-qubit Pauli memory noise.

The model stores three probabilities: `p_x`, `p_y`, and `p_z`. Their sum is the
probability that a non-identity Pauli error happens during one memory interval.
The remaining probability is the no-error case.

Stim supports this model directly through `PAULI_CHANNEL_1(px, py, pz)`, so the
module includes an `append_to_circuit` method that writes the channel into an
actual `stim.Circuit`.
