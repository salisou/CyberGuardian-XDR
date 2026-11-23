from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QPlainTextEdit, QMessageBox
)
from modules.ai_assistant.ollama_client import list_models, generate_response


class ModelWorker(QThread):
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)

    def run(self):
        try:
            self.completed.emit(list_models())
        except Exception as exc:
            self.failed.emit(str(exc))


class AssistantWorker(QThread):
    completed = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, model: str, prompt: str):
        super().__init__()
        self.model = model
        self.prompt = prompt

    def run(self):
        try:
            self.completed.emit(generate_response(self.model, self.prompt))
        except Exception as exc:
            self.failed.emit(str(exc))


class AIAssistantPage(QWidget):
    def __init__(self):
        super().__init__()
        self.model_worker = None
        self.assistant_worker = None
        layout = QVBoxLayout(self)
        note = QLabel(
            "Assistente AI locale tramite Ollama su 127.0.0.1. "
            "Il testo inserito viene inviato solo al servizio locale; non allegare password, "
            "chiavi API o dati personali non necessari."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        controls = QHBoxLayout()
        self.models = QComboBox()
        self.load_button = QPushButton("Carica modelli")
        self.load_button.clicked.connect(self.load_models)
        controls.addWidget(self.models, 1)
        controls.addWidget(self.load_button)
        layout.addLayout(controls)
        self.prompt = QPlainTextEdit()
        self.prompt.setPlaceholderText("Descrivi un evento, un alert o una domanda di sicurezza (max 20.000 caratteri)…")
        self.prompt.setMaximumBlockCount(1000)
        layout.addWidget(self.prompt, 1)
        self.ask_button = QPushButton("Invia al modello locale")
        self.ask_button.clicked.connect(self.ask)
        layout.addWidget(self.ask_button)
        self.status = QLabel("Ollama non ancora verificato")
        layout.addWidget(self.status)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output, 2)

    def load_models(self):
        self.load_button.setEnabled(False)
        self.status.setText("Connessione a Ollama…")
        self.model_worker = ModelWorker()
        self.model_worker.completed.connect(self.show_models)
        self.model_worker.failed.connect(self.show_error)
        self.model_worker.finished.connect(lambda: self.load_button.setEnabled(True))
        self.model_worker.start()

    def show_models(self, names):
        self.models.clear()
        self.models.addItems(names)
        self.status.setText(f"{len(names)} modelli disponibili" if names else "Nessun modello installato in Ollama")

    def ask(self):
        prompt = self.prompt.toPlainText().strip()
        if not self.models.currentText():
            QMessageBox.information(self, "Assistente AI", "Caricare e selezionare prima un modello Ollama.")
            return
        if not prompt:
            QMessageBox.information(self, "Assistente AI", "Inserire una domanda.")
            return
        self.ask_button.setEnabled(False)
        self.status.setText("Generazione locale in corso…")
        self.output.clear()
        self.assistant_worker = AssistantWorker(self.models.currentText(), prompt)
        self.assistant_worker.completed.connect(self.show_answer)
        self.assistant_worker.failed.connect(self.show_error)
        self.assistant_worker.finished.connect(lambda: self.ask_button.setEnabled(True))
        self.assistant_worker.start()

    def show_answer(self, answer):
        self.output.setPlainText(answer)
        self.status.setText("Risposta generata dal modello locale")

    def show_error(self, message):
        self.status.setText("Operazione non completata")
        QMessageBox.warning(self, "Assistente AI", message)
