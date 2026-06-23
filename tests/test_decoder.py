"""Tests for the transparent Steane-code lookup decoder."""

from itertools import product

import pytest

from concatenated_steane.decoder import SteaneLookupDecoder
from concatenated_steane.pauli import Pauli
from concatenated_steane.steane_code import SteaneCode
from concatenated_steane.syndromes import full_syndrome, trivial_syndrome


def test_lookup_table_covers_every_three_bit_syndrome() -> None:
    decoder = SteaneLookupDecoder()
    table = decoder.syndrome_lookup_table()

    assert len(table) == 8
    for syndrome in product((0, 1), repeat=3):
        assert syndrome in table


def test_zero_syndrome_decodes_to_identity() -> None:
    code = SteaneCode()
    decoder = SteaneLookupDecoder(code)

    assert decoder.decode(trivial_syndrome(code)) == Pauli.identity(code.n_data_qubits)


@pytest.mark.parametrize("letter", ["X", "Y", "Z"])
@pytest.mark.parametrize("qubit_index", range(7))
def test_lookup_decoder_recovers_all_single_qubit_pauli_errors(
    qubit_index: int,
    letter: str,
) -> None:
    code = SteaneCode()
    decoder = SteaneLookupDecoder(code)
    error = Pauli.single_qubit(letter, qubit=qubit_index, n_qubits=code.n_data_qubits)

    correction = decoder.correction_for_error(error)
    residual = error.compose(correction)

    assert residual == Pauli.identity(code.n_data_qubits)
    assert full_syndrome(residual, code) == trivial_syndrome(code)
