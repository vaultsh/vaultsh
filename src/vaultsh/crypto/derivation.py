"""Derivation-path parsing helpers; no private-key derivation is performed.

Each blockchain and wallet standard must select its own derivation rules and
be tested against authoritative vectors before key derivation is implemented.
"""

from dataclasses import dataclass

_HARDENED = 1 << 31
_MAX_INDEX = _HARDENED - 1


@dataclass(frozen=True, slots=True)
class DerivationPath:
    """A parsed BIP32-style path represented as (index, hardened) pairs."""

    components: tuple[tuple[int, bool], ...]

    def __post_init__(self) -> None:
        for index, hardened in self.components:
            if (
                isinstance(index, bool)
                or not isinstance(index, int)
                or not 0 <= index <= _MAX_INDEX
            ):
                raise ValueError("derivation indices must be integers between 0 and 2**31-1")
            if not isinstance(hardened, bool):
                raise ValueError("hardened flags must be booleans")

    @classmethod
    def parse(cls, value: str) -> "DerivationPath":
        """Parse strings such as ``m/44'/0'/0'/0/0``."""
        if not isinstance(value, str) or not value:
            raise ValueError("derivation path must be a non-empty string")
        parts = value.split("/")
        if parts[0] != "m":
            raise ValueError("derivation path must start with 'm'")
        components: list[tuple[int, bool]] = []
        for part in parts[1:]:
            if not part:
                raise ValueError("derivation path contains an empty component")
            hardened = part.endswith(("'", "h", "H"))
            digits = part[:-1] if hardened else part
            if not digits.isascii() or not digits.isdigit():
                raise ValueError(f"invalid derivation path component: {part!r}")
            index = int(digits)
            if index > _MAX_INDEX:
                raise ValueError("derivation index must be less than 2**31")
            components.append((index, hardened))
        return cls(tuple(components))

    def __str__(self) -> str:
        parts = ["m"]
        for index, hardened in self.components:
            suffix = "'" if hardened else ""
            parts.append(f"{index}{suffix}")
        return "/".join(parts)


def parse_derivation_path(value: str) -> DerivationPath:
    """Convenience wrapper around :meth:`DerivationPath.parse`."""
    return DerivationPath.parse(value)
