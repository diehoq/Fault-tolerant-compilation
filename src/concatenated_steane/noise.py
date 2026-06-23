"""Memory-noise models used by the first Stim-backed simulations.

The MVP starts with independent single-qubit Pauli memory noise. On each idle
qubit, exactly one of four things happens:

- no error,
- an X error,
- a Y error,
- a Z error.

Stim represents this model directly with the `PAULI_CHANNEL_1(px, py, pz)`
instruction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import stim


def _validate_probability(value: float, *, name: str) -> float:
    """Return a probability as a float after checking its range."""

    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1, received {value!r}.")
    return probability


@dataclass(frozen=True)
class IndependentPauliMemoryNoise:
    """Independent single-qubit Pauli noise applied during a memory interval."""

    p_x: float = 0.0
    p_y: float = 0.0
    p_z: float = 0.0

    def __post_init__(self) -> None:
        """Validate the individual probabilities and total error probability."""

        p_x = _validate_probability(self.p_x, name="p_x")
        p_y = _validate_probability(self.p_y, name="p_y")
        p_z = _validate_probability(self.p_z, name="p_z")
        total = p_x + p_y + p_z
        if total > 1.0:
            raise ValueError(
                "The total Pauli error probability p_x + p_y + p_z must be at most 1."
            )
        object.__setattr__(self, "p_x", p_x)
        object.__setattr__(self, "p_y", p_y)
        object.__setattr__(self, "p_z", p_z)

    @classmethod
    def depolarizing(cls, probability: float) -> IndependentPauliMemoryNoise:
        """Build symmetric X/Y/Z memory noise with total probability `probability`."""

        total = _validate_probability(probability, name="probability")
        single_pauli_probability = total / 3.0
        return cls(
            p_x=single_pauli_probability,
            p_y=single_pauli_probability,
            p_z=single_pauli_probability,
        )

    @property
    def total_error_probability(self) -> float:
        """Return the probability that any non-identity Pauli error occurs."""

        return self.p_x + self.p_y + self.p_z

    def append_to_circuit(self, circuit: stim.Circuit, qubits: Iterable[int]) -> None:
        """Append this memory-noise channel to the given Stim circuit."""

        targets = list(qubits)
        if not targets:
            return
        circuit.append("PAULI_CHANNEL_1", targets, [self.p_x, self.p_y, self.p_z])
