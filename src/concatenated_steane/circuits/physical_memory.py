"""Stim circuits for the unencoded level-0 memory experiment.

Level 0 means one physical qubit with no error-correcting code. We prepare an
eigenstate, apply one interval of memory noise, and measure in the same basis.

The two supported bases expose the two physical Pauli components separately:

- Z-basis memory detects X or Y components as bit flips.
- X-basis memory detects Z or Y components as phase flips.
"""

from __future__ import annotations

from typing import Literal, TypeAlias

import stim

from ..noise import IndependentPauliMemoryNoise

MemoryBasis: TypeAlias = Literal["X", "Z"]


def build_level0_memory_circuit(
    noise: IndependentPauliMemoryNoise,
    *,
    basis: MemoryBasis,
) -> stim.Circuit:
    """Build a one-qubit Stim circuit for one level-0 memory interval."""

    circuit = stim.Circuit()
    if basis == "Z":
        circuit.append("R", [0])
        noise.append_to_circuit(circuit, [0])
        circuit.append("M", [0])
        return circuit
    if basis == "X":
        circuit.append("RX", [0])
        noise.append_to_circuit(circuit, [0])
        circuit.append("MX", [0])
        return circuit
    raise ValueError(f"Unsupported memory basis {basis!r}; expected 'X' or 'Z'.")
