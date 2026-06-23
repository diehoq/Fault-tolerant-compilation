"""Syndrome computation for the Steane [[7,1,3]] code.

Because the Steane code is a CSS code, X errors and Z errors can be decoded
separately:

- X errors are detected by measuring Z-type stabilizers.
- Z errors are detected by measuring X-type stabilizers.

This module keeps those two pieces separate so the decoder logic stays easy to
trace.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from .pauli import BitTuple, Pauli
from .steane_code import SteaneCode

SyndromeBits: TypeAlias = BitTuple


@dataclass(frozen=True)
class CSSSyndrome:
    """A pair of three-bit syndromes for CSS decoding.

    Attributes:
        x_error_syndrome: The syndrome used to locate X components of the error.
        z_error_syndrome: The syndrome used to locate Z components of the error.
    """

    x_error_syndrome: SyndromeBits
    z_error_syndrome: SyndromeBits

    def as_tuple(self) -> tuple[int, ...]:
        """Flatten the CSS syndrome into one six-bit tuple."""

        return self.x_error_syndrome + self.z_error_syndrome

    def is_trivial(self) -> bool:
        """Return True when both syndrome halves are all zero."""

        return all(bit == 0 for bit in self.as_tuple())


def _commutation_syndrome(error: Pauli, checks: tuple[Pauli, ...]) -> SyndromeBits:
    """Compute syndrome bits by testing commutation with each check operator."""

    if not checks:
        return ()
    if error.n_qubits != checks[0].n_qubits:
        raise ValueError("The error and check operators must act on the same number of qubits.")
    return tuple(error.symplectic_product(check) for check in checks)


def x_error_syndrome(error: Pauli, code: SteaneCode) -> SyndromeBits:
    """Return the syndrome used to decode X components of the error."""

    return _commutation_syndrome(error, code.z_stabilizers())


def z_error_syndrome(error: Pauli, code: SteaneCode) -> SyndromeBits:
    """Return the syndrome used to decode Z components of the error."""

    return _commutation_syndrome(error, code.x_stabilizers())


def full_syndrome(error: Pauli, code: SteaneCode) -> CSSSyndrome:
    """Return both CSS syndrome halves for one Pauli error."""

    return CSSSyndrome(
        x_error_syndrome=x_error_syndrome(error, code),
        z_error_syndrome=z_error_syndrome(error, code),
    )


def trivial_syndrome(code: SteaneCode) -> CSSSyndrome:
    """Return the all-zero syndrome for the given code."""

    zero_bits = (0,) * len(code.parity_check_matrix())
    return CSSSyndrome(zero_bits, zero_bits)
