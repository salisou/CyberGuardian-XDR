from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from modules.forensics.evidence import build_evidence_manifest
from modules.reports.exporter import export_records


class EvidenceWorker(QThread):
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, folder: str, include_hashes: bool):
        super().__init__()
        self.folder = folder
        self.include_hashes = include_hashes

    def run(self):
        try:
            self.completed.emit(build_evidence_manifest(self.folder, self.include_hashes))
        except Exception as exc:
            self.failed.emit(str(exc))


class ForensicsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.folder = ""
        self.records = []
        self.worker = None
        layout = QVBoxLayout(self)
        note = QLabel(
            "Crea un inventario forense in sola lettura: percorso relativo, dimensione, "
            "timestamp filesystem, permessi e SHA-256 opzionale. Non modifica i file."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        controls = QHBoxLayout()
        self.folder_label = QLabel("Nessuna cartella selezionata")
        choose = QPushButton("Seleziona cartella")
        choose.clicked.connect(self.choose_folder)
        self.hashes = QCheckBox("Calcola SHA-256")
        self.hashes.setChecked(True)
        self.collect_button = QPushButton("Crea inventario")
        self.collect_button.clicked.connect(self.collect)
        self.export_button = QPushButton("Esporta JSON")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export)
        controls.addWidget(choose)
        controls.addWidget(self.hashes)
        controls.addWidget(self.collect_button)
        controls.addWidget(self.export_button)
        layout.addLayout(controls)
        layout.addWidget(self.folder_label)
        self.status = QLabel("Pronto")
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Percorso relativo", "Dimensione", "SHA-256", "Stato"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table, 1)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella da inventariare")
        if folder:
            self.folder = folder
            self.folder_label.setText(folder)

    def collect(self):
        if not self.folder:
            QMessageBox.information(self, "Forensics", "Selezionare prima una cartella.")
            return
        self.collect_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.status.setText("Creazione inventario in corso…")
        self.worker = EvidenceWorker(self.folder, self.hashes.isChecked())
        self.worker.completed.connect(self.show_records)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(lambda: self.collect_button.setEnabled(True))
        self.worker.start()

    def show_records(self, records):
        self.records = records
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            values = [
                str(record["relative_path"]), str(record["size"]),
                str(record.get("sha256") or ""), str(record["status"]),
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.status.setText(f"Inventario completato · {len(records)} record")
        self.export_button.setEnabled(bool(records))

    def show_error(self, message):
        self.status.setText(f"Inventario non completato: {message}")
        QMessageBox.warning(self, "Forensics", message)

    def export(self):
        if not self.records:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Esporta inventario", "evidence-manifest.json", "JSON (*.json)")
        if not path:
            return
        try:
            saved = export_records(self.records, path, "json")
            self.status.setText(f"Inventario esportato: {saved}")
        except Exception as exc:
            QMessageBox.warning(self, "Esportazione inventario", str(exc))
