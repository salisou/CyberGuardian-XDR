"""Export structured security data to JSON and CSV without leaking secrets."""
from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Mapping, Any

ALLOWED_FORMATS = {"json", "csv"}
MAX_ROWS = 100_000


def _safe_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def export_records(records: Iterable[Mapping[str, Any]], destination: str,
                   file_format: str = "json") -> Path:
    """Write a bounded list of records to a user-selected destination."""
    fmt = file_format.lower().lstrip(".")
    if fmt not in ALLOWED_FORMATS:
        raise ValueError("Formato supportato: json o csv")
    rows = []
    for index, record in enumerate(records):
        if index >= MAX_ROWS:
            raise ValueError(f"Numero massimo di righe superato ({MAX_ROWS})")
        if not isinstance(record, Mapping):
            raise TypeError("Ogni record deve essere una mappatura")
        rows.append({str(key): _safe_value(value) for key, value in record.items()})

    target = Path(destination).expanduser()
    if target.exists() and target.is_dir():
        raise ValueError("La destinazione deve essere un file")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    try:
        if fmt == "json":
            temporary.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            fieldnames = list(dict.fromkeys(key for row in rows for key in row))
            with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
                if fieldnames:
                    writer.writeheader()
                    writer.writerows(rows)
        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return target
