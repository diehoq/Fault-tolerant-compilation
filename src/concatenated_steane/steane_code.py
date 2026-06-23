"""Explicit algebraic data for the Steane [[7,1,3]] code.

The Steane code is a CSS code built from the classical [7,4,3] Hamming code.
This module keeps that structure visible by storing the Hamming parity-check
matrix directly and building the X-type and Z-type stabilizers from its rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from .pauli import BitTuple, Pauli

ParityCheckMatrix: TypeAlias = tuple[BitTuple, ...]

HAMMING_PARITY_CHECK_MATRIX: ParityCheckMatrix = (
    (1, 0, 0, 1, 0, 1, 1),
    (0, 1, 0, 1, 1, 0, 1),
    (0, 0, 1, 0, 1, 1, 1),
)


def _row_to_pauli(row: BitTuple, *, pauli_letter: str) -> Pauli:
    """Turn one binary parity-check row into an X-type or Z-type Pauli."""

    if pauli_letter == "X":
        return Pauli(row, (0,) * len(row))
    if pauli_letter == "Z":
        return Pauli((0,) * len(row), row)
    raise ValueError(f"Unsupported stabilizer type {pauli_letter!r}.")


@dataclass(frozen=True)
class SteaneCode:
    """Container for the fixed algebraic structure of the Steane code."""

    n_data_qubits: int = 7
    n_logical_qubits: int = 1
    distance: int = 3

    def __post_init__(self) -> None:
        """Verify that the hard-coded matrix matches the declared code size."""

        if len(HAMMING_PARITY_CHECK_MATRIX) != 3:
            raise ValueError("The Steane code should have three parity-check rows.")
        if any(len(row) != self.n_data_qubits for row in HAMMING_PARITY_CHECK_MATRIX):
            raise ValueError("Each Hamming parity-check row must have seven entries.")

    def parity_check_matrix(self) -> ParityCheckMatrix:
        """Return the [7,4,3] Hamming parity-check matrix used by the code."""

        return HAMMING_PARITY_CHECK_MATRIX

    def hamming_columns(self) -> tuple[BitTuple, ...]:
        """Return the seven nonzero syndrome columns of the Hamming matrix."""

        return tuple(
            tuple(row[column_index] for row in HAMMING_PARITY_CHECK_MATRIX)
            for column_index in range(self.n_data_qubits)
        )

    def x_stabilizers(self) -> tuple[Pauli, ...]:
        """Return the three X-type stabilizer generators."""

        return tuple(_row_to_pauli(row, pauli_letter="X") for row in HAMMING_PARITY_CHECK_MATRIX)

    def z_stabilizers(self) -> tuple[Pauli, ...]:
        """Return the three Z-type stabilizer generators."""

        return tuple(_row_to_pauli(row, pauli_letter="Z") for row in HAMMING_PARITY_CHECK_MATRIX)

    def stabilizer_generators(self) -> tuple[Pauli, ...]:
        """Return all six stabilizer generators in a single tuple."""

        return self.x_stabilizers() + self.z_stabilizers()

    def logical_x(self) -> Pauli:
        """Return one standard representative of the logical X operator."""

        return Pauli.from_label("XXXXXXX")

    def logical_z(self) -> Pauli:
        """Return one standard representative of the logical Z operator."""

        return Pauli.from_label("ZZZZZZZ")
