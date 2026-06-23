"""Tests for explicit Steane-code syndrome computation."""

from concatenated_steane.pauli import Pauli
from concatenated_steane.steane_code import SteaneCode
from concatenated_steane.syndromes import full_syndrome, trivial_syndrome, x_error_syndrome, z_error_syndrome


def test_identity_has_trivial_syndrome() -> None:
    code = SteaneCode()
    identity = Pauli.identity(code.n_data_qubits)

    assert full_syndrome(identity, code) == trivial_syndrome(code)


def test_single_qubit_x_syndromes_match_hamming_columns() -> None:
    code = SteaneCode()

    for qubit_index, expected_syndrome in enumerate(code.hamming_columns()):
        error = Pauli.single_qubit("X", qubit=qubit_index, n_qubits=code.n_data_qubits)
        assert x_error_syndrome(error, code) == expected_syndrome
        assert z_error_syndrome(error, code) == (0, 0, 0)


def test_single_qubit_z_syndromes_match_hamming_columns() -> None:
    code = SteaneCode()

    for qubit_index, expected_syndrome in enumerate(code.hamming_columns()):
        error = Pauli.single_qubit("Z", qubit=qubit_index, n_qubits=code.n_data_qubits)
        assert x_error_syndrome(error, code) == (0, 0, 0)
        assert z_error_syndrome(error, code) == expected_syndrome


def test_single_qubit_y_errors_trigger_both_css_syndromes() -> None:
    code = SteaneCode()

    for qubit_index, expected_syndrome in enumerate(code.hamming_columns()):
        error = Pauli.single_qubit("Y", qubit=qubit_index, n_qubits=code.n_data_qubits)
        syndrome = full_syndrome(error, code)
        assert syndrome.x_error_syndrome == expected_syndrome
        assert syndrome.z_error_syndrome == expected_syndrome
