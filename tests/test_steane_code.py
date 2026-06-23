"""Tests for the fixed Steane-code algebraic data."""

from concatenated_steane.steane_code import SteaneCode


def test_hamming_columns_are_unique_and_nonzero() -> None:
    code = SteaneCode()
    columns = code.hamming_columns()

    assert len(columns) == code.n_data_qubits
    assert len(set(columns)) == code.n_data_qubits
    assert all(column != (0, 0, 0) for column in columns)


def test_stabilizer_generators_commute_pairwise() -> None:
    code = SteaneCode()
    stabilizers = code.stabilizer_generators()

    for left in stabilizers:
        for right in stabilizers:
            assert left.commutes_with(right)


def test_logical_operators_commute_with_stabilizers() -> None:
    code = SteaneCode()

    for stabilizer in code.stabilizer_generators():
        assert code.logical_x().commutes_with(stabilizer)
        assert code.logical_z().commutes_with(stabilizer)


def test_logical_x_and_logical_z_anticommute() -> None:
    code = SteaneCode()
    assert code.logical_x().anticommutes_with(code.logical_z())
