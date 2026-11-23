from datetime import datetime, timezone

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox
from sqlalchemy import select

from core.database import SessionLocal, SecurityEvent, ReportRecord
from modules.reports.exporter import export_records


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Esporta gli eventi di sicurezza registrati localmente. "
            "Controlla e oscura eventuali dati sensibili prima di condividere il report."
        ))
        controls = QHBoxLayout()
        self.format = QComboBox()
        self.format.addItem("JSON", "json")
        self.format.addItem("CSV", "csv")
        self.export_button = QPushButton("Esporta eventi")
        self.export_button.clicked.connect(self.export_events)
        controls.addWidget(self.format)
        controls.addWidget(self.export_button)
        layout.addLayout(controls)
        self.status = QLabel("Pronto")
        layout.addWidget(self.status)
        layout.addStretch(1)

    def export_events(self):
        fmt = self.format.currentData()
        extension = "json" if fmt == "json" else "csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Salva report", f"cyberguardian-events.{extension}",
            "JSON (*.json)" if fmt == "json" else "CSV (*.csv)"
        )
        if not path:
            return
        session = SessionLocal()
        try:
            events = session.scalars(select(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).limit(10000)).all()
            records = [{
                "timestamp": event.timestamp,
                "severity": event.severity,
                "source": event.source,
                "title": event.title,
                "details": event.details,
            } for event in events]
            saved = export_records(records, path, fmt)
            session.add(ReportRecord(
                format=fmt,
                file_path=str(saved),
                created_at=datetime.now(timezone.utc),
            ))
            session.commit()
            self.status.setText(f"Report esportato: {saved} · {len(records)} eventi")
        except Exception as exc:
            session.rollback()
            QMessageBox.warning(self, "Esportazione report", str(exc))
            self.status.setText("Esportazione non completata")
        finally:
            session.close()
