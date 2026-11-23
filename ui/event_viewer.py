from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem

from modules.windows_events.service import collect_recent_events


class EventLogWorker(QThread):
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, log_name: str):
        super().__init__()
        self.log_name = log_name

    def run(self):
        try:
            self.completed.emit(collect_recent_events(self.log_name, limit=200))
        except Exception as exc:
            self.failed.emit(str(exc))


class EventViewerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        layout = QVBoxLayout(self)
        note = QLabel("Visualizzazione in sola lettura degli eventi recenti di Windows.")
        layout.addWidget(note)
        controls = QHBoxLayout()
        self.log_name = QComboBox()
        self.log_name.addItems(["System", "Application", "Security"])
        self.refresh_button = QPushButton("Carica eventi")
        self.refresh_button.clicked.connect(self.load_events)
        controls.addWidget(self.log_name)
        controls.addWidget(self.refresh_button)
        layout.addLayout(controls)
        self.status = QLabel("Pronto")
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Data", "ID", "Origine", "Tipo", "Messaggio"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

    def load_events(self):
        self.refresh_button.setEnabled(False)
        self.status.setText("Lettura eventi…")
        self.worker = EventLogWorker(self.log_name.currentText())
        self.worker.completed.connect(self.show_events)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(lambda: self.refresh_button.setEnabled(True))
        self.worker.start()

    def show_events(self, events):
        self.table.setRowCount(len(events))
        for row, event in enumerate(events):
            values = [event["generated_at"], str(event["event_id"]), event["source"],
                      str(event["event_type"]), event["message"]]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.status.setText(f"{len(events)} eventi caricati · {self.log_name.currentText()}")

    def show_error(self, message):
        self.status.setText(f"Impossibile caricare gli eventi: {message}")
