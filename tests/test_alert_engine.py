from datetime import datetime, timezone

from core.alert_engine import correlate_windows_events, persist_alerts, list_alerts, update_alert_status
from core.database import Base, engine


def test_windows_event_rules_detect_log_clear_and_failed_logons():
    events = [{"event_id": 1102}, *[{"event_id": 4625} for _ in range(6)]]
    findings = correlate_windows_events(events)
    rules = {item["rule_id"] for item in findings}
    assert "WINDOWS-LOG-CLEARED" in rules
    assert "WINDOWS-FAILED-LOGONS" in rules


def test_failed_logon_rule_has_threshold():
    assert not any(
        item["rule_id"] == "WINDOWS-FAILED-LOGONS"
        for item in correlate_windows_events([{"event_id": 4625}] * 4)
    )


def test_alert_lifecycle_persistence():
    Base.metadata.create_all(engine)
    finding = [{
        "rule_id": "TEST-ALERT",
        "severity": "MEDIUM",
        "title": "Test alert",
        "source": "Unit test",
        "details": "Synthetic test event",
    }]
    assert persist_alerts(finding, datetime.now(timezone.utc)) == 1
    alert = next(item for item in list_alerts() if item["title"] == "Test alert")
    assert alert["status"] == "OPEN"
    assert update_alert_status(alert["id"], "ACKNOWLEDGED")
    assert next(item for item in list_alerts() if item["id"] == alert["id"])["status"] == "ACKNOWLEDGED"
    assert update_alert_status(alert["id"], "CLOSED")
