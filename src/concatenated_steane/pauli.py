"""Phase-free Pauli operators for small stabilizer-code calculations.

The core representation is the binary symplectic form used throughout stabilizer
theory. For each qubit we store one bit telling us whether an X component is
present and one bit telling us whether a Z component is present.

Examples:

- I -> x=0, z=0
- X -> x=1, z=0
- Z -> x=0, z=1
- Y -> x=1, z=1

We intentionally ignore global phases such as -1 or i. That information matters
for exact operator multiplication, but it is not needed for syndrome
computation, commutation checks, or the simple decoder used in Phase 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence, TypeAlias

BitTuple: TypeAlias = tuple[int, ...]
SingleQubitPauli: TypeAlias = Literal["I", "X", "Y", "Z"]


def _normalize_bits(bits: Sequence[int], *, name: str) -> BitTuple:
    """Convert a bit-like sequence into a tuple of literal 0/1 integers."""

    normalized = tuple(int(bit) for bit in bits)
    if any(bit not in (0, 1) for bit in normalized):
        raise ValueError(f"{name} must contain only 0/1 values, received {bits!r}.")
    return normalized


def _letter_from_bits(x_bit: int, z_bit: int) -> SingleQubitPauli:
    """Convert one pair of symplectic bits into an I/X/Y/Z label."""

    if (x_bit, z_bit) == (0, 0):
        return "I"
    if (x_bit, z_bit) == (1, 0):
        return "X"
    if (x_bit, z_bit) == (0, 1):
        return "Z"
    return "Y"


@dataclass(frozen=True)
class Pauli:
    """A phase-free n-qubit Pauli operator.

    Attributes:
        x_bits: A 1 at position j means the operator has an X component on qubit j.
        z_bits: A 1 at position j means the operator has a Z component on qubit j.
    """

    x_bits: BitTuple
    z_bits: BitTuple

    def __post_init__(self) -> None:
        """Validate that the Pauli stores two equally long binary strings."""

        normalized_x = _normalize_bits(self.x_bits, name="x_bits")
        normalized_z = _normalize_bits(self.z_bits, name="z_bits")
        if len(normalized_x) != len(normalized_z):
            raise ValueError("x_bits and z_bits must have the same length.")
        object.__setattr__(self, "x_bits", normalized_x)
        object.__setattr__(self, "z_bits", normalized_z)

    @property
    def n_qubits(self) -> int:
        """Return the number of qubits acted on by this Pauli operator."""

        return len(self.x_bits)

    @property
    def weight(self) -> int:
        """Return the number of qubits where the operator is not the identity."""

        return sum(1 for x_bit, z_bit in zip(self.x_bits, self.z_bits) if x_bit or z_bit)

    @property
    def support(self) -> tuple[int, ...]:
        """Return the qubit indices where the operator acts nontrivially."""

        return tuple(
            index
            for index, (x_bit, z_bit) in enumerate(zip(self.x_bits, self.z_bits))
            if x_bit or z_bit
        )

    @classmethod
    def identity(cls, n_qubits: int) -> Pauli:
        """Construct the identity operator on n qubits."""

        if n_qubits < 0:
            raise ValueError("n_qubits must be non-negative.")
        return cls((0,) * n_qubits, (0,) * n_qubits)

    @classmethod
    def from_label(cls, label: str) -> Pauli:
        """Build a Pauli from a string such as 'IXYZ'."""

        x_bits: list[int] = []
        z_bits: list[int] = []
        for letter in label.upper():
            if letter == "I":
                x_bits.append(0)
                z_bits.append(0)
            elif letter == "X":
                x_bits.append(1)
                z_bits.append(0)
            elif letter == "Y":
                x_bits.append(1)
                z_bits.append(1)
            elif letter == "Z":
                x_bits.append(0)
                z_bits.append(1)
            else:
                raise ValueError(f"Unsupported Pauli letter {letter!r}.")
        return cls(tuple(x_bits), tuple(z_bits))

    @classmethod
    def single_qubit(cls, letter: SingleQubitPauli, *, qubit: int, n_qubits: int) -> Pauli:
        """Construct an n-qubit Pauli that acts on only one qubit."""

        if not 0 <= qubit < n_qubits:
            raise ValueError(f"qubit index {qubit} is out of range for {n_qubits} qubits.")
        x_bits = [0] * n_qubits
        z_bits = [0] * n_qubits
        if letter in ("X", "Y"):
            x_bits[qubit] = 1
        if letter in ("Z", "Y"):
            z_bits[qubit] = 1
        return cls(tuple(x_bits), tuple(z_bits))

    def as_label(self) -> str:
        """Render the operator as a human-readable I/X/Y/Z string."""

        return "".join(_letter_from_bits(x_bit, z_bit) for x_bit, z_bit in zip(self.x_bits, self.z_bits))

    def compose(self, other: Pauli) -> Pauli:
        """Multiply two Paulis while discarding the global phase.

        In the binary symplectic representation, phase-free multiplication is
        just bitwise XOR of the X and Z support vectors.
        """

        self._check_compatible_size(other)
        return Pauli(
            tuple(left ^ right for left, right in zip(self.x_bits, other.x_bits)),
            tuple(left ^ right for left, right in zip(self.z_bits, other.z_bits)),
        )

    def symplectic_product(self, other: Pauli) -> int:
        """Return 0 if the operators commute and 1 if they anticommute."""

        self._check_compatible_size(other)
        total = sum(
            (self_x & other_z) ^ (self_z & other_x)
            for self_x, self_z, other_x, other_z in zip(
                self.x_bits,
                self.z_bits,
                other.x_bits,
                other.z_bits,
            )
        )
        return total % 2

    def commutes_with(self, other: Pauli) -> bool:
        """Return True exactly when the two Paulis commute."""

        return self.symplectic_product(other) == 0

    def anticommutes_with(self, other: Pauli) -> bool:
        """Return True exactly when the two Paulis anticommute."""

        return self.symplectic_product(other) == 1

    def _check_compatible_size(self, other: Pauli) -> None:
        """Raise an error if two Paulis act on different numbers of qubits."""

        if self.n_qubits != other.n_qubits:
            raise ValueError(
                "Pauli operators must act on the same number of qubits: "
                f"{self.n_qubits} != {other.n_qubits}."
            )

    def __str__(self) -> str:
        """Return the I/X/Y/Z label when the object is printed."""

        return self.as_label()
