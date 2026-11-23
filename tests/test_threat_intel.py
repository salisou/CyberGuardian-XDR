import pytest

from modules.threat_intel.service import validate_indicator


@pytest.mark.parametrize("value", ["127.0.0.1", "::1", "8.8.8.8"])
def test_valid_ip(value):
    assert validate_indicator(value, "ip") == value


@pytest.mark.parametrize("value", ["not-an-ip", "999.1.1.1", ""])
def test_invalid_ip(value):
    with pytest.raises(ValueError):
        validate_indicator(value, "ip")


def test_valid_sha256():
    digest = "a" * 64
    assert validate_indicator(digest, "hash") == digest


def test_invalid_hash():
    with pytest.raises(ValueError):
        validate_indicator("xyz", "hash")


def test_domain_normalization():
    assert validate_indicator("Example.COM.", "domain") == "example.com"


@pytest.mark.parametrize("value", ["https://example.com", "example.com/path", "example.com?x=1", "-invalid.example"])
def test_rejects_non_domain_values(value):
    with pytest.raises(ValueError):
        validate_indicator(value, "domain")


def test_international_domain_is_normalized():
    assert validate_indicator("caffè.example", "domain") == "xn--caff-5qa.example"
