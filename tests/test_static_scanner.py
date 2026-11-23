import hashlib

from modules.malware_analysis.static_scanner import scan_file


def test_static_scanner_hashes_without_execution(tmp_path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"benign test bytes")
    result = scan_file(str(sample))
    assert result.sha256 == hashlib.sha256(b"benign test bytes").hexdigest()
    assert result.size == len(b"benign test bytes")
    assert result.matches == []


def test_static_scanner_rejects_directory(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        scan_file(str(tmp_path))
