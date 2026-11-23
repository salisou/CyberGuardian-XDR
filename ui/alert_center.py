from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from core.alert_engine import correlate_windows_events, list_alerts, persist_alerts, update_alert_status
from modules.windows_events.service import collect_recent_events


class CorrelationWorker(QThread):
    completed = pyqtSignal(int)
    failed = pyqtSignal(str)

    def __init__(self, log_name: str):
        super().__init__()
        self.log_name = log_name

    def run(self):
        try:
            events = collect_recent_events(self.log_name, limit=500)
            findings = correlate_windows_events(events)
            self.completed.emit(persist_alerts(findings))
        except Exception as exc:
            self.failed.emit(str(exc))


class AlertCenterPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.selected_alert_id = None
        layout = QVBoxLayout(self)
        note = QLabel(
            "Correlazione euristica degli eventi Windows 1102, 7045 e 4625. "
            "Le regole producono indicatori da verificare, non verdetti di compromissione."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        controls = QHBoxLayout()
        self.log_name = QComboBox()
        self.log_name.addItems(["Security", "System", "Application"])
        self.correlate_button = QPushButton("Esegui correlazione")
        self.correlate_button.clicked.connect(self.correlate)
        self.filter_status = QComboBox()
        self.filter_status.addItems(["Tutti", "OPEN", "ACKNOWLEDGED", "CLOSED"])
        self.filter_status.currentTextChanged.connect(lambda _: self.refresh())
        self.refresh_button = QPushButton("Aggiorna")
        self.refresh_button.clicked.connect(self.refresh)
        controls.addWidget(self.log_name)
        controls.addWidget(self.correlate_button)
        controls.addWidget(self.filter_status)
        controls.addWidget(self.refresh_button)
        layout.addLayout(controls)
        actions = QHBoxLayout()
        self.ack_button = QPushButton("Prendi in carico")
        self.ack_button.clicked.connect(lambda: self.change_status("ACKNOWLEDGED"))
        self.close_button = QPushButton("Chiudi alert")
        self.close_button.clicked.connect(lambda: self.change_status("CLOSED"))
        self.reopen_button = QPushButton("Riapri alert")
        self.reopen_button.clicked.connect(lambda: self.change_status("OPEN"))
        actions.addWidget(self.ack_button)
        actions.addWidget(self.close_button)
        actions.addWidget(self.reopen_button)
        layout.addLayout(actions)
        self.status = QLabel("Pronto")
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Severità", "Stato", "Titolo", "Origine", "Occorrenze", "Ultimo evento"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.selection_changed)
        layout.addWidget(self.table, 1)
        self.refresh()

    def correlate(self):
        self.correlate_button.setEnabled(False)
        self.status.setText("Lettura eventi e correlazione in corso…")
        self.worker = CorrelationWorker(self.log_name.currentText())
        self.worker.completed.connect(self.correlation_done)
        self.worker.failed.connect(self.correlation_failed)
        self.worker.finished.connect(lambda: self.correlate_button.setEnabled(True))
        self.worker.start()

    def correlation_done(self, count):
        self.status.setText(f"Correlazione completata · {count} alert creati o aggiornati")
        self.refresh()

    def correlation_failed(self, message):
        self.status.setText("Correlazione non completata")
        QMessageBox.warning(self, "Alert Center", message)

    def refresh(self):
        selected = self.filter_status.currentText() if hasattr(self, "filter_status") else "Tutti"
        alerts = list_alerts(None if selected == "Tutti" else selected)
        self.table.setRowCount(len(alerts))
        for row, alert in enumerate(alerts):
            values = [
                str(alert["id"]), alert["severity"], alert["status"], alert["title"],
                alert["source"], str(alert["occurrences"]), alert["last_seen"],
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.status.setText(f"{len(alerts)} alert visualizzati")

    def selection_changed(self):
        rows = self.table.selectionModel().selectedRows()
        self.selected_alert_id = int(self.table.item(rows[0].row(), 0).text()) if rows else None

    def change_status(self, status):
        if self.selected_alert_id is None:
            QMessageBox.information(self, "Alert Center", "Selezionare prima un alert.")
            return
        if update_alert_status(self.selected_alert_id, status):
            self.refresh()
        else:
            QMessageBox.warning(self, "Alert Center", "Alert non trovato.")
