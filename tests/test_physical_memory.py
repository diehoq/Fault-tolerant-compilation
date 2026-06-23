"""Tests for direct Stim level-0 memory simulations."""

import pytest

from concatenated_steane.circuits.physical_memory import build_level0_memory_circuit
from concatenated_steane.noise import IndependentPauliMemoryNoise
from concatenated_steane.simulation.direct_stim import sample_level0_memory_failures


def test_level0_z_basis_circuit_is_explicit_stim() -> None:
    noise = IndependentPauliMemoryNoise(p_x=0.1, p_y=0.2, p_z=0.3)

    circuit = build_level0_memory_circuit(noise, basis="Z")

    assert str(circuit) == "R 0\nPAULI_CHANNEL_1(0.1, 0.2, 0.3) 0\nM 0"


def test_level0_x_basis_circuit_is_explicit_stim() -> None:
    noise = IndependentPauliMemoryNoise(p_x=0.1, p_y=0.2, p_z=0.3)

    circuit = build_level0_memory_circuit(noise, basis="X")

    assert str(circuit) == "RX 0\nPAULI_CHANNEL_1(0.1, 0.2, 0.3) 0\nMX 0"


@pytest.mark.parametrize(
    ("noise", "basis", "expected_failures"),
    [
        (IndependentPauliMemoryNoise(p_x=1.0), "Z", 8),
        (IndependentPauliMemoryNoise(p_z=1.0), "Z", 0),
        (IndependentPauliMemoryNoise(p_z=1.0), "X", 8),
        (IndependentPauliMemoryNoise(p_x=1.0), "X", 0),
        (IndependentPauliMemoryNoise(p_y=1.0), "Z", 8),
        (IndependentPauliMemoryNoise(p_y=1.0), "X", 8),
    ],
)
def test_level0_memory_sampling_detects_basis_flips(
    noise: IndependentPauliMemoryNoise,
    basis: str,
    expected_failures: int,
) -> None:
    result = sample_level0_memory_failures(noise, basis=basis, shots=8, seed=123)

    assert result.shots == 8
    assert result.failures == expected_failures
    assert result.failure_rate == expected_failures / 8


def test_level0_memory_sampling_requires_positive_shots() -> None:
    with pytest.raises(ValueError, match="positive"):
        sample_level0_memory_failures(
            IndependentPauliMemoryNoise(),
            basis="Z",
            shots=0,
        )
