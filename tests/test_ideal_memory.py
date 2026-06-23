"""Tests for ideal level-1 Steane memory simulation."""

import pytest

from concatenated_steane.noise import IndependentPauliMemoryNoise
from concatenated_steane.pauli import Pauli
from concatenated_steane.simulation.ideal_memory import (
    IdealSteaneMemorySimulator,
    sample_level1_ideal_memory_failures,
)


def test_ideal_recovery_corrects_single_qubit_errors() -> None:
    simulator = IdealSteaneMemorySimulator()

    for qubit_index in range(7):
        for letter in ("X", "Y", "Z"):
            error = Pauli.single_qubit(letter, qubit=qubit_index, n_qubits=7)
            result = simulator.run_cycle_for_error(error)

            assert result.residual == Pauli.identity(7)
            assert not result.any_logical_failure


def test_ideal_recovery_classifies_residual_logical_x_failure() -> None:
    simulator = IdealSteaneMemorySimulator()

    result = simulator.run_cycle_for_error(Pauli.from_label("XXXXXXX"))

    assert result.x_logical_failure
    assert not result.z_logical_failure


def test_ideal_recovery_classifies_residual_logical_z_failure() -> None:
    simulator = IdealSteaneMemorySimulator()

    result = simulator.run_cycle_for_error(Pauli.from_label("ZZZZZZZ"))

    assert not result.x_logical_failure
    assert result.z_logical_failure


def test_ideal_recovery_classifies_residual_logical_y_failure() -> None:
    simulator = IdealSteaneMemorySimulator()

    result = simulator.run_cycle_for_error(Pauli.from_label("YYYYYYY"))

    assert result.x_logical_failure
    assert result.z_logical_failure


def test_ideal_recovery_rejects_wrong_sized_error() -> None:
    simulator = IdealSteaneMemorySimulator()

    with pytest.raises(ValueError, match="7 qubits"):
        simulator.run_cycle_for_error(Pauli.identity(1))


def test_level1_sampling_has_no_failures_without_noise() -> None:
    result = sample_level1_ideal_memory_failures(
        IndependentPauliMemoryNoise(),
        shots=20,
        seed=123,
    )

    assert result.shots == 20
    assert result.x_logical_failures == 0
    assert result.z_logical_failures == 0
    assert result.joint_logical_failures == 0


def test_level1_sampling_reports_rates() -> None:
    result = sample_level1_ideal_memory_failures(
        IndependentPauliMemoryNoise(p_y=1.0),
        shots=5,
        seed=123,
    )

    assert result.x_logical_failure_rate == 1.0
    assert result.z_logical_failure_rate == 1.0
    assert result.joint_logical_failure_rate == 1.0


def test_level1_sampling_requires_positive_shots() -> None:
    with pytest.raises(ValueError, match="positive"):
        sample_level1_ideal_memory_failures(
            IndependentPauliMemoryNoise(),
            shots=0,
        )
