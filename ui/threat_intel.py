from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from modules.threat_intel.service import lookup_all, validate_indicator


class LookupWorker(QThread):
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, indicator: str, kind: str):
        super().__init__()
        self.indicator = indicator
        self.kind = kind

    def run(self):
        try:
            self.completed.emit(lookup_all(self.indicator, self.kind))
        except Exception as exc:
            self.failed.emit(str(exc))


class ThreatIntelligencePage(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        layout = QVBoxLayout(self)
        intro = QLabel(
            "Verifica la reputazione di IP, domini e hash tramite provider esterni. "
            "Le interrogazioni inviano l'indicatore al provider selezionato."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        controls = QHBoxLayout()
        self.kind = QComboBox()
        self.kind.addItem("Indirizzo IP", "ip")
        self.kind.addItem("Dominio", "domain")
        self.kind.addItem("Hash file", "hash")
        self.indicator = QLineEdit()
        self.indicator.setPlaceholderText("Es. 8.8.8.8, example.org o SHA-256")
        self.lookup_button = QPushButton("Verifica reputazione")
        self.lookup_button.clicked.connect(self.start_lookup)
        controls.addWidget(self.kind)
        controls.addWidget(self.indicator, 1)
        controls.addWidget(self.lookup_button)
        layout.addLayout(controls)

        self.status = QLabel("Pronto")
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Provider", "Verdetto", "Punteggio", "Dettagli"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

    def start_lookup(self):
        value = self.indicator.text().strip()
        kind = self.kind.currentData()
        try:
            validate_indicator(value, kind)
        except ValueError as exc:
            QMessageBox.warning(self, "Indicatore non valido", str(exc))
            return
        self.lookup_button.setEnabled(False)
        self.status.setText("Interrogazione dei provider in corso…")
        self.table.setRowCount(0)
        self.worker = LookupWorker(value, kind)
        self.worker.completed.connect(self.show_results)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(lambda: self.lookup_button.setEnabled(True))
        self.worker.start()

    def show_results(self, results):
        self.table.setRowCount(len(results))
        for row, result in enumerate(results):
            values = [result.provider, result.verdict,
                      "" if result.score is None else str(result.score), result.details]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.status.setText(f"Controllo completato · {len(results)} provider")

    def show_error(self, message):
        self.status.setText("Errore durante la verifica")
        QMessageBox.warning(self, "Threat Intelligence", message)
