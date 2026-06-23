"""Ideal level-1 Steane memory simulation.

This module implements the first encoded memory experiment. One cycle is:

1. draw independent physical Pauli memory faults on the seven data qubits,
2. compute the ideal Steane syndrome,
3. apply the lookup-decoder correction in a Pauli frame,
4. classify any remaining logical X or logical Z component.

The error-correction step is idealized on purpose. No noisy syndrome-extraction
circuit is modeled here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..decoder import SteaneLookupDecoder
from ..noise import IndependentPauliMemoryNoise
from ..pauli import Pauli
from ..steane_code import SteaneCode


@dataclass(frozen=True)
class IdealSteaneCycleResult:
    """Result of applying ideal Steane recovery to one physical error."""

    physical_error: Pauli
    correction: Pauli
    residual: Pauli
    x_logical_failure: bool
    z_logical_failure: bool

    @property
    def any_logical_failure(self) -> bool:
        """Return True when either logical component failed."""

        return self.x_logical_failure or self.z_logical_failure


@dataclass(frozen=True)
class Level1MemoryExperimentResult:
    """Aggregated logical failures from many ideal level-1 memory cycles."""

    shots: int
    x_logical_failures: int
    z_logical_failures: int
    joint_logical_failures: int

    @property
    def x_logical_failure_rate(self) -> float:
        """Return the sampled logical-X failure probability per cycle."""

        return self.x_logical_failures / self.shots

    @property
    def z_logical_failure_rate(self) -> float:
        """Return the sampled logical-Z failure probability per cycle."""

        return self.z_logical_failures / self.shots

    @property
    def joint_logical_failure_rate(self) -> float:
        """Return the sampled probability that both logical components fail."""

        return self.joint_logical_failures / self.shots


@dataclass(frozen=True)
class IdealSteaneMemorySimulator:
    """Simulator for one level-1 Steane block with ideal error correction."""

    code: SteaneCode = field(default_factory=SteaneCode)
    decoder: SteaneLookupDecoder | None = None

    def __post_init__(self) -> None:
        """Create a matching decoder when one was not provided."""

        if self.decoder is None:
            object.__setattr__(self, "decoder", SteaneLookupDecoder(self.code))

    def run_cycle_for_error(self, physical_error: Pauli) -> IdealSteaneCycleResult:
        """Apply ideal recovery to one seven-qubit physical error."""

        if physical_error.n_qubits != self.code.n_data_qubits:
            raise ValueError(
                "A level-1 Steane memory cycle expects an error on "
                f"{self.code.n_data_qubits} qubits, received {physical_error.n_qubits}."
            )

        correction = self.decoder.correction_for_error(physical_error)
        residual = physical_error.compose(correction)
        x_logical_failure = residual.anticommutes_with(self.code.logical_z())
        z_logical_failure = residual.anticommutes_with(self.code.logical_x())
        return IdealSteaneCycleResult(
            physical_error=physical_error,
            correction=correction,
            residual=residual,
            x_logical_failure=x_logical_failure,
            z_logical_failure=z_logical_failure,
        )

    def sample_cycles(
        self,
        noise: IndependentPauliMemoryNoise,
        *,
        shots: int,
        seed: int | None = None,
    ) -> Level1MemoryExperimentResult:
        """Sample independent physical errors and classify ideal-recovery failures."""

        if shots <= 0:
            raise ValueError(f"shots must be positive, received {shots}.")

        rng = np.random.default_rng(seed)
        x_failures = 0
        z_failures = 0
        joint_failures = 0
        for _ in range(shots):
            physical_error = _sample_physical_error(
                noise,
                n_qubits=self.code.n_data_qubits,
                rng=rng,
            )
            result = self.run_cycle_for_error(physical_error)
            x_failures += int(result.x_logical_failure)
            z_failures += int(result.z_logical_failure)
            joint_failures += int(result.x_logical_failure and result.z_logical_failure)
        return Level1MemoryExperimentResult(
            shots=shots,
            x_logical_failures=x_failures,
            z_logical_failures=z_failures,
            joint_logical_failures=joint_failures,
        )


def sample_level1_ideal_memory_failures(
    noise: IndependentPauliMemoryNoise,
    *,
    shots: int,
    seed: int | None = None,
) -> Level1MemoryExperimentResult:
    """Convenience wrapper for sampling a default level-1 Steane memory block."""

    return IdealSteaneMemorySimulator().sample_cycles(noise, shots=shots, seed=seed)


def _sample_physical_error(
    noise: IndependentPauliMemoryNoise,
    *,
    n_qubits: int,
    rng: np.random.Generator,
) -> Pauli:
    """Draw one n-qubit Pauli error from independent memory noise."""

    no_error_probability = 1.0 - noise.total_error_probability
    letters = rng.choice(
        ["I", "X", "Y", "Z"],
        size=n_qubits,
        p=[no_error_probability, noise.p_x, noise.p_y, noise.p_z],
    )
    return Pauli.from_label("".join(str(letter) for letter in letters))
