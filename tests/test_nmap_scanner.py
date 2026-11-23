import pytest

from modules.vulnerability_scanner.nmap_scanner import validate_target, run_nmap_scan


@pytest.mark.parametrize("target,expected", [
    ("192.168.1.10", "192.168.1.10"),
    ("192.168.1.0/24", "192.168.1.0/24"),
    ("Example.COM", "example.com"),
])
def test_valid_targets(target, expected):
    assert validate_target(target) == expected


@pytest.mark.parametrize("target", ["", "bad target", "example.com;whoami", "10.0.0.0/16"])
def test_invalid_or_oversized_targets(target):
    with pytest.raises(ValueError):
        validate_target(target)


def test_scan_requires_explicit_authorization():
    with pytest.raises(PermissionError):
        run_nmap_scan("127.0.0.1", authorized=False)
