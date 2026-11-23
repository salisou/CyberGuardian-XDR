"""Optional, read-only Windows Event Log collector."""
from __future__ import annotations

import platform
from datetime import datetime, timezone


def collect_recent_events(log_name: str = "System", limit: int = 100,
                          event_types: tuple[int, ...] = (1, 2, 3)) -> list[dict]:
    if platform.system() != "Windows":
        raise OSError("La raccolta eventi è disponibile solo su Windows")
    if not 1 <= limit <= 1000:
        raise ValueError("Il limite deve essere compreso tra 1 e 1000")
    try:
        import win32evtlog  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Installare la dipendenza opzionale pywin32") from exc

    handle = win32evtlog.OpenEventLog(None, log_name)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    collected = []
    try:
        while len(collected) < limit:
            batch = win32evtlog.ReadEventLog(handle, flags, 0)
            if not batch:
                break
            for event in batch:
                if event.EventType not in event_types:
                    continue
                collected.append({
                    "log": log_name,
                    "event_id": event.EventID & 0xFFFF,
                    "source": str(event.SourceName),
                    "event_type": int(event.EventType),
                    "generated_at": event.TimeGenerated.Format(),
                    "record_number": int(event.RecordNumber),
                    "computer": str(event.ComputerName),
                    "message": " | ".join(str(item) for item in (event.StringInserts or [])),
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                })
                if len(collected) >= limit:
                    break
    finally:
        win32evtlog.CloseEventLog(handle)
    return collected
