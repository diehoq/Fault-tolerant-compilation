"""Tests for explicit memory-noise models."""

import pytest
import stim

from concatenated_steane.noise import IndependentPauliMemoryNoise


def test_depolarizing_noise_splits_probability_evenly() -> None:
    noise = IndependentPauliMemoryNoise.depolarizing(0.3)

    assert noise.p_x == pytest.approx(0.1)
    assert noise.p_y == pytest.approx(0.1)
    assert noise.p_z == pytest.approx(0.1)
    assert noise.total_error_probability == pytest.approx(0.3)


def test_pauli_noise_rejects_invalid_probabilities() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        IndependentPauliMemoryNoise(p_x=-0.1)

    with pytest.raises(ValueError, match="at most 1"):
        IndependentPauliMemoryNoise(p_x=0.4, p_y=0.4, p_z=0.4)


def test_pauli_noise_appends_real_stim_instruction() -> None:
    circuit = stim.Circuit()
    noise = IndependentPauliMemoryNoise(p_x=0.1, p_y=0.2, p_z=0.3)

    noise.append_to_circuit(circuit, [0, 1])

    assert str(circuit) == "PAULI_CHANNEL_1(0.1, 0.2, 0.3) 0 1"
