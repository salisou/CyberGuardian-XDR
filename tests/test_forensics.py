import hashlib

from modules.forensics.evidence import build_evidence_manifest


def test_evidence_manifest_hashes_files(tmp_path):
    sample = tmp_path / "evidence.txt"
    sample.write_text("evidence", encoding="utf-8")
    records = build_evidence_manifest(str(tmp_path))
    assert len(records) == 1
    assert records[0]["relative_path"] == "evidence.txt"
    assert records[0]["sha256"] == hashlib.sha256(b"evidence").hexdigest()


def test_evidence_manifest_can_skip_hashes(tmp_path):
    (tmp_path / "evidence.txt").write_text("evidence", encoding="utf-8")
    records = build_evidence_manifest(str(tmp_path), include_hashes=False)
    assert records[0]["sha256"] is None
