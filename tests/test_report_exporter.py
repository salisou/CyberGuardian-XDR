import csv
import json
from datetime import datetime, timezone

import pytest

from modules.reports.exporter import export_records


def test_json_export(tmp_path):
    target = tmp_path / "report.json"
    export_records([{"event": "test", "created": datetime(2026, 1, 1, tzinfo=timezone.utc)}], str(target))
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload[0]["event"] == "test"
    assert payload[0]["created"].startswith("2026-01-01")


def test_csv_export(tmp_path):
    target = tmp_path / "report.csv"
    export_records([{"event": "test", "severity": "LOW"}], str(target), "csv")
    with target.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows == [{"event": "test", "severity": "LOW"}]


def test_rejects_unknown_format(tmp_path):
    with pytest.raises(ValueError):
        export_records([], str(tmp_path / "report.xml"), "xml")
