import pytest

from vaultsh.crypto.derivation import DerivationPath, parse_derivation_path


def test_parse_and_render_path() -> None:
    path = parse_derivation_path("m/44'/0'/0'/0/12")
    assert path.components == ((44, True), (0, True), (0, True), (0, False), (12, False))
    assert str(path) == "m/44'/0'/0'/0/12"


@pytest.mark.parametrize("value", ["", "44/0", "m//1", "m/-1", "m/2147483648", "m/1x"])
def test_invalid_paths_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        DerivationPath.parse(value)
