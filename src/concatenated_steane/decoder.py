"""Transparent lookup-table decoder for single-qubit Steane-code errors.

The Steane code uses the Hamming parity-check matrix, whose seven columns are
all distinct nonzero three-bit strings. That means every nonzero three-bit
syndrome identifies one qubit location.

In this first decoder we use that fact directly:

- decode the X-error syndrome into an X correction,
- decode the Z-error syndrome into a Z correction,
- combine them to produce the full Pauli correction.

This decoder is intentionally simple and designed for teaching, not for maximum
likelihood performance under arbitrary noise models.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .pauli import Pauli
from .steane_code import SteaneCode
from .syndromes import CSSSyndrome, SyndromeBits, full_syndrome


def _normalize_syndrome(syndrome: SyndromeBits, *, expected_length: int) -> SyndromeBits:
    """Validate that a syndrome is a binary tuple of the expected length."""

    normalized = tuple(int(bit) for bit in syndrome)
    if len(normalized) != expected_length:
        raise ValueError(
            f"Syndrome must have length {expected_length}, received length {len(normalized)}."
        )
    if any(bit not in (0, 1) for bit in normalized):
        raise ValueError(f"Syndrome must contain only 0/1 values, received {syndrome!r}.")
    return normalized


@dataclass(frozen=True)
class SteaneLookupDecoder:
    """Lookup-table decoder for the Phase 1 Steane-code implementation."""

    code: SteaneCode = field(default_factory=SteaneCode)

    def syndrome_lookup_table(self) -> dict[SyndromeBits, int | None]:
        """Map each three-bit syndrome to the qubit it identifies."""

        table: dict[SyndromeBits, int | None] = {(0, 0, 0): None}
        for qubit_index, column in enumerate(self.code.hamming_columns()):
            table[column] = qubit_index
        return table

    def decode_x_syndrome(self, syndrome: SyndromeBits) -> Pauli:
        """Convert an X-error syndrome into an X-type correction."""

        qubit_index = self._lookup_qubit_index(syndrome)
        if qubit_index is None:
            return Pauli.identity(self.code.n_data_qubits)
        return Pauli.single_qubit("X", qubit=qubit_index, n_qubits=self.code.n_data_qubits)

    def decode_z_syndrome(self, syndrome: SyndromeBits) -> Pauli:
        """Convert a Z-error syndrome into a Z-type correction."""

        qubit_index = self._lookup_qubit_index(syndrome)
        if qubit_index is None:
            return Pauli.identity(self.code.n_data_qubits)
        return Pauli.single_qubit("Z", qubit=qubit_index, n_qubits=self.code.n_data_qubits)

    def decode(self, syndrome: CSSSyndrome) -> Pauli:
        """Combine the two CSS halves into one phase-free Pauli correction."""

        x_correction = self.decode_x_syndrome(syndrome.x_error_syndrome)
        z_correction = self.decode_z_syndrome(syndrome.z_error_syndrome)
        return x_correction.compose(z_correction)

    def correction_for_error(self, error: Pauli) -> Pauli:
        """Convenience wrapper that syndromes and decodes one Pauli error."""

        return self.decode(full_syndrome(error, self.code))

    def _lookup_qubit_index(self, syndrome: SyndromeBits) -> int | None:
        """Return the qubit index associated with one three-bit syndrome."""

        normalized = _normalize_syndrome(
            syndrome,
            expected_length=len(self.code.parity_check_matrix()),
        )
        table = self.syndrome_lookup_table()
        if normalized not in table:
            raise ValueError(f"Unknown Steane syndrome {normalized!r}.")
        return table[normalized]
