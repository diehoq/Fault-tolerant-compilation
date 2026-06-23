"""Direct Stim sampling for small memory experiments.

This module is intentionally thin. Circuit construction lives in
`concatenated_steane.circuits`, while this module owns the mechanics of
compiling a Stim sampler and converting sampled measurement bits into failure
counts.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..circuits.physical_memory import MemoryBasis, build_level0_memory_circuit
from ..noise import IndependentPauliMemoryNoise


@dataclass(frozen=True)
class MemoryExperimentResult:
    """Summary of sampled failures for one memory experiment."""

    basis: MemoryBasis
    shots: int
    failures: int

    @property
    def failure_rate(self) -> float:
        """Return the sampled failure fraction."""

        return self.failures / self.shots


def sample_level0_memory_failures(
    noise: IndependentPauliMemoryNoise,
    *,
    basis: MemoryBasis,
    shots: int,
    seed: int | None = None,
) -> MemoryExperimentResult:
    """Estimate level-0 memory failures by sampling a real Stim circuit."""

    if shots <= 0:
        raise ValueError(f"shots must be positive, received {shots}.")

    circuit = build_level0_memory_circuit(noise, basis=basis)
    sampler = circuit.compile_sampler(seed=seed)
    samples = sampler.sample(shots)
    failures = int(samples[:, 0].sum())
    return MemoryExperimentResult(basis=basis, shots=shots, failures=failures)
