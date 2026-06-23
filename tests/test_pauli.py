"""Unit tests for the phase-free Pauli representation."""

from concatenated_steane.pauli import Pauli


def test_pauli_label_round_trip() -> None:
    pauli = Pauli.from_label("IXYZ")
    assert pauli.x_bits == (0, 1, 1, 0)
    assert pauli.z_bits == (0, 0, 1, 1)
    assert pauli.as_label() == "IXYZ"


def test_phase_free_composition_tracks_support_correctly() -> None:
    x_error = Pauli.single_qubit("X", qubit=2, n_qubits=5)
    z_error = Pauli.single_qubit("Z", qubit=2, n_qubits=5)
    y_error = x_error.compose(z_error)

    assert y_error.as_label() == "IIYII"
    assert y_error.compose(y_error) == Pauli.identity(5)


def test_symplectic_product_detects_anticommutation() -> None:
    x_on_zero = Pauli.single_qubit("X", qubit=0, n_qubits=3)
    z_on_zero = Pauli.single_qubit("Z", qubit=0, n_qubits=3)
    z_on_one = Pauli.single_qubit("Z", qubit=1, n_qubits=3)

    assert x_on_zero.anticommutes_with(z_on_zero)
    assert x_on_zero.commutes_with(z_on_one)
