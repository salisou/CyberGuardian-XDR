"""Read-only evidence inventory for explicitly selected local folders."""
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_FILES = 10_000
MAX_FILE_SIZE = 512 * 1024 * 1024


@dataclass
class EvidenceRecord:
    relative_path: str
    size: int
    modified_time_ns: int
    created_time_ns: int
    mode: str
    sha256: str | None
    status: str


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            total += len(chunk)
            if total > MAX_FILE_SIZE:
                raise ValueError("File oltre il limite di 512 MiB")
            digest.update(chunk)
    return digest.hexdigest()


def build_evidence_manifest(root_path: str, include_hashes: bool = True,
                            max_files: int = MAX_FILES) -> list[dict]:
    root = Path(root_path).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Selezionare una cartella")
    if not 1 <= max_files <= MAX_FILES:
        raise ValueError(f"Il limite deve essere compreso tra 1 e {MAX_FILES}")
    records: list[dict] = []
    for current, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(
            name for name in directories
            if not (Path(current) / name).is_symlink()
        )
        for filename in sorted(filenames):
            if len(records) >= max_files:
                records.append(asdict(EvidenceRecord(
                    "[LIMIT]", 0, 0, 0, "", None,
                    f"Interrotto: limite massimo di {max_files} file raggiunto",
                )))
                return records
            path = Path(current) / filename
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                info = path.stat(follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode):
                    continue
                digest = None
                status = "OK"
                if include_hashes:
                    if info.st_size > MAX_FILE_SIZE:
                        status = "SKIPPED_TOO_LARGE"
                    else:
                        try:
                            digest = _hash_file(path)
                        except (OSError, ValueError) as exc:
                            status = f"HASH_ERROR: {type(exc).__name__}"
                records.append(asdict(EvidenceRecord(
                    str(path.relative_to(root)), info.st_size,
                    info.st_mtime_ns, getattr(info, "st_ctime_ns", 0),
                    oct(stat.S_IMODE(info.st_mode)), digest, status,
                )))
            except OSError as exc:
                records.append(asdict(EvidenceRecord(
                    str(path.relative_to(root)), 0, 0, 0, "", None,
                    f"STAT_ERROR: {type(exc).__name__}",
                )))
    return records
